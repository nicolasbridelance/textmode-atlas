<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Research programme

How the museum learns about its corpus: what it asks, from which data, with which methods, in
which order, and how each result flows back into what visitors see. The
[foundation document](Le%20caractère%20comme%20matière%20—%20document%20de%20fondation.md#programme-de-recherche)
names six workstreams; this programme places them on the foundations they need, adds the
linkage and description work that comes first, and phases everything against the milestones.

## Why research is central

The museum's promise is to show one work at a time **and** to say where it sits: who made it,
with whom, for whom, what it answered, what answered it, what is missing around it. Almost none
of that is written down in one place. It is scattered in NFO files, file headers, member lists,
greetings, BBS advertisements drawn inside the art, and in the art itself. The research
programme is how those scattered traces become links, and how links become understanding.

Three kinds of output, always kept apart (invariants 4, 5, 8):

| Output | Nature in the database | Example |
| --- | --- | --- |
| **Extracted facts** | `documented`, with the file that proves it | "Artist X is listed as a member of group Y in pack Z's NFO" |
| **Testimonies** | `testified`, with the trace | "I joined Y in spring 1994" |
| **Computations** | `inferred`, signed `algo:<name>@<version>`, with a calibrated confidence | "Work A is stylistically closest to work B" |

## Principles

These apply to every study. Most are already rules in the foundation document; they are
repeated here because they shape the design of every dataset and notebook.

1. **Describe before inferring.** Every workstream starts with descriptive statistics and
   coverage, published as such, before any model or test.
2. **Pre-register.** A confirmatory question is filed in `research/NNNN-name/hypothesis.md`
   (question, measure, null model, the result that would refute it) and committed before the
   data is examined. Exploratory work is labelled exploratory.
3. **Split by pack.** Training and test sets never share a pack: logos, templates and shared
   lettering otherwise inflate every score. Where time matters, split by date as well.
   The test split of 16colo is fixed now, before anyone looks at the grids: a pack is `test`
   when the first byte of its archive's SHA-256 is below 52 (about one pack in five, column
   `split` of dataset `catalogue`). Exploration reads the `train` packs only, so that a question
   it raises can still be tested on packs nobody has examined. The catalogue exploration saw
   the metadata of every pack, not their grids, features or images.
4. **Null models.** Every effect is compared with the same computation on permuted dates, labels
   or network edges.
5. **Uncertainty and coverage.** Intervals come from resampling by pack. Every number is
   published with the share of the known corpus it rests on.
6. **Tools before talent.** A formal novelty is checked against the release dates and features
   of the drawing tools (`tool.released`, `tool.features`) before it is credited to an artist.
7. **Precedence needs intervals.** "A precedes B" only when `A.date_max < B.date_min`.
8. **The witnesses answer.** Every published result has a page with data, code and a response
   form; answers come back as `testified` assertions and can overturn a computation.
9. **No generation, no model release.** Models predict and measure; they never produce works
   (invariant 9), and models trained on the works are not distributed. Measurements are.
10. **Pseudonyms stay pseudonyms.** Stylometry can link handles a person chose to keep apart.
    Alias detection results stay internal unless a document or the person confirms them; they
    are never used toward a civil identity.

## Data foundations

Research reads **datasets**, never the production database (see the foundation document,
section "Datasets"). Each is frozen, versioned, reproducible, split by pack, and comes with a
datasheet.

| Dataset | Content | Available | Used by |
| --- | --- | --- | --- |
| D0 golden | the project's CC0 reference artifacts | M2 | tests, method checks |
| D1 pilot | 20 packs: artifacts, SAUCE, grids, features, NFO text | M2 | R0, R1 |
| D2 linkage gold set | 200+ hand-checked NFO / DIZ lines with their extracted credits, greetings and BBS ads | M3 | R1 evaluation |
| D3 16colo metadata | every pack and file of 16colo: hashes, SAUCE, dates, credits | M4 | R2 onwards |
| D4 features and embeddings | grid features, symbolic / visual / text embeddings for D3 | M4 | R2, R3 |
| D5 graph | active assertions as a temporal multigraph (identities, groups, places, works, tools) | M4 | R2, R5 |
| D6 cross-platform | Amiga ASCII, PETSCII, teletext, as decoders land | M5 | R6 |

## Layer 1 — Linkage: turning traces into links

This layer produces most of the museum's links. It comes before the six workstreams because
they all need it: you cannot study transfers without memberships, nor novelty without dates.

