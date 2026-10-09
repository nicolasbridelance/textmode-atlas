# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Pilot samples (ADR 0017): drawn once from a frame, frozen in Git, read back by the build.

`tm dataset draw` runs the frame query of a pilot definition, draws the units with
`tm.sampling`, adds the units chosen by hand with their reason, and writes `sample.yaml` beside
the definition. The build reads that frozen list as a CTE named `sample` (unit, stratum, weight,
selection, reason); a frame query changed since the draw stops it.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Connection, text

from tm.sampling import draw


class SampleError(Exception):
    """A sample that cannot be drawn, or no longer matches its frame."""


class Addition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    unit: str
    reason: str


class Sample(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frame: str  # query file: one row per unit, with its stratum and order columns
    unit: str
    label: str  # frame column that names a unit for the reader of sample.yaml
    stratum: str
    order: list[str]
    per_stratum: int
    seed: int
    additions: list[Addition] = []  # chosen by hand, each with its reason; no weight


SAMPLE_FILE = "sample.yaml"
# REUSE-IgnoreStart: the header of the files `write_sample` writes, not this file's license.
SAMPLE_HEADER = (
    "# SPDX-FileCopyrightText: 2026 textmode-atlas contributors\n"
    "# SPDX-License-Identifier: CC0-1.0\n"
    "#\n"
    "# Written by `tm dataset draw {name}`: do not edit; change dataset.yaml and draw again.\n"
)
# REUSE-IgnoreEnd
SAMPLE_COLUMNS = ("unit", "stratum", "weight", "selection", "reason")
SAMPLE_CTE = (
    "sample (unit, stratum, weight, selection, reason) as (select * from unnest("
    "cast(:sample_unit as text[]), cast(:sample_stratum as text[]),"
    " cast(:sample_weight as double precision[]), cast(:sample_selection as text[]),"
    " cast(:sample_reason as text[])))"
)


@dataclass(frozen=True)
class FrozenSample:
    units: list[dict[str, object]]
    digest: str

    def params(self) -> dict[str, list[object]]:
        return {f"sample_{c}": [u[c] for u in self.units] for c in SAMPLE_COLUMNS}


def write_sample(
    conn: Connection, directory: Path, name: str, spec: Sample, params: Mapping[str, object]
) -> Path:
    """Draw the sample from its frame and write `sample.yaml` in `directory`, to be committed."""
    query = (directory / spec.frame).read_text(encoding="utf-8")
    frame = [dict(r) for r in conn.execute(text(query), dict(params)).mappings()]
    strata = {str(r[spec.unit]): str(r[spec.stratum]) for r in frame}
    labels = {str(r[spec.unit]): str(r[spec.label]) for r in frame}
    drawn = draw(
        frame,
        unit=spec.unit,
        stratum=spec.stratum,
        order=spec.order,
        per_stratum=spec.per_stratum,
        seed=spec.seed,
    )
    units: list[dict[str, object]] = [
        {
            "unit": d.unit,
            "label": labels[d.unit],
            "stratum": d.stratum,
            "weight": d.weight,
            "selection": "drawn",
            "reason": None,
        }
        for d in drawn
    ]
    taken = {d.unit for d in drawn}
    for addition in spec.additions:
        if addition.unit not in strata:
            raise SampleError(f"addition {addition.unit} is not in the frame")
        if addition.unit in taken:
            raise SampleError(f"addition {addition.unit} was drawn already")
        units.append(
            {
                "unit": addition.unit,
                "label": labels[addition.unit],
                "stratum": strata[addition.unit],
                "weight": None,
                "selection": "added",
                "reason": addition.reason,
            }
        )
    sizes: dict[str, int] = {}
    for stratum in strata.values():
        sizes[stratum] = sizes.get(stratum, 0) + 1
    document = {
        "frame_sha256": hashlib.sha256(query.encode()).hexdigest(),
        "frame_sizes": dict(sorted(sizes.items())),
        "seed": spec.seed,
        "units": units,
    }
    path = directory / SAMPLE_FILE
    body = yaml.safe_dump(document, sort_keys=False, allow_unicode=True)
    path.write_text(SAMPLE_HEADER.format(name=name) + body, "utf-8")
    return path


def frozen_sample(directory: Path, spec: Sample | None) -> FrozenSample | None:
    """The sample frozen in `directory`, checked against the frame it was drawn from."""
    if spec is None:
        return None
    path = directory / SAMPLE_FILE
    if not path.exists():
        raise SampleError(f"{path} is missing: run `tm dataset draw {directory.name}`")
    raw = path.read_bytes()
    document = yaml.safe_load(raw)
    frame = (directory / spec.frame).read_text(encoding="utf-8")
    if document["frame_sha256"] != hashlib.sha256(frame.encode()).hexdigest():
        raise SampleError(f"{spec.frame} changed since the sample was drawn: draw it again")
    return FrozenSample(document["units"], hashlib.sha256(raw).hexdigest())
