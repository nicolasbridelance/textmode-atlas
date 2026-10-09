<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Source note: Defacto2

M0 note: access, limits and terms, checked on 2026-10-09. Incomplete: the site refuses the
codespace.

## What it is

[defacto2.net](https://defacto2.net/), "a website conserving defunct software, wares, and elite
digital subcultures of the PC": NFO and DIZ files, BBStros, cracktros, group histories, artpacks,
magazines of the PC warez and art scenes. Its database is published.

## What it holds (measured through Demozoo, 2026-10-09)

Demozoo links productions to Defacto2: 1,706 BBStros, 1,357 cracktros, 434 tools, 249 diskmags,
169 artpacks, 119 textmags, 73 graphics, 41 ANSI. Its README speaks of "thousands of records" and
shows a `files` table of 50,000 rows as an example. For the museum: the BBStros (the BBS's
advertising intro, often ANSI), the NFO files and the group histories, more than the art itself.

## Access

- **SQL export**, daily: `https://defacto2.net/sql/files.sql` (PostgreSQL 16+), documented in
  [github.com/Defacto2/database](https://github.com/Defacto2/database) (no license on the
  repository; last push 2026-06-09).
- **REST API**: `defacto2.net/api`.
- **Both behind a Cloudflare managed challenge**, which answered 403 to the codespace on
  2026-10-09, robots.txt included. Like Demozoo's API on 2026-10-08, it is not reachable from
  here; the dump has to be fetched from another machine (lead I67).

## Terms

Not stated in the repository. The site's own pages could not be read from the codespace.

## How the museum uses it

- **The SQL export first** (metadata only), from another machine, loaded into a separate
  database `defacto2_raw` like Demozoo's, to measure: how many artpacks, NFO and BBStros it holds
  that 16colo and textfiles do not, and how its dates compare (Q21).
- Files later, once the terms are read and the disk allows: its files are larger than the art
  archives' (executables, magazines).
