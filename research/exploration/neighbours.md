<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# The nearest-works graph, read as a social network

Roadmap step 12 (leads I48), exploratory: train packs only, leads rather than results. Graph
build 1 (`just graph`, [build.py](../graph/build.py)): each of the 84,110 measured works of
`works` v5 points to its 10 nearest works by `tm_analysis.neighbours` v1. The profile has 15
measures of features v1 and the 16 foreground colour shares, standardized, with a Euclidean
distance. Communities come from Leiden (modularity, seed 20261009) on the graph without
directions; the layout comes from UMAP on the same neighbours. Notebook:
[neighbours.py](neighbours.py). Built 2026-10-09.

## Shape: a single continent, no stars

| Measure | Value |
| --- | ---: |
| works, edges | 84,110, 841,100 |
| mutual edges (reciprocity) | 47.1% |
| works nobody has as a neighbour | 2.3% |
| largest in-degree (times a work is someone's neighbour) | 125 |
| share of in-edges held by the top 1% | 3.9% |
| connected components | 1 |
| transitivity | 0.213 |
| communities, modularity | 33, 0.806 |

A social network of people has stars: a few accounts hold most of the followers. This graph has
none. The top 1% of works hold 3.9% of the in-edges, barely four times their share. The most
"central" works are not famous works. They are typical works of the mass: coloured block art of
1996 (`opx-0996`, `ane-0296`, `blend02`, `ciapak33`), where the corpus is densest. Centrality
here measures typicality, not influence, and must never be shown as importance.

## Homophily: what neighbours share

For each attribute: how often an edge joins two works with the same value, against chance
(picking the target at random among works whose value is known). The last column compares
instead with chance within the source's content kind and five-year era, which removes what
technique and period alone explain.

| Attribute | Edges with both known | Same | Chance | Lift | Lift within kind and era |
| --- | ---: | ---: | ---: | ---: | ---: |
| content kind | 841,100 | 95.4% | 41.5% | 2.3 | – |
| five-year era | 841,100 | 53.7% | 41.6% | 1.3 | – |
| year | 841,100 | 18.2% | 10.1% | 1.8 | 0.7 |
| group (SAUCE) | 275,227 | 5.4% | 0.66% | 8.1 | 1.8 |
| author (SAUCE) | 298,872 | 4.3% | 0.10% | 45.0 | 6.7 |
| pack | 841,100 | 2.3% | 0.05% | 48.3 | 2.4 |
| country (Demozoo, inferred) | 19,088 | 38.0% | 25.5% | 1.5 | 1.3 |
| same grid (byte variants) | 841,100 | 0.5% | 0.00% | 333 | 4.9 |

Readings, all to be tested on the test packs before they are claimed:

1. **Technique first.** 95% of edges stay within a content kind, and the communities are kinds
   cut into palettes and textures (below). Features v1 mostly measure which glyph classes and
   which colours a work uses, so this is partly what the instrument can see.
2. **The artist survives the controls; the group signal is weak.** Within the same kind and
   era, neighbours share an author 6.7 times more often than chance. They share a group 1.8
   times more often, and a pack 2.4 times. A hand is visible in these crude measures; a group's
   "house style" is a weak signal under features v1, which is not evidence that groups had
   none. Homophily is not classification accuracy either: whether a work's author or group can
   be predicted needs its own test on held-out packs, with duplicate grids controlled. This
   matches H3 explored in works.md (2.3% same author among nearest works, 0.6% by chance) and is
   the baseline any style representation has to beat (I21).
3. **Within an era, the year adds nothing.** Neighbours share their exact year less often than
   two works of the same kind and five-year era picked at random (lift 0.7). Change over time,
   as these features see it, is slow; the eras of works.md are the right grain.
4. **Countries barely cluster.** Matching SAUCE groups to Demozoo groups and taking the country
   of most members gives a country for 11,191 works (13%). Lift 1.3 within kind and era: the
   art of the 1990s, as measured here, does not divide by country. US groups dominate every
   community. The match is crude (same name, different groups), so this is a weak lead.

## The communities

| # | Works | Years (quartiles) | Main kind | Most frequent groups | Most central work's pack |
| ---: | ---: | --- | --- | --- | --- |
| 0 | 13,059 | 1996–1998–2000 | text 94% | remorse, wicked, acid productions | kwest-ho |
| 1 | 8,647 | 1996–1997–1999 | coloured text 97% | wicked, blade productions, read the ini file | mist0996 |
| 2 | 8,445 | 1995–1996–1998 | coloured blocks 99% | fuel, fire, cia | int-0295 |
| 3 | 8,335 | 1994–1996–1997 | coloured blocks 99% | cia, mistigris, fire | fire0996 |
| 4 | 7,524 | 1995–1996–1998 | coloured blocks 100% | mistigris, cia, fire | opx-0996 |
| 5 | 6,840 | 1994–1996–1998 | coloured blocks 98% | mistigris, cia, blocktronics | tst-july |
| 6 | 4,593 | 1995–1996–1998 | coloured blocks 99% | cia, mistigris, fire | danone003 |
| 7 | 4,348 | 1999–2001–2004 | blocks 94% | mistigris, acid productions, thelo0p | cro1204 |
| 8 | 4,083 | 1995–1996–1998 | coloured blocks 96% | cia, mistigris, blocktronics | tea-003 |
| 9 | 3,004 | 1994–1996–1998 | coloured blocks 99% | mistigris, blocktronics, cia | lgc-0493 |

The text art (0) and the coloured text (1) are islands of their own. Coloured block art splits
into many communities with the same groups and the same years: palettes and textures, not
schools. One community stands out by period: **7**, monochrome block art of 1999–2004, the time
when ANSI groups turned to ASCII and "blocky" one-colour work (works.md, era 2000–04). It is the
only community whose quartiles miss 1996.

## Archetypes and variability

`research/graph/communities.py` (run by `just graph`) describes each community in the same
profile space. Its archetype is the work nearest the community's centre, followed by the four
next most typical works. Its spread is the mean distance of its works to the centre (corpus:
5.0). Its main axis of variation is the first principal component inside it, with works at both
ends (2nd and 98th percentiles). Its name is computed from the measures where it stands furthest
from the corpus and is signed `algo:graph-communities@1` (invariant 8): a description until a
person names it. The cards are in the graph explorer (`just explore`, then "constellation").

What they show:

- **The coloured block art sorts by hue.** Communities 2, 3, 4, 6, 8, 9 and 10 are reds,
  blues, greens, magentas, cyans, yellows and browns. Inside each, the main axis opposes the dark
  and the bright version of the same hue (12–29% of the variation): the shading ramp an artist
  chose. Groups and years are spread across all of them.
- **Text art varies by density, not by colour.** Community 0 (text, 13,059 works) varies from
  "many glyphs, letters, weight high" to "few glyphs, no letters": from text-heavy NFO-like
  screens to sparse line drawings.
- **Tight small communities are genres of utility.** Spread near 0: 52 one-line separators
  (`──ZIP──`, `──ANS──`) made for BBS file lists, one pack's house template (`ztart01`), and
  the info files of a monthly pack (`IMPURE34.INF` to `IMPURE44.INF`) (field notes).
- **The loosest communities are mixed bags**, kept together by one strong trait: bright
  backgrounds (17, spread 10.0), drawing strictly line by line (19, 8.8). They are the first to split
  with better features.

## What to project next

- **The greets graph (I23) on this one:** do groups that greet each other draw closer in style
  than groups that do not (Q37)? That would be the first link between the social network the
  scene wrote down and the one its works form.
- **Time as a front:** colour by year and play the years in the graph explorer (step 13). If a
  technique spreads, a colour should travel across a community.
- **Better features:** the same table for each new representation (W1). Lift within kind and
  era is the number to beat.

## Cautions

- Communities are visual similarity under one representation: never schools, nations or
  attributions.
- Train packs only, one representation, one k, one seed. Leiden and UMAP are stochastic; the
  seeds make this run reproducible, not the partition true.
- The same artwork saved twice with other bytes counts twice (I40): 0.5% of edges join two
  files with the same grid, which inflates author and pack lifts a little.
- SAUCE authors and groups are as signed. Spelling varies (`acid`, `acid productions`), which
  lowers the group and author lifts.
- Countries come from Demozoo members' locations, aggregated to groups and kept in the notebook.
  They are never attached to a person, and never leave our machines.
