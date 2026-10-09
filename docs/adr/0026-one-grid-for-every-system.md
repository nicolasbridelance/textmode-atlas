<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0026. Grid v2: one grid for every system, read across the whole corpus

- Status: Accepted
- Date: 2026-10-09
- Deciders: Nicolas Bridelance ("il faut qu'on soit future proof et qu'on puisse lancer des
  analyses de données sur tout le corpus"); Claude drafted it
- Amends: the grid of the foundation document ("Étape 1, décodage"), ADR 0010 (render from the
  grid), ADR 0022 (`grid.tmg`); supersedes the grid parts of the legacy-formats work (ADR 0025)
  where they differ

## Context

The foundation document makes the grid the one intermediate format: every decoder writes it,
every renderer, measure and page reads it, nobody reads the original bytes twice. The grid we
have is a PC grid without saying so: `codepoint` is a CP437 index, `fg` and `bg` are VGA
attribute colours, the font is the VGA ROM's, `blink` is the only attribute.

What is coming does not fit it:

- **Formats of the PC scene** with their own font and palette (XBIN, ADF, IDF, BIN with a
  palette), PabloDraw's 24-bit colour. The legacy-formats branch adds a palette, a base64 font
  and 32-bit colours to the cell for them.
- **Other systems** the corpus must hold (lead I54, milestone M5): PETSCII and ATASCII (other
  character ROMs, other palettes), teletext and Minitel (mosaic characters, double height, and
  control codes that occupy a cell on screen), VT100 (DEC special graphics, double-width lines,
  animation), RTTY (a teleprinter typing several characters on the same spot), Unicode terminal
  art (wide characters).
- **Works that are not grids at all**: RIP is vector drawing; Japanese AA is set in a
  proportional font (the foundation document already refuses to force a grid on it).
- **Analysis over the whole corpus.** The decoded corpus today is about 110,000 grids and 535
  million canvas cells (decoder v4, 365 million writes). Measures must run on all of them, and
  compare a C64 work with a PC one, without reading 110,000 files one by one.

Two ways were open: a grid per system (each with its own columns), or one grid whose values are
read through the system it declares. Per-system grids would make every cross-system measure a
special case; one grid, with the system's tables as data, keeps a single query for all.

## Decision

### 1. Three kinds of document, one per decoding

A decoding yields a `grid`, a `vector` document or a `text` document (`decoding.document_kind`).

- **grid**: every fixed-pitch character art, whatever the machine (below).
- **vector**: the drawing commands, parsed (RIP): one row per command with its arguments. A
  bitmap drawn from it by a pinned backend is a rendering with its recipe (invariant 3), not the
  document.
- **text**: lines of Unicode with the reference font they were set in (Japanese AA). Measured
  only by what does not assume a grid.

### 2. The grid declares its system; cells keep native values

A grid has a **header** and **cells**. The header names, by identifier, entries of registries
kept as data in `corpus/` (CC0, validated by JSON Schema like the rest of `corpus/`):

| Header field | Meaning |
| --- | --- |
| `grid_version` | 2 |
| `system` | the machine or medium (`pc-vga`, `amiga`, `c64`, `atari-8bit`, `teletext`, `minitel`, `vt100`, `teleprinter`, `unicode-terminal`): `corpus/systems/` |
| `charset` | the character repertoire the glyph numbers index (`cp437`, `petscii-upper`, `atascii`, `teletext-g0-en`, `videotex-g1`, `dec-special`, `ita2`, `unicode`): `corpus/charsets/` |
| `palette` | an identifier of `corpus/palettes/` (`vga16`, `c64-pepto`, `teletext8`), or the SHA-256 of a palette the work carries |
| `font` | an identifier of a ROM font, or the SHA-256 of a font the work carries |
| `cols`, `rows`, `cell_w`, `cell_h`, `pixel_aspect` | canvas size and the native cell, for rendering and for measures in pixels |
| `decoder`, `decoder_version` | as today (ADR 0012) |

A font or a palette carried by a work (XBIN, ADF) is stored once in the derived store,
addressed by its SHA-256, and the grid names the hash. It is not copied into each grid, and two
works with the same font share it.

**Cells**, one row per written cell:

| Column | Type | Meaning |
| --- | --- | --- |
| `row`, `col` | u32, u16 | position |
| `layer` | u8 | 0, or the rank of a character struck over an earlier one in the same cell (teleprinter, backspace overprinting); the renderer draws every layer |
| `glyph` | u32 | the character's number in the header's charset: a ROM index, or a Unicode code point for `unicode` |
| `fg`, `bg` | u16 | indexes in the header's palette. A work in 24-bit colour gets a palette of the colours it uses, so colour is always an index |
| `attrs` | u16 | bits from a fixed registry: blink, underline, inverse, conceal, double height (top, bottom), double width, wide character (lead, trail), bold where the system draws it apart from colour |
| `control` | u16, null | the code written at this cell when the screen shows something else there (teletext and Minitel spacing attributes, which display as a space or a held mosaic) |
| `t` | u32 | offset of the byte that last wrote the cell, as today |

The glyph is a native number, not Unicode, because exactness comes first: some PETSCII and
teletext characters have no Unicode equivalent, and two ROM characters can map to one code
point. Unicode, the glyph's class (block, shade, line, mosaic, letter, digit, punctuation,
control) and its name are **columns of the charset table**, joined when needed. The same holds
for colour: RGB and CIELAB are columns of the palette table.

