# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Datasets: frozen extracts of the database that research reads instead of the database.

A dataset is defined in `datasets/<name>/`: `dataset.yaml` names its tables, each with a SQL
query, the key that orders and identifies its rows, and its typed, described columns. A build
writes one Parquet file per table and a manifest (migration, extractor versions, SHA-256 of every
query and file) into `datasets/build/<name>/<version>/`. Nothing in a build depends on when it
ran: building twice from the same database gives byte-identical files.

A pilot dataset also declares a `sample` (ADR 0017): `tm dataset draw` runs its frame query,
draws the units, and writes `sample.yaml` beside the definition, to be committed. The build
reads that frozen list as a CTE named `sample` (unit, stratum, weight, selection, reason), which
the tables' queries and filters can use; a frame query changed since the draw stops the build.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pyarrow as pa
import pyarrow.parquet as pq
import yaml
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Connection, text
from tm_analysis.versions import FEATURES_VERSION, TEXT_VERSION
from tm_render.versions import DECODER_VERSION, RENDERER_VERSION

from tm.decode import DECODER
from tm.sampling import draw

ColumnType = Literal["string", "int32", "int64", "float64", "bool", "list<int32>", "list<string>"]
ARROW_TYPES: dict[str, pa.DataType] = {
    "string": pa.string(),
    "int32": pa.int32(),
    "int64": pa.int64(),
    "float64": pa.float64(),
    "bool": pa.bool_(),
    "list<int32>": pa.list_(pa.int32()),
    "list<string>": pa.list_(pa.string()),
}
# Bound in every query, and recorded in the manifest: which results the dataset reads.
PARAMETERS = {
    "decoder_version": DECODER_VERSION,
    "renderer_version": RENDERER_VERSION,
    "features_version": FEATURES_VERSION,
    "text_version": TEXT_VERSION,
}
EXTRACTORS = {
    "decoder": f"{DECODER}@{DECODER_VERSION}",
    "renderer": RENDERER_VERSION,
    "features": FEATURES_VERSION,
    "text": TEXT_VERSION,
}


