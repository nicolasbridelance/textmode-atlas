<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0016. Store grid features in a database table, publish them as `features.parquet`

- Status: Accepted
- Date: 2026-10-08
- Deciders: Claude (autonomous mode, ADR 0008); Nicolas Bridelance reviews afterwards
- Amends: the foundation document, "Pipeline d'analyse" (where features are stored)

## Context

The foundation document stores the measurements of each grid "in `features.parquet`, keyed by
the artifact hash and the extractor version". The first use is the exploration of all of
16colo: about 111,000 grids, read through datasets, which are built by SQL queries from the
database. Features kept as files in the derived bucket would have to be read back one by one,
or gathered into a file outside the database, for every dataset build.

## Decision

`tm features` writes one row per grid and extractor version into a `features` table (migration
0004). The row names the grid it measured (`grid_sha256`). Datasets read the table and publish
it as `features.parquet`, so researchers still receive the file the foundation document
describes.

Version 1 of the extractor (`tm_analysis.features`) fixes these definitions:

- A cell **shows ink** when it is not black on black: a visible glyph (not NUL, space or 0xFF)
  whose colour differs from its background, or any non-black background. Painted spaces are ink.
- **Glyph classes** in CP437: block (DB), half blocks (DC–DF), shades (B0–B2), box drawing
  (B3–DA), alphanumeric (ASCII letters and digits, accented letters 80–9A and A0–A5),
  punctuation (other printable ASCII), other. Shares are over visible glyphs.
- **Symmetry** is the Jaccard index of the ink positions and their mirror, within the ink's
  bounding box.
- **Sequence** measures use `t`, the offset of the byte that last wrote each cell: the share of
  writes that do not follow the previous cell, and the Spearman correlation between byte order
  and reading order.

The extractor is versioned and guarded like the decoder (ADR 0012), and the features of the
golden artifact are pinned in a test.

## Alternatives considered

- **One Parquet file per grid in the derived bucket**: matches the letter of the document, but
  every dataset build would read 111,000 objects.
- **One Parquet file for the corpus**: no per-grid idempotence; a rerun or a new version
  rewrites everything.
- **JSON in a `jsonb` column**: flexible, but loses types and constraints (histogram sizes,
  ranges), which the table checks.

## Consequences

- Features are queryable with the rest of the record, and datasets join them to metadata.
- They are derived data: the database backups do not need them, `tm features` rebuilds them.
- `t` keeps only the last write of each cell, so the sequence measures see the final state of an
  animation, not its frames.
