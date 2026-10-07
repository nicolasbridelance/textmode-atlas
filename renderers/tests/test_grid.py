# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

from tm_render.ansi import decode
from tm_render.grid import Grid, read_parquet, write_parquet

GOLDEN = Path(__file__).resolve().parents[2] / "tests" / "golden" / "ansi" / "horizon.ans"


def test_parquet_round_trip(tmp_path: Path) -> None:
    grid = decode(GOLDEN.read_bytes()).grid
    write_parquet(grid, tmp_path / "grid.parquet")
    again = read_parquet(tmp_path / "grid.parquet")
    assert again == grid
    assert again.digest() == grid.digest()


def test_empty_grid_round_trip(tmp_path: Path) -> None:
    grid = Grid(80, 1, {})
    write_parquet(grid, tmp_path / "grid.parquet")
    assert read_parquet(tmp_path / "grid.parquet") == grid
