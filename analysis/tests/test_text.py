# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from tm_analysis.text import TextLine, text_lines
from tm_render.ansi import decode
from tm_render.grid import Cell, Grid


def test_rows_with_words_are_kept_and_blocks_are_not() -> None:
    grid = decode(b"\xdb\xdb\xdb\xdb\r\nrs^mdn 1996\r\n|_|.\r\n").grid
    assert text_lines(grid) == [TextLine(1, "rs^mdn 1996")]


def test_wide_gaps_are_shortened_and_hidden_letters_dropped() -> None:
    cells = {(0, c): Cell(ord(x), 7, 0, False, c) for c, x in enumerate("call") if x != " "}
    cells |= {(0, 20 + c): Cell(ord(x), 7, 0, False, 20 + c) for c, x in enumerate("now")}
    cells[(0, 30)] = Cell(ord("x"), 0, 0, False, 30)  # black on black: not shown
    assert text_lines(Grid(80, 1, cells)) == [TextLine(0, "call   now")]


def test_an_empty_grid_has_no_text() -> None:
    assert text_lines(Grid(80, 2, {})) == []


def test_cp437_letters_are_kept_and_texture_is_not_text() -> None:
    grid = decode("año é\r\nÑÑÑÑ ¢¢¢\r\nGrüße\r\n".encode("cp437")).grid
    assert text_lines(grid) == [TextLine(0, "año é"), TextLine(2, "Grüße")]
