# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

from tm_render.ansi import decode
from tm_render.grid import Grid, from_parquet, to_parquet

GOLDEN = Path(__file__).resolve().parents[2] / "tests" / "golden" / "ansi" / "horizon.ans"


def test_parquet_round_trip() -> None:
    grid = decode(GOLDEN.read_bytes()).grid
    again = from_parquet(to_parquet(grid))
    assert again == grid
    assert again.digest() == grid.digest()


def test_empty_grid_round_trip() -> None:
    grid = Grid(80, 1, {})
    assert from_parquet(to_parquet(grid)) == grid
