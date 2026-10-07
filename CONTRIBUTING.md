<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Contributing

Thank you. This project deals with the work of real people, often under a handle: it asks for a
little more care than an ordinary code repository.

## Four prohibitions

1. **Never commit an artwork file** (ANSI, XBIN, pack archive, module, rendering of a third-party
   work). Works live in object storage, addressed by their hash. CI refuses the matching
   extensions.
2. **Never modify an original.** An original is written once; a correction is new data.
3. **Never write an assertion without `nature` and `asserted_by`.** Every relation says who
   asserts it and on what evidence. The database refuses it anyway.
4. **Never bypass `can_display()`.** It is the only function that decides what may be shown or
   played ([ADR 0009](docs/adr/0009-show-what-the-scene-released.md)).

And a fifth, which follows from the others: never publish a link between a handle and a civil
identity without that person's consent.

## Method

- One branch per topic and a pull request; a green CI is required to merge (see
  [ADR 0008](docs/adr/0008-autonomous-development.md)).
- Significant decisions are recorded in [docs/adr/](docs/adr/); explorations are time-boxed
  [spikes](docs/spikes/) whose code is never merged.
- `just hooks` installs git hooks: fast checks on commit, message rules, `just check` on push.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):
  `type(scope): summary`, subject of 72 characters at most, a body that says why. A functional
  change and the cleanup it allows go in two separate commits (`feat`/`fix`, then
  `chore(hygiene)`).
- Code rules: [docs/vibe-coding-rules.md](docs/vibe-coding-rules.md). Linters enforce what can be
  decided mechanically; reviews look after the rest.
- `tm` commands are idempotent: run twice, they leave the same state. Tests run them twice.
- Code, comments, commit messages and contributor docs are in English. Everything a visitor reads
  goes through localization, with English and French required.
- Every new file carries an SPDX header (`reuse annotate` helps). CI runs `reuse lint`.
- A research hypothesis is filed in `research/` **before** looking at the data.

## Where to start

The [foundation document](docs/Le%20caractère%20comme%20matière%20—%20document%20de%20fondation.md)
is authoritative. If the code must depart from it, the document is changed first, in the same
pull request.