| Link family | Sources | Method | Output |
| --- | --- | --- | --- |
| **Provenance** | file hashes across packs and archives | exact SHA-256 matches; near-duplicates by grid similarity (same work, re-saved or edited) | `set_member` rows; `references` / version links |
| **Credits** | SAUCE author and group fields, NFO and FILE_ID.DIZ credits, member lists, file-name conventions (`xx-name.ans`) | rule-based parsers first, then a sequence-labelling model trained on D2; every line keeps its source file | `created`, `member_of`, `had_role` as `documented` |
| **Greetings** | "greets", "shouts", "respect to" sections of NFOs and of the art | the same parsers; a greeting is a directed, dated tie | a social network of acknowledgement (new relation to add to the vocabulary) |
| **Places** | BBS advertisements inside the art and the NFOs: names, phone numbers, sysops, "world HQ" and "distro site" lists | parsing, phone-number normalisation by country and era, name reconciliation | `place` rows, `distributed_by`, `made_for` |
| **Commissions** | logos and adverts drawn for a BBS or a group: the name is *drawn* in block letters | **reading the lettering**: recognise text drawn with blocks and shades (see W7 below), match to known places and groups | `made_for` |
| **Dates** | SAUCE date, pack release date, file timestamps, NFO dates, testimonies | an interval per work, from the tightest consistent bounds; conflicts kept and flagged | `version.date_min/max`, `date_basis` |
| **Identity resolution** | handles across packs, spelling variants, `aka` mentions | string similarity plus co-occurrence in the same groups and months; documented `aka` only | `identity.aliases`; candidate merges for human review |

Evaluation: precision and recall on D2 for every extractor, published with the extractor
version. The M4 exit criterion (precision measured on 200 checked lines) is this layer.

## Layer 2 — Description: an atlas of the corpus

Descriptive studies, published as data stories and as the museum's views. They answer "what is
there" before "why".

- **Corpus shape**: works per year, per group, per platform; canvas widths and heights; the rise
  of long scrolling pieces; file formats over time.
- **Material**: glyph-class shares (full blocks, half blocks, shades, box drawing, letters),
  palette use, iCE colours, the share of each tool (from SAUCE and editor signatures).
- **Social structure**: group sizes and lifespans, membership turnover, artists' careers
  (first and last appearance, number of groups), the greeting network's communities and
  brokers, BBS distribution networks by country.
- **Coverage and loss**: what is known to have existed (packs announced in NFOs, members listed
  without surviving works, BBSes advertised) versus what survives. Where archives overlap
  (16colo, textfiles, Demozoo, scene.org), **capture–recapture estimators** give an estimate of
  how much of the scene's output is lost, by year and by scene. This is the honest denominator
  of every other result, and it feeds the "map of gaps" view and the calls for contributions.

## Layer 3 — The workstreams

Each workstream lists its question, a first hypothesis to pre-register, the data and methods,
the test that can fail, what it gives the museum, and what it depends on.

### W1. Representing style

- **Question**: can a representation learned from grids capture what makes an artist or a group
  recognisable?
- **First hypothesis**: an embedding trained to predict masked cells (glyph, foreground,
  background) retrieves the author of unseen works better than glyph histograms and better than
  a generic vision model applied to the rendering.
- **Data**: D3, D4; grids as a three-channel discrete tensor (glyph 0–255, fg 0–15, bg 0–15).
- **Method**: self-supervised masked-cell model on grid patches; baselines `emb_symbolic` and
  `emb_visual`; retrieval evaluated by pack-split.
- **Fails if**: it does no better than the histogram baseline on held-out packs.
- **For the museum**: "closest in style" exits; the style axis of the timeline.
- **Depends on**: decoders (M2), D3–D4 (M4).

### W2. Attribution and aliases

- **Question**: who made the unsigned works, and which handles are the same hand?
- **First hypothesis**: calibrated author probabilities on signed works with their signature
  removed reach a useful precision at a fixed coverage.
- **Method**: classifier on W1 embeddings and features; calibration; abstention below a
  threshold; signatures masked by detecting and removing signature regions.
- **Fails if**: calibrated precision stays below an agreed threshold on held-out packs.
- **For the museum**: "possibly by" suggestions, always `inferred`, never shown as a credit;
  internal alias candidates (principle 10).
- **Depends on**: W1, Layer 1 credits.

### W3. Novelty, transience and resonance

- **Question**: which works brought something new that others then took up?
- **First hypothesis**: works cited as landmarks at the time (yearly "best of" lists, pack
  reviews, magazine mentions) have higher resonance than random works of the same month.
- **Method**: novelty = divergence of a work's feature distribution from the preceding window;
  transience = divergence from the following window; resonance = novelty − transience (Barron
  et al., PNAS 2018). Windows in months, with date intervals respected.
- **Fails if**: resonance does not separate cited works from random ones better than permuted
  dates do.
- **For the museum**: the computational canon, compared with the historical canon by rank
  correlation; the largest disagreements go to the witnesses ("Memory versus computation" view).
- **Depends on**: dates (Layer 1), W1 or features, a list of period citations (historical canon).

### W4. Diffusion of techniques

- **Question**: how did techniques spread — through tools, through groups, through who greeted
  whom?
- **First hypothesis**: after controlling for the release date of the tools that enable a
  technique, an artist adopts it sooner when someone in their group or greeting network already
  uses it.
