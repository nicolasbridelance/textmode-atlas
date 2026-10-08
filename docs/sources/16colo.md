<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Source note: 16colo.rs (Sixteen Colors)

M0 note: access, limits and terms, checked at the source on 2026-10-08. The preliminary report
([01_cartographie.md](../research/01_cartographie.md), entry "Sixteencolors") is superseded by
this note where they differ.

## What it is

An online archive of ANSI and ASCII artpacks, run by volunteers of the scene
([16colo.rs](https://16colo.rs/)); formerly sixteencolors.net, a name the legacy API still uses.
It is the main source of the museum's PC textmode corpus (scene archive `16colo` in ADR 0009).

## What it holds (measured 2026-10-08)

| Measure | Value | How |
| --- | --- | --- |
| Packs | 5,485 | API v1 `/year/` |
| Art magazines | 1,003 | API v1 `/year/` |
| Pack archives in the mirror | 5,862 (5,518 zip, 321 rar, a few lha / lzh), 9.1 GB | `rsync --list-only rsync://16colo.rs/archive-pack/` |
| Years | 1990 to 2026 | both |
| Files in extracted packs | 221,462, 12.2 GB (not counting 16colo's PNG renders, 19.6 GB) | `rsync --list-only rsync://16colo.rs/pack/` |
| Textmode files (ans, asc, xb, bin, adf, idf, pcb, avt, rip, ice, nfo, diz, txt…) | about 127,000, about 1 GB, 8 KB on average; 62,517 `.ans` | same listing, by extension |
| Largest shares of the bytes | mp3 27 %, jpg 24 %, png 9 % | same listing |

The mirror holds 377 more archives than the API counts packs; some packs have several archives
or are not listed. To be explained when packs are ingested.

Packs per year are very uneven: 3,224 of 5,485 date from 1993 to 1997, and 2005 to 2012 hold
88 together. A random sample of the whole catalogue is a sample of the mid-1990s.

## Access

- **Mirror.** `rsync://16colo.rs/` with four modules: `pack` (extracted files and 16colo's
  renders, `x1`, `x2`, `tn`), `archive-pack` (the pack archives as released), `mag`,
  `archive-mag`. Also `ftp://16colo.rs`. The FAQ invites mirroring (below). The museum mirrors
  `archive-pack` into the ignored `data/16colo/`, rate-limited (`--bwlimit=5000`).
- **API v1.** `https://api.16colo.rs/v1/`, documented at
  [16colo.rs/api.php](https://16colo.rs/api.php): `pack`, `pack/:name` (files, SAUCE,
  dimensions, artists, groups, FILE_ID candidates), `year`, `year/:year`, `group`, `artist`,
  `latest/releases`; pages of up to 500. Read access needs no key. No rate limit is stated:
  stay polite (one request at a time, cache responses).
- **Legacy API v0.** `https://api.sixteencolors.net/v0/` still answers (`/year`); not to be
  used for new code.
- A nightly export of the search database is announced in the FAQ; not found yet.

## Terms

From the [FAQ](https://16colo.rs/faq/):

- The artwork "remains at all times the intellectual property of the author".
- Reuse of artwork: "get in touch with the author and seek his or her permission".
- Archive data: "we encourage anyone to mirror/reuse the data wherever he/she sees fit".
- Editors "can also remove packs or remove unappropriate content"; visitors can report files
  that "should not be displayed at all".
- No terms of use beyond the FAQ and the privacy policy; no stated license.

For the museum this means: keeping a private mirror and computing measurements is in line with
the FAQ; showing a file relies on ADR 0009 (released freely by the scene, held by 16colo,
credited as signed, withdrawn on request), and a withdrawal at 16colo should reach us too.

## Rendering

The site credits ansilove, PabloDraw and Moebius. The renders in the mirror (`x1`, `x2`, `tn`)
are 16colo's own; their engine and settings are not documented. The museum draws its own from
the grid (ADR 0010) and does not reuse them.

## Limits and open points

- About ten packs are deliberately not downloadable (forum, unverified).
- Pack counts differ between the API and the mirror (see above).
- Removals at 16colo: no feed found. Until one exists, compare the mirror listing with the
  ingested packs at each sync.
- Contact: contact@16colo.rs, and the scene chat linked from the FAQ. Informing them of the
  project is an M0 task for the owner (roadmap).

## Sources

- [16colo.rs](https://16colo.rs/), [FAQ](https://16colo.rs/faq/), [API v1](https://16colo.rs/api.php)
- [Forum: downloading the archive](https://forum.16colo.rs/t/new-github-project-to-help-downloading-the-ansi-art-packs-archive/330)
- Measurements: rsync listings and API calls of 2026-10-08, by Claude.
