# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Ingestion of the files a scene archive holds loose, outside any pack (ADR 0024).

The mirror is laid out as the archive's site (`scripts/mirror_textfiles_collections.py`), so a
file's path under the mirror's root is its path on the site. Every file is stored, addressed by
its SHA-256; an art file is also a `single` work, with no set. Art is found as in packs
(extension, SAUCE, content); in a tree the archive's curator declares as art of one kind, other
text files take that kind. Archives are packs (`tm ingest pack`), and the site's own index files
are not the scene's: both are left out here. Run twice, it leaves the same state: a file the
museum holds is skipped, whichever source brought it first.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from sqlalchemy import Connection
from tm_render.sauce import split

from tm.packs import (
    ARCHIVES,
    CHARSET,
    DOCUMENTS,
    PackSource,
    art_format,
    extension,
    scene_rights,
)
from tm.records import (
    ArtifactRow,
    Dating,
    artifact_known,
    ensure_source,
    insert_artifact,
    insert_work,
    sauce_date,
)
from tm.storage import ObjectStore, put_original

SITE_INDEX = ".descs"  # textfiles.com's per-directory descriptions


@dataclass
class LooseIngested:
    path: str
    sha256: str
    new: bool
    format: str | None = None
    work: bool = False


def loose_files(paths: list[Path]) -> list[Path]:
    """The files named, or found under the directories named, that are not packs or site index
    files, in a stable order."""
    found: set[Path] = set()
    for path in paths:
        candidates = path.rglob("*") if path.is_dir() else [path]
        found.update(
            p
            for p in candidates
            if p.is_file() and p.suffix.lower() not in ARCHIVES and p.name != SITE_INDEX
        )
    return sorted(found, key=lambda path: path.as_posix())


def ingest_loose(
    conn: Connection,
    store: ObjectStore,
    path: Path,
    *,
    site_root: Path,
    source: PackSource,
    declared: str | None = None,
) -> LooseIngested:
    """Store one loose file and record it; `declared` is the art kind the archive gives the tree."""
    source_path = path.relative_to(site_root).as_posix()
    data = path.read_bytes()
    sha256, _ = put_original(store, data)
    if artifact_known(conn, sha256):
        return LooseIngested(source_path, sha256, new=False)
    sauce = split(data)[1]
    art = art_format(path.name, sauce, data, declared)
    version_id = None
    if art:
        date = sauce_date(sauce)
        version_id = insert_work(
            conn,
            "single",
            sauce.title if sauce and sauce.title else path.name,
            scene_rights(source, source.url + source_path),
            Dating(date, date, "sauce" if date else None),
        )
    doc = DOCUMENTS.get(PurePosixPath(path.name).suffix.lower())
    insert_artifact(
        conn,
        ArtifactRow(
            sha256=sha256,
            bytes=len(data),
            format=art or doc or extension(path.name),
            charset=CHARSET if art or doc else None,
            sauce=sauce,
            source_id=ensure_source(conn, "archive", source.name, source.url, source.note),
            source_path=source_path,
            version_id=version_id,
        ),
    )
    return LooseIngested(source_path, sha256, new=True, format=art, work=art is not None)
