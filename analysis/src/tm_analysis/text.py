# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The text layer of a grid: what is written in letters inside a work (leads I2).

Signatures, titles, greetings and BBS ads are drawn with the same cells as the picture. A row
keeps the cells that show (glyph colour differs from its background) and hold printable ASCII or
a CP437 letter of the 0x80–0xA5 range (é, ü, ñ…) or ß, read as Unicode; everything else becomes a
space. A row counts as text when it holds a word of at least `MIN_WORD` letters or digits with
one of them in ASCII, so that lone block-drawing punctuation (`|`, `_`, `.`) and rows of accented
letters used as texture (`ÑÑÑ`) are not taken for writing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from tm_render.grid import Grid

PRINTABLE = range(0x21, 0x7F)
LATIN = [*range(0x80, 0xA6), 0xE1]  # CP437 accented letters (¢ £ ¥ ₧ ƒ among them), and ß
SHOWN = {code: bytes([code]).decode("cp437") for code in [*PRINTABLE, *LATIN]}
MIN_WORD = 3
TOKEN = re.compile(r"[^\W_]+")  # letters and digits, accented ones included
ASCII = re.compile(r"[A-Za-z0-9]")
GAP = re.compile(r" {4,}")  # wide gaps are columns of the drawing, not spaces in a sentence


@dataclass(frozen=True)
class TextLine:
    row: int
    text: str


def text_lines(grid: Grid) -> list[TextLine]:
    lines: list[TextLine] = []
    for row in range(grid.rows):
        chars = [" "] * grid.cols
        for col in range(grid.cols):
            cell = grid.cell(row, col)
            if cell and cell.glyph in SHOWN and cell.fg != cell.bg:
                chars[col] = SHOWN[cell.glyph]
        text = GAP.sub("   ", "".join(chars)).strip()
        if _has_word(text):
            lines.append(TextLine(row, text))
    return lines


def _has_word(text: str) -> bool:
    return any(len(token) >= MIN_WORD and ASCII.search(token) for token in TOKEN.findall(text))
