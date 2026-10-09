# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Datasets: frozen extracts of the database that research reads instead of the database.

A dataset is defined in `datasets/<name>/`: `dataset.yaml` names its tables, each with a SQL
query, the key that orders and identifies its rows, and its typed, described columns. A build
writes one Parquet file per table and a manifest (migration, extractor versions, SHA-256 of every
query and file) into `datasets/build/<name>/<version>/`. Nothing in a build depends on when it
ran: building twice from the same database gives byte-identical files.

A pilot dataset also declares a `sample` (ADR 0017), drawn and frozen by `tm.pilots`; the build
reads the frozen list as a CTE named `sample`, which the tables' queries and filters can use.
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
from tm.pilots import SAMPLE_CTE, FrozenSample, Sample, frozen_sample, write_sample

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
    sample = frozen_sample(directory, definition.sample)
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


def draw_sample(conn: Connection, directory: Path) -> Path:
    """Draw the sample a pilot definition declares, and freeze it beside the definition."""
    definition = load(directory)
    if definition.sample is None:
        raise DatasetError(f"{definition.name}: dataset.yaml declares no sample")
    return write_sample(conn, directory, definition.name, definition.sample, PARAMETERS)
