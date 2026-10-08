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
    """Record a pack, or complete one recorded before: members already listed are left alone,
    members an earlier run could not read are added."""
    year = path.parent.name if _is_year(path.parent.name) else None
    source_path = f"{year}/{path.name}" if year else path.name
    data = path.read_bytes()
    sha256 = sha256_hex(data)
    rights = Rights(
        scene_publication=ScenePublication.model_validate(
            {"archive": "16colo", "url": PACK_URL.format(name=path.stem)}
        )
    )
    dating = _year_dating(year)
    source_id = ensure_source(conn, "archive", SOURCE, SOURCE_URL, SOURCE_NOTE)
    pack = _Pack(source_id, source_path, dating, rights)
    set_work = _set_work_of(conn, sha256)
    result = PackIngested(source_path, sha256, new=set_work is None)
    if set_work is None:
        set_work = _record_archive(conn, store, path, data, pack)
    try:
        expanded = expand(path, ARCHIVES[path.suffix.lower()])
    except ArchiveError as err:
        result.error_class = err.kind
        return result
    result.unreadable = expanded.unreadable
    listed = set(
        conn.execute(
            text("select path from set_member where set_work_id = :w"), {"w": set_work}
        ).scalars()
    )
    for member in enumerate(expanded.members):
        if member[1][0] not in listed:
            _add_member(conn, store, pack, set_work, member)
            result.members += 1
    return result


def _set_work_of(conn: Connection, sha256: str) -> str | None:
    """The set work an archive already stands for, if any."""
    found = conn.execute(
        text(
            "select w.id from artifact a join version v on v.id = a.version_id"
            " join work w on w.id = v.work_id where a.sha256 = :s and w.kind = 'set'"
        ),
        {"s": sha256},
    ).scalar()
    return None if found is None else str(found)


def _record_archive(
    conn: Connection, store: ObjectStore, path: Path, data: bytes, pack: _Pack
) -> str:
    """Store the archive and make it a set work. An archive already met as a file inside another
    pack keeps its artifact row and gains the set."""
    put_original(store, data)
    set_version = insert_work(conn, "set", path.stem, pack.rights, pack.dating)
    sha256 = sha256_hex(data)
    if artifact_known(conn, sha256):
        conn.execute(
            text("update artifact set version_id = :v where sha256 = :s and version_id is null"),
            {"v": set_version, "s": sha256},
        )
    else:
        insert_artifact(
            conn,
            ArtifactRow(
                sha256=sha256,
                bytes=len(data),
                format=ARCHIVES[path.suffix.lower()],
                charset=None,
                sauce=None,
                source_id=pack.source_id,
                source_path=pack.source_path,
                version_id=set_version,
            ),
        )
    return _work_of(conn, set_version)


def _add_member(
    conn: Connection,
    store: ObjectStore,
    pack: _Pack,
    set_work: str,
    member: tuple[int, tuple[str, bytes]],
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
        {"set_work": set_work, "sha256": sha256, "path": name, "position": position},
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
