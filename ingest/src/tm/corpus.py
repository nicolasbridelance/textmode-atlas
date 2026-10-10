# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Models for the YAML files in `corpus/`: rendering profiles, collections, radios, the
audience grid, the registry of practices (ADR 0031), and the registries a grid's header names
(ADR 0026): character systems, character sets, palettes.

Pydantic models are the source of truth. The JSON Schemas in `corpus/schema/` are derived from
them by `tm corpus schema`; CI checks that they are current and that every YAML file conforms.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Annotated, Any, Literal, get_args

import yaml
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator
from tm_render.grid import ATTRIBUTES

from tm.i18n import LocalizedText
from tm.rights import SceneArchive

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


GlyphClass = Literal[
    "blank", "block", "half_block", "shade", "line", "mosaic", "letter", "digit", "punctuation",
    "symbol", "control",
]  # fmt: skip
Size = Annotated[str, Field(pattern=r"^\d+x\d+$")]


class CharsetGlyph(BaseModel):
    """One character of a set: its number, what Unicode calls it when it can, its class."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    index: Annotated[int, Field(ge=0)]
    unicode: Annotated[str, Field(pattern=r"^[0-9A-F]{4,6}$")] | None
    glyph_class: GlyphClass = Field(alias="class")


class Charset(BaseModel):
    """The repertoire a grid's glyph numbers index (ADR 0026)."""

    model_config = ConfigDict(extra="forbid")

    title: LocalizedText
    size: Annotated[int, Field(gt=0)]
    glyphs: list[CharsetGlyph]
    sources: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def _every_glyph_once(self) -> Charset:
        if [glyph.index for glyph in self.glyphs] != list(range(self.size)):
            raise ValueError(f"glyphs must list indexes 0 to {self.size - 1} in order")
        return self


class Palette(BaseModel):
    """The colours a grid's `fg` and `bg` index, in index order."""

    model_config = ConfigDict(extra="forbid")

    title: LocalizedText
    colours: list[Annotated[str, Field(pattern=r"^#[0-9A-F]{6}$")]] = Field(min_length=2)
    sources: list[str] = Field(min_length=1)


class CharacterSystem(BaseModel):
    """A machine or medium a grid belongs to: what its charsets, palettes and fonts can be."""

    model_config = ConfigDict(extra="forbid")

    title: LocalizedText
    charsets: list[Slug] = Field(min_length=1)
    palettes: list[Slug] = Field(min_length=1)
    fonts: list[Slug] = Field(min_length=1)
    cell: Size
    attributes: list[str]
    sources: list[str] = Field(min_length=1)

    @field_validator("attributes")
    @classmethod
    def _known_attributes(cls, names: list[str]) -> list[str]:
        unknown = sorted(set(names) - set(ATTRIBUTES))
        if unknown:
            raise ValueError(f"unknown attributes {unknown}; known: {sorted(ATTRIBUTES)}")
        return names


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


Holding = Literal["file", "excerpt", "capture", "reproduction", "record"]
LeadId = Annotated[str, Field(pattern=r"^[QHIC]\d+$")]


