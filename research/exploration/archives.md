<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Three archives, one curve? Artpacks per year in 16colo, textfiles.com and Demozoo

Exploratory, 2026-10-09, for Q21 ("is 1996 the peak of the scene, or of 16colo?") and H8. Pack
counts only: no work is examined, so the test packs are not touched. Sources and their terms:
[docs/sources/](../../docs/sources/README.md).

## Method

- **16colo**: packs of dataset `catalogue` v1 by the year 16colo files them under (all splits).
- **textfiles.com**: archives listed in `artscene.textfiles.com/artpacks/<year>/` (zip, arj, lzh,
  rar, exe, 7z), 2026-10-09. Corrected the same day: the first count missed rows where two shared
  a line of the listing (3,956 then, 3,989 now; `scripts/mirror_textfiles.py`).
- **Demozoo**: productions of type Artpack (51) with a release date, in the dump of 2026-10-09
  loaded into a local `demozoo_raw` database; 11 undated artpacks left out. Also its types ANSI,
  ASCII (with ASCII Collection) and BBStro, for comparison.
- **Overlap**: a textfiles archive is "in 16colo" when a 16colo pack has the same name, lower
  case, extension removed. A Demozoo artpack is "linked" when it carries a `SixteenColorsPack`
  link. Names are not hashes: two packs with one name can differ, and a renamed pack is missed.

## Counts

| Year | 16colo packs | textfiles artpacks | of which named in 16colo | Demozoo artpacks | of which linked to 16colo | Demozoo ANSI | Demozoo ASCII | Demozoo BBStros |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1990 | 5 | — | — | 0 | — | 42 | 0 | 128 |
| 1991 | 7 | — | — | 0 | — | 150 | 0 | 500 |
| 1992 | 46 | 16 | 16 | 23 | 19 | 364 | 6 | 731 |
| 1993 | 246 | 105 | 98 | 166 | 58 | 13 | 93 | 971 |
| 1994 | 598 | 357 | 354 | 429 | 130 | 86 | 105 | 1,954 |
| 1995 | 747 | 435 | 429 | 425 | 113 | 48 | 238 | 2,175 |
| 1996 | 851 | 639 | 600 | 476 | 124 | 140 | 177 | 1,025 |
| 1997 | 948 | 706 | 630 | 161 | 66 | 85 | 179 | 310 |
| 1998 | 615 | 563 | 460 | 103 | 39 | 115 | 152 | 78 |
| 1999 | 434 | 398 | 348 | 76 | 26 | 78 | 242 | 27 |
| 2000 | 199 | 199 | 156 | 41 | 12 | 48 | 73 | 10 |
| 2001 | 190 | 140 | 134 | 20 | 6 | 21 | 45 | 5 |
| 2002 | 165 | 140 | 130 | 26 | 2 | 20 | 51 | 2 |
| 2003 | 133 | 125 | 113 | 31 | 5 | 14 | 102 | 5 |
| 2004 | 109 | 103 | 97 | 33 | 6 | 12 | 67 | 2 |
| 2005 | 44 | 39 | 37 | 15 | 3 | 13 | 68 | 0 |
| 2006 | 16 | 12 | 12 | 5 | 0 | 10 | 48 | 2 |
| 2007 | 6 | 6 | 6 | 3 | 0 | 10 | 56 | 2 |
| 2008 | 7 | 6 | 5 | 6 | 1 | 13 | 27 | 0 |

After 2008, 16colo holds 3 to 37 packs a year and Demozoo 1 to 27; textfiles stops in 2008.
Demozoo's ANSI and ASCII productions rise again after 2013 (over 200 ANSI a year in 2023–25):
the scene's revival is recorded as single works more than as packs.

## What it shows

1. **The peak is in 1996–97 in all three**, and all three fall by half or more between 1997 and
   2000. By packs, 16colo's peak is 1997 (948), not 1996; textfiles' is 1997 (706); Demozoo's is
   1996 (476).
2. **But the three are not independent witnesses.** 91% of textfiles' artpacks (3,625 of 3,989)
   have a 16colo namesake, and from 2000 the yearly counts are nearly equal (199 and 199, 109
   and 103): 16colo probably grew out of textfiles' collection, or both out of one. Demozoo links
   about a quarter of its artpacks to 16colo, and is known to have imported from it. A
   capture–recapture estimate (R2) between these sources would count the copying, not the scene.
3. **Demozoo's artpacks thin out after 1996** (476 → 161) while the two file archives stay near
   their peak: its curve says where its editors worked, not when packs stopped (Q27).
4. **Demozoo's 1992 ANSI** (364 that year, 13 the next) and its BBStros (2,175 in 1995) look like
   bulk imports of single collections (Q28).

So H8 is neither supported nor refuted: the mid-90s peak appears everywhere, but "everywhere" is
one lineage of archives. An independent witness is needed: BBS file lists of the time, magazine
release lists, or the packs' own NFO lists of members and releases (I28).

## By hash: what textfiles holds that 16colo does not (2026-10-09)

`scripts/compare_archives.py` reads every archive of the textfiles mirror and compares it with
16colo by SHA-256: the archive's own bytes, and each file inside it against every file of every
16colo pack (all splits; hashes only, no work is read). All 3,989 archives, mirrored 2026-10-09.

| textfiles archives | archives | same bytes as a 16colo pack | holding files 16colo lacks | those files |
| --- | --- | --- | --- | --- |
| without a 16colo namesake | 364 | 64 | 278 | 4,301 |
| with one | 3,625 | 3,464 | 49 | 185 |

One archive (`bad_archive`) could not be read at all.

1. **Names undercount the overlap.** 64 archives without a namesake are byte-identical to a
   16colo pack filed under another name, and 22 more hold only files 16colo has.
2. **One collection, held twice.** Where names match, 3,464 of 3,625 archives (96%) are the same
   bytes, and most of the others are the same files in another archive (repacked, or a comment
   added). 16colo and textfiles hold one collection, not two.
3. **What textfiles adds is mostly photographs of graffiti.** The 327 archives that bring
   something new hold, in the first 289 measured, 2,948 JPEG, 112 GIF and 44 IFF files, against 61 textmode works (37 ANSI,
   24 ASCII). By textfiles' own descriptions, 168 of them are graffiti photo packs of 1997–2000
   (words graffiti, train, bomb, backjump, wall, crew): Die Kranken Bomber, Writaz Express,
   The Aeroholics, Freeside Graffiti Compilation, Omen, mostly from Cologne and other German
   cities, numbered like art packs. 16colo, an archive of textmode, does not hold them.

The 327 archives were ingested as packs (`tm ingest pack --source textfiles`); the others add no
file, and would only duplicate a set. They bring 95 textmode works; 85 works of works v5 are
placed in a textfiles pack. 382 files explored through 16colo became test (works datasheet).
