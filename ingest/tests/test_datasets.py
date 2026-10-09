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
import yaml
from sqlalchemy import Connection, text
from stores import Stores
from tm.datasets import DatasetError, build, draw_sample
from tm.decode import decode_pending
from tm.features import extract_artifact, pending_features
from tm.packs import ingest_pack
from tm.text_layer import pending_text, read_artifact
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


def pilot(tmp_path: Path) -> Path:
    """The real D1 definition, without its hand-picked packs, which the test corpus lacks."""
    for name in ("catalogue", "works"):
        definition(tmp_path, name)
    d1 = definition(tmp_path, "d1")
    spec = yaml.safe_load((d1 / "dataset.yaml").read_text())
    spec["sample"]["additions"] = []
    (d1 / "dataset.yaml").write_text(yaml.safe_dump(spec))
    return d1


def test_the_pilot_draws_its_packs_then_builds_from_the_frozen_sample(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    for year in (1992, 1995, 1996):
        for name in ("a", "b", "c", "d"):
            art = HORIZON + f"{name}{year}".encode()
            members = {f"{name.upper()}.ANS": art, "X.NFO": f"nfo {year}\r\n".encode()}
            ingest(db, stores, tmp_path / str(year) / f"{name}{year}.zip", members, "train")
    decode_pending(db, stores.originals, stores.derived)
    d1 = pilot(tmp_path)
    first = draw_sample(db, d1).read_text()
    sample = yaml.safe_load(first)
    assert first.startswith("# SPDX-FileCopyrightText")
    assert sample["frame_sizes"] == {"1990-93": 4, "1994-95": 4, "1996-97": 4}
    assert [u["weight"] for u in sample["units"]] == [4 / 3] * 9
    assert draw_sample(db, d1).read_text() == first
    built = build(db, d1, tmp_path / "build")
    drawn = {u["unit"] for u in sample["units"]}
    packs = pq.read_table(built.directory / "packs.parquet").to_pylist()
    assert {p["pack_sha256"] for p in packs} == drawn
    weights = pq.read_table(built.directory / "sample.parquet").to_pylist()
    assert {(w["pack_sha256"], w["weight"]) for w in weights} == {(u, 4 / 3) for u in drawn}
    files = pq.read_table(built.directory / "files.parquet").to_pylist()
    assert {f["pack_sha256"] for f in files} == drawn
    assert len(files) == 18
    works = pq.read_table(built.directory / "works.parquet").to_pylist()
    assert len(works) == 9


def test_a_pilot_whose_frame_changed_is_not_built(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    ingest(db, stores, tmp_path / "1995" / "a.zip", {"A.ANS": HORIZON}, "train")
    d1 = pilot(tmp_path)
    draw_sample(db, d1)
    frame = d1 / "frame.sql"
    frame.write_text(frame.read_text() + "\n-- edited\n")
    with pytest.raises(DatasetError, match="changed since the sample was drawn"):
        build(db, d1, tmp_path / "build")


def test_a_pack_added_by_hand_has_a_reason_and_no_weight(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    for name in "abcd":
        art = {"A.ANS": HORIZON + name.encode()}
        ingest(db, stores, tmp_path / "1994" / f"{name}.zip", art, "train")
    d1 = pilot(tmp_path)
    drawn = {u["unit"] for u in yaml.safe_load(draw_sample(db, d1).read_text())["units"]}
    frame = db.execute(text("select pack_sha256 from pack_split")).scalars().all()
    [left] = set(frame) - drawn
    spec = yaml.safe_load((d1 / "dataset.yaml").read_text())
    spec["sample"]["additions"] = [{"unit": left, "reason": "rare"}]
    (d1 / "dataset.yaml").write_text(yaml.safe_dump(spec))
    added = yaml.safe_load(draw_sample(db, d1).read_text())["units"][-1]
    assert (added["unit"], added["selection"], added["weight"], added["reason"]) == (
        left,
        "added",
        None,
        "rare",
    )
    spec["sample"]["additions"] = [{"unit": "f" * 64, "reason": "absent"}]
    (d1 / "dataset.yaml").write_text(yaml.safe_dump(spec))
    with pytest.raises(DatasetError, match="not in the frame"):
        draw_sample(db, d1)
