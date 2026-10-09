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
   - [x] Decoder counts overwritten cells (decoder v3); exploratory animation rule chosen on their distribution, in `works` v3 and the notebook (constraint 3)
6. [x] D1 pilot: 21 train packs drawn by era (seven strata bounded by the mass, three each, systematic within a stratum by content and size, seed 20261009, weights recorded) and 3 added by hand with a reason ([ADR 0017](adr/0017-d1-pilot-sampling.md)); frozen in `datasets/d1/sample.yaml` with its datasheet; notebook and pre-registration templates in `research/templates/`
7. [x] `tm export` → public bucket: record JSON, compact grid (`grid.tmg`) and PNG per work, gated by `can_display()` and `audience()`, with credit, provenance and withdrawal link; refuses a shown file without credit ([ADR 0022](adr/0022-the-public-export.md))
8. [x] Work screen, first version: canvas renderer from the grid and the bitmap font (pixel for pixel the conservation PNG), arrival at 2,400 baud, credit as signed, audience badges, source link, "withdraw or claim" on every record (ADR 0009); `/work?w=<sha256>`
   - [ ] Owner's choices on the [museography proposal](museography.md) (rooms, games, feeds): the work screen is its first room

Session 8 order (2026-10-09, owner's requests: a viewer that is a snapshot of the visit, the
nearest-works graph, Wikipedia, the words in the works). Each step is one branch; a step that
needs the one before says so.

9. [x] Explorer thumbnails: "best fit" (the whole work scaled into the card, since most works are
   long portraits and the first screen misrepresents them) with the first screen as an option, and
   the whole work in a corner of a first-screen card (I47). Small, and every later look at the
   corpus goes through it.
10. [ ] Wikipedia and Wikidata, downloaded politely: the articles of the source note in every
    language that has one, with revision ids, and their Wikidata items, into `data/wikipedia/`
    (local, CC BY-SA text never republished), one request at a time with our User-Agent (I50).
    Runs in the background while the next steps go on.
11. [ ] Work screen, second pass: a snapshot of what visitors will get (foundation document,
    "Expérience du visiteur"; museography room 1). Entrance on a work (work of the day), five-line
    label opening by levels (context, analysis, bytes), keys (`?`, space, arrows, `r`), full width
    on a phone redrawn from the grid, zoom to the cell, the words of the work as text for screen
    readers, ways out that need no new data (next in the pack, same author, same month);
    typography and layout with care; checked in screenshots, desktop and phone, both locales.
12. [ ] Nearest-works graph: k nearest neighbours on features v1 (standardized, versioned, train
    packs), stored as a dataset table; studied as a social network: degree, communities,
    homophily by year, group, archive, content kind, and country where Demozoo gives one; what
    the projections show, written in an exploration note (I48, exploratory). Feeds I21.
13. [ ] Corpus as a graph to explore (local research tool, not public): every work a node, edges
    from step 12 (and pack, group, greets later), WebGL, thumbnails drawn on nodes when zoomed in,
    a click opens the work (I49).
14. [ ] Work screen: "nearest in style" as a way out, from step 12, published by `tm export`
    (marked as computed, dotted, foundation document).
15. [ ] Reading the words in the works, plan then first layer: zones of text in the grid, line
    classes (I22: greets, credits, BBS ad, news, dedication, prose), entities (handles, groups,
    BBS, phone numbers, dates, places) as `inferred` assertions; lettering drawn in blocks read
    against TheDraw fonts; a per-work reading exported as Parquet for NLP and as Markdown for
    people (I51). ADR before code.
16. [ ] Nomenclature from Wikipedia and Wikidata: a controlled vocabulary (kinds, techniques,
    formats, tools, groups) with QIDs and labels in every language, as data in `corpus/`, used by
    the records and the explorer (I27, I50). ADR before code.
17. [ ] Where is the adult material? An exploratory note on Q36: what keyword inference misses,
    what dedicated collections exist (textfiles.com, Defacto2, Discmaster), what 16colo kept.
18. [ ] Then, as planned before: the review queue (D2) for inferred ratings and the rule 4
    sample; Discmaster over the 16colo archives (I33).

Later, deliberately (nothing depends on them yet):

