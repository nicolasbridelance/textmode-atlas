<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0017. Draw the D1 pilot by era, three packs per stratum, systematically within it

- Status: Accepted
- Date: 2026-10-09
- Deciders: Claude (autonomous mode, ADR 0008), at the owner's request ("c'est aux données de
  parler"); Nicolas Bridelance reviews afterwards
- Amends: the research program, D1 ("20 packs"): 21 drawn packs, plus rare cases added by hand

## Context

D1 is the pilot dataset (research program, R0): a few packs taken through the whole pipeline,
read by hand, and annotated for the gold set D2 (credits, greetings, NFO text). Its first job is
to meet the diversity of the corpus, not to estimate its averages; but whatever is measured on
it should be reweightable to the corpus, and thin years should not vanish (owner, leads I19).

The frame is the 4,559 train packs of 16colo whose archive was read whole (dataset `catalogue`,
2026-10-09). Their mass is very uneven: 1,419 packs are filed under 1996–97 and 71 under
2005–12. The archives note (2026-10-09) found the peak in 1996–97 in three archives and the
fall beginning in 1998; the works note found that content kind, not extension, separates the
corpus (constraint 1), and that pack size grows after 2013 (90th percentile 137 files against
about 60 before).

## Decision

- **Strata: seven eras of filing year**, bounded by the mass: 1990–93 (249 packs), 1994–95
  (1,034), 1996–97 (1,419), 1998–99 (834), 2000–04 (644), 2005–12 (71), 2013–26 (309). The
  former 1998–2004 stratum is split where the counts halve (1999: 336, 2000: 162), so that the
  end of the peak and the decline are not averaged together.
- **Allocation: three packs per stratum, 21 in all.** Equal allocation gives every era the
  same precision, which is what comparisons between eras need, and over-represents thin eras:
  a 2005–12 pack stands for 24 packs, a 1996–97 pack for 473. Square-root allocation would have
  left 2005–12 a single pack.
- **Within a stratum: systematic sampling** from a random start, over the packs sorted by their
  dominant content kind, then by number of files (implicit stratification). The sample spreads
  over content and size without more strata, which 21 packs could not fill.
- **Seed 20261009**, and a start drawn per stratum from the seed and the stratum's name, so a
  change in one stratum does not redraw the others.
- **Weights.** Each drawn pack keeps its inclusion weight N/n; packs added by hand have no
  weight and a written reason, and are left out of any reweighted statistic.
- **Frozen.** `tm dataset draw d1` writes `datasets/d1/sample.yaml` (committed), with the SHA-256
  of the frame query; `tm dataset build d1` refuses to build if the frame query changed since.

## Consequences

- D1 has 21 drawn packs plus the added ones, not 20; the research program is amended.
- Estimates from D1 are design-weighted, with seven strata of three: variances are large, and
  D1 is not for estimating anything precisely. It is for building and checking the instruments.
- Datasets gain a `sample` section, `same_as` tables (another dataset's query, key and columns,
  with a filter) and `x-` keys for YAML anchors.

## Alternatives considered

- **Proportional allocation**: 1996–97 would take six packs, 2005–12 none. Rejected: the owner
  asked for thin years, and eras could not be compared.
- **Two-way strata (era × content kind)**: 28 cells for 21 packs. Rejected for implicit
  stratification by sorting.
- **Strata by group or by pack size**: groups are not resolved yet (I20); size is used for
  ordering instead.
- **Simple random sample of 20 packs**: about 6 from 1996–97 and none from 2005–12 in most
  draws.
