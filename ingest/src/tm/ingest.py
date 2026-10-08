# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Ingestion of the golden source: the project's own artifacts, CC0, kept in `tests/golden/`.

Each file is stored as an original (write-once, addressed by SHA-256) and described by one
`source`, `work`, `version` and `artifact` row. Run twice, it leaves the same state: an artifact
already known is left alone.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Connection, text
from tm_render.sauce import Sauce, split

from tm.rights import Permission, Rights
from tm.storage import ObjectStore, put_original

GOLDEN_SOURCE = "golden"
GOLDEN_LICENSE = "CC0-1.0"
GOLDEN_GRANTOR = "human:nicolasbridelance"
FORMATS = {".ans": "ansi"}
CHARSET = "cp437"


@dataclass(frozen=True)
class Ingested:
    path: str
    sha256: str
    new: bool


def golden_files(root: Path) -> list[Path]:
    """Golden artifacts under `root`, in a stable order."""
    return sorted(path for path in root.rglob("*") if path.suffix.lower() in FORMATS)


def ingest_golden(conn: Connection, store: ObjectStore, root: Path) -> list[Ingested]:
    source_id = _golden_source(conn)
    return [_ingest_file(conn, store, source_id, root, path) for path in golden_files(root)]


def _golden_source(conn: Connection) -> str:
    conn.execute(
        text(
            "insert into source (kind, name, terms_note) values ('golden', :name, :note)"
            " on conflict (name) do nothing"
        ),
        {
            "name": GOLDEN_SOURCE,
            "note": f"Made for the project and dedicated to the public domain ({GOLDEN_LICENSE}).",
        },
    )
    return str(
        conn.execute(
            text("select id from source where name = :name"), {"name": GOLDEN_SOURCE}
        ).scalar_one()
    )


def _ingest_file(
    conn: Connection, store: ObjectStore, source_id: str, root: Path, path: Path
) -> Ingested:
    data = path.read_bytes()
    sha256, _ = put_original(store, data)
    relative = path.relative_to(root).as_posix()
    known = conn.execute(
        text("select 1 from artifact where sha256 = :sha256"), {"sha256": sha256}
    ).first()
    if known:
        return Ingested(relative, sha256, new=False)
    sauce = split(data)[1]
    version_id = _insert_work_and_version(conn, sauce, fallback_title=path.stem)
    conn.execute(
        text(
            "insert into artifact (sha256, version_id, bytes, format, charset, sauce, source_id,"
            " source_path) values (:sha256, :version_id, :bytes, :format, :charset,"
            " cast(:sauce as jsonb), :source_id, :source_path)"
        ),
        {
            "sha256": sha256,
            "version_id": version_id,
            "bytes": len(data),
            "format": FORMATS[path.suffix.lower()],
            "charset": CHARSET,
            "sauce": json.dumps(dataclasses.asdict(sauce)) if sauce else None,
            "source_id": source_id,
            "source_path": relative,
        },
    )
    return Ingested(relative, sha256, new=True)


def _insert_work_and_version(conn: Connection, sauce: Sauce | None, fallback_title: str) -> str:
    title = sauce.title if sauce and sauce.title else fallback_title
    work_id = conn.execute(
        text(
            "insert into work (kind, title, rights) values ('single', :title,"
            " cast(:rights as jsonb)) returning id"
        ),
        {"title": title, "rights": _golden_rights().model_dump_json()},
    ).scalar_one()
    sauce_date = _sauce_date(sauce)
    return str(
        conn.execute(
            text(
                "insert into version (work_id, date_min, date_max, date_basis, behavior)"
                " values (:work_id, :date, :date, :basis, 'static') returning id"
            ),
            {"work_id": work_id, "date": sauce_date, "basis": "sauce" if sauce_date else None},
        ).scalar_one()
    )


def _golden_rights() -> Rights:
    return Rights(
        permission=Permission(
            display=True,
            granted_by=GOLDEN_GRANTOR,
            evidence_note="Golden artifact made for the project (tests/golden/README.md).",
        ),
        license=GOLDEN_LICENSE,
    )


def _sauce_date(sauce: Sauce | None) -> dt.date | None:
    """The SAUCE date (`YYYYMMDD`), or None when absent or not a real date."""
    if sauce is None:
        return None
    try:
        return dt.datetime.strptime(sauce.date, "%Y%m%d").replace(tzinfo=dt.UTC).date()
    except ValueError:
        return None
