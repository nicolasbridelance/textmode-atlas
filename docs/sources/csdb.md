<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Source note: CSDb

M0 note: access, limits and terms, checked at the source on 2026-10-09.

## What it is

The C64 Scene Database ([csdb.dk](https://csdb.dk/)), edited by registered users: releases,
groups, sceners and their handles, events, BBSes, SIDs, with the release files themselves stored
on the site. The reference database of the Commodore 64 scene; for the museum, the home of most
PETSCII art (M5, platform C64; leads I54, I55).

## What it holds for the museum (measured 2026-10-09, through Demozoo's dump)

CSDb has no PETSCII release type: PETSCII pictures are releases of type "C64 Graphics", told
apart from bitmap graphics only by their compo, their tags or their file. Demozoo's tag is the
measure used here.

| Measure | Value |
| --- | --- |
| Demozoo productions tagged `petscii` | 2,118 (1,886 of type Graphics) |
| with a download link to CSDb | 1,624 (1,686 links) |
| of which files stored by CSDb (`getinternalfile.php`) / through `release/download.php` | 1,156 / 530 links |
| with a link to scene.org as well | 471 |
| **only on CSDb** | **1,153** |
| `atascii` / `teletext` productions linked to CSDb | 0 / 0 |

Files are mostly `.prg` (a C64 program that shows the screen) and `.d64` disk images, a few
kilobytes each: the PETSCII files sampled on scene.org have a median of 10 KB
([scene-org.md](scene-org.md)). The 1,153 CSDb-only productions would weigh in the low hundreds
of megabytes at most. Not measured on CSDb itself (below).

## Access

- **Web service.** `https://csdb.dk/webservice/?type=<type>&id=<id>&depth=<d>`, XML, types
  `release`, `group`, `scener`, `event`, `bbs`, `sid`, `forum`; one entry per request, depth ≤ 4
  (default 2). Its own page: "only in it's very early stage, so no real documentation for the
  format of the XML"; "can either be used for private use, or to make some of the information in
  CSDb available on other websites." Answered the codespace on 2026-10-09 (release 200000,
  type "C64 Graphics", with its screenshot URL).
- **No bulk dump** found. A list of releases by type needs the search pages, which robots.txt
  closes (below).
- **robots.txt (2026-10-09).** For every agent: `Disallow: /search/`, `/browse.php`, `/storage/`,
  `/release/download.php`, `/gfx/sceners/`. And the whole site (`Disallow: /`) for AI crawlers by
  name: ClaudeBot, anthropic-ai, Claude-SearchBot, GPTBot, ChatGPT-User, OAI-SearchBot,
  Google-Extended, CCBot, PerplexityBot, Bytespider and others.

## Terms

- The [disclaimer](https://csdb.dk/disclaimer.php): "CSDb is an open database containing
  information and material related to the Commodore 64 scene. All information and material found
  here is entered and maintained by the registered users"; copyright or privacy problems go to
  admin[at]csdb.dk "for immediate removal". No license is stated for the data or the files.
- The robots.txt says more than the disclaimer: the site's operators **do not want automated
  downloads of release files**, and they do not want AI agents on the site at all. The museum's
  fetcher would run under its own User-Agent, but it is built and driven with an AI assistant,
  and the intent of the file is plain.

## How the museum uses it

- **Not as a bulk source, until CSDb agrees.** The 1,153 CSDb-only PETSCII productions wait for
  a reply from admin[at]csdb.dk: what the museum is, that it keeps originals unchanged and shows
  them only under ADR 0009, the number of files, the request rate. The owner sends it (lead I62).
- **scene.org first.** 891 PETSCII productions are on scene.org, which welcomes mirroring
  ([scene-org.md](scene-org.md)).
- **Single lookups by hand** (one release, to check a credit or a date) stay within the
  disclaimer, as a person reading the site.
- Later, once agreed: release, group and scener records as assertions
  (`nature = 'imported'`, `asserted_by = 'source:csdb'`), linked to Demozoo through its 38,832
  CSDb links.
