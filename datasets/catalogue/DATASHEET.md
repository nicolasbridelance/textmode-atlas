<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Datasheet: catalogue

After *Datasheets for Datasets* (Gebru et al.). Definition: [dataset.yaml](dataset.yaml), with
the meaning of every column. Build: `uv run tm dataset build catalogue`.

## Motivation

Describe all of 16colo before choosing anything from it (roadmap, step 2): years, groups,
formats, SAUCE presence, widths, iCE colours, fonts, NFO and DIZ files. The strata of the D1
pilot are drawn from this description. It is the first form of D3 (16colo metadata,
[research programme](../../docs/research-program.md#data-foundations)).

## Composition

- `packs`: one row per pack archive of the local 16colo mirror (`rsync://16colo.rs/archive-pack/`)
  that `tm ingest pack` has recorded, with the outcome of reading it.
- `files`: one row per file found in a pack. A file present in several packs has one row per
  pack and one `sha256`; deduplicate on `sha256` to count distinct files.
- Metadata only: no artwork, no grid, no image. SAUCE fields are copied as recorded, unchecked
  (dates can be impossible, names inconsistent). Authors and groups are handles as signed; the
  dataset holds no civil identity.
- `split`: about one pack in five is `test`, drawn from the archive hash; every file follows its
  pack. A descriptive study does not need it; it is there so that later models on this data
  never mix a pack across train and test.

## Collection and processing

- Packs come from 16colo's mirror, as released by the scene ([source note](../../docs/sources/16colo.md)).
- A file is art when its extension, its SAUCE record or its content says so (`tm.packs`); other
  files keep their extension as format, NFO and DIZ files are named as such.
- `decoding` and the canvas size come from the current ANSI decoder (`manifest.json` names its
  version); only ANSI is decoded so far, other art formats are null there.
- Packs ingested before migration 0002 have a null `expansion` until `tm ingest pack` runs again.

## Known limits

- Coverage: 16colo is one archive among several, and holds what was submitted to it. The
  `lost_items` count of the manifest (packs known to have existed but not found) is empty until
  the gap register is filled; the coverage of this dataset is unknown.
- The mirror holds more archives than the 16colo API lists packs; some packs are split over
  several archives. A pack here is an archive.
- About ten packs are withheld by 16colo (source note); six were refused by the server when the
  mirror was made (journal, 2026-10-08).
- `year` is the year 16colo files the pack under, not a release date.

## Uses

Description of the corpus and choice of strata. Not suitable alone for claims about the scene as
a whole (see coverage).

## Distribution and maintenance

Built locally into `datasets/build/catalogue/<version>/` (not in Git). Deposit on Zenodo comes
with the public datasets (M4). The version in `dataset.yaml` changes when a column changes;
`manifest.json` records the database migration, the extractor versions, the SHA-256 of every
query and file.
