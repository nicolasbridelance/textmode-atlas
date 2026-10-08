<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Leads

Every question, hypothesis, idea and curiosity the work raises, written when it comes, even when
it would lead too far. Nothing here is a result. A lead that is taken up moves to the roadmap,
a study (`research/NNNN-name/`, pre-registered when confirmatory), an ADR or a field note, and
its line here says where it went.

Rules:

- One line or a short paragraph each, with an id that never changes (`Q12`, `H3`, `I40`, `C7`).
- Say where it came from (a note, a work, a query) and what would answer it.
- Status: **open**, **taken** (and where), **answered** (and where), **dropped** (and why).
- Questions about the scene and hypotheses are tested on the test packs only when confirmatory
  ([research program](research-program.md), rules 2–3); exploring them on the train packs is
  fine and labelled exploratory.

## Questions about the scene and the corpus

| Id | Question | From | What would answer it | Status |
| --- | --- | --- | --- | --- |
| Q1 | Which editor writes `ESC[?7h` (line wrap on) in 15% of the ANSI of 1994–99? | works note, byte scan | byte habits of files whose tool is known (SAUCE comments, NFO, tool release dates) | open |
| Q2 | Is the fall of shades and the rise of punctuation (1994 → 2004) one shift in style, or text-heavy files (NFO-like ANSI, ASCII in ANSI) growing in the packs? | works note | the same measure by content kind (I1), and within artists over time | answered for exploration: composition; within coloured block art shades stay 22–28% (works note) |
| Q3 | Why does the median height double after 2005? The end of the 25-line BBS screen as reading frame, web viewers, or a change in what packs hold? | works note | heights by content kind and by pack type; scroll works vs logos | open |
| Q4 | What are the 5.8% of ANSI of 1990–93 written out of reading order: animations, BBS menus, editors that saved by blocks? | works note | contact sheet sorted by draw order; overwrite counts (I3) | open |
| Q5 | Are the 2005–12 years thin because the scene was, or because 16colo holds less of them? | catalogue, works note | other archives (Demozoo, textfiles.com) for the same years; `lost_item` | open |
| Q6 | Do groups have house palettes or house glyph habits that outlive their members? | explorer | features by group against by artist, over time | open |
| Q7 | Which files travel most between packs (`packs` > 1): intros, ads, logos, member lists? | works dataset | the shared files, by content and position in the pack | open |
| Q8 | Did artists save bytes for slow modems (cursor-forward `ESC[nC` instead of spaces, minimal SGR), and did the habit fade with faster connections? | byte scan | bytes per visible cell and compression habits by year (H1) | open |
| Q9 | What were the first 25 rows for? Do one-screen works centre their composition in the 80×25 frame, and do long scrolls open with a title screen? | works note | centre of mass and fill of the first screen against the rest | open |
| Q10 | Which languages are written inside the works (English, Portuguese, Spanish, German, Finnish…)? A geography of the scene from its texts. | explorer | text runs extracted from grids (I2), language detection, by group | open |
| Q11 | Why are some ANSI files named `.JPG` or `.GIF` (about 660 and 500 in the train packs)? A BBS file-list habit, a disguise, a joke? | works dataset | the packs and NFOs around them, years, groups | open |
| Q12 | How often do artists sign inside the drawing (`rs^mdn`), and can the in-grid signature credit works with no SAUCE author? | explorer (cenobite logos) | text runs near borders, matched to known handles | open |
| Q13 | Who or what was "iLL", whose `-EnCrYptEd by iLL` overflows the SAUCE records of four groups in 1995–97? | field notes | NFOs and member lists of cnc, Damage, taura, Polyester | open |
| Q14 | Which tool wrote `READ THE INI FILE` as a default group? | catalogue | WiCKED packs' NFOs, tool archives | open |
| Q15 | How was colour shading built: are there shared ramps (black → dark grey → grey → white, blue → cyan → white) that mark schools? | explorer | colour transitions along rows (I5) | open |
| Q16 | How much of each pack is art, and how does that change (art packs → NFO and intro packs)? | catalogue | content kinds per pack over time | open |
| Q17 | When did the SAUCE font field (80×50, Amiga Topaz, others) start to be used, and by whom? | catalogue | `sauce_font` by year and group | open |
| Q18 | Is the scene's iCE turn (after 2013) one tool (PabloDraw's default?) or a choice of artists? | works note | iCE flag and blink use by tool fingerprint and group | open |
| Q19 | Are the empty and near-empty works (fill near 0) blank pages, file-list art, or decoding faults? | works dataset | contact sheet of the least filled works | open |
| Q21 | Is 1996 the peak of the scene, or of 16colo? The archive holds what was submitted to it, and its submitters may favour the years they lived. | owner, works note | artpacks by year in other sources (Demozoo has 1,519 artpacks, type 51; its API ignores date filters and blocks the codespace, so a paging script from elsewhere or a dump is needed), textfiles.com, Defacto2; capture–recapture (R2), knowing that Demozoo imported part of 16colo, so the sources are not independent | open |
| Q22 | What is the colourless block art of 2000–04, as common then as coloured block art (2,419 against 2,536)? A style (block ASCII), a medium (IRC, web, e-mail without colour codes), or one prolific group? | works note | contact sheet of `blocks` 2000–04, by group and pack; first look (explorer, 2002): `.asc` files drawn in grey blocks (BAFH, sac, spr, mfn), most with no SAUCE author, so a style rather than a fault | open |
| Q23 | Simpson's traps elsewhere: which other trends over time are mixtures of content kinds, packs or groups changing weight? | works note (Q2) | every trend shown by content kind and with pack and group weights | open |
| Q20 | How alike are the works of one pack? Do packs have a house style, a template header or footer? | explorer | within-pack distances against between-pack | open |

