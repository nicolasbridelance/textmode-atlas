# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Validated readings of acquired works, with visible origin and method (ADR 0027)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class Reading(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)
    locale: Literal["en", "fr"]
    kind: Literal["explanation", "science", "vision"]
    nature: Literal["documented", "testified", "inferred"]
    level: Literal["interpretation"] = "interpretation"
    asserted_by: str = Field(pattern=r"^(human:|identity:|algo:).+")
    method: str = Field(min_length=1)
    input_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    sources: list[HttpUrl] = Field(default_factory=list)
    uncertainty: str = Field(min_length=1)
    model: str | None = None
    prompt_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    representation_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def origin(self) -> Self:
        if self.nature == "inferred" and not self.asserted_by.startswith("algo:"):
            raise ValueError("inferred readings require an algo: author")
        if self.kind == "vision" and not (
            self.model and self.prompt_sha256 and self.representation_sha256
        ):
            raise ValueError(
                "vision readings require model and prompt identity and input rendering"
            )
        if self.kind == "vision" and self.nature != "inferred":
            raise ValueError("model judgements are inferred, never documented facts")
        return self


def readings(root: Path, sha256: str) -> list[dict[str, object]]:
    path = root / f"{sha256}.json"
    if not path.exists():
        return []
    found = [Reading.model_validate(row) for row in json.loads(path.read_text(encoding="utf-8"))]
    if any(row.input_sha256 != sha256 for row in found):
        raise ValueError("reading input does not match the acquired work")
    return [row.model_dump(mode="json") for row in found]
