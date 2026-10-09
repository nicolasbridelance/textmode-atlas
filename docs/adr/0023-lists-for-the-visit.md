<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0023. Export the lists a visit walks through, and the words of a shown work

- Status: Accepted
- Date: 2026-10-09
- Deciders: Claude (autonomous mode, ADR 0008), roadmap step 11; Nicolas Bridelance reviews
  afterwards
- Relates to: ADR 0009 (credit), 0020 (audience grid), 0022 (public export); invariants 6, 7, 10

## Context

The work screen's second pass (roadmap step 11) needs what the first could not do with one
record per work:

- an entrance on a work, the same for everyone on a given day (foundation document, "Arriver");
- ways out: the next work of the pack, another work with the same signature, a work of the same
  year elsewhere ("Continuer");
- the words of the work as text, for screen readers ("Accessibilité").

ADR 0022 said that such lists would be written by `tm export`, so that a list never names a work
it may not show. The site still decides nothing.

## Decision

1. **Record schema 2.** `record.json` gains:
   - `text`: the lines of the text layer (`text_layer`, current extractor version, same grid),
     as `{row, text}`. Only when the files are shown: the words of a work are part of the work.
   - `lists`: the paths of the lists the work belongs to (`pack`, `author`, `year`), or `null`.
2. **`tm lists`** writes, under `lists/`, from the same decision as the works
   (`tm.export.decide`), and only works whose files are shown:

   | File | Content | Order |
   | --- | --- | --- |
   | `packs/<archive>-<pack>.json` | the pack's shown works | path in the pack |
   | `authors/<handle>.json` | the works signed with that handle in SAUCE | year, pack, path |
   | `years/<year>.json` | at most 120 works of that year | a fixed hash of the SHA-256 |
   | `days.json` | 366 works, one per day of the year | a fixed hash of the SHA-256 |

   An entry carries what a way out shows: SHA-256, title, file, signature, pack, year, size and
   audience level. The site does not filter on the level (invariant 10 is applied here).
3. **The work of the day** is drawn among shown works of level 12 or under, 80 columns wide and
   20 to 60 rows high (one or two screens, so it arrives in under a minute at 2,400 baud), by a
   fixed hash. Day *n* of the year shows entry *n*. It is a draw, not a selection by merit.
4. **A signature is a handle, as signed.** `authors/` keys are the handle folded to lower case
   letters and digits. Two artists with the same handle share a list, which the screen says
   ("signed …", never "by the same artist"). No civil name ever enters a list (invariant 7).
5. **Removal.** `lists/index.json` names every list written. A run deletes the lists of the
   previous index that it no longer writes, so a pack whose works may no longer be shown leaves
   no list behind, without listing the bucket.

## Alternatives considered

- **Ways out inside each record.** A change in one pack would rewrite every record of every
  author and year it touches; lists are written once and shared.
- **A list of every shown work for the site to draw from.** About 107,000 entries, 7 MB at the
  entrance, against two seconds to the first work.
- **The site extracts the words from the grid.** The text layer is versioned in the pipeline;
  a second extractor in TypeScript would drift from it.

## Consequences

- The site can open on a work, offer three ways out and give screen readers the words, with no
  new rule in the frontend.
- `tm lists` runs after `tm export`; it is not sharded (it reads the database only, about
  ten seconds).
- "Nearest in style" (roadmap step 14) and "same month" (once dates have months, Q30) will be
  added as more lists under the same rules.