## Hypotheses (to pre-register before a confirmatory test)

| Id | Hypothesis | Measure | Null model | Status |
| --- | --- | --- | --- | --- |
| H1 | Byte economy declines over time: files spend more bytes per visible cell as connections get faster. | bytes per ink cell; share of cursor-forward runs | permuted years within groups | open |
| H2 | The fall of shades from 1994 to 2004 happens within artists, not only by new artists replacing old ones. | shade share per artist over years | shuffled years within artists | open |
| H3 | Features v1 carry an author signal: nearest neighbours share the author more often than the same group, year and content kind would predict. | same-author rate among 12 nearest | neighbours drawn within group × year | explored (train): weak, 2.3% against 0.6% by chance and 14.2% knowing the group (works note); to retest with richer features |
| H4 | Formal novelties follow tool releases (rule 6): a new habit (wide canvas, iCE, 24-bit colour) appears in the packs after the editor that makes it easy. | first appearance and adoption curves | release dates shifted at random | open |
| H5 | Animation-like files peak in the mid-nineties and fall with the end of the BBS. | share of works over 20 bytes per cell | permuted years | open |
| H6 | One-screen works compose for the 80×25 frame: their ink is centred and their fill higher than the first screen of long scrolls. | centre of mass, fill of rows 0–24 | same rows of scrolls | open |
| H8 | The golden age is real: across independent sources, artpacks per year peak in the mid-nineties, not only in 16colo. | artpacks per year in each source, overlap-corrected | each source's own curve, resampled | open |
| H7 | Groups keep a house palette: colour histograms are closer within a group than between groups of the same years. | distance of `fg_hist`/`bg_hist` | group labels permuted within year | open |

## Ideas (tools, measures, museum)