| Item | When | Why it can wait |
| --- | --- | --- |
| Work screen: profile switch and authentic level, modem-speed playback, zoom to the cell, draw-order layer | after the first version; spike 0002 before the playback | the first version stands without them |
| Visual regression screenshots of the golden artifacts | after the first work screen | the golden pixels are already pinned in CI |
| Golden artifact #2 (blink, iCE, 8 px cells) | next renderer change | spike 0001 checked these paths on real packs |
| Near-duplicates beyond bytes: same grid (works v5: 84,104 decoded files, 83,172 grids), same grid but SAUCE, cell similarity, perceptual hash of the rendering (leads I40) | before M4 counts and before any "unique works" figure | byte identity is enough for storage; counts of works need the next levels |
| White-background reading: an `interpretation` profile (palette mapping, not the conservation PNG), tested by content kind and colour family before anything is shown (leads I41, spike 0004) | after the first work screen | the screen stands on the authentic and conservation levels |
| A vision model as a reader of the works: describe, then comment, blind or with context, at several sizes; marked `interpretation` / `algo:` (invariant 8), local open-weight models only until rights allow more (leads I42, Q33, spike 0005) | after D1 by hand, which gives the human descriptions to compare with | nothing in M2–M3 depends on it |
| M1 schema test by hand | after D1 | real packs test the schema first; M1 then covers what they do not (BBS, radios, testimonies) |
| Offline copy of the originals and a database export (the foundation document's three copies start in production) | before the first hand-made records (M1) or the first source beyond 16colo | 16colo still holds every original, and every `tm` command is idempotent: the local corpus can be rebuilt from the mirror. Only hand-entered records would be lost |
| Preservation package: originals laid out as OCFL objects with JSON metadata, readable without our database; published spec of the grid format | ADR before M4 | until then the database is the only index of the store, which is fine while it can be rebuilt |
| Normalized preservation copies of the formats we do not decode (PCX/LBM/BMP → PNG, FLI/FLC → FFV1 in MKV, tracker modules → FLAC as a rendering with its recipe) | with each M5 decoder | the originals are kept as written; these formats are documented and readable today |

## Leads

Every question, hypothesis, idea and curiosity is written in [leads.md](leads.md) when it comes,
even when it would lead too far; a lead taken up moves here or into a study. Next in line:

- I33, Discmaster: search the 16colo archives by hash for dated copies on CD-ROMs and FTP sites,
  the independent witness Q21 needs ([register](sources/README.md)). I25 (textfiles) is done.
- I2 is done (text layer v2, `tm text`, table `text` of `works` v4, explorer search). Next from
  it: classify lines (I22) and a greets graph (I23), signatures (Q12), a language detector (Q10).
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
| 0004 | Can a white background keep a work legible and faithful? Palette mappings (inverted value, swapped black/white, ink on paper) on 30 works across content kinds and colour families, judged side by side | 3 h | white-background profile |
| 0005 | Does a vision model see what an ANSI shows? The ten Calvin and Hobbes works of works v5 (title or text says so) and controls, blind then with context, at 4 sizes, PNG and JPEG: recognition rate, and what the descriptions get wrong | 4 h | any model-written text on the site |

## M0 tasks that need a person (Nicolas)

- [x] Branch protection on `main`: ruleset with the CI jobs required, no review (ADR 0008)
- [x] Add `devcontainer` to the required checks of the `main` ruleset
- [x] Repository description and topics

- [ ] Before M4: contacts with 16colo.rs, Demozoo, IF Archive (access, API limits, terms); not needed before, packs and API are public. Access, limits and terms are checked in the [source register](sources/README.md) and the notes on 16colo, Demozoo (daily dump, no data license stated: ask before republishing), textfiles.com and Wikipedia
- [ ] Radios: Nectarine, SLAY Radio, Ericade, Kohina, BitJam (agreement, HTTPS stream); until then the site links out to the station instead of embedding its stream
- [ ] First artists and groups for display permission
- [ ] Before M3: inform 16colo and Demozoo of the project (Claude drafts, Nicolas sends)
- [ ] Before M4: lawyer review of ADR 0009
- [ ] Decide ADR 0019 (content descriptors, audiences, age check), with the lawyer for its legal points; before any feed, game or kiosk reaches the public
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
| Planner estimates of the `work_split` view (an aggregate) are wrong by orders of magnitude, even after `analyze` | a filter `x in (subquery)` over a corpus-wide dataset query ran for minutes (D1 build) | write such filters as `= any(array(…))`, computed once; revisit if the views become tables |
| The `web` CI job sometimes spends 20 minutes installing Playwright's system packages | slows every merge | cache the browsers, or install without `--with-deps` on a runner that has them |
| OpenTofu for staging / production not written | needed from M4 | after the host decision |
