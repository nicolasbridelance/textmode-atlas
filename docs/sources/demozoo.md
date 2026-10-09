<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Source note: Demozoo

M0 note: access, limits and terms, checked at the source on 2026-10-09. Supersedes the entry of
[01_cartographie.md](../research/01_cartographie.md) where they differ.

## What it is

A database of the demoscene and its neighbours ([demozoo.org](https://demozoo.org/)), edited by
volunteers: productions, releasers (groups and sceners), their handles and aliases, credits,
parties, and links to the archives that hold the files. It holds metadata and screenshots, not
the art itself. For the museum it is the linking layer (R1): who made what, under which names,
and where else a work lives.

## What it holds (measured on the dump of 2026-10-09)

| Measure | Value |
| --- | --- |
| Productions | 390,066 |
| of type Artpack / ANSI / ASCII / ASCII Collection | 2,296 / 2,895 / 1,670 / 1,159 |
| of type BBStro / Cracktro / Textmag | 8,435 / 36,204 / 987 |
| Pack members (files listed inside packs), in artpacks | 3,825 |
| Releasers / of which groups | 145,407 / 28,991 |
| Nicks (handles, with aliases) | 165,502 |
| Credits | 412,113 |
| Info files (NFO and the like) | 37,796 |
| Links to 16colo packs / asciiarena / Defacto2 / CSDb / Pouët | 848 / 715 / 3,800 / 38,832 / 101,776 |

Artpacks with a release date, by year: 23 in 1992, 166 in 1993, 429, 425, 476 in 1994–96, then
161 in 1997 and fewer after; 16colo has 948 packs filed under 1997. Coverage of artpacks is
uneven over time (lead Q27).

## Access

- **Dump.** A full PostgreSQL export, refreshed daily, at
  [data.demozoo.org/demozoo-export.sql.gz](https://data.demozoo.org/demozoo-export.sql.gz)
  (201,667,299 bytes on 2026-10-09). Loaded locally into a separate database `demozoo_raw`
  (`gunzip -c … | psql`), never into the museum's schema. Downloaded copies go to the ignored
  `data/demozoo/`, named by date, with their SHA-256 recorded.
- **API.** `https://demozoo.org/api/v1/`, REST. Behind Cloudflare, which refused the codespace
  on 2026-10-08 and accepted it on 2026-10-09; its list endpoints ignore date filters. Use the
  dump for anything in bulk.
- **Source code.** [github.com/demozoo/demozoo](https://github.com/demozoo/demozoo).

## Terms

- The [FAQ](https://demozoo.org/pages/faq/): "The entire website is open source, and we post a
  daily dump of our database, in the interest of an open data model."
- **No license is stated for the data.** Reading the dump for research is what it is published
  for; republishing records or screenshots needs Demozoo's agreement (to ask in the M3 contact,
  roadmap M0).
- Screenshots are of works whose rights stay with their authors (ADR 0009 applies).

## How the museum uses it

- Exploratory: artpacks per year against 16colo (Q21), handles and aliases for author strings
  (I20), links to 16colo packs to check Demozoo's dating.
- Later, as a source of assertions (`nature = 'imported'`, `asserted_by = 'source:demozoo'`),
  once the import is written and the terms are clear.
