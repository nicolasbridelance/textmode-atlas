<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0029. The research room as an index of studies, one page each, from one registry

- Status: Accepted
- Date: 2026-10-10
- Deciders: Claude (autonomous mode, ADR 0008), at the owner's request; Nicolas Bridelance
  reviews afterwards
- Relates to: ADR 0027 (one museum), 0028 (live exploration, amendment 2); research programme
  ("How results reach the museum"); foundation document, languages

## Context

The research room (`/research`, ADR 0028 amendment 2) is one long page: the live exploration
of the corpus (seven chapters), then six dated notes listed by hand in `reports.ts` and folded
in `<details>`. The owner asked to organise it so that every study can be added. The
programme foresees dozens: Layer 1 extractors with their precision, Layer 2 descriptions, the
workstreams W1–W7, spikes, negative results. One page does not scale, a hand-written import
list forgets studies (`archives.md` is already missing), and the folded notes have no title or
summary in French, though everything a visitor reads is localised.

## Decision

1. **One registry, `research/studies.json`** (CC0 data), lists every public study: `id` (the
   page's address), `date`, `kind` (`exploration` live, `study` dated note, `trial` spike,
   `programme`), `strand` (the research programme's place: `programme`, `linkage`,
   `description`, `W1`–`W7`, `museum`), `status` (`exploratory`, `preregistered`,
   `confirmed`, `refuted`, `ongoing`), `dataset` (name and version, or `live`), `leads` (ids
   of `docs/leads.md`), `title` and `summary` in every required locale, `source` (a Markdown
   file in the repository, or `live:corpus` for the live exploration) and `language` (of the
   source). Adding a study is adding an entry; a unit test checks the registry (unique ids,
   known kinds, strands and statuses, every required locale, every source present).
2. **`/research` is an index**: the programme first, then every study as a card (date, kind,
   status, strand, dataset, title, summary), newest first, filterable by strand with the
   filter in the address (`?strand=linkage`). The strands come from the programme, so the
   room shows its gaps: a strand with no study yet says so.
3. **`/research/<id>` is one page per study**: its header (kind, status, strand, dataset,
   date, leads), then the source Markdown (with the original-language note when it differs
   from the visitor's), or the live exploration for `live:corpus`. The live exploration moves
   to `/research/corpus`; `/research#corpus` sends there. Pages are prerendered from the
   registry, once per locale, and load their Markdown lazily.
4. **What is not public stays out**: the registry lists what may be read by visitors. Field
   notes, the lexicon report (it quotes works) and private datasets are not registered.

## Consequences

- Each new study needs a title and a summary in English and French, written when it is
  registered; its body may stay in its original language, as now.
- The room grows without code changes; a new kind of live study (a component, not Markdown)
  needs a new `live:` source and its component.
- Amends ADR 0028 amendment 2: the exploration's address is `/research/corpus`.

## Alternatives

- **Keep one page with sections**: no code, but it grows without bound and cannot be linked
  study by study.
- **A content collection framework (mdsvex, a CMS)**: more features than needed; Markdown is
  already rendered by `Markdown.svelte`.
- **Registry in YAML**: friendlier to edit, but the site would need a parser; JSON is read by
  the site and by Python without dependencies.
