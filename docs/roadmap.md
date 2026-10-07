<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Roadmap

The living plan. Milestones and their exit criteria come from the
[foundation document](Le%20caractère%20comme%20matière%20—%20document%20de%20fondation.md#jalons);
this file tracks where we are. It is updated at the end of every working session (see
[journal/](journal/)). Once the repository opens to contributors (M3), open tasks move to GitHub
issues and this file keeps only milestones and the current focus.

Status: ✅ done · 🔨 in progress · ⏳ next · 💤 later

## Milestones

| Milestone | Status | Exit criterion |
| --- | --- | --- |
| M0 Framing | 🔨 | one note per source (access, limits, terms); radio and artist contacts started |
| Scaffold | ✅ | repository on the target architecture, every check green locally |
| M1 Schema test | 💤 | ~180 hand-entered objects fit the schema with no free-form field |
| M2 ANSI chain | ⏳ | `tm ingest/decode/render/features` on 20 packs; determinism green; every file has a grid or a classified error |
| M3 Minimal site | 💤 | one work viewable from source to analysis; `can_display()` tested; tour works on a phone |
| M4 Scale | 💤 | all of 16colo in metadata; NFO credit extraction precision measured |
| M5 Extensions | 💤 | one decoder, profile and collection per added system |

## Current focus: the work screen, end to end (M2, started early)

The first thing a visitor sees, built in pipeline order so that nothing is throwaway.

- [ ] Push `scaffold`, open the pull request, get the first CI run green
- [ ] Golden artifact #1: an ANSI made for the project (CC0), with its SAUCE record
- [ ] `tm_render`: SAUCE reader; ANSI/CP437 decoder → grid (`row, col, codepoint, fg, bg, blink, t`) in Parquet; property tests (no input crashes a decoder)
- [ ] `tm ingest` for the golden source → `source`, `work`, `version`, `artifact` rows; `tm decode` → `decoding` rows
- [ ] Conservation renderer (Python → PNG, integer scale, 9th column, blink / iCE) with recipe; determinism test; comparison with ansilove
- [ ] `tm export` → public bucket: compact grid file and record JSON, gated by `can_display()`
- [ ] Work screen: canvas renderer from the grid and the bitmap font, profile switch, modem-speed playback, zoom to the cell, draw-order layer (honest about file order versus gesture)
- [ ] Visual regression screenshots of the golden artifacts

## M0 tasks that need a person (Nicolas)

- [ ] Contacts: 16colo.rs, Demozoo, IF Archive (access, API limits, terms)
- [ ] Radios: Nectarine, SLAY Radio, Ericade, Kohina, BitJam (agreement, HTTPS stream)
- [ ] First artists and groups for display permission
- [ ] Decisions: legal structure, host, domain name, lawyer, partner radios

## Known debt

| Item | Why it matters | Plan |
| --- | --- | --- |
| Paraglide fetches its inlang plugins from a CDN at build time | breaks the offline, reproducible build goal | vendor the plugins or pin them in the lockfile |
| TAKEDOWN has no contact address | withdrawals must not go through public issues | publish with the domain name |
| Embedding tables not in the schema | their dimension depends on models not chosen yet | add with research workstream 1 |
| OpenTofu for staging / production not written | needed from M4 | after the host decision |
