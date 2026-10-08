<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 16colo works: first look at the grids

Roadmap step 5, exploratory: what the decoded grids of the **train** packs show, measured by
feature extractor v1. Leads, not results; each one is to be tested later on the test packs,
which nobody has examined. Notebook: [works.py](works.py); explorer:
[../explorer/](../explorer/) (`just explore`). Dataset `works` v1 (migration 0006, decoder
`tm_render.ansi@2`, features 1), built 2026-10-08: 88,951 art files, 85,977 measured grids.

Eras are groups of 16colo's filing years, chosen to keep each one large enough to read; they are
not periods of the scene.

## ANSI over time

| Era | ANSI works | block | half block | shade | box | letters | punctuation | median rows | median colours |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1990–93 | 5,448 | 28.0% | 28.3% | 22.9% | 6.6% | 10.4% | 2.5% | 29 | 9 |
| 1994–95 | 17,516 | 24.6% | 25.1% | 23.8% | 3.3% | 13.8% | 6.7% | 30 | 8 |
| 1996–97 | 20,764 | 22.9% | 25.9% | 18.6% | 1.6% | 15.0% | 12.9% | 26 | 9 |
| 1998–99 | 7,341 | 22.7% | 26.0% | 17.8% | 2.1% | 14.3% | 13.3% | 26 | 9 |
| 2000–04 | 3,998 | 21.5% | 21.3% | 15.0% | 3.6% | 12.7% | 23.2% | 29 | 9 |
| 2005–12 | 535 | 30.8% | 28.4% | 17.9% | 1.4% | 7.5% | 13.2% | 60 | 12 |
| 2013–26 | 6,984 | 28.2% | 21.6% | 18.2% | 2.0% | 11.9% | 14.9% | 50 | 9 |

Glyph classes are mean shares of the visible glyphs of each work (ADR 0016).

- **Shades recede, punctuation rises.** Shades (░▒▓) fall from about a quarter of the glyphs in
  1994–95 to 15% in 2000–04; punctuation grows from 2.5% to 23%. Box drawing, already rare,
  halves after 1993. A lead for workstream W6 (ruptures): is it one shift, or several schools
  mixing in the packs?
- **One screen, then scrolls.** Until 2004 the median work is one screen high (26–30 rows),
  with a tail of long scrolls (90th percentile 124–148 rows). From 2005 the median doubles
  (50–60 rows).
- **Wider than 80 columns** is a recent habit: 0.6% of ANSI in 2000–04, 8.2% since 2013. These
  are the works whose SAUCE record is coherent (ADR 0015).
- **Typed, not drawn.** In byte order, almost every ANSI after 1993 writes its cells in reading
  order (draw order ≥ 0.9 for 99%). In 1990–93, 5.8% do not. A lead: early screens built with
  cursor movements (menus, animations), against later editors that save line by line.
- **Animation-like files.** About 3% of the ANSI of 1994–99 hold over 20 bytes of file per cell:
  the screen is redrawn, and the grid keeps only its last state.

## Bright backgrounds were rare, not unrecorded

The catalogue exploration found the SAUCE iCE flag almost never set before 1998, and asked
whether iCE colours were rare or whether editors did not write the flag. In the grids, the
attribute that iCE draws as a bright background (the blink bit, under ink) is just as rare:

| Era | blink bit used | over 5% of ink | SAUCE says iCE |
| --- | ---: | ---: | ---: |
| 1990–93 | 6.0% | 1.5% | 0.0% |
| 1994–95 | 1.1% | 0.2% | 0.2% |
| 1996–97 | 2.3% | 0.2% | 0.0% |
| 1998–99 | 2.1% | 0.1% | 2.7% |
| 2000–04 | 3.6% | 0.6% | 7.0% |
| 2005–12 | 6.9% | 0.9% | 3.0% |
| 2013–26 | 22.0% | 10.5% | 32.5% |

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

## Constraints for the next steps

These change the roadmap's later steps, as rule 3 of the program requires before D1:

1. **Classify works by content, not extension.** A content kind (escape sequences or not,
   colours, block share) is needed before any stratum or comparison by format. Feature
   extractor v2 or a catalogue column; D1 strata use it.
2. **D1 strata are bounded by the mass, and sampled against it.** Three quarters of the works
   are filed 1994–98, so strata by era are unequal in width (1990–93, 1994–95, 1996–97,
   1998–2004, 2005–12, 2013–26). Each stratum gets the same number of packs (or a square-root
   share), so that thin years are over-represented, and every pack keeps its inclusion weight
   for reweighting (leads I19). Whether 1996 is the scene's peak or 16colo's is open (Q21, H8).
3. **Animation needs the byte stream.** For about 3% of works the grid is not the work. The
   decoder should count overwritten cells, the work screen needs playback (spike 0002), and
   the features of those works should be flagged, not compared as still images.
4. **The default rendering is right for most of the corpus.** Blink, not iCE, is the reading of
   nineties files; the iCE profile matters mostly after 2013.

## Cautions

- 16colo holds what was submitted to it; the eras are filing years, not release dates.
- Works shared with a test pack are left out (about a fifth); group intros and logos that
  travelled between packs are under-counted.
- Means of shares weigh a one-line logo like a 300-row scroll.
- The renderer fixes the font (IBM VGA); Amiga-style ASCII drawn for Topaz is not seen as its
  authors saw it.
