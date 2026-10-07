<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Bitmap fonts

`.f16` format: raw array of 256 glyphs, 16 bytes per glyph, one 8-pixel row per byte, most
significant bit on the left. Each file's hash is written into the profiles that use it, so a font
change changes the rendering recipe.

| File | Origin | License |
| --- | --- | --- |
| `ibm-vga-8x16.f16` | IBM VGA ROM font as distributed by libansilove (`src/fonts/font_pc_80x25.h`), extracted by `scripts/font_from_c_header.py` | BSD-2-Clause (libansilove) |

Taking ansilove's font guarantees that the museum's renderings and ansilove's start from the same
glyphs. VileR's Ultimate Oldschool PC Font Pack (CC BY-SA 4.0) will serve other video cards.
