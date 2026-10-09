# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path

import pytest
from tm_render.ansi import decode as decode_ansi
from tm_render.compact import CELL, HEADER, decode, encode
from tm_render.grid import Cell, Grid

HORIZON = Path(__file__).resolve().parents[2] / "tests/golden/ansi/horizon.ans"


def test_a_grid_comes_back_whole() -> None:
    grid = decode_ansi(HORIZON.read_bytes()).grid
    data = encode(grid, ice=True)
    assert len(data) == HEADER.size + CELL.size * grid.cols * grid.rows
    back, ice = decode(data)
    assert ice is True
    assert back.digest() == grid.digest()


def test_blink_and_unwritten_cells() -> None:
    grid = Grid(2, 1, {(0, 1): Cell(0xDB, 12, 4, True, 7)})
    back, ice = decode(encode(grid, ice=False))
    assert (back.cells, ice) == (grid.cells, False)


def test_a_foreign_file_is_refused() -> None:
    with pytest.raises(ValueError, match="TMG1"):
        decode(b"PNG\x00" + bytes(12))
