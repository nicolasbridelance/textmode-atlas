<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0018. Split the packs of every scene archive by the same rule, and name the archive

- Status: Accepted
- Date: 2026-10-09
- Deciders: Claude (autonomous mode, ADR 0008), at the owner's request (explore the train packs
  of every source, with the source shown); Nicolas Bridelance reviews afterwards
- Amends: migration 0005 (split views), ADR 0017 (D1 frame)

## Context

The split views of migration 0005 decide which packs exploration may read (research program,
rule 3): a pack is `test` when the first byte of its archive's SHA-256 is below 52, and a file
is `train` only when every pack holding it is. They read 16colo alone, the only archive at the
time. textfiles.com now enters as a second archive of packs (lead I25), and the owner wants the
explorer to show the train packs of every source, with the archive of each work (lead I31).

Left as they were, the views would keep every textfiles pack out of exploration, and a file
shared between a 16colo train pack and a textfiles test pack would stay `train`: the held-out
packs could be seen through another archive.

## Decision

1. `pack_split` covers the packs of every source of kind `archive`, by the same hash rule, and
   gains a column `archive` (the source's name). The rule does not depend on the source, so a
   16colo pack keeps its split.
2. `work_split` keeps its rule over every archive: a file held by a test pack anywhere is
   `test`. It gains `archives`, the archives that hold the file.
3. Dataset `works` v5 holds the train files of every archive, with `archive` (of the pack it
   is placed in: earliest year, then archive, then path) and `archives`.
4. D1 keeps its 16colo frame, now written in its query (`p.archive = '16colo'`): its sample was
   drawn on 16colo and is unchanged by the redraw (the same 24 packs; only the frame's digest
   in `sample.yaml` changes). Its version goes to 2, since its `works` table gains the columns.
5. Dataset `catalogue` stays the catalogue of 16colo, as its name in the datasheet says.

## Consequences

- Some files explored as `train` through 16colo may become `test` when a textfiles test pack
  also holds them. They have been seen already; the number is measured when textfiles is
  ingested and written in the works datasheet, and a confirmatory test can leave them out.
- The guard of a frozen sample checks the text of its frame query, not its rows (lead I32): the
  D1 frame names its archive so that a new archive cannot enter it unnoticed.
- Every further archive of packs (scene.org, Defacto2) enters the split without a new decision.
