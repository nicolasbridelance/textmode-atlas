<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Datasheet: d1 (pilot)

After *Datasheets for Datasets* (Gebru et al.). Definition: [dataset.yaml](dataset.yaml); sample:
[sample.yaml](sample.yaml); design: [ADR 0017](../../docs/adr/0017-d1-pilot-sampling.md). Draw:
`uv run tm dataset draw d1` (only to redraw); build: `uv run tm dataset build d1`.

## Motivation

The pilot of the research program (R0): a handful of packs taken through the whole pipeline,
read by hand, and annotated for the gold set D2 (credits, greetings, NFO text). It is for
building and checking instruments, not for estimating anything about the corpus precisely.

## Composition

- `sample`: the 21 packs drawn, three per era, and the 3 added by hand, with the stratum, the
  inclusion weight (packs of the stratum in the frame / packs drawn) and, for an added pack, the
  reason.
- `packs`: those packs as in dataset `catalogue` (name, path, year, archive, members).
- `files`: every file of those packs, art or not (NFO, DIZ, pictures, music), as in dataset
  `catalogue`.
- `works`, `features`, `text`: the art files of those packs and their measures, as in dataset
  `works` (train files only).
- No artwork and no grid. `text` quotes the works: the dataset stays local, like `works`.

## Collection and processing

- **Frame** ([frame.sql](frame.sql)): train packs of 16colo whose archive was read whole, 4,559
  on 2026-10-09; other archives are left out by name (ADR 0018, v2: same sample, new columns). Strata: seven eras of filing year (1990–93, 1994–95, 1996–97, 1998–99, 2000–04,
  2005–12, 2013–26), bounded by the mass of packs.
- **Draw**: three packs per era, systematic from a random start (seed 20261009) over the packs
  sorted by dominant content kind, then by number of files. Each drawn pack has inclusion
  probability n/N in its era; its weight is N/n.
- **Added by hand**: rare cases the draw missed, each with its reason in `sample.yaml`; no weight.
- `sample.yaml` records the SHA-256 of the frame query; the build stops if the query changed.

## Known limits

- Three packs per era: any estimate has a large variance. Weighted means must use `weight`
  and leave added packs out.
- The era is 16colo's filing year, not a release date (works note).
- A file shared with a test pack is in `files` but not in `works`, `features` or `text`
  (rule 3: test files stay unexamined).
- The frame excludes the 34 train packs whose archives could not be read whole; one of them may
  be added by hand as a rare case.

## Uses

Building the notebook template, checking the pipeline on whole packs, annotating credits and
greetings by hand (D2). Not for confirmatory tests, and not alone for claims about the scene.

## Distribution and maintenance

Built locally into `datasets/build/d1/<version>/` (not in Git). The sample is frozen in Git; a
new draw is a new version, decided by an ADR.
