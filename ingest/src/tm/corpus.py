# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Models for the YAML files in `corpus/`: rendering profiles, collections, radios, the
audience grid.

Pydantic models are the source of truth. The JSON Schemas in `corpus/schema/` are derived from
them by `tm corpus schema`; CI checks that they are current and that every YAML file conforms.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Annotated, Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

from tm.i18n import LocalizedText

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Slug = Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]

System = Literal[
    "ansi-cp437",
    "ascii",
    "xbin",
    "petscii",
    "atascii",
    "teletext",
    "videotex",
    "shift-jis",
    "amiga-latin1",
    "unicode",
]


class Font(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file: str
    sha256: Sha256


class Profile(BaseModel):
    """Display parameters of one system at one time. No profile is "the true one"."""

    model_config = ConfigDict(extra="forbid")

    title: LocalizedText
    system: System
    grid: Annotated[str, Field(pattern=r"^\d+x\d+$")]
    cell: Annotated[str, Field(pattern=r"^\d+x\d+$")]
    font: Font
    palette: Literal["vga", "ega", "c64-pepto", "atari-ntsc", "teletext"] = "vga"
    high_bg: Literal["blink", "ice"] = "blink"
    letter_spacing: Literal[8, 9] = 9
    pixel_aspect: Annotated[float, Field(gt=0.5, lt=2.5)] = 1.0
    baud: Annotated[int, Field(gt=0)] | None = None
    sources: list[str] = Field(min_length=1)


class Collection(BaseModel):
    """A collection is a saved query over the facets of works."""

    model_config = ConfigDict(extra="forbid")

    title: LocalizedText
    description: LocalizedText | None = None
    where: dict[Literal["usage", "system", "scene", "channel", "function"], list[str]]
    order_by: Literal["date_min", "date_max", "title"] = "date_min"


class Radio(BaseModel):
    """A scene radio station whose stream the museum may play."""

    model_config = ConfigDict(extra="forbid")

    id: Slug
    name: str
    homepage: HttpUrl
    stream: HttpUrl | None = None
    agreement: Literal["none", "requested", "granted", "refused"] = "none"
    verified_at: dt.date | None = None
    now_playing: HttpUrl | None = None
    notes: str | None = None

    @field_validator("stream")
    @classmethod
    def _https_only(_cls, v: HttpUrl | None) -> HttpUrl | None:
        if v is not None and v.scheme != "https":
            raise ValueError("a stream must use HTTPS to be playable by the site")
        return v

    @property
    def playable(self) -> bool:
        return self.agreement == "granted" and self.stream is not None


class Radios(BaseModel):
    model_config = ConfigDict(extra="forbid")

    radios: list[Radio]


LevelCode = Literal["3", "7", "12", "16", "18", "withheld"]
Glyph = Annotated[int, Field(ge=0, le=255)]  # a CP437 code point
Code = Annotated[str, Field(pattern=r"^[a-z]+(_[a-z]+)*$")]  # also a database value
VgaColour = Annotated[int, Field(ge=0, le=15)]


class Colours(BaseModel):
    model_config = ConfigDict(extra="forbid")

    background: VgaColour
    ink: VgaColour


class Level(BaseModel):
    """An age at which a work may be shown, or `withheld`: never shown."""

    model_config = ConfigDict(extra="forbid")

    code: LevelCode
    min_age: Annotated[int, Field(ge=0)] | None
    colour: Colours
    label: LocalizedText
    summary: LocalizedText


class Descriptor(BaseModel):
    """Something a work shows, and the level each degree of it calls for."""

    model_config = ConfigDict(extra="forbid")

    code: Code
    glyph: Glyph
    label: LocalizedText
    levels: dict[LevelCode, LocalizedText] = Field(min_length=1)


class Notice(BaseModel):
    """A warning for every visitor, whatever the level."""

    model_config = ConfigDict(extra="forbid")

    code: Code
    glyph: Glyph
    label: LocalizedText
    text: LocalizedText


class Grid(BaseModel):
    """The museum's audience grid (ADR 0020), adapted from PEGI."""

    model_config = ConfigDict(extra="forbid")

    version: Annotated[int, Field(ge=1)]
    levels: list[Level]
    descriptors: list[Descriptor]
    notices: list[Notice]
    rules: list[LocalizedText] = Field(min_length=1)

    @model_validator(mode="after")
    def _consistent(self) -> Grid:
        codes = [level.code for level in self.levels]
        if codes != ["3", "7", "12", "16", "18", "withheld"]:
            raise ValueError(f"levels must be 3, 7, 12, 16, 18, withheld in that order: {codes}")
        names = [d.code for d in self.descriptors] + [n.code for n in self.notices]
        if len(set(names)) != len(names):
            raise ValueError("descriptor and notice codes must be unique")
        for descriptor in self.descriptors:
            if "3" in descriptor.levels:
                raise ValueError(f"{descriptor.code}: level 3 means no descriptor")
        return self


KINDS: dict[str, type[BaseModel]] = {
    "profile": Profile,
    "collection": Collection,
    "radios": Radios,
    "grid": Grid,
}


def kind_of(path: Path) -> str:
    if path.name == "radios.yaml":
        return "radios"
    if path.parent.name == "profiles":
        return "profile"
    if path.parent.name == "collections":
        return "collection"
    if path.parent.name == "ratings" and path.name == "grid.yaml":
        return "grid"
    raise ValueError(f"unknown corpus file: {path}")


def load(path: Path) -> BaseModel:
    data: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    return KINDS[kind_of(path)].model_validate(data)


def load_grid(path: Path) -> Grid:
    return Grid.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def corpus_files(root: Path) -> list[Path]:
    files = sorted([*root.glob("profiles/*.yaml"), *root.glob("collections/*.yaml")])
    extra = [root / "radios.yaml", root / "ratings" / "grid.yaml"]
    return files + [path for path in extra if path.exists()]


def json_schemas() -> dict[str, str]:
    """JSON Schema of each file kind, serialized deterministically."""
    return {
        f"{kind}.schema.json": json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False)
        + "\n"
        for kind, model in KINDS.items()
    }
