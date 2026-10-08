<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 16colo works: first look at the grids

Roadmap step 5, exploratory: what the decoded grids of the **train** packs show, measured by
feature extractor v1. Leads, not results; each one is to be tested later on the test packs,
which nobody has examined. Notebook: [works.py](works.py); explorer:
[../explorer/](../explorer/) (`just explore`). Dataset `works` v3 (migration 0007, decoder
`tm_render.ansi@4`, features 1), built 2026-10-08: 88,951 art files, 84,382 measured grids.
Counts were redone on v3 after decoder 4 set aside about 2,000 pictures, programs and modules
that a SAUCE record called ANSI (field notes); earlier drafts counted them as text and as
animations.

Eras are groups of 16colo's filing years, chosen to keep each one large enough to read; they are
not periods of the scene.

## ANSI over time

| Era | ANSI works | block | half block | shade | box | letters | punctuation | median rows | median colours |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1990–93 | 5,447 | 28.0% | 28.3% | 22.9% | 6.6% | 10.4% | 2.5% | 29 | 9 |
| 1994–95 | 16,924 | 25.5% | 25.9% | 24.6% | 3.1% | 12.8% | 6.6% | 34 | 8 |
| 1996–97 | 20,098 | 23.7% | 26.8% | 19.2% | 1.4% | 14.3% | 13.1% | 27 | 9 |
| 1998–99 | 7,081 | 23.5% | 26.9% | 18.4% | 1.9% | 13.5% | 13.6% | 26 | 9 |
| 2000–04 | 3,993 | 21.5% | 21.3% | 15.0% | 3.6% | 12.7% | 23.2% | 29 | 9 |
| 2005–12 | 535 | 30.8% | 28.4% | 17.9% | 1.4% | 7.5% | 13.2% | 60 | 12 |
| 2013–26 | 6,932 | 28.4% | 21.8% | 18.4% | 2.0% | 11.7% | 14.9% | 50 | 9 |

Glyph classes are mean shares of the visible glyphs of each work (ADR 0016).

- **Shades seem to recede, punctuation to rise, but the packs changed, not the drawing.** Over
  all ANSI files, shades (░▒▓) fall from about a quarter of the glyphs in 1994–95 to 15% in
  2000–04, and punctuation grows from 2.5% to 23%. Within coloured block art alone (content
  kind, below), shades stay between 22% and 28% in every era and punctuation under 3.5%: the
  shift came from text files, coloured or not, filling a growing share of the packs (Q2,
  answered for exploration). Within block art, full blocks gain after 2000 (29% → 37%).
- **One screen, then scrolls.** Until 2004 the median work is about one screen high (26–34
  rows), with a tail of long scrolls (90th percentile 123–150 rows). From 2005 the median doubles
  (50–60 rows).
- **Wider than 80 columns** is a recent habit: 0.6% of ANSI in 2000–04, 8.2% since 2013. These
  are the works whose SAUCE record is coherent (ADR 0015).
- **Animation belongs to the early years.** Decoder 3 counts how the bytes drew: a work is
  taken as animated when a tenth of its writes or more fall on cells already written, or when
  it clears the screen twice or more (exploratory rule; one clear is the usual header). 98.5% of
  works rewrite less than 1% of their cells. Animated ANSI are 7.2% of 1990–93, 1.2% of
  1994–95, then 0.2–0.4% (Q4, H5: the peak is earlier than supposed). Earlier drafts used bytes
  per cell and found 3% in 1994–99: most of those were pictures stamped as ANSI.
- **Typed, not drawn.** In byte order, almost every ANSI after 1993 writes its cells in reading
  order (draw order ≥ 0.9 for 99%). In 1990–93, 5.8% do not, and about half of the animated
  works do not: out-of-order writing is mostly animation.

## What the files hold

Content kind is read from the grid (`works` v2): **blocks** when a quarter of the visible glyphs
or more are █▄▀▌▐░▒▓ (the share is bimodal, with its trough between 10% and 35%), **coloured**
when the work uses more than two colours.

| Era | coloured blocks | blocks | coloured text | text |
| --- | ---: | ---: | ---: | ---: |
| 1990–93 | 5,116 | 32 | 298 | 30 |
| 1994–95 | 14,844 | 277 | 2,158 | 2,728 |
| 1996–97 | 16,317 | 640 | 5,671 | 5,730 |
| 1998–99 | 5,486 | 466 | 2,196 | 3,283 |
| 2000–04 | 2,536 | 2,419 | 1,498 | 3,746 |
| 2005–12 | 439 | 429 | 91 | 284 |
| 2013–26 | 5,040 | 474 | 1,235 | 858 |

