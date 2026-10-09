<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Source note: aSCIIaRENA

M0 note: access, limits and terms, checked at the source on 2026-10-09.

## What it is

[asciiarena.se](https://asciiarena.se/), the archive of the "colly" (ASCII collection) scene,
largely Amiga and BBS based: plain-text ASCII collections by crews and artists, ASCII mags and
apps, artists' and crews' pages, logos, BBS lists, a timeline. Run by its users; code by Burps,
Nicomen, Phantasm, Spot, Ziphoid; admins Dino, Dipswitch, dMG, h7, Ne7, Skope, Spot, Yonx, Zito
(its about page). Demozoo links 706 productions to it (686 ASCII collections).

## What it holds (measured 2026-10-09 through its API)

| Measure | Value |
| --- | --- |
| Collys | 3,993 (its about page says the same) |
| Bytes, sum of `filesize` | 293 MB |
| Files | 3,875 `.txt`, 72 `.lha`, 23 `.asc`, 11 `.zip`, 4 `.ans`, 2 `.lzh` |
| Artists / crews (sitemap) | 808 / 489 |
| Largest crews | Independent 629, Style 156, Epsilon Design 135, Save Our Souls 90, Artcore 84, Link124 81, Divine Stylers 78, Twisted 77 |

Collys by release date (`cdate`, entered by whoever submitted, sometimes to the month): 8 in
1992, 125 in 1993, 249, **889, 827** in 1994–96, then 421, 289, 236, 131 to 2000, fewer after; a
small revival from 2010 (41, 39). 403 have no date.

**A lineage of its own.** Only 269 of the 3,993 file names are the name of a file the museum
already holds (16colo and textfiles): 7 %, at most 13 % in a single year (1997). Names only;
bytes may differ. The year counts are therefore close to an independent witness for Q21 (field
note, 2026-10-09).

## Access

- **API**, announced on its news page ("a public API for you guys to fetch data"):
  `https://asciiarena.se/api/collys?page=<n>`, JSON, 25 collys a page, 160 pages; each row has
  `id`, `name`, `filename`, `filesize`, `artists`, `crews`, `cdate`, `url`.
- **Files**: each colly at `/release/<filename>`, shown as text on the page.
- **robots.txt**: `Allow: /` for every agent; sitemap of 5,294 URLs.
- Contact: Discord, IRCNet `#asciiarena`, a Facebook page; no email.

## Terms

None stated, on the site or the about page. The works stay their authors'; many collys carry
their own notices (`© Groovy People Productions` in Twisted's `-t-crime.txt`). A scene archive
holding what the scene released: ADR 0009 applies to showing them.

## How the museum uses it

- **Now**: the API metadata (3,993 rows, kept locally in `data/`, never in Git) as a dated count
  for Q21, and artists' and crews' names for R1 linkage.
- **Then**: the 293 MB of collys, once disk space allows, one request a second, with the API row
  kept as provenance; a hash comparison with the 269 namesakes.
- **Decoding**: collys made on the Amiga are meant for its Topaz font and ISO 8859-1, not CP437
  (to confirm file by file); they need the `amiga` system of ADR 0026 before they are rendered
  (M5).
- Tell the admins on Discord before the bulk fetch: a courtesy, and the source of the dating
  questions (who entered `cdate`, from what).
