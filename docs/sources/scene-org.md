<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Source note: scene.org files

M0 note: access, limits and terms, checked at the source on 2026-10-09.

## What it is

The file archive of the International Scene Organization ([files.scene.org](https://files.scene.org/)),
a non-profit run by volunteers: party releases sorted by year and party, then by compo
(`/parties/<year>/<party>/<compo>/`), demos, music, and `mirrors/` of older collections. The
archive where most demoparty compos have put their entries since the late 1990s.

## What it holds for the museum (measured 2026-10-09)

**PETSCII, ATASCII and teletext entries** (through Demozoo's dump; lead I55):

| Practice | Demozoo links to scene.org | Distinct files | of which under `/parties/` |
| --- | --- | --- | --- |
| PETSCII | 915 (891 productions) | 859 | 912 links |
| ATASCII | 109 | 106 | 109 |
| teletext | 127 | 127 | 124 |
| **total** | | **1,092** | |

Sizes, from 60 `HEAD` requests on a random sample: median 10 KB, mean 138 KB once one file over
10 MB is left out (a 183 MB teletext video entered in an Assembly 2016 "real wild" compo). The
whole set, files over 10 MB excluded, is **about 150 MB** (sample estimate, ± a factor of two).

**`mirrors/artpacks/`** (`rsync --list-only`, 2026-10-09): 8,838 files, 3.75 GB.

| Directory | Files | Size |
| --- | --- | --- |
| `artpacks/1992` … `artpacks/2004` | 2,951 | 3.16 GB |
| `www/` (a copy of a web site) | 4,770 | 0.21 GB |
| `mags/` | 406 | 0.18 GB |
| `unsorted/` | 502 | 0.10 GB |
| `programs/` | 196 | 0.09 GB |

Pack archives by file date: 16 in 1992, then 61, 289, 220, 359, 587, 577, 393, 136, 48 up to
2001, 236 in 2002, none in 2003, 29 in 2004. Of 2,928 distinct pack names, 2,591 are a 16colo
archive name; compared by base name (`.rar` here, `.zip` there), only **59 files (42 names,
89 MB)** have no 16colo namesake. Same name is not same bytes: a hash comparison needs the
files, so it is limited to those 59 first.

## Access

- **HTTP.** `https://files.scene.org/browse/<path>` (listing), `https://files.scene.org/get/<path>`
  answers 302 to a mirror (mirror.netcologne.de when tested). No robots.txt (404).
- **rsync.** `rsync://rsync.scene.org/ftp/` (the archive) and `rsync://rsync.scene.org/mirrors/`;
  `--list-only` gives names, sizes and dates without downloading. Also anonymous FTP at
  ftp.scene.org.
- **Mirrors** listed in the FAQ: mirror.netcologne.de, ftp/http.hu.scene.org, ftp/http.no.scene.org,
  ftp/http.pl.scene.org, scene.modshrine.com, mirror.scenesat.com, sceneorg.retropc.se,
  http.us.scene.org.
- **Rate.** None stated. The FAQ says a mirror script "probably shouldn't run more than once a
  day"; the museum's fetch is one pass, one request at a time with a pause, through rsync or the
  `/get/` redirect.

## Terms

- [FAQ](https://files.scene.org/faq/): "Mirrors of scene.org are welcomed and encouraged by us",
  and one may "only mirror certain sections of the archive". Copying sections for keeping is what
  the archive invites.
- Rights: "Not all of the works … present in our archives are in the public domain"; "The
  International Scene Organization only has distribution rights of the works contained in its
  archive"; for other uses, contact the authors. Showing a work stays under ADR 0009 (released by
  the scene at a party, held by a scene archive, credited, withdrawable).
- Contact: ftp@scene.org.

## How the museum uses it

- **First source of PETSCII, ATASCII and teletext files**: the 1,092 files above, through
  `/get/`, files over 10 MB skipped and listed. Kept as originals, not shown until a decoder for
  their system exists (M5).
- **The 59 artpack files without a 16colo namesake**, then a hash comparison against 16colo.
  The rest of `mirrors/artpacks` (3.1 GB) only if those 59 show that names hide different bytes.
- Party and compo paths are a dating and context source of their own: the directory says where
  and in which compo a work was shown (field note, 2026-10-09).