### 3. The stream beside the grid

The grid is the final state. Works that redraw (VT100 and ANSI animations, screens cleared and
written again: `decoding.overwrites > 0` or `clears > 0`) also get a **writes stream**: one row
per write, clear or scroll, in byte order, with the cell's values. It feeds replay, draw-order
layers and the study of how works were made; others need none, the cells' `t` is enough.

### 4. Reading the whole corpus

- Grids stay one Parquet object per artifact in the derived bucket (ADR 0011), with the header
  in the Parquet metadata and in the `decoding` row (`system`, `charset`, `document_kind`), so
  that a query can pick grids without opening them.
- `tm dataset cells` builds a **corpus-wide cell table**: the cells of every train grid, with the
  artifact's hash and the header fields as columns, partitioned by `system` and by the first
  byte of the hash, read by DuckDB or Polars by glob. With the charset and palette tables
  exported beside it, one query measures every system. About half a billion rows at today's
  size: it is built on demand, outside the repository's disk, and is not kept in Git or backed
  up (derived, rebuilt from the grids).
- **Features v2** are computed on the joined, comparable columns (glyph class, Unicode, Lab
  colour, cell aspect), so that a measure means the same on every system. Features v1 stay what
  they are: valid for `pc-vga`, `cp437`, `vga16` grids only, and marked so in their datasheet.

### 5. One file for the site

`grid.tmg` version 2 carries the header (identifiers and hashes; the site loads fonts and
palettes once, by hash) and every cell with its layer, glyph, colours, attributes and `t`, field
widths set in the header so that a PC grid stays as small as in version 1. The site keeps never
decoding a source format (CLAUDE.md, target architecture).

### 6. Moving from grid v1

A grid v1 is a grid v2 with `system = pc-vga`, `charset = cp437`, `palette = vga16`, `layer = 0`,
`attrs` = blink, no `control`: nothing is lost. Grids are derived, so they are rebuilt by a new
decoder version (ADR 0012), not converted in place; the old rows stay in `decoding` until
dropped by the usual rule. The determinism test and the ansilove parity carry over unchanged on
PC files.

## Consequences

- Every new system costs a decoder, a charset table, a palette, a font and a profile, and no
  change to the grid, the cell table, the measures or the site: that is the foundation
  document's "a decoder, a profile and a collection per system", made true for the data.
- The legacy-formats work changes before it merges: palettes and fonts by hash in the header,
  colours as palette indexes, `document_kind` in (`grid`, `vector`, `text`) instead of (`vga`,
  `extended`, `raster`), RIP's parsed commands as its document. Its decoders and its rendering
  stay.
- Charset tables are work in themselves (each ROM character with its Unicode mapping and class),
  but they are small, testable and reusable by anyone: CC0 data in `corpus/charsets/`.
- The corpus-wide cell table needs disk the codespace does not have today (6.6 GB free):
  it is built under the temporary disk or on a larger machine, and the ADR does not depend on
  where.
- Order of work: registries and grid v2 in `tm_render`, PC decoders moved to it (decoder v5),
  `tm dataset cells`, then `grid.tmg` v2 and the site; features v2 after.
