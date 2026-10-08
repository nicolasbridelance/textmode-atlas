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

- [x] Push `scaffold`, open the pull request, get the first CI run green ([#1](https://github.com/nicolasbridelance/textmode-atlas/pull/1))
- [x] Golden artifact #1: Horizon, an ANSI made for the project (CC0), with its SAUCE record; also the README showcase
- [x] `tm_render`: SAUCE reader; ANSI/CP437 decoder → grid (`row, col, codepoint, fg, bg, blink, t`) in Parquet; property tests (no input crashes a decoder)
- [x] Spike 0001: grid rendering matches ansilove on 96 of 99 VGA files ([report](spikes/0001-ansilove-parity.md), [ADR 0010](adr/0010-render-from-the-grid.md))
- [x] Decoder: canvas height is the last written row + 1, not the SAUCE height (spike 0001)
- [x] Conservation renderer (grid → PNG, integer scale, 9th column, blink / iCE) with recipe; determinism test; ansilove parity on the golden artifacts in CI (`just parity`)
- [x] `tm ingest golden` → `source`, `work`, `version`, `artifact` rows, original stored write-once
- [x] `tm decode` → `decoding` rows (grid or classified error); grids in the private `tm-derived` bucket ([ADR 0011](adr/0011-a-private-bucket-for-derived-data.md))
- [x] `tm render` → conservation `representation` rows with the recipe, PNGs in `tm-derived` (the authentic level comes with the profiles, on the work screen)
- [ ] `tm export` → public bucket: compact grid file and record JSON, gated by `can_display()`; refuses a shown file without credit (ADR 0009)
- [ ] Work screen: credit as signed, source link and "withdraw or claim" on every record (ADR 0009); canvas renderer from the grid and the bitmap font, profile switch, modem-speed playback, zoom to the cell, draw-order layer (honest about file order versus gesture)
- [ ] Visual regression screenshots of the golden artifacts

## Research track

Detailed in [research-program.md](research-program.md). Phases run alongside the milestones.

| Phase | Milestone | Status | Exit criterion |
| --- | --- | --- | --- |
| R0 Instruments: features v1, datasets D0–D1, notebook and pre-registration templates | M2 | ⏳ | features reproducible; D1 datasheet |
| R1 Linkage v1: credits, greetings, BBS ads, dating, provenance; gold set D2 | M2–M3 | 💤 | precision and recall published on D2 |
| R2 Atlas: description of all of 16colo, capture–recapture coverage, graph D5 | M4 | 💤 | coverage estimate with intervals |
| R3 Style: W1 representation, W2 attribution | M4 | 💤 | W1 beats baselines on held-out packs, or negative result published |
| R4 Change: W3 resonance, W6 ruptures | after R3 | 💤 | pre-registered tests published |
| R5 Mechanisms: W4 diffusion, W5 transfers, W7 reading the art | after R1–R3 | 💤 | pre-registered tests published |
| R6 Platforms: PC, Amiga, C64, teletext | M5 | 💤 | cross-platform distances with coverage |

## Spikes to run

| Spike | Question | Time box | Before |
| --- | --- | --- | --- |
| 0002 | Can a canvas draw a 500-line ANSI at cell zoom and modem speed at 60 fps on a mid-range phone? | 2 h | work screen |
| 0003 | Can Paraglide build offline (vendored inlang plugins)? | 1 h | known debt below |

## M0 tasks that need a person (Nicolas)

- [x] Branch protection on `main`: ruleset with the CI jobs required, no review (ADR 0008)
- [x] Add `devcontainer` to the required checks of the `main` ruleset
- [x] Repository description and topics

- [ ] Before M4: contacts with 16colo.rs, Demozoo, IF Archive (access, API limits, terms); not needed before, packs and API are public
- [ ] Radios: Nectarine, SLAY Radio, Ericade, Kohina, BitJam (agreement, HTTPS stream); until then the site links out to the station instead of embedding its stream
- [ ] First artists and groups for display permission
- [ ] Before M3: inform 16colo and Demozoo of the project (Claude drafts, Nicolas sends)
- [ ] Before M4: lawyer review of ADR 0009
- [ ] Decisions: legal structure, host, domain name, lawyer, partner radios

## Known debt

| Item | Why it matters | Plan |
| --- | --- | --- |
| Paraglide fetches its inlang plugins from a CDN at build time | breaks the offline, reproducible build goal | spike 0003 |
| Contact address is a personal Gmail | fine for now; should become a project address | move to the domain once chosen |
| Vitest 5 and @vitest/browser-playwright 5 | must move together; the config fails at startup ("reading 'project'") | dedicated migration |
| TypeScript 7 held back (#11 closed) | the native compiler drops the JS API used by svelte-kit sync, svelte-check, ESLint and knip | lift the Dependabot ignore once those tools support it |
| deptry passed locally but failed in CI on first-party imports | local and CI environments differ | first-party packages are now declared explicitly; watch for other differences |
| PabloDraw 24-bit colour (`ESC[1;R;G;Bt`) skipped by the decoder | recent packs use it; colours and sometimes layout differ (spike 0001) | decoder extension before M4 |
| No golden artifact with blink, iCE or 8 px cells | Horizon covers 9 px only; renderer paths stay untested on golden files | golden artifact #2 |
| Embedding tables not in the schema | their dimension depends on models not chosen yet | add with research workstream 1 |
| OpenTofu for staging / production not written | needed from M4 | after the host decision |
