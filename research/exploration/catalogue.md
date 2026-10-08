<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 16colo catalogue: first description

Roadmap step 2, exploratory: what the whole 16colo mirror holds, before D1 is drawn. Leads, not
results. Notebook: [catalogue.py](catalogue.py), on dataset `catalogue` v1 (migration 0002,
decoder `tm_render.ansi@1`), built 2026-10-08 from every archive of `archive-pack`.

## What was ingested

- 5,858 archives → **5,766 packs**: 92 archives are byte-identical copies of another
  ([field notes](../../docs/field-notes.md)). Some packs also exist as two different archives
  (`1995/wkd-0695.rar` and `.zip`); those count twice here.
- 217,670 files in packs, 186,752 distinct. **115,156 art works**: ANSI 90,208, ASCII 34,548,
  RIP 2,674, XBIN 875, BIN 437, Tundra 32, ADF 31, PCBoard 24, IDF 6 (files in packs; distinct
  files are about 10 % fewer).
- Archives: 5,723 read whole, 37 partly (67 members unreadable), 6 not at all (`bad_archive`).
- Decoding: every art work has a result. 111,405 grids; 3,682 `unsupported_format` (RIP, XBIN,
  BIN and the rarer formats); 68 empty files; 1 too large.

## Shape of the corpus

| Era | Packs | Art files | of which ASCII | other formats | with SAUCE |
| --- | --- | --- | --- | --- | --- |
| 1990–1993 | 304 | 7,908 | 37 | 38 | 0 % |
| 1994–1997 | 3,144 | 75,722 | 17,105 | 2,407 | 67 % |
| 1998–2004 | 1,845 | 32,753 | 15,484 | 790 | 46 % |
| 2005–2026 | 473 | 12,452 | 1,922 | 844 | 71 % |

- The archive is the mid-1990s: 1994–1997 hold 55 % of the packs and 59 % of the art files. A sample
  drawn uniformly from packs is a sample of those four years.
- **ASCII is a second wave**: 37 files before 1994, then 17,105 in 1994–1997 and 15,484 in
  1998–2004, where it is almost half of the art.
- **SAUCE appears in 1994** (35 % of art files that year, 73 % in 1995) and never covers
  everything: it falls back to about half around 2000.
- **RIP is a 1994–1998 format** (89 % of its files; 700 in 1995 alone); **XBIN is recent**
  (76 % of its files from 2015 on).
- Canvas width is 80 columns for 99 % of decoded files (123,266); 940 are wider, 460 narrower.
- Height of decoded ANSI: median 28 rows, 90th percentile 145, 99th 384, longest 5,955. Since 2005 the median
  piece is twice as tall (50 rows; 90th percentile 221): the long scrolling piece is a later
  form.
- NFO files are in 55–62 % of packs until 2004 and 20 % after; FILE_ID.DIZ in 85–96 % from 1994.
- 24,684 art files sit in more than one pack (10,510 distinct works in exactly two). Part is
  the identical archives above; the rest is art travelling between packs (R1, provenance).

## Leads and cautions

- **SAUCE group is not a clean credit.** The most frequent group name is `READ THE INI FILE`
  (1,874 files, 167 packs, 1994–1998): a tool's default value. 5,891 group spellings shrink to
  4,691 once case and spaces are ignored (`CiA` / `cia`, `fire` / `Fire`). The font field also
  carries tool names (`SAUCE-ADDER V1.4`). Credits need NFO parsing and normalisation (R1).
- **SAUCE dates**: 5,326 of 74,946 art files with SAUCE have a date that is not a plausible
  `YYYYMMDD` between 1980 and 2029.
- **iCE flag**: SAUCE marks iCE colours on none of the art files of 1994–1997 and on 1 % in
  1998, then up to 57 % (2017). Either iCE art was rare then, or the editors of the time did
  not write the flag. To check on the grids (blink attribute on bright backgrounds) once
  features exist; do not use the flag as a measure of iCE before 2000.
- **Fonts**: 90 % of SAUCE records name no font; then IBM VGA, and Amiga Topaz / mOsOul on
  about 1,100 files, the Amiga ASCII inside the PC archive.
- **Pack listings as art**: 1,541 empty files in 377 packs; 730 of them, in 207 packs from 1993
  to 2004, have names made of blocks and lines that draw logos and section headers in the
  archive listing ([field notes](../../docs/field-notes.md)). They are part of the pack's
  design and the museum should be able to show a pack's listing.

## Proposed strata for D1 (roadmap step 4)

Strata by **era** (the four rows above), not proportional: five packs per era, so that
1990–1993 and 2005–2026 are seen at all. Within an era, packs are drawn with a fixed seed from
those with at least one decoded grid, and at least one of the five has a majority of ASCII
where the era has such packs. Rare cases added by hand, each with its reason in the datasheet:
a RIP pack (1995), an XBIN pack (after 2015), a pack with listing art (`1993/chs-0893.zip`),
and a pre-SAUCE pack whose art is found only by content. D1 then has about 24 packs, against 20
in the research programme; the datasheet states the difference.