Files named ANSI are 81% coloured block art, 14% coloured text and 3% plain text; files named
ASCII are 63% text, 19% coloured text and 18% colourless block art. In 2000–04, colourless
block art is as common as coloured block art (Q22).

## Bright backgrounds were rare, not unrecorded

The catalogue exploration found the SAUCE iCE flag almost never set before 1998, and asked
whether iCE colours were rare or whether editors did not write the flag. In the grids, the
attribute that iCE draws as a bright background (the blink bit, under ink) is just as rare:

| Era | blink bit used | over 5% of ink | SAUCE says iCE |
| --- | ---: | ---: | ---: |
| 1990–93 | 6.0% | 1.5% | 0.0% |
| 1994–95 | 1.1% | 0.2% | 0.2% |
| 1996–97 | 2.3% | 0.2% | 0.0% |
| 1998–99 | 2.2% | 0.1% | 2.8% |
| 2000–04 | 3.6% | 0.6% | 7.0% |
| 2005–12 | 6.9% | 0.9% | 3.0% |
| 2013–26 | 22.2% | 10.6% | 32.8% |

To exclude a decoder blind spot, the raw bytes of 3,000 ANSI of 1994–99 (fixed sample) were
searched for the other ways to ask for a bright background: no `ESC[100–107m`, no
`ESC[?33h`; `ESC[5m` appears in 2.1% of the files, as in the grids. So the lead is the first
answer: **artists of the nineties drew with eight backgrounds**, and the sixteen came later.

`ESC[?7h` (line wrap on) appears in 15% of the same files: perhaps one editor's habit, a lead
for dating by tool (research program, rule 6).

## "ASCII" by extension is not ASCII by content

In 1994–99, 32% of the `.ASC` files of a fixed sample of 600 contain ANSI escape sequences, and
27% are drawn in more than two colours. From 2000, files filed as ASCII are about a third to a
half block characters (░▒▓█▄▀) with no colour. The format recorded from the extension mixes at
least three things: plain text art, coloured text art, and colourless block art.

## Do features v1 carry an author signal? (H3, exploratory)

Coloured block art with a SAUCE author: 31,127 works, 1,366 authors with five works or more.
For 2,000 of their works (fixed seed), the 12 nearest works by standardized features v1
(measures, foreground and background shares), **never from the same pack**, were compared with
12 works drawn at random:

| Among 12 works… | same author |
| --- | ---: |
| nearest by features, other packs | 2.3% |
| random, same year, other packs | 0.6% |
| random, same group and year, other packs | 14.2% |

Features v1 carry a signal (about four times chance), but a weak one: knowing the group says six
times more. 15% of the works have at least one work by their author among their 12 neighbours.
Workstream W1 should not start from these features alone: lettering (I4), colour ramps (I5) and
learned representations are needed. Author names are SAUCE strings, lower-cased, not resolved
identities (aliases and typos split one artist, shared defaults merge several).

## Constraints for the next steps

These change the roadmap's later steps, as rule 3 of the program requires before D1:

1. **Classify works by content, not extension.** Done in `works` v2 (content kind); every
   comparison by format, and the D1 strata, use it. The shade lead shows why: a composition
   effect looked like a change of style.
2. **D1 strata are bounded by the mass, and sampled against it.** Three quarters of the works
   are filed 1994–98, so strata by era are unequal in width (1990–93, 1994–95, 1996–97,
   1998–2004, 2005–12, 2013–26). Each stratum gets the same number of packs (or a square-root
   share), so that thin years are over-represented, and every pack keeps its inclusion weight
   for reweighting (leads I19). Whether 1996 is the scene's peak or 16colo's is open (Q21, H8).
3. **Animation needs the byte stream.** For about 700 works of the train packs (7% of the
   ANSI of 1990–93) the grid is not the work. The decoder counts overwrites (version 3); the
   work screen needs playback (spike 0002), and the features of those works are to be flagged,
   not compared as still images.
4. **The default rendering is right for most of the corpus.** Blink, not iCE, is the reading of
   nineties files; the iCE profile matters mostly after 2013.

## Cautions

- 16colo holds what was submitted to it; the eras are filing years, not release dates.
- Works shared with a test pack are left out (about a fifth); group intros and logos that
  travelled between packs are under-counted.
- Means of shares weigh a one-line logo like a 300-row scroll.
- The renderer fixes the font (IBM VGA); Amiga-style ASCII drawn for Topaz is not seen as its
  authors saw it.