- **Method**: technique detectors on grids (shade gradients ░▒▓, half-block "high resolution",
  iCE colours, lettering styles, shading directions); survival analysis of time to adoption
  with network exposure as a time-varying covariate; edge-permutation null model.
- **Fails if**: exposure has no effect beyond tool release and calendar time.
- **For the museum**: "Adoption curves" view; for each technique, its first known uses.
- **Depends on**: Layer 1 (memberships, greetings, dates), tool table, W1 optional.

### W5. Transfers between groups

- **Question**: when an artist joins a group, does the group's style move?
- **First hypothesis**: the receiving group's style moves toward the newcomer's earlier style
  after the arrival, compared with control groups.
- **Method**: difference-in-differences on group style over time; event-study plot to check
  parallel trends before the transfer.
- **Fails if**: effects appear before the arrival date (no parallel trends), or vanish against
  controls.
- **For the museum**: "Artist–group flows" view; before/after works for each transfer.
- **Depends on**: Layer 1 memberships with dates, W1.

### W6. Ruptures and convergences

- **Question**: when did the scene change, and did PC and Amiga styles converge?
- **First hypothesis**: change points in monthly feature distributions coincide with tool
  releases or platform shifts more often than chance.
- **Method**: change-point detection on monthly distributions; distance between platform
  distributions per year.
- **Fails if**: detected ruptures do not survive resampling by pack.
- **For the museum**: the eras of the timeline, argued from data rather than asserted.
- **Depends on**: D3–D4; D6 for the cross-platform part.

### W7. Reading the art (added)

- **Question**: what does the art say? Much textmode art is lettering — group names, BBS names,
  phone numbers, titles — drawn in block letters that no text extractor reads.
- **First hypothesis**: a recogniser trained on lettering in the corpus reads group and BBS
  names in logos well enough to propose `made_for` links with useful precision.
- **Method**: detect lettering regions in grids; recognise characters drawn from blocks and
  shades (the training set comes from works whose NFO names what the logo says); match against
  known places and groups.
- **Fails if**: precision of proposed `made_for` links stays below an agreed threshold on a
  checked sample.
- **For the museum**: commission links ("drawn for Mirage BBS"); searchable text inside the art;
  better accessibility (the readable text of a work, offered separately).
- **Depends on**: decoders, Layer 1 places and groups.

## How results reach the museum

| Museum feature | Comes from |
| --- | --- |
| Record credits, groups, places | Layer 1 (`documented`, `testified`) |
| Exits: next in pack, same artist | Layer 1 |
| Exit: closest in style | W1 (`similar_to`, `inferred`) |
| Exit: a rival group's answer, the same month elsewhere | Layer 1 dates and groups, W1 |
| Timeline positions and eras | W1 projection, W6 |
| Three canons | historical list (curated), W3 (computational), curators (signed) |
| Views: styles over time, memory versus computation, analysis layers, flows, adoption, gaps | W1/W6, W3, features, W5, W4, Layer 2 coverage |
| Calls for contributions | Layer 2 gaps and `lost_item` |

Every inferred link is drawn dashed, every documented link solid, with a "method" link to the
code and data that produced it.

## Phasing

| Phase | Milestone | Work | Exit criterion |
| --- | --- | --- | --- |
| R0 Instruments | M2 | feature extractor v1 on grids; D0, D1; notebook and pre-registration templates; first exploratory look at the pilot | features reproducible bit for bit; D1 datasheet |
| R1 Linkage v1 | M2–M3 | credit, greeting and BBS-ad parsers; dating intervals; provenance by hash; D2 gold set | precision and recall published on D2 |
| R2 Atlas | M4 | Layer 2 on all of 16colo; capture–recapture coverage; graph D5 and its descriptive statistics | coverage estimate with intervals; first data stories |
| R3 Style | M4 | W1, then W2 | W1 retrieval beats baselines on held-out packs, or the negative result is published |
| R4 Change | after R3 | W3, W6 | pre-registered tests run and published |
| R5 Mechanisms | after R1–R3 | W4, W5, W7 | pre-registered tests run and published |
| R6 Platforms | M5 | Layer 2 and W6 across PC, Amiga, C64, teletext | cross-platform distances with coverage |

Negative results are results: each pre-registered test is published whatever its outcome.

## Tools

Python in `analysis/` (`tm_analysis`), notebooks in [marimo](https://marimo.io/) under
`research/`, data in Parquet read with Polars and DuckDB, models with scikit-learn and later
PyTorch, survival analysis with lifelines, change points with ruptures, statistics with
statsmodels. Dependencies enter `analysis/` with the first code that uses them.

## Open questions

- Which period sources make the **historical canon** (yearly lists, pack reviews, magazines),
  and who curates them?
- Which **thresholds** make an inferred link worth showing to visitors (W2, W7)?
- How far can **greetings** be read as social ties, and not just politeness? Interviews should
  calibrate this early.
- Which **archives overlap** enough for capture–recapture to be meaningful?
