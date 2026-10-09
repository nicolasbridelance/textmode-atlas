# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The extractors that read stored grids: features and text layer."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from sqlalchemy import Connection, text
from stores import Stores
from tm import features, render, text_layer
from tm.decode import DECODER
from tm.storage import IntegrityError, grid_key
from tm_analysis.features import extract
from tm_analysis.text import text_lines
from tm_analysis.versions import FEATURES_VERSION, TEXT_VERSION
from tm_render.ansi import decode
from tm_render.conservation import BitmapFont
from tm_render.grid import Grid, to_parquet
from tm_render.versions import DECODER_VERSION

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "tests" / "golden"
HORIZON = (GOLDEN / "ansi" / "horizon.ans").read_bytes()
EMPTY = Grid(80, 1, {})

pytestmark = pytest.mark.db

Run = Callable[[Connection, Stores], list[str]]


def measure_all(db: Connection, stores: Stores) -> list[str]:
    measured = []
    for row in features.pending_features(db):
        features.extract_artifact(db, stores.derived, row)
        measured.append(row.sha256)
    return measured


def read_all(db: Connection, stores: Stores) -> list[str]:
    read = []
    for row in text_layer.pending_text(db):
        text_layer.read_artifact(db, stores.derived, row)
        read.append(row.sha256)
    return read


def test_features_are_measured_on_the_stored_grid(
    db: Connection, stores: Stores, horizon: str
) -> None:
    assert measure_all(db, stores) == [horizon]
    row = db.execute(text("select * from features where sha256 = :sha"), {"sha": horizon}).one()
    expected = extract(decode(HORIZON).grid)
    assert row.extractor_version == FEATURES_VERSION
    assert (row.cols, row.rows, row.cells) == (expected.cols, expected.rows, expected.cells)
    assert row.glyph_hist == expected.glyph_hist
    assert row.fill_ratio == expected.fill_ratio


def test_features_are_measured_once(db: Connection, stores: Stores, horizon: str) -> None:
    measure_all(db, stores)
    assert features.pending_features(db) == []


def test_the_text_layer_is_read_from_the_stored_grid(
    db: Connection, stores: Stores, horizon: str
) -> None:
    assert read_all(db, stores) == [horizon]
    row = db.execute(text("select * from text_layer where sha256 = :sha"), {"sha": horizon}).one()
    expected = text_lines(decode(HORIZON).grid)
    assert row.extractor_version == TEXT_VERSION
    assert row.line_rows == [line.row for line in expected]
    assert row.lines == [line.text for line in expected]


def test_a_grid_without_words_is_read_once(db: Connection, stores: Stores, horizon: str) -> None:
    stores.derived.put(grid_key(horizon, DECODER, DECODER_VERSION), to_parquet(EMPTY))
    db.execute(
        text("update decoding set grid_sha256 = :g where sha256 = :sha"),
        {"g": EMPTY.digest(), "sha": horizon},
    )
    assert read_all(db, stores) == [horizon]
    assert db.execute(text("select lines from text_layer")).scalar_one() == []
    assert text_layer.pending_text(db) == []


@pytest.mark.parametrize("run", [measure_all, read_all])
def test_a_grid_that_differs_from_its_decoding_row_stops_the_run(
    db: Connection, stores: Stores, horizon: str, run: Run
) -> None:
    stores.derived.put(grid_key(horizon, DECODER, DECODER_VERSION), to_parquet(EMPTY))
    with pytest.raises(IntegrityError, match="does not match its decoding row"):
        run(db, stores)


def test_the_v1_extractors_and_the_renderer_leave_other_systems_alone(
    db: Connection, stores: Stores, horizon: str
) -> None:
    """Features v1, text v2 and the conservation renderer read VGA and CP437 (ADR 0026)."""
    db.execute(
        text("update decoding set system = 'c64', charset = 'petscii-upper' where sha256 = :s"),
        {"s": horizon},
    )
    assert measure_all(db, stores) == []
    assert read_all(db, stores) == []
    font = BitmapFont.load(ROOT / "corpus" / "fonts" / "ibm-vga-8x16.f16")
    assert render.pending_renderings(db, font, 1) == []