class Column(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: ColumnType
    description: str


class Table(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = ""  # file, relative to dataset.yaml
    key: list[str] = []
    columns: list[Column] = []
    filter: str | None = None  # SQL condition on the query's rows
    same_as: str | None = None  # `dataset.table`: its query, key and columns, with this filter


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


class Definition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    version: str
    description: str
    tables: dict[str, Table]
    sample: Sample | None = None


class DatasetError(Exception):
    """A definition that does not match what its query returns."""


@dataclass(frozen=True)
class Built:
    directory: Path
    rows: dict[str, int]


def load(directory: Path) -> Definition:
    raw = yaml.safe_load((directory / "dataset.yaml").read_text(encoding="utf-8"))
    # `x-` keys hold YAML anchors shared by several tables, as in OpenAPI.
    definition = Definition.model_validate({k: v for k, v in raw.items() if not k.startswith("x-")})
    for name, table in definition.tables.items():
        if table.same_as:
            definition.tables[name] = _same_as(directory, table)
        elif not (table.query and table.key and table.columns):
            raise DatasetError(f"{name}: a table needs a query, a key and columns, or same_as")
    return definition


def _same_as(directory: Path, table: Table) -> Table:
    """The table named `dataset.table`, its query path made relative to `directory`."""
    dataset, _, name = str(table.same_as).partition(".")
    other = directory.parent / dataset
    source = load(other).tables.get(name)
    if source is None or source.same_as:
        raise DatasetError(f"same_as {table.same_as}: no such table")
    query = str((other / source.query).relative_to(directory.parent))
    return source.model_copy(update={"query": f"../{query}", "filter": table.filter})


def build(conn: Connection, directory: Path, out_root: Path) -> Built:
    """Build the dataset defined in `directory` under `out_root/<name>/<version>/`."""
    definition = load(directory)
    out = out_root / definition.name / definition.version
    sample = _frozen_sample(directory, definition.sample)
    out.mkdir(parents=True, exist_ok=True)
    tables: dict[str, dict[str, object]] = {}
    for name, table in sorted(definition.tables.items()):
        query = (directory / table.query).read_text(encoding="utf-8")
        arrow = _extract(conn, name, table, query, sample)
        path = out / f"{name}.parquet"
        pq.write_table(arrow, path, compression="zstd")  # pyright: ignore[reportUnknownMemberType]
        tables[name] = {
            "query_sha256": hashlib.sha256(query.encode()).hexdigest(),
            "rows": arrow.num_rows,
            "file": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    manifest = {
        "name": definition.name,
        "version": definition.version,
        "migration": conn.execute(text("select version_num from alembic_version")).scalar_one(),
        "extractors": EXTRACTORS,
        "lost_items": _lost_items(conn),
        "tables": tables,
    }
    if sample is not None:
        manifest["sample_sha256"] = sample.digest
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return Built(out, {name: int(str(t["rows"])) for name, t in tables.items()})


def _extract(
    conn: Connection, name: str, table: Table, query: str, sample: FrozenSample | None
) -> pa.Table:
    """Run the query in key order and type its result as the definition says."""
    declared = [c.name for c in table.columns]
    if not set(table.key) <= set(declared):
        msg = f"{name}: key {table.key} names columns that are not declared"
        raise DatasetError(msg)
    order = ", ".join(table.key)
    where = f" where {table.filter}" if table.filter else ""
    sql = f"select * from ({query}) q{where} order by {order}"
    params: dict[str, object] = dict(PARAMETERS)
    if sample is not None:
        sql = f"with {SAMPLE_CTE} {sql}"
        params |= sample.params()
    result = conn.execute(text(sql), params)
    if list(result.keys()) != declared:
        msg = f"{name}: query returns {list(result.keys())}, dataset.yaml declares {declared}"
        raise DatasetError(msg)
    rows = [dict(r) for r in result.mappings()]
    keys = [tuple(r[k] for k in table.key) for r in rows]
    if len(set(keys)) != len(keys):
        msg = f"{name}: key {table.key} does not identify rows: duplicates found"
        raise DatasetError(msg)
    schema = pa.schema(
        [
            pa.field(c.name, ARROW_TYPES[c.type], metadata={"description": c.description})
            for c in table.columns
        ]
    )
    return pa.Table.from_pylist(rows, schema=schema)


def _lost_items(conn: Connection) -> dict[str, int]:
    """Items known to have existed and not found, by kind: the denominator of coverage."""
    found = conn.execute(text("select kind, count(*) from lost_item group by kind order by kind"))
    return {kind: count for kind, count in found}


SAMPLE_FILE = "sample.yaml"
# REUSE-IgnoreStart: the header of the files `draw_sample` writes, not this file's license.
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


def draw_sample(conn: Connection, directory: Path) -> Path:
    """Draw the definition's sample from its frame and write `sample.yaml` beside it."""
    definition = load(directory)
    spec = definition.sample
    if spec is None:
        raise DatasetError(f"{definition.name}: dataset.yaml declares no sample")
    query = (directory / spec.frame).read_text(encoding="utf-8")
    frame = [dict(r) for r in conn.execute(text(query), PARAMETERS).mappings()]
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
            raise DatasetError(f"addition {addition.unit} is not in the frame")
        if addition.unit in taken:
            raise DatasetError(f"addition {addition.unit} was drawn already")
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
    path.write_text(SAMPLE_HEADER.format(name=definition.name) + body, "utf-8")
    return path


def _frozen_sample(directory: Path, spec: Sample | None) -> FrozenSample | None:
    if spec is None:
        return None
    path = directory / SAMPLE_FILE
    if not path.exists():
        raise DatasetError(f"{path} is missing: run `tm dataset draw {directory.name}`")
    raw = path.read_bytes()
    document = yaml.safe_load(raw)
    frame = (directory / spec.frame).read_text(encoding="utf-8")
    if document["frame_sha256"] != hashlib.sha256(frame.encode()).hexdigest():
        raise DatasetError(f"{spec.frame} changed since the sample was drawn: draw it again")
    return FrozenSample(document["units"], hashlib.sha256(raw).hexdigest())
