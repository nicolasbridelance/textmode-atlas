# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Datasets: frozen extracts of the database that research reads instead of the database.

A dataset is defined in `datasets/<name>/`: `dataset.yaml` names its tables, each with a SQL
query, the key that orders and identifies its rows, and its typed, described columns. A build
writes one Parquet file per table and a manifest (migration, extractor versions, SHA-256 of every
query and file) into `datasets/build/<name>/<version>/`. Nothing in a build depends on when it
ran: building twice from the same database gives byte-identical files.
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
from tm_render.versions import DECODER_VERSION, RENDERER_VERSION

from tm.decode import DECODER

ColumnType = Literal["string", "int32", "int64", "bool"]
ARROW_TYPES: dict[str, pa.DataType] = {
    "string": pa.string(),
    "int32": pa.int32(),
    "int64": pa.int64(),
    "bool": pa.bool_(),
}
# Bound in every query, and recorded in the manifest: which results the dataset reads.
PARAMETERS = {"decoder_version": DECODER_VERSION}
EXTRACTORS = {"decoder": f"{DECODER}@{DECODER_VERSION}", "renderer": RENDERER_VERSION}


class Column(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: ColumnType
    description: str


class Table(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str  # file next to dataset.yaml
    key: list[str]
    columns: list[Column]


class Definition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    version: str
    description: str
    tables: dict[str, Table]


class DatasetError(Exception):
    """A definition that does not match what its query returns."""


@dataclass(frozen=True)
class Built:
    directory: Path
    rows: dict[str, int]


def load(directory: Path) -> Definition:
    raw = yaml.safe_load((directory / "dataset.yaml").read_text(encoding="utf-8"))
    return Definition.model_validate(raw)


def build(conn: Connection, directory: Path, out_root: Path) -> Built:
    """Build the dataset defined in `directory` under `out_root/<name>/<version>/`."""
    definition = load(directory)
    out = out_root / definition.name / definition.version
    out.mkdir(parents=True, exist_ok=True)
    tables: dict[str, dict[str, object]] = {}
    for name, table in sorted(definition.tables.items()):
        query = (directory / table.query).read_text(encoding="utf-8")
        arrow = _extract(conn, name, table, query)
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
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return Built(out, {name: int(str(t["rows"])) for name, t in tables.items()})


def _extract(conn: Connection, name: str, table: Table, query: str) -> pa.Table:
    """Run the query in key order and type its result as the definition says."""
    declared = [c.name for c in table.columns]
    if not set(table.key) <= set(declared):
        msg = f"{name}: key {table.key} names columns that are not declared"
        raise DatasetError(msg)
    order = ", ".join(table.key)
    result = conn.execute(text(f"select * from ({query}) q order by {order}"), PARAMETERS)
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
