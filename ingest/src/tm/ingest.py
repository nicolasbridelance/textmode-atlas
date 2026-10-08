# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Ingestion of the golden source: the project's own artifacts, CC0, kept in `tests/golden/`.

Each file is stored as an original (write-once, addressed by SHA-256) and described by one
`source`, `work`, `version` and `artifact` row. Run twice, it leaves the same state: an artifact
already known is left alone.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Connection
from tm_render.sauce import split

from tm.records import (
    ArtifactRow,
    Dating,
    artifact_known,
    ensure_source,
    insert_artifact,
    insert_work,
    sauce_date,
)
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
    source_id = ensure_source(
        conn,
        "golden",
        GOLDEN_SOURCE,
        None,
        f"Made for the project and dedicated to the public domain ({GOLDEN_LICENSE}).",
    )
    return [_ingest_file(conn, store, source_id, root, path) for path in golden_files(root)]


def _ingest_file(
    conn: Connection, store: ObjectStore, source_id: str, root: Path, path: Path
) -> Ingested:
    data = path.read_bytes()
    sha256, _ = put_original(store, data)
    relative = path.relative_to(root).as_posix()
    if artifact_known(conn, sha256):
        return Ingested(relative, sha256, new=False)
    sauce = split(data)[1]
    date = sauce_date(sauce)
    version_id = insert_work(
        conn,
        "single",
        sauce.title if sauce and sauce.title else path.stem,
        _golden_rights(),
        Dating(date, date, "sauce" if date else None),
    )
    insert_artifact(
        conn,
        ArtifactRow(
            sha256=sha256,
            bytes=len(data),
            format=FORMATS[path.suffix.lower()],
            charset=CHARSET,
            sauce=sauce,
            source_id=source_id,
            source_path=relative,
            version_id=version_id,
        ),
    )
    return Ingested(relative, sha256, new=True)


def _golden_rights() -> Rights:
    return Rights(
        permission=Permission(
            display=True,
            granted_by=GOLDEN_GRANTOR,
            evidence_note="Golden artifact made for the project (tests/golden/README.md).",
        ),
        license=GOLDEN_LICENSE,
    )
