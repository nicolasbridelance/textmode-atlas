<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Sources: the register

Every source the museum uses or might use, with what was checked at the source and what is
still only claimed. The preliminary report
[01_cartographie.md](../research/01_cartographie.md) listed sources from a generated survey;
this register supersedes it where they differ, and says where it could not be confirmed. A
source the museum ingests gets its own note in this directory (M0 exit criterion: access,
limits, terms).

Checked 2026-10-09 unless noted. "Measured" figures come from the source itself (dump, listing,
API); "claimed" figures come from the report or the source's own description and are leads.

## Already in use

| Source | Domain | Note |
| --- | --- | --- |
| 16colo.rs (Sixteen Colors) | PC artpacks, ANSI, ASCII, 1990–today | [16colo.md](16colo.md): 5,485 packs, rsync mirror, API v1, no data license, art stays the author's |

## Fast: usable within days

Ranked by what they bring for the effort. All are downloadable in bulk, so no crawling.

| # | Source | What it brings | Volume (measured) | Access | Terms | Note |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **Demozoo** (demozoo.org) | Credits, groups, handles and their aliases, releases dated to the day, links to 16colo, Pouët, CSDb, Defacto2, scene.org, asciiarena: the backbone of R1 linkage and of Q21 | 390,066 productions, 2,296 artpacks, 2,895 ANSI, 1,670 ASCII, 1,159 ASCII collections, 8,435 BBStros, 145,407 releasers (28,991 groups), 165,502 nicks, 412,113 credits, 37,796 info files; 848 links to 16colo packs, 715 to asciiarena, 3,800 to Defacto2 | Daily PostgreSQL dump, [data.demozoo.org/demozoo-export.sql.gz](https://data.demozoo.org/demozoo-export.sql.gz) (200 MB); the REST API is behind Cloudflare and refused the codespace on 2026-10-08 | "We post a daily dump of our database, in the interest of an open data model" ([FAQ](https://demozoo.org/pages/faq/)); **no data license stated**; the code is open source | [demozoo.md](demozoo.md) |
| 2 | **textfiles.com artscene** (artscene.textfiles.com) | A second archive of PC artpacks, sorted by year, plus ACiD and iCE collections, ASCII art, BBS-era documents | 3,989 artpack archives 1992–2008; 3,650 have a 16colo pack of the same name, **339 do not**; by hash, 289 bring files 16colo lacks, mostly pictures (archives note) | Static HTTP directories; mirrors in Texas and Virginia | No stated terms; Jason Scott's archive, long open to mirroring | [textfiles.md](textfiles.md) |
| 3 | **Wikipedia and Wikidata** | Reference articles in up to 44 languages, Wikidata identifiers to link groups, tools and formats to the rest of the web | 29 topic articles followed in 70 languages | API (Wikimedia asks for a `name/version (url)` User-Agent, otherwise 429) | Wikipedia text CC BY-SA 4.0; Wikidata CC0 | [wikipedia.md](wikipedia.md) |
| 4 | **Pouët** (pouet.net) | Demoscene productions, votes, party placings; bbstros and cracktros; cross-ids to Demozoo and CSDb | 102,973 productions (7,830 bbstros, 11,323 cracktros); no ANSI or artpack type | Weekly JSON dumps, [data.pouet.net](https://data.pouet.net/) (prods 15 MB) | Not stated on the dump page | register only, until needed |
| 5 | **Defacto2** (defacto2.net) | PC warez and art scene: NFO, DIZ, BBStros, group histories; Demozoo links 3,800 productions to it | "thousands of records" (claimed) | Daily SQL export on GitHub ([defacto2/database](https://github.com/defacto2/database)); REST API | Not stated in the repository | to measure |
| 6 | **Discmaster** (discmaster.textfiles.com) | Files extracted from the CD-ROMs, disks and FTP captures on the Internet Archive, each with its file date and the disc or site it sits on: a dated witness of where a pack travelled (Q21, Q26, I33) | 1,743,521,591 indexed files from 43,856 items (its home page) | Search by BLAKE3 hash (`&b3sum=`), JSON output (`&outputAs=json`); one request per file | none stated; run by textfiles.com (sysop@textfiles.com); only errors and hit counts are logged | below |

**Discmaster, first probe (2026-10-09).** 16colo's `acid-50a.zip` is byte-identical (BLAKE3) to
the copy in a 2014 capture of `ftp.sunet.se/pub/pictures/ACiD-artpacks/artpacks/1996/`, whose
file date, 1996-10-13, survived. One hash lookup per archive gives where and since when a pack
existed outside the art archives, a witness that does not descend from 16colo.

## Medium: a week or more, or terms to clarify first

| Source | What it brings | Access | Blocking point |
| --- | --- | --- | --- |
| scene.org files (files.scene.org) | `mirrors/artpacks/` (artpacks, programs, mags), party archives, demos; 173,654 Demozoo links point to it | HTTP and FTP, browsable tree | volume unknown; overlap with 16colo to measure by hash |
| CSDb (csdb.dk) | C64 scene: PETSCII, releases, sceners, groups (M5, platform C64) | Web service, XML, one entry per request, depth ≤ 4, "very early stage", undocumented | no bulk dump; per-entry requests only; terms point to a disclaimer page |
| asciiarena.se | ASCII art releases (new school), 715 Demozoo links | Website | access and terms not checked |
| Internet Archive | BBS collections, scans, CD-ROM images of BBS file areas | advancedsearch API | few hits by keyword (84 items `subject:ansi` and software); collections to find by hand |
| roysac.com | ANSI and ASCII galleries, TheDraw fonts, histories | Website | single-person site; contact before any reuse |
| Modland, Nectarine, AMP | Music of the packs (MOD, S3M, XM) | Mirrors, APIs | out of scope until the work screen plays music (radios, M0) |

## Later: other platforms and neighbouring practices (M5 and beyond)

| Domain (cartography section) | Candidate source | Status |
| --- | --- | --- |
| Teletext art | teletextart.com; the International Teletext Art Festival (ITAF) | answers (301); not examined |
| RTTY art | rtty.com gallery (`.pix` / `.pox`) | answers; a few hundred files claimed |
| ZX Spectrum, Atari, Amiga | ZXArt (zxart.ee), Atarimania, amigascne mirror on scene.org | ZXArt answers; Demozoo links 1,700 productions to it |
| PETSCII | CSDb; petscii.krissz.hu (an editor, not an archive) | see CSDb |
| Japanese Shift_JIS art (AA), kaomoji | 2channel / 5channel archives; no source identified | open (leads) |
| Soviet and post-Soviet pseudographics, FidoNet | no source identified; ru and uk Wikipedia articles on pseudographics are long (27 KB) | open (leads) |
| Taiwan PTT, Korean BBS art | PTT itself (still running); ko Wikipedia has a long "artscene" article | open (leads) |
| Latin American BBS scenes | none identified; Brazilian texts found inside 16colo works (field notes, 2026-10-09) | open |
| Typewriter art, concrete poetry | Sackner Archive (University of Iowa), physical, no API | out of scope for the corpus; context for the museum |
| Interactive fiction, roguelikes, MUDs | IFDB (ifdb.org, answers) | out of scope: games of text, not pictures of characters |
| Minitel, Videotex | Joconde and Europeana are claimed to hold Minitel collections | **not confirmed**; to check before relying on it |
| Academic work | Gleb J. Albert, "From Currency in the Warez Economy to Self-Sufficient Art Form", WiderScreen 2017 | to read at the source; bibliography to start (leads) |

## What the cartography report got wrong or could not support

- **Demozoo's license.** The report says "licence permissive permettant la réutilisation des
  métadonnées"; Demozoo states no license for its data. Its dump is published "in the interest of
  an open data model", which is an intent, not a license. Ask before republishing anything.
- **Citations that do not support their claim.** Note 44 (Demozoo) points to a Hacker News thread
  about an unrelated database; note 50 (Sixteencolors) points to an oss-fuzz coverage report.
  The Demozoo volume ("more than 250,000") is right in order of magnitude: 390,066 measured.
- **Missing sources.** Defacto2, Pouët's dumps and textfiles.com's artscene mirror are not in
  the report's tables; the last is the one closest to 16colo.
- **Joconde / Europeana and Minitel.** No evidence yet that they hold Minitel pages as art.

## How the sources depend on each other

Archives copy each other, so counting the same pack twice is the first risk and capture–recapture
needs sources that did not copy each other (R2).

- textfiles.com → 16colo: 92% of textfiles' artpacks have a 16colo pack of the same name, and
  after 2000 the yearly counts are nearly equal. 16colo likely grew from it, or both from the same
  collection (lead Q26).
- 16colo → Demozoo: Demozoo imported part of 16colo, and links 848 productions to 16colo packs.
- Demozoo's artpacks fall from 476 in 1996 to 161 in 1997 while 16colo and textfiles stay near
  their peak: Demozoo's coverage of artpacks thins after 1996 (lead Q27).
