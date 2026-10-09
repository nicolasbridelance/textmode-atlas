# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from samples import CORRUPT_SAUCE_ART
from sqlalchemy import Connection, text
from stores import Stores
from tm.decode import DECODER, NO_DECODER, decode_pending
from tm.ingest import ingest_golden
from tm.packs import ingest_pack
from tm.storage import IntegrityError, grid_key
from tm_render.ansi import decode
from tm_render.grid import Grid, from_parquet, to_parquet
from tm_render.versions import DECODER_VERSION

GOLDEN = Path(__file__).resolve().parents[2] / "tests" / "golden"
HORIZON = (GOLDEN / "ansi" / "horizon.ans").read_bytes()

pytestmark = pytest.mark.db


def ingested(db: Connection, stores: Stores) -> str:
    return ingest_golden(db, stores.originals, GOLDEN)[0].sha256


def test_grid_key_follows_the_decoding_primary_key() -> None:
    sha = "ab" * 32
    assert grid_key(sha, "d", "1.2") == f"grids/ab/ab/{sha}/d@1.2.parquet"
    with pytest.raises(ValueError, match="invalid SHA-256"):
        grid_key("nope", "d", "1")


def test_decode_records_the_grid_and_stores_it(db: Connection, stores: Stores) -> None:
    sha = ingested(db, stores)
    [item] = decode_pending(db, stores.originals, stores.derived)
    expected = decode(HORIZON).grid
    assert (item.path, item.error_class) == ("ansi/horizon.ans", None)
    assert (item.cols, item.rows, item.grid_sha256) == (80, 40, expected.digest())
    row = db.execute(text("select * from decoding where sha256 = :sha"), {"sha": sha}).one()
    assert (row.decoder, row.decoder_version) == (DECODER, DECODER_VERSION)
    assert (row.status, row.error_class) == ("ok", None)
    assert (row.cols, row.rows, row.grid_sha256) == (80, 40, expected.digest())
    assert (row.document_kind, row.system, row.charset) == ("grid", "pc-vga", "cp437")
    stream = decode(HORIZON).stream
    assert (row.writes, row.overwrites, row.clears) == (
        stream.writes,
        stream.overwrites,
        stream.clears,
    )
    stored = stores.derived.get(grid_key(sha, DECODER, DECODER_VERSION))
    assert from_parquet(stored) == expected


def test_decode_is_idempotent(db: Connection, stores: Stores) -> None:
    ingested(db, stores)
    assert len(decode_pending(db, stores.originals, stores.derived)) == 1
    assert decode_pending(db, stores.originals, stores.derived) == []
    assert db.execute(text("select count(*) from decoding")).scalar_one() == 1


def test_an_unreadable_file_gets_a_classified_error_and_no_grid(
    db: Connection, tmp_path: Path, stores: Stores
) -> None:
    root = tmp_path / "golden"
    root.mkdir()
    (root / "empty.ans").write_bytes(b"")
    sha = ingest_golden(db, stores.originals, root)[0].sha256
    [item] = decode_pending(db, stores.originals, stores.derived)
    assert (item.error_class, item.grid_sha256) == ("empty", None)
    row = db.execute(text("select * from decoding where sha256 = :sha"), {"sha": sha}).one()
    assert (row.status, row.error_class, row.grid_sha256) == ("error", "empty", None)
    assert not stores.derived.exists(grid_key(sha, DECODER, DECODER_VERSION))


def test_a_corrupt_sauce_is_set_aside_and_named(
    db: Connection, tmp_path: Path, stores: Stores
) -> None:
    root = tmp_path / "golden"
    root.mkdir()
    (root / "padded.ans").write_bytes(CORRUPT_SAUCE_ART)
    sha = ingest_golden(db, stores.originals, root)[0].sha256
    [item] = decode_pending(db, stores.originals, stores.derived)
    assert (item.cols, item.rows, item.sauce_problems) == (80, 2, ("size_exceeds_file",))
    row = db.execute(text("select * from decoding where sha256 = :sha"), {"sha": sha}).one()
    assert row.sauce_problems == ["size_exceeds_file"]


def test_a_new_decoder_version_decodes_again(
    db: Connection, stores: Stores, monkeypatch: pytest.MonkeyPatch
) -> None:
    ingested(db, stores)
    decode_pending(db, stores.originals, stores.derived)
    monkeypatch.setattr("tm.decode.DECODER_VERSION", "99")
    assert len(decode_pending(db, stores.originals, stores.derived)) == 1
    versions = db.execute(text("select decoder_version from decoding order by 1")).scalars().all()
    assert versions == sorted([DECODER_VERSION, "99"])


def test_a_stored_grid_that_differs_stops_the_run(db: Connection, stores: Stores) -> None:
    sha = ingested(db, stores)
    other = Grid(80, 1, {})
    stores.derived.put(grid_key(sha, DECODER, DECODER_VERSION), to_parquet(other))
    with pytest.raises(IntegrityError, match="decoder is not stable"):
        decode_pending(db, stores.originals, stores.derived)


def test_a_stored_grid_that_matches_is_kept(db: Connection, stores: Stores) -> None:
    sha = ingested(db, stores)
    key = grid_key(sha, DECODER, DECODER_VERSION)
    stores.derived.put(key, to_parquet(decode(HORIZON).grid))
    assert len(decode_pending(db, stores.originals, stores.derived)) == 1


def test_every_art_file_gets_a_result_and_ascii_is_read_as_ansi(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    pack = tmp_path / "1996" / "mixed.zip"
    pack.parent.mkdir(parents=True)
    with zipfile.ZipFile(pack, "w") as archive:
        archive.writestr("LOGO.ASC", b"  ___\r\n /   \\\r\n")
        archive.writestr("WIDE.XB", b"XBIN\x1a\x50\x00\x19\x00\x10\x00")
        archive.writestr("README.NFO", b"not art\r\n")
    ingest_pack(db, stores.originals, pack)
    results = {
        item.path.rsplit("/", 1)[1]: item
        for item in decode_pending(db, stores.originals, stores.derived)
    }
    assert set(results) == {"LOGO.ASC", "WIDE.XB"}
    assert (results["LOGO.ASC"].error_class, results["LOGO.ASC"].cols) == (None, 80)
    assert results["WIDE.XB"].error_class == "unsupported_format"
    assert db.execute(text("select decoder, status from decoding order by decoder")).all() == [
        (NO_DECODER, "error"),
        (DECODER, "ok"),
    ]
    assert decode_pending(db, stores.originals, stores.derived) == []
