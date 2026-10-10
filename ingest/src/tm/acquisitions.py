# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Acquisitions (ADR 0021): where and when each original was fetched, from a mirror's record.

A mirror writes `acquisitions.tsv` (columns below) as it fetches, or after the fact with the
basis of its times said honestly. Loading it records one `acquisition` row per file the museum
holds; files it does not hold are counted and left out. Loading twice changes nothing.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Connection, text

from tm.records import artifact_known

COLUMNS = ("path", "url", "method", "retrieved_at", "retrieved_basis", "remote", "sha256")
RECORDED_BY = "algo:tm.acquisitions@1"


@dataclass(frozen=True)
class Fetch:
    """One fetch of one file: what came back, from where, when and on what basis."""

    sha256: str
    url: str
    method: str
    retrieved_at: str | None
    basis: str
    remote: dict[str, str]


def insert_acquisition(conn: Connection, fetch: Fetch, source_id: str, recorded_by: str) -> bool:
    """Record a fetch of a file the museum holds; False when it was recorded already."""
    inserted = conn.execute(
        text(
            "insert into acquisition (sha256, source_id, url, method, retrieved_at,"
            " retrieved_basis, remote, recorded_by) values (:sha256, :source, :url,"
            " :method, :retrieved_at, :basis, cast(:remote as jsonb), :by)"
            " on conflict (sha256, url, retrieved_at) do nothing returning id"
        ),
        {
            "sha256": fetch.sha256,
            "source": source_id,
            "url": fetch.url,
            "method": fetch.method,
            "retrieved_at": fetch.retrieved_at,
            "basis": fetch.basis,
            "remote": json.dumps(fetch.remote, sort_keys=True),
            "by": recorded_by,
        },
    ).first()
    return inserted is not None


@dataclass
class Loaded:
    recorded: int = 0
    already: int = 0
    not_held: int = 0


def load_acquisitions(conn: Connection, path: Path, source: str) -> Loaded:
    source_id = conn.execute(
        text("select id from source where name = :n"), {"n": source}
    ).scalar_one()
    loaded = Loaded()
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if not artifact_known(conn, row["sha256"]):
                loaded.not_held += 1
                continue
            inserted = insert_acquisition(
                conn,
                Fetch(
                    sha256=row["sha256"],
                    url=row["url"],
                    method=row["method"],
                    retrieved_at=row["retrieved_at"] or None,
                    basis=row["retrieved_basis"],
                    remote=json.loads(row["remote"] or "{}"),
                ),
                source_id,
                RECORDED_BY,
            )
            if not inserted:
                loaded.already += 1
            else:
                loaded.recorded += 1
    return loaded
