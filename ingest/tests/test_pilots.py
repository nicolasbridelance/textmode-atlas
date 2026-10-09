# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq
import pytest
import yaml
from packs_on_disk import HORIZON, definition, ingest
from sqlalchemy import Connection, text
from stores import Stores
from tm.datasets import build, draw_sample
from tm.decode import decode_pending
from tm.pilots import SampleError

pytestmark = pytest.mark.db


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
    with pytest.raises(SampleError, match="changed since the sample was drawn"):
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
    with pytest.raises(SampleError, match="not in the frame"):
        draw_sample(db, d1)
