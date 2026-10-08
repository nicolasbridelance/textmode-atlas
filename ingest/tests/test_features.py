# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import Connection, text
from stores import Stores
from tm.decode import DECODER, decode_pending
from tm.features import extract_artifact, pending_features
from tm.ingest import ingest_golden
from tm.storage import IntegrityError, grid_key
from tm_analysis.features import extract
from tm_analysis.versions import FEATURES_VERSION
from tm_render.ansi import decode
from tm_render.grid import Grid, to_parquet
from tm_render.versions import DECODER_VERSION

GOLDEN = Path(__file__).resolve().parents[2] / "tests" / "golden"
HORIZON = (GOLDEN / "ansi" / "horizon.ans").read_bytes()

pytestmark = pytest.mark.db


def decoded(db: Connection, stores: Stores) -> str:
    sha = ingest_golden(db, stores.originals, GOLDEN)[0].sha256
    decode_pending(db, stores.originals, stores.derived)
    return sha


def measure_all(db: Connection, stores: Stores) -> list[str]:
    measured = []
    for row in pending_features(db):
        extract_artifact(db, stores.derived, row)
        measured.append(row.sha256)
    return measured


def test_features_are_measured_on_the_stored_grid(db: Connection, stores: Stores) -> None:
    sha = decoded(db, stores)
    assert measure_all(db, stores) == [sha]
    row = db.execute(text("select * from features where sha256 = :sha"), {"sha": sha}).one()
    expected = extract(decode(HORIZON).grid)
    assert row.extractor_version == FEATURES_VERSION
    assert (row.cols, row.rows, row.cells) == (expected.cols, expected.rows, expected.cells)
    assert row.glyph_hist == expected.glyph_hist
    assert row.fill_ratio == expected.fill_ratio


def test_features_are_measured_once(db: Connection, stores: Stores) -> None:
    decoded(db, stores)
    measure_all(db, stores)
    assert pending_features(db) == []


def test_a_grid_that_differs_from_its_decoding_row_stops_the_run(
    db: Connection, stores: Stores
) -> None:
    sha = decoded(db, stores)
    stores.derived.put(grid_key(sha, DECODER, DECODER_VERSION), to_parquet(Grid(80, 1, {})))
    with pytest.raises(IntegrityError, match="does not match its decoding row"):
        measure_all(db, stores)
