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
| 2 | **textfiles.com artscene** (artscene.textfiles.com) | A second archive of PC artpacks, sorted by year, plus ACiD and iCE collections, ASCII art, BBS-era documents | 3,989 artpack archives 1992–2008; 3,625 have a 16colo pack of the same name, **364 do not**; by hash, 3,464 namesakes are the same bytes, and 327 archives bring files 16colo lacks, mostly pictures (archives note) | Static HTTP directories; mirrors in Texas and Virginia | No stated terms; Jason Scott's archive, long open to mirroring | [textfiles.md](textfiles.md) |
| 3 | **Wikipedia and Wikidata** | Reference articles in up to 44 languages, Wikidata identifiers to link groups, tools and formats to the rest of the web | 29 topic articles followed in 70 languages | API (Wikimedia asks for a `name/version (url)` User-Agent, otherwise 429) | Wikipedia text CC BY-SA 4.0; Wikidata CC0 | [wikipedia.md](wikipedia.md) |
| 4 | **Pouët** (pouet.net) | Demoscene productions, votes, party placings; bbstros and cracktros; cross-ids to Demozoo and CSDb | 102,973 productions (7,830 bbstros, 11,323 cracktros); no ANSI or artpack type | Weekly JSON dumps, [data.pouet.net](https://data.pouet.net/) (prods 15 MB) | Not stated on the dump page | register only, until needed |
| 5 | **Defacto2** (defacto2.net) | PC warez and art scene: NFO, DIZ, BBStros, group histories; Demozoo links 1,706 BBStros, 1,357 cracktros, 169 artpacks to it | "thousands of records" (claimed); not measured, the site refuses the codespace | Daily SQL export (`defacto2.net/sql/files.sql`), REST API, both behind a Cloudflare challenge (403 here, 2026-10-09) | Not stated in the repository | [defacto2.md](defacto2.md) |
| 6 | **Discmaster** (discmaster.textfiles.com) | Files extracted from the CD-ROMs, disks and FTP captures on the Internet Archive, each with its file date and the disc or site it sits on: a dated witness of where a pack travelled (Q21, Q26, I33) | 1,883,127,002 indexed files from 43,856 items (its home page, 2026-10-09) | Search by BLAKE3 hash (`&b3sum=`), JSON output (`&outputAs=json`); one request per file | none stated; run by textfiles.com (sysop@textfiles.com); only errors and hit counts are logged | [discmaster.md](discmaster.md) |

**Discmaster, first probe (2026-10-09).** 16colo's `acid-50a.zip` is byte-identical (BLAKE3) to
the copy in a 2014 capture of `ftp.sunet.se/pub/pictures/ACiD-artpacks/artpacks/1996/`, whose
file date, 1996-10-13, survived. One hash lookup per archive gives where and since when a pack
existed outside the art archives, a witness that does not descend from 16colo.

## Medium: a week or more, or terms to clarify first

| Source | What it brings | Access | Blocking point |
| --- | --- | --- | --- |
| scene.org files (files.scene.org) | PETSCII, ATASCII and teletext compo entries (1,092 files, ~150 MB); `mirrors/artpacks/` (2,951 pack files, 3.2 GB, 59 without a 16colo namesake) | rsync, HTTP `/get/` → mirrors, FTP; mirroring encouraged | rights stay with the authors; [scene-org.md](scene-org.md) |
| CSDb (csdb.dk) | C64 scene: PETSCII (1,153 productions only there), releases, sceners, groups (M5, platform C64) | Web service, XML, one entry per request, depth ≤ 4, undocumented | robots.txt closes downloads to all robots and the whole site to AI agents: ask admin[at]csdb.dk first; [csdb.md](csdb.md) |
| asciiarena.se | 3,993 ASCII collys (293 MB), 808 artists, 489 crews, dated by year; only 7 % share a name with the corpus: a near-independent lineage (Q21) | Public JSON API (`/api/collys?page=n`), robots allow all | no terms stated; tell the admins (Discord) before the bulk fetch; [asciiarena.md](asciiarena.md) |
| Internet Archive | BBS collections, scans, CD-ROM images of BBS file areas | advancedsearch API | few hits by keyword (84 items `subject:ansi` and software); collections to find by hand |
| roysac.com | TheDraw fonts collection (118.8 MB ZIP) and `.TDF` specification (lead I52); galleries, histories | Static HTTP, robots allow | single-person site; ask Carsten Cumbrowski before downloading; [roysac.md](roysac.md) |
| Modland, Nectarine, AMP | Music of the packs (MOD, S3M, XM) | Mirrors, APIs | out of scope until the work screen plays music (radios, M0) |

## Later: other platforms and neighbouring practices (M5 and beyond)

| Domain (cartography section) | Candidate source | Status |
| --- | --- | --- |
| Teletext art | edit.tf URLs, scene.org compo entries, teletextart.co.uk (TARL), teletextart.com (MUTA, ITAF); broadcast recoveries (teletextarchaeologist.org, teletextarchive.com, zxnet.co.uk) | [teletext.md](teletext.md): pages survive mostly as images; files are few |
| ASCII art of Usenet and the early web | Internet Archive Giganews mbox (alt.ascii-art 2003–2015, rec.arts.ascii); asciiart.eu's Usenet archive (128,008 messages, 1993–2013, no scraping); chris.com via the Wayback Machine | [ascii-usenet.md](ascii-usenet.md) |
| RTTY art | rtty.com gallery (`.pix` / `.pox`) | answers; a few hundred files claimed |
| ZX Spectrum, Atari, Amiga | ZXArt (zxart.ee), Atarimania, amigascne mirror on scene.org | ZXArt answers; Demozoo links 1,700 productions to it |
| PETSCII | scene.org party compos, then CSDb; petscii.krissz.hu (an editor, not an archive) | [scene-org.md](scene-org.md), [csdb.md](csdb.md) |
| Japanese Shift_JIS art (AA), kaomoji | 2channel / 5channel archives; no source identified | open (leads) |
| Soviet and post-Soviet pseudographics, FidoNet | no source identified; ru and uk Wikipedia articles on pseudographics are long (27 KB) | open (leads) |
| Taiwan PTT, Korean BBS art | PTT itself (still running); ko Wikipedia has a long "artscene" article | open (leads) |
| Latin American BBS scenes | none identified; Brazilian texts found inside 16colo works (field notes, 2026-10-09) | open |
| Typewriter art, concrete poetry | Sackner Archive (University of Iowa), physical, no API | out of scope for the corpus; context for the museum |
| Interactive fiction, roguelikes, MUDs | IFDB (ifdb.org, answers) | out of scope: games of text, not pictures of characters |
| Minitel, Videotex | Joconde and Europeana are claimed to hold Minitel collections | **not confirmed**; to check before relying on it |
| Academic work | Gleb J. Albert, "From Currency in the Warez Economy to Self-Sufficient Art Form", WiderScreen 2017 | to read at the source; bibliography to start (leads) |

## Screens and documents of text-mode computing (ADR 0030)

Owner's request of 2026-10-10: operating systems, software, splash screens, games, Minitel,
walkthroughs, NFO, readme, manuals, man pages, warez, cracks. Checked 2026-10-10; "claimed"
figures are the source's own words or a search result, to measure before relying on them.

| Family | Source | What it brings | Volume | Access | Terms and limits |
| --- | --- | --- | --- | --- | --- |
| Warez scene, NFO | textfiles.com `piracy/` | NFO and information files by group (Fairlight, Razor 1911, INC, TDU-Jam, The Humble Guys, Hybrid, Prestige, The Dream Team), a large `NFO/` directory (1990 on), applications, courier lists, texts on cracking, unprotection schemes, BBS and group tags in ANSI | measured: 2,573 files, 24 MB (site statistics, 2005); 978 entries in `NFO/`, 180 in `SOFTDOCS/`, 107 in `CRACKING/`, 27 in `ANSI/` | one archive per directory (`archives.textfiles.com/piracy.zip`, `.tar.gz`), offered "to assist this research" | as [textfiles.md](textfiles.md); `UNPROTECTS/` describes how to remove protections: texts, kept as documents, never applied |
| Documentation | textfiles.com `piracy/SOFTDOCS/` | "On-line documentation, usually for pirated programs": the manuals that travelled with cracks | measured: 180 entries | same | manuals of commercial programs: records only until ADR 0030 point 5 is decided |
| Walkthroughs | textfiles.com `adventure/` | walkthroughs and hints for text adventures | measured: 557 files, 6.9 MB | per-directory archive | as textfiles |
| Games, computers, programming | textfiles.com `games/`, `computers/`, `programming/`, `apple/` | information files on home and arcade games, computer lore, programming texts; many with ASCII headers | measured: 991, 1,714, 608, 1,558 files | per-directory archives | as textfiles |
| The whole of textfiles.com | [textfiles.com](http://www.textfiles.com/directory.html) | 58,227 files, 1.33 GB in 40 sections (2005 statistics) | measured | per-directory archives | sections outside ADR 0030 (anarchy, drugs, sex: 5,264 files, …) are not ingested by it; `sex/` matters to Q36 |
| Shareware CDs | cd.textfiles.com | CD-ROM images of shareware and BBS collections: readme files, manuals, splash screens in ANSI and BIN, programs released for distribution | answers (HTTP 200); not measured | static HTTP | shareware was released for distribution; commercial CDs are not |
| Readme, manuals, dated copies | Discmaster | files of 43,856 CD-ROM, disk and FTP items, searchable by name and hash | see above | JSON search | one request per query |
| Quit screens | DOOM `ENDOOM` lumps, idgames archive | the 80 × 25 text-mode screen shown on quitting, one per WAD that sets it: raw video memory (BIN layout) | claimed: thousands of WADs; not measured | idgames mirrors (FTP, HTTP) | WADs are released freely by their authors, most with a text file of terms |
| Text-mode games | Museum of ZZT (museumofzzt.com) | ZZT and Super ZZT worlds, boards drawn in CP437 cells, with a file viewer | claimed: 3,000 to 4,000 files | zipped downloads; site code on GitHub (DrDos0016/museum-of-zzt), no API found | ask the museum before a bulk fetch |
| Man pages | Unix history repository (github.com/dspinellis/unix-history-repo), BSD and GNU sources | `roff` sources rendered by `mandoc` into a character grid: the documentation of Unix from 1970 on, dated by commit | not measured | Git | BSD and GNU licences: may be shown with their notice |
| Minitel pages | awesome-minitel list (github.com/bill-of-materials/awesome-minitel), 3615 IUT Auxerre mirror, goto10 | editors, emulators, some servers' pages | no bulk collection of `.vdt` pages found (I57) | Git, HTTP | per page |
| Scene NFO of the 2000s on | srrdb, pre databases | NFO of release groups | not checked (search found no documentation) | unknown | warez: NFO only, never the release |
| Captures of running programs | emulators (DOSBox-X copies a text screen; B800 dump tools; `TheDraw` imports BIN) | OS prompts, program interfaces, game screens as grids read from video memory | none until made | spike first | program must be freely distributable, or the capture is records only |

## Single acquisitions (ADR 0031)

Sources from which the museum takes one file at a time, to give a practice its first
representative. Each file, its basis and its check are in
[`corpus/acquisitions.yaml`](../../corpus/acquisitions.yaml); `tm acquire` fetches them.

| Source | Basis | Checked 2026-10-10 |
| --- | --- | --- |
| scene.org (`files.scene.org/get/…`) | scene (ADR 0009) | compo entries found through Demozoo's tags and placings (I91) |
| textfiles.com (www and artscene) | scene (ADR 0009) | `art/DECUS/`, `adventure/`, `piracy/`, `ansimusic/` listings |
| Wikimedia Commons | public domain or the file's licence | licence read from each file's metadata (API `extmetadata`) |
| Unix history repository (GitHub) | the file's licence | 4.4BSD-Lite2 files carry the University of California licence with its advertising clause |
| IOCCC | CC BY-SA 4.0 | [ioccc.org/license.html](https://www.ioccc.org/license.html) |
| The Ultimate Oldschool PC Font Pack (int10h.org) | CC BY-SA 4.0 | its readme |
| Esolang wiki | CC0 1.0 | its copyright page |

Candidates for the next manifests, by family, are leads I91–I94: Demozoo tags, the Wayback
Machine, searches by practice, loose files found elsewhere.

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
