# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The text layer of a grid: what is written in letters inside a work (leads I2).

Signatures, titles, greetings and BBS ads are drawn with the same cells as the picture. A row
keeps its printable ASCII cells that show (glyph colour differs from its background); everything
else becomes a space. A row counts as text when it holds a word of at least `MIN_WORD` letters or
digits, so that lone block-drawing punctuation (`|`, `_`, `.`) is not taken for writing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from tm_render.grid import Grid

PRINTABLE = range(0x21, 0x7F)
MIN_WORD = 3
WORD = re.compile(rf"[A-Za-z0-9]{{{MIN_WORD},}}")
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
            if cell and cell.codepoint in PRINTABLE and cell.fg != cell.bg:
                chars[col] = chr(cell.codepoint)
        text = GAP.sub("   ", "".join(chars)).strip()
        if WORD.search(text):
            lines.append(TextLine(row, text))
    return lines
