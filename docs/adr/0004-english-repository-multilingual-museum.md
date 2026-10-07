<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0004. English repository, multilingual museum

- Status: Accepted
- Date: 2026-10-07
- Deciders: Nicolas Bridelance (choice between "all English" and "multilingual at every level")

## Context

The textmode scene is international; the project is French, and its foundation documents are in
French. Contributors and visitors will not share one language.

## Decision

- The repository is in English: code, comments, CLI and database messages, commits, contributor
  documentation.
- Everything a visitor reads is localized, at every layer: site interface (Paraglide, locale in
  the URL), cartels (one row per language in the database), tours, titles of profiles and
  collections (`tm.i18n.LocalizedText`). English and French are required; other languages are
  welcome without migration.
- Work titles are never translated. A translation names its source; a machine translation is
  signed `algo:` and shown as an interpretation.
- `README` and `TAKEDOWN` have a French version next to the English reference. The foundation
  document and the research reports stay in French.

## Alternatives considered

- **Everything in English**: simpler, but excludes French-speaking visitors of a French project.
- **Everything in French**: excludes most of the scene.

## Consequences

- Every visitor-facing text needs two translations before it ships; CI checks the YAML corpus.
- Database messages and tests are in English.
