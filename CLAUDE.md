<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# textmode-atlas — conventions for Claude Code

Digital Museum of Character Arts. The reference specification is the
[foundation document](docs/Le%20caractère%20comme%20matière%20—%20document%20de%20fondation.md)
(French). When in doubt it is authoritative; if code must depart from it, change the document
first, in the same pull request.

## Working protocol

**Session start.** Read [docs/roadmap.md](docs/roadmap.md), the latest entry in
[docs/journal/](docs/journal/), `git log --oneline -15` and `git status`. Take the next unchecked
task of the current focus unless the owner asks otherwise.

**Autonomous mode** ([ADR 0008](docs/adr/0008-autonomous-development.md)). Claude opens and
merges its own pull requests once every CI job is green; the owner reviews afterwards. Ask the
owner only for what needs a person (accounts, secrets, contacts, legal or financial decisions);
prepare anything sent on his behalf, never send it.

**During the session.**
- One topic per branch (`feat/work-screen`, `fix/…`), merged into `main` by pull request.
- A decision that is hard to reverse, has alternatives, or departs from the spec → an ADR in
  [docs/adr/](docs/adr/). An unknown that blocks a decision → a time-boxed spike on a
  `spike/NNNN-topic` branch, never merged, reported in [docs/spikes/](docs/spikes/).
- Visible changes are checked in rendering, not only in code: `just shots [path…]`, then look at
  the images (desktop and mobile, every locale).
- Something the work reveals about the scene's history (a habit in the files, a gap in the
  record, how works travelled) → an entry in [docs/field-notes.md](docs/field-notes.md), dated,
  with how it was found and its evidence. It feeds future visitor stories; write it when found,
  not at the end.
- Commits follow the rules below; `just check` must be green before a push (the pre-push hook
  runs it).

**After each functional commit** (post-commit protocol, docs/vibe-coding-rules.md):
1. Run `just hygiene`. Remove what the commit made obsolete: dead code, temporary files, debug
   output, orphan fixtures, stale TODOs. Run the tests first. Up to ~30 lines or 3 files, do it;
   beyond that, or when unsure (dynamic use, documented skip, TODO linked to an issue), list the
   candidates and ask. Separate commit: `chore(hygiene): …`.
2. Audit the touched area. If friction, special cases or duplication grew (rule of three),
   propose a refactor: target, warning signal, expected gain, 2–3 step plan. Never execute it
   without approval.

**Session end.** Write `docs/journal/YYYY-MM-DD.md` (goal, done, decisions, problems, field
notes added, state, next). Update the roadmap checkboxes and known debt. Update this file if a convention changed.

## Commit rules

- Conventional Commits, enforced by the `commit-msg` hook: `type(scope): summary`, type in
  feat, fix, refactor, perf, test, docs, build, ci, chore, revert; subject ≤ 72 characters,
  imperative, no final period; the body says why.
- Two stages, two commits: the functional change (`feat`/`fix`), then pruning
  (`chore(hygiene)`). Never mix behavior, cleanup and formatting in one commit.
- End every message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Code rules

[docs/vibe-coding-rules.md](docs/vibe-coding-rules.md) (French). What a tool can decide is
enforced by tools, so it is not repeated here: complexity ≤ 8, nesting depth, magic numbers,
print / console, commented-out code, TODO without issue link (ruff, ESLint); unused code and
dependencies (vulture, deptry, knip); duplication (jscpd). What stays judgment: single
responsibility, YAGNI, KISS, dependency injection, law of Demeter, fail fast with a useful
message, names that make comments unnecessary.

Logging: `logging.getLogger(__name__)` in library code, configured once by the CLI; user-facing
output through `typer.echo`; `print` only in `scripts/`.

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
- Never bypass `can_display()`. Without the author's permission, a file is shown only under
  [ADR 0009](docs/adr/0009-show-what-the-scene-released.md): released freely by the scene, held
  by a scene archive, credited as signed, withdrawable on request.
- Never link a handle to a civil person publicly.

## Conventions

- **Languages.** Repository in English (code, comments, CLI output, commits, contributor docs).
  Everything a visitor reads is localized: `en` and `fr` required (`tm.i18n.REQUIRED_LOCALES`),
  others welcome. Work titles are never translated. Machine translations are signed `algo:`.
  Conversations with the project owner are in French.
- **Target architecture from the first line.** No throwaway prototype: each piece goes where the
  spec puts it (the site reads grids exported by the Python pipeline, it never decodes ANSI itself).
- Python 3.12, `uv` workspace (`ingest/` → `tm`, `renderers/` → `tm_render`, `analysis/` →
  `tm_analysis`, `api/` → `tm_api`); dependencies are added with the code that uses them.
- Every `tm` command is idempotent. Decoders never crash: unreadable input yields a classified error.
- Schema changes are Alembic migrations in raw SQL; invariants live in constraints and triggers,
  each with a test that makes it fail.
- REUSE: SPDX header on every file (code Apache-2.0; data CC0-1.0; texts CC-BY-4.0).
- Secrets come from the environment (`TM_*`), never from files in the repository.
- Preliminary reports in `docs/research/` are leads to verify at the primary source.

## Commands

```sh
just setup        # deps, services (PostgreSQL + Garage), migrations, storage, git hooks
just check        # everything CI runs
just test -k foo  # pytest with args
just hygiene      # post-commit pruning candidates
just shots /fr    # screenshots of the built site
just parity       # ansilove draws the golden artifacts as we do (needs ansilove)
uv run tm --help  # corpus check|schema, dev storage-init
```

Local services: PostgreSQL on 5432, Garage S3 API on 3900 (signed requests only), public bucket
web endpoint on 3902 (Host `tm-public.web.localhost`), Garage admin on 3903.
