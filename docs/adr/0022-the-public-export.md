<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0022. What `tm export` publishes: a record, a compact grid and a PNG per work, nothing else

- Status: Accepted
- Date: 2026-10-09
- Deciders: Claude (autonomous mode, ADR 0008), roadmap step 7; Nicolas Bridelance reviews
  afterwards
- Relates to: ADR 0009 (credit, withdrawal), 0011 (derived bucket), 0020 (audience grid),
  0021 (provenance); invariants 1, 6, 9, 10

## Context

The site reads what the pipeline exports; it never decodes ANSI and never decides what may be
shown (foundation document). The export is therefore where the rules are applied. Rights come
from `can_display()`, the audience from `audience()`, the credit and the withdrawal link from
ADR 0009, provenance from ADR 0021. Only renderings of acquired files may leave (invariant 9).

## Decision

1. **One decision per work, on the server.**

   | Outcome | When | Published |
   | --- | --- | --- |
   | nothing | withdrawn, or `withheld` | nothing; whatever an earlier export published is deleted |
   | record | display for metadata only, or level 18 while there is no age check (ADR 0019) | `record.json` |
   | files | everything else | `record.json`, `grid.tmg`, `conservation.png` |

   A work that would be shown without a credit link to its archive, or without a conservation
   rendering of its acquired file, is refused, and the export says so.
2. **Every object lives under `works/<sha256>/`.** An export removes what it may no longer
   show without listing the bucket. The record names the SHA-256 of every file, so an unchanged
   work is not written again.
3. **`record.json`**, schema 1:
   - the title and the file name;
   - the year;
   - the credit as signed: handle and group from SAUCE, never a civil name, then the pack, the
     archive and the link to the pack;
   - the audience: level, descriptors, notices, whether reviewed;
   - what is shown, and the canvas size and iCE flag;
   - the files and their hashes;
   - the provenance of every acquisition, direct or through the archive;
   - the withdrawal link (`TM_WITHDRAW_URL`).
4. **`grid.tmg`**, the compact grid ([tm_render/compact.py](../../renderers/src/tm_render/compact.py)):
   - a 16-byte header: magic `TMG1`, version, flags (iCE), columns, rows;
   - then 8 bytes for every cell of the canvas, row by row: code point (u16), foreground,
     background with the blink bit on top, and `t` (u32, `0xFFFFFFFF` for a cell never written).

   The site draws the cells in increasing `t` to replay the arrival at modem speed. The format
   is versioned by its magic and version byte, and is part of the published grid specification
   that preservation will need (roadmap).
5. **`conservation.png`**, the rendering of ADR 0010 with international text chunks added
   (`Title`, `Author`, `Source`, `Copyright` with the withdrawal link, `Comment` with the
   provenance). Its pixels are the stored rendering's, which a test checks.
6. **`tm export` is idempotent and sharded** like the other commands. The module that decides,
   `tm.export`, is held at 100% branch coverage with `rights.py` and `audience.py`, and a test
   checks that a withdrawn work never stays in the public bucket.

## Consequences

- The work screen (step 8) reads a record, a grid and a PNG per work, all public, with no
  database and no ANSI.
- Lists for the rooms (by audience ceiling, by pack, by year) are not exported yet; they will be
  written by the same command, so that a list never names a work it may not show.
- 18 stays metadata only until the owner and the lawyer decide the age check.
- Three indexes (migration 0013) bring the export query from minutes to seconds for the whole
  corpus.