| Id | Idea | Why | Status |
| --- | --- | --- | --- |
| I1 | Content kind of each work: escape sequences or not, colours, block share; plain text art, coloured text art, colourless block art, ANSI | the extension does not say it (works note, constraint 1) | done: `works` v2, `content_kind` |
| I2 | Extract text runs from grids (letters and punctuation in rows) | search inside works, signatures (Q12), greetings, languages (Q10) | taken: `tm_analysis.text`, explorer detail; next, corpus-wide with a search index. Short tags (`rs!`, two letters) escape the three-character word rule |
| I3 | Decoder counts overwritten cells; keep frames of animations | the grid is not the work for animations (constraint 3) | taken (roadmap step 5) |
| I4 | Lettering fingerprints: glyph n-grams of logos, to find shared or copied letterforms | diffusion and borrowing (W4, W5) | open |
| I5 | Colour ramps: the sequences of colours along rows and down columns | shading schools (Q15), house palettes (H7) | open |
| I6 | "Time to arrive": bytes / (baud / 10) at 2400 and 14400 baud, on each record | a cartel fact for visitors; also a measure of byte economy | taken: explorer detail; the museum record later |
| I7 | Tool fingerprints from byte habits (SGR order, `ESC[?7h`, cursor-forward, line ends, SAUCE quirks) | dating by tool (rule 6), Q1, Q14, Q18 | open |
| I8 | Explorer: filters by group and author, pack view in archive order (with drawn listings), side-by-side comparison | looking together | open |
| I9 | Explorer: byte-stream playback at modem speed, zoom to the cell, the grid's text layer | see animations and drawing order (Q4) | open |
| I10 | Explorer: local annotations on a work, exported as a list to feed field notes and leads | turn looking into notes | open |
| I11 | Explorer: a clickable map (UMAP or PCA) of the works, coloured by year, group or content kind | see schools and outliers | open |
| I12 | Pack-level features: house style, template detection, art share | Q16, Q20 | open |
| I13 | ASCII font hint: pure 7-bit text with no CP437 upper half may be Amiga art drawn for Topaz | render it with the right font (works note, cautions) | open |
| I14 | Weight measures by area as well as by work, and show both | a one-line logo weighs like a 300-row scroll (works note, cautions) | open |
| I15 | First-screen features beside whole-work features | what a BBS reader saw first (Q9, H6) | open |
| I16 | Data stories for the museum: "Eight backgrounds", "ASCII was coloured", "A screen at 2400 baud", "Widths that were not widths" | field notes become visitor stories | open |
| I17 | Distances between works on the grid itself (cell-level edit distance on aligned grids) to find versions, edits and recolours of one work | versions of a work across packs | open |
| I20 | Resolve SAUCE author strings into handles (case, spacing, aliases, typos) before any author statistic | H3 counted lower-cased strings | open |
| I21 | An "author signal" benchmark: same-author rate among nearest works from other packs, against random and group baselines, rerun for every new representation | H3 gives a first number to beat | open |
| I19 | D1 sampling design: strata bounded by the mass, equal (or square-root) allocation per stratum so that thin years are over-represented, and each pack's inclusion weight recorded so that statistics can be reweighted to the corpus | owner: over-represent thin years | taken (roadmap step 6) |
| I18 | Detect the artist's handle in NFO and in-grid text and link it to SAUCE authors, with confidence | linkage R1 | open |

## Curiosities

| Id | Curiosity | From | Status |
| --- | --- | --- | --- |
| C1 | The earliest, longest, widest, most colourful, least filled works of 16colo: a cabinet of extremes | explorer sorts | open |
| C2 | The 64 KB cut download (`1994/itr-9401.zip`): what was the last file, the one lost? | field notes | open |
| C3 | Packs whose archive listing is a drawing (`TOTAL CHAOS`, 1993): how many groups did it, and did it spread? | field notes | open |
| C4 | Ninety-two archives are copies under another name: who renamed them, and when? | field notes | open |
| C5 | A `.ANS` of 1996 with 605 rows of grey line drawing (`02-STEPS.ANS`, swap07): line art in ANSI, how common? | explorer | open |
