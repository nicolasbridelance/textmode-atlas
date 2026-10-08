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

## Current focus: see and measure the corpus, then the pilot dataset and the work screen (M2)

Order set on 2026-10-08, revised the same day: all of 16colo is ingested and decoded, so the
next step is to look at it, as images and as measurements, before choosing the pilot. What the
exploration finds may become constraints for the steps after it, so it comes first. It reads
the `train` packs only (research program, rule 3). Nothing below is throwaway: each step is
where the foundation document puts it.

Done, pipeline on the golden source:

- [x] Push `scaffold`, open the pull request, get the first CI run green ([#1](https://github.com/nicolasbridelance/textmode-atlas/pull/1))
- [x] Golden artifact #1: Horizon, an ANSI made for the project (CC0), with its SAUCE record; also the README showcase
- [x] `tm_render`: SAUCE reader; ANSI/CP437 decoder → grid (`row, col, codepoint, fg, bg, blink, t`) in Parquet; property tests (no input crashes a decoder)
- [x] Spike 0001: grid rendering matches ansilove on 96 of 99 VGA files ([report](spikes/0001-ansilove-parity.md), [ADR 0010](adr/0010-render-from-the-grid.md))
- [x] Decoder: canvas height is the last written row + 1, not the SAUCE height (spike 0001)
- [x] Conservation renderer (grid → PNG, integer scale, 9th column, blink / iCE) with recipe; determinism test; ansilove parity on the golden artifacts in CI (`just parity`)
- [x] `tm ingest golden` → `source`, `work`, `version`, `artifact` rows, original stored write-once
- [x] `tm decode` → `decoding` rows (grid or classified error); grids in the private `tm-derived` bucket ([ADR 0011](adr/0011-a-private-bucket-for-derived-data.md))
- [x] Explicit decoder and renderer versions, guarded by a source digest ([ADR 0012](adr/0012-explicit-versions-for-decoders-and-renderers.md))
- [x] `tm render` → conservation `representation` rows with the recipe, PNGs in `tm-derived`

Next, in this order:

1. [x] `tm ingest pack`: 16colo packs from the local mirror as `set` works with their `set_member` files, art found by extension, SAUCE or content, scene publication recorded (ADR 0009); archives read by Python, Info-ZIP, 7-Zip and arj ([ADR 0013](adr/0013-archive-readers-for-artpacks.md)); a rerun completes what an earlier one could not read
2. [x] Catalogue exploration (exploratory): describe all of 16colo from the local mirror (years, groups, formats, SAUCE presence, widths, iCE, fonts, NFO and DIZ) before choosing anything; D1 strata come out of it ([source note](sources/16colo.md), [findings](../research/exploration/catalogue.md), dataset `catalogue`); 16colo's own tags (API v1) not used yet
3. [x] Conservation renderings of the whole corpus (`tm render --shard`, private bucket): 111,453 on 2026-10-08
4. [x] Feature extractor v1 in `analysis/` (geometry, glyphs, colour, sequence, from the foundation document) and `tm features` → `features.parquet`, reproducible bit for bit
5. [x] Visual and statistical exploration of the `train` packs: a `works` dataset (metadata, features, rendering keys), marimo notebook, local corpus explorer (`just explore`), first note ([works.md](../research/exploration/works.md)) with the constraints it puts on later steps
   - [x] Content kind of each work (colours, block share), since the extension does not say it (constraint 1): `works` v2, explorer filter
   - [ ] Decoder counts overwritten cells (done, decoder v3); animation rule chosen on their distribution and flagged in features and notebook (constraint 3)
6. [ ] D1 pilot: 20 packs drawn by stratum with a fixed seed, strata revised after step 5 (eras bounded by the mass, equal allocation so thin years are over-represented, inclusion weights recorded, content kind: constraints 1–2 of the works note, leads I19), rare cases added by hand with a reason; frozen with its datasheet; marimo notebook template
7. [ ] `tm export` → public bucket: compact grid file and record JSON, gated by `can_display()`; refuses a shown file without credit (ADR 0009)
8. [ ] Work screen, first version: canvas renderer from the grid and the bitmap font, credit as signed, source link, "withdraw or claim" on every record (ADR 0009)

Later, deliberately (nothing depends on them yet):

| Item | When | Why it can wait |
| --- | --- | --- |
| Work screen: profile switch and authentic level, modem-speed playback, zoom to the cell, draw-order layer | after the first version; spike 0002 before the playback | the first version stands without them |
| Visual regression screenshots of the golden artifacts | after the first work screen | the golden pixels are already pinned in CI |
| Golden artifact #2 (blink, iCE, 8 px cells) | next renderer change | spike 0001 checked these paths on real packs |
| M1 schema test by hand | after D1 | real packs test the schema first; M1 then covers what they do not (BBS, radios, testimonies) |
| Offline copy of the originals and a database export (the foundation document's three copies start in production) | before the first hand-made records (M1) or the first source beyond 16colo | 16colo still holds every original, and every `tm` command is idempotent: the local corpus can be rebuilt from the mirror. Only hand-entered records would be lost |
| Preservation package: originals laid out as OCFL objects with JSON metadata, readable without our database; published spec of the grid format | ADR before M4 | until then the database is the only index of the store, which is fine while it can be rebuilt |
| Normalized preservation copies of the formats we do not decode (PCX/LBM/BMP → PNG, FLI/FLC → FFV1 in MKV, tracker modules → FLAC as a rendering with its recipe) | with each M5 decoder | the originals are kept as written; these formats are documented and readable today |

## Leads

Every question, hypothesis, idea and curiosity is written in [leads.md](leads.md) when it comes,
even when it would lead too far; a lead taken up moves here or into a study. Next in line, after
the open tasks of step 5:

- I2, text runs extracted from the grids: it opens signatures (Q12), languages (Q10) and
  greetings at once.
- I21, an author-signal benchmark: H3 explored on the train packs found a weak signal in
  features v1 (2.3% same author among nearest works, 0.6% by chance, 14.2% knowing the group);
  every new representation is measured against it.
- I7, tool fingerprints from byte habits (Q1, Q14, Q18): rule 6 of the research program needs
  them before any claim about style.
- I6, time to arrive at modem speed, a fact for every record.

## Research track

Detailed in [research-program.md](research-program.md). Phases run alongside the milestones.

| Phase | Milestone | Status | Exit criterion |
| --- | --- | --- | --- |
| R0 Instruments: features v1, datasets D0–D1, notebook and pre-registration templates | M2 | 🔨 | features reproducible; D1 datasheet |
| R1 Linkage v1: credits, greetings, BBS ads, dating, provenance; gold set D2 | M2–M3 | 💤 | precision and recall published on D2 |
| R2 Atlas: description of all of 16colo, capture–recapture coverage, graph D5 | M4 | 💤 | coverage estimate with intervals |
| R3 Style: W1 representation, W2 attribution | M4 | 💤 | W1 beats baselines on held-out packs, or negative result published |
| R4 Change: W3 resonance, W6 ruptures | after R3 | 💤 | pre-registered tests published |
| R5 Mechanisms: W4 diffusion, W5 transfers, W7 reading the art | after R1–R3 | 💤 | pre-registered tests published |
| R6 Platforms: PC, Amiga, C64, teletext | M5 | 💤 | cross-platform distances with coverage |

## Spikes to run

| Spike | Question | Time box | Before |
| --- | --- | --- | --- |
| 0002 | Can a canvas draw a 500-line ANSI at cell zoom and modem speed at 60 fps on a mid-range phone? | 2 h | modem-speed playback |
| 0003 | Can Paraglide build offline (vendored inlang plugins)? | 1 h | known debt below |

## M0 tasks that need a person (Nicolas)

- [x] Branch protection on `main`: ruleset with the CI jobs required, no review (ADR 0008)
- [x] Add `devcontainer` to the required checks of the `main` ruleset
- [x] Repository description and topics

- [ ] Before M4: contacts with 16colo.rs, Demozoo, IF Archive (access, API limits, terms); not needed before, packs and API are public. Access, limits and terms of 16colo are checked in its [source note](sources/16colo.md) (contact@16colo.rs)
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
| About 1,600 pictures, programs and modules stamped with an ANSI SAUCE record were ingested as works before the fix (artifact rows are immutable) | they stay `single` works whose decoding is `binary_content`; catalogue counts of art include them | a correction mechanism for misclassified artifacts (an assertion, not an update), before M3 |
| XBIN, BIN, RIP, ADF, IDF, PCBoard, Avatar and Tundra are recorded as `unsupported_format` | their works have no grid, so no rendering and no features | decoders by count of files in the catalogue; ASCII is read by the ANSI decoder, as ansilove does |
| The `web` CI job sometimes spends 20 minutes installing Playwright's system packages | slows every merge | cache the browsers, or install without `--with-deps` on a runner that has them |
| OpenTofu for staging / production not written | needed from M4 | after the host decision |
