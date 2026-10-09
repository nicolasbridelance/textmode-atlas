# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Write `corpus/charsets/cp437.yaml`: the 256 glyphs of the IBM PC ROM, with Unicode and class.

Unicode follows the glyph as the VGA ROM draws it, not the control meaning: 0x01–0x1F and 0x7F
are the pictures ☺ ☻ ♥ … ⌂ (as in Unicode's own CP437 mapping for display), 0x00 and 0xFF draw
nothing. Classes are the ones features v1 counts, named for every system (ADR 0026), and the rest
of the repertoire by its Unicode category.

    uv run python scripts/make_charset_cp437.py > corpus/charsets/cp437.yaml
"""

from __future__ import annotations

import unicodedata

# The VGA ROM's pictures for the C0 controls and DEL.
LOW = "☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼"
DEL = "⌂"
SPACE, DEL_INDEX = 0x20, 0x7F
BLANK = {0x00, 0x20, 0xFF}
FULL_BLOCK = 0xDB
HALF_BLOCKS = {0xDC, 0xDD, 0xDE, 0xDF}
SHADES = {0xB0, 0xB1, 0xB2}
LINES = set(range(0xB3, 0xDB))
LETTERS = {*range(0x41, 0x5B), *range(0x61, 0x7B), *range(0x80, 0x9B), *range(0xA0, 0xA6)}
DIGITS = set(range(0x30, 0x3A))
ASCII_PUNCTUATION = set(range(0x21, 0x7F)) - LETTERS - DIGITS
HEADER = """\
# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: CC0-1.0
# Written by scripts/make_charset_cp437.py; edit the script, not this file.
title:
  en: Code page 437, the IBM PC character set as the VGA ROM draws it
  fr: Page de code 437, le jeu de caractères de l'IBM PC tel que le dessine la ROM VGA
size: 256
sources:
  - "IBM VGA Technical Reference (1987), character set"
  - "Unicode Consortium, CP437 to Unicode mapping (graphic forms of 0x01-0x1F and 0x7F)"
glyphs:"""


def char(index: int) -> str | None:
    if index in (0x00, 0xFF):
        return None if index == 0 else " "
    if index < SPACE:
        return LOW[index - 1]
    if index == DEL_INDEX:
        return DEL
    return bytes([index]).decode("cp437")


def glyph_class(index: int, text: str | None) -> str:
    fixed = (
        (BLANK, "blank"),
        ({FULL_BLOCK}, "block"),
        (HALF_BLOCKS, "half_block"),
        (SHADES, "shade"),
        (LINES, "line"),
        (LETTERS, "letter"),
        (DIGITS, "digit"),
        (ASCII_PUNCTUATION, "punctuation"),
    )
    for indexes, name in fixed:
        if index in indexes:
            return name
    category = unicodedata.category(text or " ")
    return "letter" if category.startswith("L") else "symbol"


def main() -> None:
    print(HEADER)
    for index in range(256):
        text = char(index)
        code = "null" if text is None else f'"{ord(text):04X}"'
        print(f"  - {{index: {index}, unicode: {code}, class: {glyph_class(index, text)}}}")


if __name__ == "__main__":
    main()
