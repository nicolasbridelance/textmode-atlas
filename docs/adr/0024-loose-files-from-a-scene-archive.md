<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0024. Files a scene archive holds loose: single works, split by their directory

- Status: Accepted
- Date: 2026-10-09
- Deciders: Claude (autonomous mode, ADR 0008), at the owner's request (enrich the corpus, and
  hold a work for every practice the reference articles name, lead I54); Nicolas Bridelance
  reviews afterwards
- Amends: migration 0009 and ADR 0018 (split views)

## Context

Until now every work came inside a pack: 16colo and textfiles.com's yearly artpacks are
archives, and the split views (ADR 0018) decide what exploration may read pack by pack. The
other sections of artscene.textfiles.com hold art as loose files in directories: ANSI and ASCII
collected from BBSes (`ansi/`, `asciiart/`), RTTY art (`rtty/`), VT100 animations (`vt100/`).
Some of it is a practice the corpus does not hold at all (RTTY, VT100, ASCII outside the art
groups). Packs sit in the same trees, by group or by year (`ascii/<group>/`,
`acid/ARTPACKS/<year>/`, `ice/icepacks/<year>/`).

A loose file is in no `set_member` row, so `work_split` does not know it: it would be neither
`train` nor `test`, and exploration would never see it. A directory of the site is a grouping
made by the archive's curator, not a release by the scene, so it is not a `set` (the schema's
set is a pack, a disk, a BBS).

## Decision

1. **A loose art file is a `single` work**, with no set. Its artifact keeps its path on the
   site (`asciiart/ASCIIPR0N/anime00.txt`) and its rights record the scene publication on that
   archive, at the file's URL (ADR 0009). A file the museum already holds keeps its first source,
   as for pack members. Non-art files of those trees (documents, pictures) are stored as
   artifacts without a work, as pack members are. The site's own index files (`.descs`) stay in
   the mirror: they describe the files, they are not part of them.
2. **Packs in the trees are packs**, ingested by `tm ingest pack`; given the mirror's root, their
   path is their path on the site and their URL is built from it.
3. **The format is the archive's word when the file does not say it.** A file is art by its
   extension, SAUCE record or content, as in packs; in a tree the curator declares as art of one
   kind, other text files take that kind (`ascii` for `asciiart/`, `rtty`, `vt100`). Formats no
   decoder reads get an `unsupported_format` decoding, as XBIN does today.
4. **Split by directory.** A loose file is `test` when the first byte of the SHA-256 of
   `<archive>:<its directory on the site>` is below 52, the threshold of the packs. A directory
   tends to gather one BBS, one artist or one collector, so splitting by file would let one hand
   sit on both sides; the directory is the nearest thing to a pack. The key is a name, not
   bytes, so a directory that grows keeps its split. A file that a pack also holds follows the
   packs' rule.
5. **Dates.** Loose files are undated unless their SAUCE record dates them. The `.descs` files
   often give a month ("123: Trippy (March, 2000)"): reading them as dating is a later step, with
   its basis recorded (lead).

## Consequences

- `work_split` returns loose files with `packs = 0` and their archive in `archives`; datasets
  built on it see them when their query does not require a pack. Dataset `works` places each
  file in a pack; including loose files is a new version of it, coordinated with the formats
  work that also changes it.
- RTTY and VT100 enter as originals and records before their decoders, and the foundation
  document says a system enters the museum with its decoder, profile and collection: they are
  held and counted, not shown, until then.
- Any other site that holds art loose (scene.org's trees, Defacto2) enters by the same rule.
