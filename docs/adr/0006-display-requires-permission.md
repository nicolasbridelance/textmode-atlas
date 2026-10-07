<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0006. Show a file only with permission; metadata otherwise

- Status: Superseded by [0009](0009-show-what-the-scene-released.md)
- Date: 2026-10-07
- Deciders: Nicolas Bridelance, Claude

## Context

The legal report (`docs/research/03_juridique.md`) rates public display as the highest risk. It
recommends hosting-provider status (LCEN, DSA), but that shield covers only what third parties
upload in a neutral role; a museum that ingests its own sources and curates them acts as an
editor.

## Decision

Display follows three paths, in order: permission from the author; deposit by the author or an
archivist (hosting status); otherwise a record without the file, linking to the source archive.
`can_display()` decides, in export and API only, and `policy.allows()` returns `False` until a
lawyer approves a written rule.

## Alternatives considered

- **Rely on hosting-provider status for everything**: likely requalification as editor.
- **Display orphan works by default**: unacceptable without legal review.

## Consequences

- The site must be beautiful when most records have no file: a design constraint, not an error.
- Asking artists for permission starts in M0 and never stops.
