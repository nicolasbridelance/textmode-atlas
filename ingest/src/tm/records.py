# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Rows written by ingestion: source, work, version, artifact. One place for their SQL."""

from __future__ import annotations

import dataclasses
import datetime as dt
import json
from dataclasses import dataclass

from sqlalchemy import Connection, text
from tm_render.sauce import Sauce

from tm.rights import Rights


@dataclass(frozen=True)
class Dating:
    """A date interval and what it rests on (`version.date_basis`)."""

    date_min: dt.date | None = None
    date_max: dt.date | None = None
    basis: str | None = None


@dataclass(frozen=True)
class ArtifactRow:
    sha256: str
    bytes: int
    format: str | None
    charset: str | None
    sauce: Sauce | None
    source_id: str
    source_path: str
    version_id: str | None = None


def ensure_source(conn: Connection, kind: str, name: str, url: str | None, note: str) -> str:
    """The id of the named source, created on first use."""
    conn.execute(
        text(
            "insert into source (kind, name, url, terms_note) values (:kind, :name, :url, :note)"
            " on conflict (name) do nothing"
        ),
        {"kind": kind, "name": name, "url": url, "note": note},
    )
    return str(
        conn.execute(text("select id from source where name = :name"), {"name": name}).scalar_one()
    )


def artifact_known(conn: Connection, sha256: str) -> bool:
    found = conn.execute(text("select 1 from artifact where sha256 = :s"), {"s": sha256}).first()
    return found is not None


def insert_work(conn: Connection, kind: str, title: str, rights: Rights, dating: Dating) -> str:
    """A work and its single version (static); return the version id."""
    work_id = conn.execute(
        text(
            "insert into work (kind, title, rights) values (:kind, :title, cast(:rights as jsonb))"
            " returning id"
        ),
        {"kind": kind, "title": title, "rights": rights.model_dump_json()},
    ).scalar_one()
    return str(
        conn.execute(
            text(
                "insert into version (work_id, date_min, date_max, date_basis, behavior)"
                " values (:work_id, :date_min, :date_max, :basis, 'static') returning id"
            ),
            {"work_id": work_id, **dataclasses.asdict(dating)},
        ).scalar_one()
    )


def insert_artifact(conn: Connection, row: ArtifactRow) -> None:
    values = dataclasses.asdict(row)
    values["sauce"] = json.dumps(dataclasses.asdict(row.sauce)) if row.sauce else None
    conn.execute(
        text(
            "insert into artifact (sha256, version_id, bytes, format, charset, sauce, source_id,"
            " source_path) values (:sha256, :version_id, :bytes, :format, :charset,"
            " cast(:sauce as jsonb), :source_id, :source_path)"
        ),
        values,
    )


def sauce_date(sauce: Sauce | None) -> dt.date | None:
    """The SAUCE date (`YYYYMMDD`), or None when absent or not a real date."""
    if sauce is None:
        return None
    try:
        return dt.datetime.strptime(sauce.date, "%Y%m%d").replace(tzinfo=dt.UTC).date()
    except ValueError:
        return None
