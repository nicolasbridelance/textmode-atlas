<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# textmode-atlas — conventions for Claude Code

Digital Museum of Character Arts. The reference specification is the
[foundation document](docs/Le%20caractère%20comme%20matière%20—%20document%20de%20fondation.md)
(French). When in doubt it is authoritative; if code must depart from it, change the document
first.

## Status

Milestone M0 (framing) and scaffold. Preliminary reports in `docs/research/` are Deep Research
output: leads to verify at the primary source, never sources themselves.

## Invariants (enforced by code)

1. An original is never modified: storage addressed by SHA-256, write-once.
2. Source, rendering and interpretation are separate: `representation.level` is mandatory.
3. Every rendering is reproducible: complete JSON recipe, determinism test in CI.
4. Every relation has an origin: append-only `assertion` table, `nature` and `asserted_by` required.
5. A computation is never presented as a fact: `nature = 'inferred'` requires an `algo:` author.
6. No file shown or played without the right to: `can_display()` in export and API, never in the frontend.
7. No handle → civil identity link without consent: `person` stays out of the public API.
8. All model-generated content is marked: `level = 'interpretation'`, `asserted_by = 'algo:…'`.
9. No work is generated "in the style of": a model-produced grid is never rendered nor exported.

## Prohibitions

- Never commit an artwork file. Only project-made golden artifacts (`tests/golden/`, CC0) are in Git.
- Never modify an original.
- Never write an assertion without `nature` and `asserted_by`.
- Never bypass `can_display()`; `policy.allows()` returns `False` until a lawyer approves a rule.
- Never link a handle to a civil person publicly.

## Conventions

- **Languages.** Repository in English (code, comments, CLI output, commits, contributor docs).
  Everything a visitor reads is localized: `en` and `fr` required (`tm.i18n.REQUIRED_LOCALES`),
  others welcome. Work titles are never translated. Machine translations are signed `algo:`.
  Conversations with the project owner are in French.
- **Target architecture from the first line.** No throwaway prototype: each piece goes where the
  spec puts it (the site reads grids exported by the Python pipeline, it never decodes ANSI itself).
- Python 3.12, `uv` workspace (`ingest/` → `tm`, `renderers/` → `tm_render`, `analysis/` →
  `tm_analysis`, `api/` → `tm_api`); `ruff`, `pyright` strict.
- Every `tm` command is idempotent. Decoders never crash: unreadable input yields a classified error.
- Schema changes are Alembic migrations in raw SQL; invariants live in constraints and triggers,
  each with a test that makes it fail.
- REUSE: SPDX header on every file (code Apache-2.0; data CC0-1.0; texts CC-BY-4.0).
- Secrets come from the environment (`TM_*`), never from files in the repository.

## Commands

```sh
just setup        # deps, services (PostgreSQL + Garage), migrations, storage
just check        # everything CI runs
just test -k foo  # pytest with args
uv run tm --help  # corpus check|schema, dev storage-init
```

Local services: PostgreSQL on 5432, Garage S3 API on 3900 (signed requests only), public bucket
web endpoint on 3902 (Host `tm-public.web.localhost`), Garage admin on 3903.
