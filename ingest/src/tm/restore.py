# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Put back in storage the originals the database records but the store lacks, from a local
mirror of the archives they came from.

The machine moved on 2026-10-09 with the database and the derived objects but without the
originals, so most artifacts had no original locally. A mirror holds the same files: each file
under the paths given, and each member of the archives among them, is stored when its SHA-256
is that of an artifact the database records. Nothing else enters: a restore adds no artifact
and no row, and the store stays content-addressed and write-once (invariant 1). Run twice, the
second run writes nothing.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Connection, text

from tm.archives import ArchiveError, expand
from tm.packs import ARCHIVES
from tm.storage import ObjectStore, original_key, put_original, sha256_hex


@dataclass
class Restored:
    written: int = 0  # originals put back
    present: int = 0  # recorded files already in the store
    unknown: int = 0  # files the database does not record
    unreadable: int = 0  # archives that could not be expanded


def restore_originals(conn: Connection, store: ObjectStore, paths: list[Path]) -> Restored:
    """Store every file of the mirror, archive member included, that the database records."""
    recorded = set(conn.execute(text("select sha256 from artifact")).scalars())
    restored = Restored()
    for data in _files(paths, restored):
        digest = sha256_hex(data)
        if digest not in recorded:
            restored.unknown += 1
        elif store.exists(original_key(digest)):  # a restart skips what an earlier run stored
            restored.present += 1
        else:
            put_original(store, data)
            restored.written += 1
    return restored


def _files(paths: list[Path], restored: Restored) -> Iterator[bytes]:
    for path in sorted({p for root in paths for p in _walk(root)}):
        yield path.read_bytes()
        archive_format = ARCHIVES.get(path.suffix.lower())
        if archive_format is None:
            continue
        try:
            members = expand(path, archive_format).members
        except ArchiveError:
            restored.unreadable += 1
            continue
        yield from (data for _, data in members)


def _walk(root: Path) -> Iterator[Path]:
    candidates = root.rglob("*") if root.is_dir() else [root]
    return (p for p in candidates if p.is_file())
