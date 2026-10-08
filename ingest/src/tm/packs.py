# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Ingestion of 16colo artpacks from the local mirror (`rsync://16colo.rs/archive-pack/`).

A pack is a `set` work. Its archive is stored whole, and so is every member, each addressed by
its SHA-256; `set_member` lists them in archive order. The same file in two packs is one
artifact and two `set_member` rows. Textmode art members are also `single` works; other members
(NFO, music, images, programs) are artifacts only. Rights record the scene publication on 16colo
(ADR 0009). Run twice, it leaves the same state: a pack whose archive is known is skipped.

Archives are read as ADR 0013 says (`tm.archives`). One that cannot be read at all is still
stored and recorded, with a classified error and no members; a member that cannot be read is
named in the result, not recorded.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from sqlalchemy import Connection, text
from tm_render.sauce import Sauce, split

from tm.archives import ArchiveError, expand
from tm.records import (
    ArtifactRow,
    Dating,
    artifact_known,
    ensure_source,
    insert_artifact,
    insert_work,
)
from tm.rights import Rights, ScenePublication
from tm.storage import ObjectStore, put_original, sha256_hex

SOURCE = "16colo"
SOURCE_URL = "https://16colo.rs/"
SOURCE_NOTE = (
    "Scene archive of ANSI and ASCII artpacks. Mirroring invited by its FAQ; artwork remains the"
    " author's property (docs/sources/16colo.md)."
)
PACK_URL = "https://16colo.rs/pack/{name}/"
ARCHIVES = {".zip": "zip", ".rar": "rar", ".lha": "lha", ".lzh": "lzh", ".arj": "arj"}
# Textmode art: each member becomes a work. Extension first, as the scene named the file.
ART = {
    ".ans": "ansi", ".ice": "ansi", ".asc": "ascii", ".xb": "xbin", ".bin": "bin",
    ".adf": "adf", ".idf": "idf", ".pcb": "pcboard", ".avt": "avatar", ".rip": "rip",
    ".tnd": "tundra",
}  # fmt: skip
DOCUMENTS = {".nfo": "nfo", ".diz": "diz", ".txt": "text", ".lit": "text"}
# SAUCE (data type, file type) of art whose extension says nothing (spec v00.5).
SAUCE_ART: dict[tuple[int, int | None], str] = {
    (1, 0): "ascii", (1, 1): "ansi", (1, 2): "ansi", (1, 3): "rip", (1, 4): "pcboard",
    (1, 5): "avatar", (1, 8): "tundra", (5, None): "bin", (6, 0): "xbin",
}  # fmt: skip
SAUCE_BINARY_TEXT = 5
CHARSET = "cp437"
YEAR_DIGITS = 4


@dataclass
class PackIngested:
    path: str
    sha256: str
    new: bool
    members: int = 0
    error_class: str | None = None
    unreadable: list[str] = field(default_factory=list[str])


@dataclass(frozen=True)
class _Pack:
    """What every row of one pack shares."""

    set_work: str
    source_id: str
    source_path: str
    dating: Dating
    rights: Rights


def pack_archives(paths: list[Path]) -> list[Path]:
    """The archives named, or found under the directories named, in a stable order."""
    found: set[Path] = set()
    for path in paths:
        candidates = path.rglob("*") if path.is_dir() else [path]
        found.update(p for p in candidates if p.is_file() and p.suffix.lower() in ARCHIVES)
    return sorted(found)


def ingest_pack(conn: Connection, store: ObjectStore, path: Path) -> PackIngested:
    year = path.parent.name if _is_year(path.parent.name) else None
    source_path = f"{year}/{path.name}" if year else path.name
    data = path.read_bytes()
    sha256 = sha256_hex(data)
    if artifact_known(conn, sha256):
        return PackIngested(source_path, sha256, new=False)
    put_original(store, data)
    source_id = ensure_source(conn, "archive", SOURCE, SOURCE_URL, SOURCE_NOTE)
    rights = Rights(
        scene_publication=ScenePublication.model_validate(
            {"archive": "16colo", "url": PACK_URL.format(name=path.stem)}
        )
    )
    dating = _year_dating(year)
    set_version = insert_work(conn, "set", path.stem, rights, dating)
    archive_format = ARCHIVES[path.suffix.lower()]
    insert_artifact(
        conn,
        ArtifactRow(
            sha256=sha256,
            bytes=len(data),
            format=archive_format,
            charset=None,
            sauce=None,
            source_id=source_id,
            source_path=source_path,
            version_id=set_version,
        ),
    )
    result = PackIngested(source_path, sha256, new=True)
    pack = _Pack(_work_of(conn, set_version), source_id, source_path, dating, rights)
    try:
        expanded = expand(path, archive_format)
    except ArchiveError as err:
        result.error_class = err.kind
        return result
    result.unreadable = expanded.unreadable
    for member in enumerate(expanded.members):
        _add_member(conn, store, pack, member)
        result.members += 1
    return result


def _add_member(
    conn: Connection, store: ObjectStore, pack: _Pack, member: tuple[int, tuple[str, bytes]]
) -> None:
    position, (name, data) = member
    sha256, _ = put_original(store, data)
    if not artifact_known(conn, sha256):
        sauce = split(data)[1]
        art = _art_format(name, sauce)
        version_id = None
        if art:
            title = sauce.title if sauce and sauce.title else PurePosixPath(name).name
            version_id = insert_work(conn, "single", title, pack.rights, pack.dating)
        doc = DOCUMENTS.get(PurePosixPath(name).suffix.lower())
        insert_artifact(
            conn,
            ArtifactRow(
                sha256=sha256,
                bytes=len(data),
                format=art or doc or _extension(name),
                charset=CHARSET if art or doc else None,
                sauce=sauce,
                source_id=pack.source_id,
                source_path=f"{pack.source_path}/{name}",
                version_id=version_id,
            ),
        )
    conn.execute(
        text(
            "insert into set_member (set_work_id, sha256, path, position)"
            " values (:set_work, :sha256, :path, :position)"
        ),
        {"set_work": pack.set_work, "sha256": sha256, "path": name, "position": position},
    )


def _art_format(name: str, sauce: Sauce | None) -> str | None:
    by_extension = ART.get(PurePosixPath(name).suffix.lower())
    if by_extension or sauce is None:
        return by_extension
    # BinaryText stores the width in the file type, so the type alone names the format.
    file_type = None if sauce.data_type == SAUCE_BINARY_TEXT else sauce.file_type
    return SAUCE_ART.get((sauce.data_type, file_type))


def _extension(name: str) -> str | None:
    suffix = PurePosixPath(name).suffix.lower()
    return suffix.removeprefix(".") or None


def _work_of(conn: Connection, version_id: str) -> str:
    return str(
        conn.execute(
            text("select work_id from version where id = :id"), {"id": version_id}
        ).scalar_one()
    )


def _is_year(name: str) -> bool:
    return len(name) == YEAR_DIGITS and name.isdigit()


def _year_dating(year: str | None) -> Dating:
    """The pack's year on 16colo, as an interval: the release date is rarely more precise."""
    if year is None:
        return Dating()
    return Dating(dt.date(int(year), 1, 1), dt.date(int(year), 12, 31), "pack")
