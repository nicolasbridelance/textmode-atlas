<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0001. Does our grid renderer match ansilove pixel for pixel?

- Date: 2026-10-07 · Time box: 3 h · Time spent: about 1 h
- Branch: spike/0001-ansilove-parity (deleted)

## Question

If the conservation PNG is drawn from our grid (decoder in `tm_render`, font from libansilove,
ADR 0005), does it match what ansilove draws from the raw bytes, on real packs, including blink,
iCE colours, the 9th column and the SAUCE flags? If it does, the museum can render from the grid
it already uses for the site and the analysis, and keep ansilove as an oracle.

## Method

- Instrument: a 40-line renderer (grid → RGB with the `.f16` font and the 16-colour VGA palette,
  8 or 9 pixel cells, 9th column repeated for C0–DF, background +8 for blink cells in iCE mode,
  foreground drawn for blink cells otherwise), compared byte for byte with ansilove's PNG
  converted to RGB.
- Reference: ansilove 4.2.2 / libansilove from the development image (`-S`: SAUCE hints).
- Corpus: Horizon, plus five packs from 16colo.rs kept in the ignored `data/` directory:
  `acid-50a`, `fire0895` (1995–1996, blink mode, 8 px), `blocktronics_1980`, `impure54`,
  `mist1014` (2014, iCE, 8 and 9 px, some with no SAUCE): 122 `.ans` files.

## Findings

| Group | Files | Outcome |
| --- | --- | --- |
| Horizon (9 px, 309 cells in C0–DF) | 1 | identical, 0 of 460,800 pixels differ |
| SAUCE font is Amiga Topaz | 23 | different glyphs, as expected: another profile, out of scope |
| IBM VGA font, or no font named | 99 | **96 identical** (iCE, blink, 8 px, 9 px, no SAUCE) |

The three remaining files, and two traps met on the way:

- **ansilove draws the SAUCE record as art** when the file has no EOF byte (0x1A) before it:
  `fil-slip.ans` ends with two extra rows reading `COMNTnvscene 2014 entry … SAUCE00under the
  black flag …`. Ours stops at the record, which is correct.
- **PabloDraw 24-bit colour** (`ESC[1;R;G;Bt`): `wz-clockmaker.ans` and `tcf - Huangzenegger.ans`
  use it; our decoder skips the sequence (3,458 times in the latter), so colours differ and, in
  the latter, the layout diverges from row 9. A decoder extension, not a renderer question.
- **Canvas height.** Our decoder takes `max(last written row + 1, SAUCE height)`. SAUCE heights
  are often too large (by 1 to 7 rows in 13 files: the trailing CR LF counted as a row). ansilove
  stops at the last written row. Once our height does the same, those 13 files are identical.
- **Aspect flag.** With `-S`, ansilove applies the SAUCE "legacy aspect" bits by stretching the
  image 1.35 times (`bf-mst20.ans`). A conservation PNG is integer-scaled, without interpolation
  (foundation document): aspect belongs to the authentic profile. Rendered without the stretch,
  `bf-mst20.ans` is identical.
- **Blink.** In blink mode ansilove draws blinking cells in their visible phase (foreground
  shown); 4 files with blinking cells are identical on that basis.

Not measured: speed (the instrument draws pixel by pixel; the production renderer will build
scanlines per glyph), and the XBIN and ASCII paths.

## Recommendation

Render conservation PNGs from the grid in `tm_render`, and keep ansilove, pinned in the
development image, as a reference to compare against: [ADR 0010](../adr/0010-render-from-the-grid.md).
Follow-ups:

- decoder: canvas height is the last written row + 1; the SAUCE height stays in `artifact.sauce`;
- decoder: PabloDraw 24-bit colour, before M4 (it appears in recent packs);
- profiles: Amiga Topaz fonts, with the other video cards (VileR's pack, ADR 0005);
- a golden artifact with blinking cells, iCE colours and 8 px cells, since Horizon has none.
