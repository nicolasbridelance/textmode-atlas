<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Source note: textfiles.com, artscene

M0 note, checked at the source on 2026-10-09.

## What it is

The art section of Jason Scott's textfiles.com ([artscene.textfiles.com](http://artscene.textfiles.com/)):
artpacks sorted by year, the ACiD and iCE collections, ANSI and ASCII artwork from BBSes, ANSI
music, emags, intros, and historical documents about the scenes. Collected from BBS file areas
and FTP sites from the late 1990s on.

## What it holds (measured 2026-10-09)

| Directory | Content |
| --- | --- |
| `artpacks/1992` … `artpacks/2008` | 3,956 archives: 16, 105, 357, 435, 638, 690, 548, 397, 199, 140, 140, 125, 103, 39, 12, 6, 6 per year |
| `ascii/` | 564 entries (ASCII artpacks) |
| `asciiart/` | 304 entries |
| `acid/`, `ice/`, `ansi/`, `intros/`, `ansimusic/`, `emags/`, `history/` | collections and documents, not counted yet |

**Against 16colo:** 3,625 of the 3,956 artpack archives (92%) have a 16colo pack of the same name
(lower case, extension removed); 331 do not. Same names are not same files: the comparison by
SHA-256 comes with ingestion.

## Access

Static HTTP directories, no API; each year's listing gives the file, its size and a description
that names the group and often the month of release. The mirrors once listed in Texas
(`artscene.tqhosting.com`) and Virginia (`psg.mtu.edu/tf/artscene`) no longer resolve
(2026-10-09). Download politely: one request at a time. `scripts/mirror_textfiles.py` mirrors
the artpacks into `data/textfiles/artpacks/<year>/` (3.4 GB) and keeps the listing as
`index.tsv`; about 1 MB/s.

## Terms

None stated. textfiles.com has long collected and served these files openly, and takes requests
for removal. ADR 0009 applies: released freely by the scene, held by a scene archive.

## How the museum uses it

- The 331 archives without a 16colo namesake are the first candidates for a second source of
  packs (`tm ingest pack` reads them as they are).
- Q21 and R2: textfiles is **not independent** of 16colo, so it cannot serve as a second capture
  for a capture–recapture estimate.
- The `history/` directory: primary documents for the scene's history (leads).
