<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0028. A live exploration of the database: written readings, re-checked on every refresh

- Status: Accepted
- Date: 2026-10-10
- Deciders: Claude (autonomous mode, ADR 0008), at the owner's request (leads I73); Nicolas
  Bridelance reviews afterwards
- Relates to: ADR 0016 (features in the database), 0018 (split), 0020 (audience grid),
  0027 (one museum); research programme rules 1, 3, 4; invariants 5, 6, 10

## Context

The owner asked for an exploratory data analysis of the corpus in the museum, read from the
live PostgreSQL database rather than from frozen datasets, so that the page is current as the
pipeline runs. He also asked that it not be a dashboard of counts chosen in advance: an
exploration goes back and forth, reads a figure, makes a hypothesis, checks it with a number
and a null model, and says what it changes. It should teach how this is done.

Until now the museum host read only frozen datasets (`works` v6, `graph` v2) and the policy
rows of PostgreSQL. Research reads datasets, never the production database (research
programme), because a dataset is frozen and reproducible. Exploration reads the `train` packs
only (rule 3), so that what it suggests can still be tested on packs nobody has looked at.
The aggregate queries the exploration needs run in under a second each on the full database,
except those that read features through the `work_split` view (about 15 seconds).

## Decision

1. **An exploration is a sequence of chapters, each with written readings and live checks.**
   A chapter asks a question, shows figures computed from the database, and gives readings
   written by a person or a model on a stated date. Each reading names the check that supports
   it: a comparison, a threshold, or an observed value against a permutation null. Every
   refresh recomputes the numbers and the checks. When a check no longer holds, the page says
   so beside the reading instead of hiding it: the text is a dated interpretation, the number
   is current, and the visitor sees when they disagree.
2. **Code in `tm.eda`, served by the museum host.** The queries, the statistics (permutation
   tests with a fixed seed, decomposition of a change into composition and within-kind parts)
   and the checks are a library module with tests on the test database. The host calls it at
   `/api/eda`; `tm eda` prints the same snapshot as JSON. The readings' text is localized in
   the site's messages, with the numbers as parameters.
3. **Refresh by fingerprint.** The host keeps the last snapshot. Every 30 seconds it reads a
   cheap fingerprint of the database (row counts and latest timestamps of the pipeline's
   tables); when it changed, it recomputes the snapshot in a background thread. The page asks
   every 30 seconds and shows when its numbers were computed and from which fingerprint.
4. **What the page may read.** Catalogue metadata (formats, years, packs, SAUCE fields,
   decoding outcomes) is read over every pack, as the catalogue exploration already did.
   Anything measured on grids (features, heights, colours) is read from `train` packs only.
   Works the policy shows nothing of (withdrawn, `withheld`; `tm.access`) are left out of
   every count. The page shows aggregates and pack-name prefixes, never a work, a file, or a
   handle; it links to the collection for that.
5. **It is not a result.** The page is labelled exploratory. A reading becomes a result only
   through a pre-registered test on the `test` packs (research programme, rule 2), which this
   page never reads for grid measures.

## Alternatives considered

- **A dashboard of fixed counts.** Rejected by the owner: it shows the corpus without
  thinking about it, and teaches nothing about how a finding is made.
- **Readings generated on each refresh.** No model call on page load (ADR 0027), and a
  generated text cannot be reviewed before visitors read it. Dated written readings with
  live checks keep text and numbers honest separately.
- **A frozen dataset rebuilt on a schedule.** Reproducible, but not live; the frozen datasets
  stay as they are for research, and the page says it reads the live database.
- **FastAPI in `api/` now.** The museum host is the live API today (ADR 0027); moving it is a
  separate decision. `tm.eda` takes a connection, so it moves with the host.

## Consequences

- The museum has a room that changes as the pipeline runs, and says when a reading written
  earlier has stopped matching the data. Readings must be reviewed when that happens.
- Feature chapters cost a scan of the features table on each refresh; the fingerprint keeps
  that to when the database changed. Faster split lookups (a materialized split) can come
  later if needed.
- The static public build cannot show this room without the host: it says so.
- A new chapter is a function returning figures and checks, plus its messages in every
  required locale.

## Amendment 1 (2026-10-10): a published snapshot for the static site

The owner asked for the charts on the website, which has no live host (the host and domain
are still to be chosen). `tm eda --publish` writes the snapshot to the public bucket at
`eda/snapshot.json`, beside what `tm export` publishes; the page reads the live host first and
falls back to that file, and then says it shows a published snapshot, with its date, not live
data. The snapshot holds only what the page draws: aggregates, pack-name prefixes, and checks,
computed with hidden works left out, grid measures from train packs only. Publishing train
aggregates does not open the test packs. Run it after `tm export`, like `tm lists`.

## Amendment 2 (2026-10-10): one research room

At the owner's request, the exploration is no longer a room of its own: it is the first part
of the research room (`/research`), above the dated studies, so that the museum has one place
for research and one header link. The chapters, checks and data sources are unchanged; the
exploration's address is `/research#corpus`.