class Family(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: Slug
    label: LocalizedText


class Representative(BaseModel):
    """The artifact that stands for a practice in the holdings: its bytes, and `<source>:<path>`
    where it came from."""

    model_config = ConfigDict(extra="forbid")

    sha256: Sha256
    path: Annotated[str, Field(pattern=r"^[a-z0-9]+([.-][a-z0-9]+)*:\S.*$")]


class Practice(BaseModel):
    """One character art, held or not (ADR 0031)."""

    model_config = ConfigDict(extra="forbid")

    code: Slug
    label: LocalizedText
    family: Slug
    holding: list[Holding] = Field(min_length=1)
    representative: Representative | None = None
    sources: list[str] = []
    leads: list[LeadId] = []
    note: str | None = None


class Practices(BaseModel):
    """The registry of practices: what the museum of the character arts covers, and its gaps."""

    model_config = ConfigDict(extra="forbid")

    version: Annotated[int, Field(ge=1)]
    families: list[Family] = Field(min_length=1)
    practices: list[Practice] = Field(min_length=1)

    @model_validator(mode="after")
    def _consistent(self) -> Practices:
        families = [family.code for family in self.families]
        codes = [practice.code for practice in self.practices]
        for name, values in (("family", families), ("practice", codes)):
            twice = sorted({v for v in values if values.count(v) > 1})
            if twice:
                raise ValueError(f"{name} codes must be unique: {', '.join(twice)}")
        unknown = sorted({p.family for p in self.practices} - set(families))
        if unknown:
            raise ValueError(f"unknown families: {', '.join(unknown)}")
        return self

    def held(self) -> list[Practice]:
        return [practice for practice in self.practices if practice.representative]


Basis = Literal["scene", "license", "public-domain", "excerpt"]
DeclaredFormat = Literal["ansi", "ascii", "rtty", "vt100", "unicode"]
Lines = Annotated[str, Field(pattern=r"^[1-9][0-9]*-[1-9][0-9]*$")]
SourceName = Annotated[str, Field(pattern=r"^[a-z0-9]+([.-][a-z0-9]+)*$")]


class AcquisitionSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: SourceName
    url: HttpUrl
    note: str


class Acquisition(BaseModel):
    """One file chosen to represent a practice, and why the museum may hold it (ADR 0031)."""

    model_config = ConfigDict(extra="forbid")

    practice: Slug
    title: str
    url: HttpUrl
    source: SourceName
    basis: Basis
    license: str | None = None
    # The art kind, when the file does not say it (a printer poster saved as .txt).
    format: DeclaredFormat | None = None
    # An excerpt (ADR 0032): the lines cut from the fetched page, tags removed if it is HTML,
    # and the maker as signed, or "unknown".
    lines: Lines | None = None
    html: bool = False
    # A regular expression whose group keeps, from each line of the cut, only the drawing.
    pattern: str | None = None
    credit: str | None = None
    why: LocalizedText

    @model_validator(mode="after")
    def _basis_is_complete(self) -> Acquisition:
        if self.basis == "license" and not self.license:
            raise ValueError(f"{self.url}: a licensed file names its licence")
        if self.basis == "scene" and self.source not in get_args(SceneArchive):
            raise ValueError(f"{self.url}: {self.source} is not a scene archive (ADR 0009)")
        if (self.basis == "excerpt") != bool(self.lines and self.credit):
            raise ValueError(f"{self.url}: an excerpt, and only an excerpt, names lines and credit")
        if self.pattern is not None and re.compile(self.pattern).groups != 1:
            raise ValueError(f"{self.url}: a pattern keeps one group of each line")
        return self


class Acquisitions(BaseModel):
    """The manifest of single acquisitions: what `tm acquire` fetches, from where, on what basis."""

    model_config = ConfigDict(extra="forbid")

    version: Annotated[int, Field(ge=1)]
    sources: list[AcquisitionSource] = Field(min_length=1)
    entries: list[Acquisition] = Field(min_length=1)

    @model_validator(mode="after")
    def _consistent(self) -> Acquisitions:
        names = {source.name for source in self.sources}
        unknown = sorted({entry.source for entry in self.entries} - names)
        if unknown:
            raise ValueError(f"unknown sources: {', '.join(unknown)}")
        urls = [str(entry.url) for entry in self.entries]
        twice = sorted({url for url in urls if urls.count(url) > 1})
        if twice:
            raise ValueError(f"each file is acquired once: {', '.join(twice)}")
        return self

    def source(self, name: str) -> AcquisitionSource:
        return next(source for source in self.sources if source.name == name)


KINDS: dict[str, type[BaseModel]] = {
    "system": CharacterSystem,
    "charset": Charset,
    "palette": Palette,
    "profile": Profile,
    "collection": Collection,
    "radios": Radios,
    "grid": Grid,
    "practices": Practices,
    "acquisitions": Acquisitions,
}


REGISTRIES = {"systems": "system", "charsets": "charset", "palettes": "palette"}


# Files named for what they hold, at the corpus root or in their folder.
NAMED = {
    "radios.yaml": "radios",
    "practices.yaml": "practices",
    "acquisitions.yaml": "acquisitions",
    "ratings/grid.yaml": "grid",
}
FOLDERS = {**REGISTRIES, "profiles": "profile", "collections": "collection"}


def kind_of(path: Path) -> str:
    folder = path.parent.name
    for name in (path.name, f"{folder}/{path.name}"):
        if name in NAMED:
            return NAMED[name]
    if folder in FOLDERS:
        return FOLDERS[folder]
    raise ValueError(f"unknown corpus file: {path}")


def load(path: Path) -> BaseModel:
    data: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    return KINDS[kind_of(path)].model_validate(data)


def load_grid(path: Path) -> Grid:
    return Grid.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def load_practices(path: Path) -> Practices:
    return Practices.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def practices_view(root: Path) -> str:
    """The registry as the site reads it (`corpus/practices.json`): each practice with what
    represents it, and, for an acquired representative, its title, reason, source and basis."""
    registry = load_practices(root / "practices.yaml")
    manifest = root / "acquisitions.yaml"
    chosen = (
        {e.practice: e for e in load_acquisitions(manifest).entries} if manifest.exists() else {}
    )
    practices = []
    for practice in registry.practices:
        entry = chosen.get(practice.code)
        acquired = (
            {
                "title": entry.title,
                "why": entry.why,
                "url": str(entry.url),
                "basis": entry.basis,
                "license": entry.license,
                "credit": entry.credit,
            }
            if entry and practice.representative
            else None
        )
        practices.append(
            practice.model_dump(include={"code", "label", "family", "holding", "representative"})
            | {"acquired": acquired}
        )
    view = {"families": [f.model_dump() for f in registry.families], "practices": practices}
    return json.dumps(view, indent=2, ensure_ascii=False) + "\n"


def corpus_files(root: Path) -> list[Path]:
    folders = ["profiles", "collections", *REGISTRIES]
    files = sorted(path for folder in folders for path in root.glob(f"{folder}/*.yaml"))
    extra = [
        root / "radios.yaml",
        root / "practices.yaml",
        root / "acquisitions.yaml",
        root / "ratings" / "grid.yaml",
    ]
    return files + [path for path in extra if path.exists()]


def json_schemas() -> dict[str, str]:
    """JSON Schema of each file kind, serialized deterministically."""
    return {
        f"{kind}.schema.json": json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False)
        + "\n"
        for kind, model in KINDS.items()
    }


def load_acquisitions(path: Path) -> Acquisitions:
    return Acquisitions.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def _unknown_practices(root: Path) -> list[str]:
    manifest = root / "acquisitions.yaml"
    if not manifest.exists():
        return []
    practices = {p.code for p in load_practices(root / "practices.yaml").practices}
    return [
        f"{manifest}: {entry.url} names no practice {entry.practice}"
        for entry in load_acquisitions(manifest).entries
        if entry.practice not in practices
    ]


def broken_references(root: Path) -> list[str]:
    """What a character system or an acquisition names that the corpus does not hold."""
    problems = _unknown_practices(root)
    for path in sorted(root.glob("systems/*.yaml")):
        system = CharacterSystem.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        wanted = [
            *(root / "charsets" / f"{name}.yaml" for name in system.charsets),
            *(root / "palettes" / f"{name}.yaml" for name in system.palettes),
            *(root / "fonts" / f"{name}.f16" for name in system.fonts),
        ]
        problems.extend(f"{path}: no {item}" for item in wanted if not item.exists())
    return problems
