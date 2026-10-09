<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0020. The museum's audience grid, adapted from PEGI, from one source to every layer

- Status: Accepted
- Date: 2026-10-09
- Deciders: Nicolas Bridelance (owner: "on écrit la grille, noir sur blanc, voire en couleur avec
  logos, et on diffuse, du README jusque dans les bases de données. C'est prioritaire");
  written by Claude
- Takes from: ADR 0019 (proposed), whose descriptors and classes this grid replaces; 0019 keeps
  the questions of rooms, age checks and the law

## Context

The corpus holds works that are not for every audience: by a rough count, thousands with
sexual, violent, drug, hate or warez content (ADR 0019). The museum needs one written answer
to the question "what may be shown to whom". Everyone must be able to read it, and every layer
must apply it the same way: the README, the site, the exports, the database.

PEGI rates games, so it does not apply to us. But it records a European consensus on what is
acceptable for protected audiences, and that consensus is what we need. Its marks belong to
PEGI, so we neither use them nor imitate them.

## Decision

1. **The grid** is [corpus/ratings/grid.yaml](../../corpus/ratings/grid.yaml), version 1:
   - **five ages, PEGI's**: 3, 7, 12, 16, 18;
   - **a sixth level, `withheld`**: never shown nor exported;
   - **eight descriptors**: violence, fear, sex and nudity, language, drugs, discrimination,
     crime, real people. Each one states, in our words and in English and French, which degree
     calls for which level;
   - **one notice**, flashing, which is not about age;
   - **six rules**, the first being that a work's level is the highest among its descriptors.

   Two descriptors are ours and not PEGI's: crime (the warez scene, how-tos, stolen data) and
   real people (caricature, degradation, sexualisation of identifiable persons, sceners
   included), because the scene's works call for them.
2. **One source, derived everywhere.** `tm corpus ratings` writes from the grid:
   - its badges, drawn cell by cell in the VGA font and palette of the works
     (`corpus/ratings/badges/`);
   - its pages in English and French (`docs/audience-grid.md`, `docs/audience-grid.fr.md`).

   `tm corpus check` fails when a written file differs from what the grid gives, and a test
   fails when the database vocabularies differ from it.
3. **In the database** (migration 0010):
   - the vocabularies `audience_level`, `content_descriptor` and `descriptor_level`, which also
     list the degrees each descriptor has (language stops at 16);
   - the append-only table `content_rating`. A program infers a rating (`algo:`), a named
     reviewer reviews it (`human:`), the artist declares one (`identity:`). A rejection is a
     row with `present` false that supersedes the inferred one;
   - the view `work_audience`, which gives each file its level, descriptors, notices, and
     whether a rating is still unreviewed.
4. **Published from the README**, in both languages, with the badges.

## Consequences

- Changing the grid means changing `grid.yaml`, regenerating, and writing a migration for the
  vocabularies, in the same pull request; the version number rises when a level or a degree
  changes meaning.
- Nothing is rated yet. The next steps are a keyword pass that writes inferred ratings, a
  review queue in D2, and `audience()` beside `can_display()` in `tm export` and the API,
  following the rooms and the age check that ADR 0019 leaves to the owner and the lawyer.

## Amendment 1 (2026-10-09): rule 4 becomes a watched trial

The first wording of rule 4 counted every unreviewed work as 16, which leaves the rooms for
every audience empty until people have reviewed a corpus of 115,308 files. The owner accepted a
relaxation as a trial, "with watching that it is acceptable":

- **Rule (grid v2).** A work no one has reviewed is shown at its inferred level, and at 12 at
  the least. In particular, a work in which no program finds anything is shown up to 12, never
  lower. `audience()` (`tm.audience`, held at 100% branch coverage) applies it.
- **What we measure.** The escape rate: among works shown at 12 without review because no
  program found anything, the share that a person rates 16 or more. Drawn nudity without a word
  is the expected case.
- **How.** A random sample of those works, drawn with a fixed seed and stratified by era as D1
  is, reviewed by named people who do not see what the programs found. The reviews are written
  as `reviewed` ratings, so the sample also rates the works it reads.
- **Threshold.** The trial holds while the one-sided 95% upper bound (Clopper–Pearson) of the
  escape rate stays at or below **1%**. That means no escape in 299 reviewed works, at most one
  in 473, two in 628, or three in 773. Above that, the strict rule returns, or a second
  program (an image classifier, lead I46) has to filter first.
- **Hard stop.** One work in the sample that calls for `withheld`, or for 18 for sexual content,
  pauses the trial until the method is reviewed.
- **Visitors.** Requests to rate a work again are answered one by one. Their rate is followed
  per 10,000 works shown, but it is not the threshold: few visitors report. A cluster on one
  pack or group triggers an audit of that pack.
- **When.** Nothing is public yet. The first sample is reviewed before `tm export` publishes
  any work at 12 or below.
