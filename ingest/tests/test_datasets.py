# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import pyarrow.parquet as pq
import pytest
from sqlalchemy import Connection, text
from stores import Stores
from tm.datasets import DatasetError, build
from tm.decode import decode_pending
from tm.features import extract_artifact, pending_features
from tm.packs import ingest_pack
from tm_render.versions import DECODER_VERSION

ROOT = Path(__file__).resolve().parents[2]
HORIZON = (ROOT / "tests/golden/ansi/horizon.ans").read_bytes()
TEST_BELOW = 52

pytestmark = pytest.mark.db


def ingest(
    db: Connection, stores: Stores, path: Path, members: dict[str, bytes], split: str = ""
) -> None:
    """Write and ingest a pack; with `split`, vary the archive comment until its hash falls in
    that split (first byte below 52: test)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1000):
        with zipfile.ZipFile(path, "w") as archive:
            archive.comment = str(attempt).encode()
            for name, data in members.items():
                archive.writestr(name, data)
        is_test = hashlib.sha256(path.read_bytes()).digest()[0] < TEST_BELOW
        if not split or split == ("test" if is_test else "train"):
            break
    ingest_pack(db, stores.originals, path)


def definition(tmp_path: Path, name: str = "catalogue") -> Path:
    copy = tmp_path / "definitions" / name
    shutil.copytree(ROOT / "datasets" / name, copy)
    return copy


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
    built = build(db, definition(tmp_path, "works"), tmp_path / "build")
    works = pq.read_table(built.directory / "works.parquet").to_pylist()
    assert {(w["path"], w["decoding"], w["decoding_error"]) for w in works} == {
        ("KEPT.ANS", "ok", None),
        ("KEPT.XB", "error", "unsupported_format"),
    }
    [kept] = [w for w in works if w["path"] == "KEPT.ANS"]
    assert (kept["year"], kept["packs"], kept["sauce_problems"]) == (1995, 1, [])
    features = pq.read_table(built.directory / "features.parquet").to_pylist()
    assert [f["sha256"] for f in features] == [kept["sha256"]]
    assert len(features[0]["glyph_hist"]) == 256


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
