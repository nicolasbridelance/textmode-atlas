# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest
from packs_on_disk import HORIZON, definition, ingest
from sqlalchemy import Connection, text
from stores import Stores
from tm.datasets import DatasetError, build
from tm.decode import decode_pending
from tm.features import extract_artifact, pending_features
from tm.text_layer import pending_text, read_artifact
from tm_render.versions import DECODER_VERSION

pytestmark = pytest.mark.db


def catalogue(tmp_path: Path) -> Path:
    return definition(tmp_path, "catalogue")


def test_the_catalogue_lists_packs_and_their_files(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    ingest(db, stores, tmp_path / "1995" / "a.zip", {"A.ANS": HORIZON, "A.NFO": b"nfo\r\n"})
    ingest(db, stores, tmp_path / "1996" / "b.zip", {"B.ANS": HORIZON})
    built = build(db, catalogue(tmp_path), tmp_path / "build")
    assert built.rows == {"files": 3, "packs": 2}
    packs = pq.read_table(built.directory / "packs.parquet").to_pylist()
    assert sorted((p["pack"], p["year"], p["expansion"], p["members"]) for p in packs) == [
        ("a", 1995, "ok", 2),
        ("b", 1996, "ok", 1),
    ]
    files = pq.read_table(built.directory / "files.parquet").to_pylist()
    art = {f["path"]: (f["is_art"], f["sauce_title"], f["sauce_width"]) for f in files}
    assert art == {
        "A.ANS": (True, "Horizon", 80),
        "A.NFO": (False, None, None),
        "B.ANS": (True, "Horizon", 80),
    }


def test_building_twice_gives_the_same_bytes(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    ingest(db, stores, tmp_path / "1995" / "a.zip", {"A.ANS": HORIZON, "A.NFO": b"nfo\r\n"})
    definition = catalogue(tmp_path)
    first = build(db, definition, tmp_path / "one").directory
    second = build(db, definition, tmp_path / "two").directory
    names = sorted(p.name for p in first.iterdir())
    assert names == ["files.parquet", "manifest.json", "packs.parquet"]
    for name in names:
        assert (first / name).read_bytes() == (second / name).read_bytes()
    manifest = json.loads((first / "manifest.json").read_text())
    head = db.execute(text("select version_num from alembic_version")).scalar_one()
    assert manifest["migration"] == head
    assert manifest["extractors"]["decoder"] == f"tm_render.ansi@{DECODER_VERSION}"


def test_works_hold_the_train_packs_only(db: Connection, stores: Stores, tmp_path: Path) -> None:
    shared = b"\x1b[1;34mshared logo\r\n"
    train = {"KEPT.ANS": HORIZON, "SHARED.ANS": shared, "KEPT.XB": b"XBIN\x1a\x50\x00\x19\x00"}
    ingest(db, stores, tmp_path / "1995" / "t.zip", train, split="train")
    ingest(
        db, stores, tmp_path / "1996" / "x.zip", {"X.ANS": b"sealed\r\n", "S.ANS": shared}, "test"
    )
    decode_pending(db, stores.originals, stores.derived)
    for row in pending_features(db):
        extract_artifact(db, stores.derived, row)
    for row in pending_text(db):
        read_artifact(db, stores.derived, row)
    built = build(db, definition(tmp_path, "works"), tmp_path / "build")
    works = pq.read_table(built.directory / "works.parquet").to_pylist()
    assert {(w["path"], w["decoding"], w["decoding_error"]) for w in works} == {
        ("KEPT.ANS", "ok", None),
        ("KEPT.XB", "error", "unsupported_format"),
    }
    [kept] = [w for w in works if w["path"] == "KEPT.ANS"]
    assert (kept["year"], kept["packs"], kept["sauce_problems"]) == (1995, 1, [])
    assert kept["content_kind"] == "coloured_blocks"
    features = pq.read_table(built.directory / "features.parquet").to_pylist()
    assert [f["sha256"] for f in features] == [kept["sha256"]]
    assert len(features[0]["glyph_hist"]) == 256
    lines = pq.read_table(built.directory / "text.parquet").to_pylist()
    assert lines
    assert {line["sha256"] for line in lines} == {kept["sha256"]}
    assert [line["row"] for line in lines] == sorted(line["row"] for line in lines)


def test_columns_must_match_the_definition(db: Connection, tmp_path: Path) -> None:
    definition = catalogue(tmp_path)
    query = definition / "packs.sql"
    query.write_text(query.read_text().replace("w.title as pack,", "w.title as name,"))
    with pytest.raises(DatasetError, match="declares"):
        build(db, definition, tmp_path / "build")


def test_the_key_must_identify_rows(db: Connection, stores: Stores, tmp_path: Path) -> None:
    ingest(db, stores, tmp_path / "1995" / "a.zip", {"A.ANS": HORIZON, "A.NFO": b"nfo\r\n"})
    definition = catalogue(tmp_path)
    yaml_file = definition / "dataset.yaml"
    yaml_file.write_text(
        yaml_file.read_text().replace("key: [pack_sha256, path]", "key: [pack_sha256]")
    )
    with pytest.raises(DatasetError, match="duplicates"):
        build(db, definition, tmp_path / "build")


def test_the_key_must_name_declared_columns(db: Connection, tmp_path: Path) -> None:
    definition = catalogue(tmp_path)
    yaml_file = definition / "dataset.yaml"
    yaml_file.write_text(yaml_file.read_text().replace("key: [pack_sha256]", "key: [sha]"))
    with pytest.raises(DatasetError, match="not declared"):
        build(db, definition, tmp_path / "build")
