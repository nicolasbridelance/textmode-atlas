<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Datasheet: works

After *Datasheets for Datasets* (Gebru et al.). Definition: [dataset.yaml](dataset.yaml), with
the meaning of every column. Build: `uv run tm dataset build works`.

## Motivation

Look at the art of 16colo, as images and as measurements, before choosing the D1 pilot
(roadmap, step 5). It is exploratory material: what it shows are leads, to be tested later on
packs nobody has examined.

## Composition

- `works`: one row per art file of the **train** packs of every scene archive (view
  `work_split`, ADR 0018): metadata, the archive of its pack and every archive holding it, SAUCE as
  recorded, decoding, and the key of its conservation rendering once `tm render` has run.
- `features`: one row per decoded grid of those files, from the feature extractor
  (`manifest.json` names its version; definitions in ADR 0016). Published as `features.parquet`.
- `text`: one row per line of a decoded grid that holds a word (letters or digits, three or
  more), from the text extractor (`tm_analysis.text`, version in `manifest.json`): signatures,
  greetings, titles, BBS ads, as drawn in the cells. Published as `text.parquet`.
- No artwork and no grid: the renderings stay in the private derived bucket, and are read from
  it locally by the notebooks. `text` does quote the works: it is an excerpt of each, and is
  the first reason this dataset stays local.
- A file held by several packs appears once, in its earliest pack; `packs` counts the others.
- From v6, files an archive holds loose, outside any pack (textfiles.com's BBS ANSI and ASCII,
  RTTY, VT100; ADR 0024), with no pack, `packs` = 0 and their path on the site; and the grid's
  `system` and `charset` (ADR 0026), all `pc-vga` and `cp437` so far.
- From v7, the texts of packs are works too (ADR 0033): NFO, FILE_ID.DIZ and text files, with
  `format` `nfo`, `diz` or `text`. Filter on `format` to study the art alone.

## Collection and processing

- Packs come from the mirrors of 16colo and, from v5, textfiles.com, as released by the scene
  ([source notes](../../docs/sources/README.md)). A file met in both archives is placed in its
  earliest pack, 16colo first in the same year.
- **Split.** A pack is `test` when the first byte of its archive's SHA-256 is below 52 (about one
  pack in five), the same rule as dataset `catalogue`, in every archive. A file is `train` only
  when every pack holding it, in any archive, is `train`, so about a fifth of the works are left out, and stay unexamined
  ([research program](../../docs/research-program.md), rule 3). A file held loose is split by
  its directory on the site, with the same threshold (ADR 0024).
- ANSI and ASCII are decoded by the ANSI decoder; other formats carry `unsupported_format` and
  have no features. A SAUCE record with corrupt binary fields gives no width (ADR 0015).
- Features are measured on the grid, never on pixels. `t` keeps the last write of each cell, so
  the sequence measures see the final state of an animation.

## Known limits

- **Seen, then held out.** When textfiles entered (v5, 2026-10-09), 382 files already explored
  as `train` through 16colo became `test`, because a textfiles test pack also holds them. They
  are listed in [seen-then-test.yaml](seen-then-test.yaml); a confirmatory test leaves them out
  (ADR 0018).

- **Loose files are a different population.** They were gathered by textfiles.com from BBSes and
  FTP sites, not released in packs: undated unless their SAUCE says, and grouped by the curator's
  directories. Compare them with pack files only knowing that.
- Coverage: as for `catalogue`; 16colo holds what was submitted to it, and the gap register is
  empty, so the coverage of this dataset is unknown.
- `year` is the year the archive files the pack under, not a release date.
- The text layer reads letters cell by cell: a word drawn in blocks or in a custom font is not
  text to it, letters used as shading are; accented letters outside CP437 (ã, õ, Polish or
  Nordic letters in other code pages) come out as other glyphs or not at all, and tags shorter than three characters (`rs`) are
  left out unless a longer word shares their row.
- Excluding files shared with test packs removes more of the widely circulated files (logos,
  intros, group ads) than of the others; counts of such files are biased down.

## Uses

Exploration: distributions over time, contact sheets, leads for hypotheses. Not for confirmatory
tests (they use the test packs), and not alone for claims about the scene as a whole.

## Distribution and maintenance

Built locally into `datasets/build/works/<version>/` (not in Git). Not deposited publicly until
the rights of each work allow it (`can_display()`). The version in `dataset.yaml` changes when a
column changes; `manifest.json` records the database migration, the extractor versions, the
SHA-256 of every query and file.
