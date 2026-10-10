# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from sqlalchemy import Connection
from stores import Stores
from tm.packs import ingest_pack
from tm.restore import restore_originals
from tm.storage import LocalStore, get_original, original_key, sha256_hex

pytestmark = pytest.mark.db

MEMBERS = {"LOGO.ANS": b"\x1b[1mlogo\x1b[0m\r\n", "PACK.NFO": b"a pack\r\n"}


def test_a_mirror_puts_back_the_originals_the_store_lacks(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    pack = tmp_path / "mirror" / "1995" / "p.zip"
    pack.parent.mkdir(parents=True)
    with zipfile.ZipFile(pack, "w") as archive:
        for name, data in MEMBERS.items():
            archive.writestr(name, data)
    ingest_pack(db, stores.originals, pack)
    (tmp_path / "mirror" / "1995" / "stranger.ans").write_bytes(b"not recorded\r\n")
    empty = LocalStore(tmp_path / "moved")  # the store after the move: the originals are gone

    restored = restore_originals(db, empty, [tmp_path / "mirror"])

    assert (restored.written, restored.present, restored.unknown) == (3, 0, 1)
    for data in [pack.read_bytes(), *MEMBERS.values()]:
        assert get_original(empty, sha256_hex(data)) == data
    assert not empty.exists(original_key(sha256_hex(b"not recorded\r\n")))
    again = restore_originals(db, empty, [tmp_path / "mirror"])
    assert (again.written, again.present) == (0, 3)


def test_an_unreadable_archive_is_counted_and_skipped(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    broken = tmp_path / "broken.zip"
    broken.write_bytes(b"not a zip at all")
    restored = restore_originals(db, stores.originals, [broken])
    assert (restored.unknown, restored.unreadable) == (1, 1)
