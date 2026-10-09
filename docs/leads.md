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
| Q4 | What are the 5.8% of ANSI of 1990–93 written out of reading order: animations, BBS menus, editors that saved by blocks? | works note | contact sheet sorted by draw order; overwrite counts (I3) | answered for exploration: about half of the animated works are out of order, and animation is 7.2% of 1990–93 ANSI (works note) |
| Q5 | Are the 2005–12 years thin because the scene was, or because 16colo holds less of them? | catalogue, works note | other archives (Demozoo, textfiles.com) for the same years; `lost_item` | open |
| Q6 | Do groups have house palettes or house glyph habits that outlive their members? | explorer | features by group against by artist, over time | open |
| Q7 | Which files travel most between packs (`packs` > 1): intros, ads, logos, member lists? | works dataset | the shared files, by content and position in the pack | open |
| Q8 | Did artists save bytes for slow modems (cursor-forward `ESC[nC` instead of spaces, minimal SGR), and did the habit fade with faster connections? | byte scan | bytes per visible cell and compression habits by year (H1) | open |
| Q9 | What were the first 25 rows for? Do one-screen works centre their composition in the 80×25 frame, and do long scrolls open with a title screen? | works note | centre of mass and fill of the first screen against the rest | open |
| Q10 | Which languages are written inside the works (English, Portuguese, Spanish, German, Finnish…)? A geography of the scene from its texts. | explorer | text runs extracted from grids (I2), language detection, by group | open; first count: under 1% of ANSI per era by function words, English dominates (field notes, 2026-10-09); a language detector on the lines is next |
| Q11 | Why are some ANSI files named `.JPG` or `.GIF` (about 660 and 500 in the train packs)? A BBS file-list habit, a disguise, a joke? | works dataset | the packs and NFOs around them, years, groups | open |
| Q12 | How often do artists sign inside the drawing (`rs^mdn`), and can the in-grid signature credit works with no SAUCE author? | explorer (cenobite logos) | text runs near borders, matched to known handles | open |
| Q13 | Who or what was "iLL", whose `-EnCrYptEd by iLL` overflows the SAUCE records of four groups in 1995–97? | field notes | NFOs and member lists of cnc, Damage, taura, Polyester | open |
| Q14 | Which tool wrote `READ THE INI FILE` as a default group? | catalogue | WiCKED packs' NFOs, tool archives | open |
| Q15 | How was colour shading built: are there shared ramps (black → dark grey → grey → white, blue → cyan → white) that mark schools? | explorer | colour transitions along rows (I5) | open |
| Q16 | How much of each pack is art, and how does that change (art packs → NFO and intro packs)? | catalogue | content kinds per pack over time | open |
| Q17 | When did the SAUCE font field (80×50, Amiga Topaz, others) start to be used, and by whom? | catalogue | `sauce_font` by year and group | open |
| Q18 | Is the scene's iCE turn (after 2013) one tool (PabloDraw's default?) or a choice of artists? | works note | iCE flag and blink use by tool fingerprint and group | open |
| Q19 | Are the empty and near-empty works (fill near 0) blank pages, file-list art, or decoding faults? | works dataset | contact sheet of the least filled works | open |
| Q21 | Is 1996 the peak of the scene, or of 16colo? The archive holds what was submitted to it, and its submitters may favour the years they lived. | owner, works note | artpacks by year in other sources (Demozoo has 1,519 artpacks, type 51; its API ignores date filters and blocks the codespace, so a paging script from elsewhere or a dump is needed), textfiles.com, Defacto2; capture–recapture (R2), knowing that Demozoo imported part of 16colo, so the sources are not independent | exploratory: the peak is 1996–97 in 16colo, textfiles.com and Demozoo alike, but the three are one lineage (92% of textfiles packs named in 16colo), so no independent witness yet ([archives.md](../research/exploration/archives.md)) |
| Q22 | What is the colourless block art of 2000–04, as common then as coloured block art (2,419 against 2,536)? A style (block ASCII), a medium (IRC, web, e-mail without colour codes), or one prolific group? | works note | contact sheet of `blocks` 2000–04, by group and pack; first look (explorer, 2002): `.asc` files drawn in grey blocks (BAFH, sac, spr, mfn), most with no SAUCE author, so a style rather than a fault | open |
| Q23 | Simpson's traps elsewhere: which other trends over time are mixtures of content kinds, packs or groups changing weight? | works note (Q2) | every trend shown by content kind and with pack and group weights | open |
| Q24 | How did scenes whose letters are not in CP437 write: Portuguese `ã`/`õ` (CP860), Polish (Mazovia, CP852), Nordic `Ø` (CP865)? Did they drop accents, switch code page, or draw letters CP437 shows as something else? | text v1 → v2: CP437 has no `ã`, so `não` cannot appear | glyphs of Brazilian, Polish and Nordic packs at 0x80–0xAF, read in each code page | open; first trace: a Brazilian text writes `näo` with CP437's ä (field notes, 2026-10-09); Black Maiden also writes ö for õ |
| Q25 | How much of the writing inside works is BBS advertising (sysop, nodes, numbers, "running")? Did the share fall when BBSes did? | first word count of the text layer: `sysop`, `board`, `member`, `site`, `running` among the most common words | lines classified by kind (I22), by year | open |
| Q26 | Did 16colo grow out of textfiles.com's artscene collection? 92% of textfiles' artpacks have a 16colo namesake, and from 2000 the yearly counts are nearly equal. | archives note | 16colo's own history (FAQ, founders), first-seen dates, comparison by hash | open |
| Q27 | Why do Demozoo's artpacks fall from 476 (1996) to 161 (1997) while 16colo and textfiles stay near their peak? An import that stopped, or editors' interests? | archives note | Demozoo's added dates and editors for artpacks (dump: `added_by`, `created_at`) | open |
| Q28 | Demozoo lists 364 ANSI productions in 1992 and 13 in 1993, and 2,175 BBStros in 1995: which collections were imported in bulk, and from where? | archives note | creation dates and links of those productions in the dump | open |
| Q29 | Which scholarship exists on the art scene beyond Gleb J. Albert (WiderScreen 2017)? A bibliography, read at the source. | cartography, sources register | Albert's references, WiderScreen, Google Scholar, theses on BBS culture | open |
| Q30 | How precisely can a pack be dated? textfiles' listings describe most packs with a month ("ACME Release #5 (January, 1996)"), 16colo files them by year only. | textfiles mirror (`index.tsv`) | parse the descriptions, compare with SAUCE dates and NFO dates of the same pack | open |
| Q31 | Were the BBSes advertised in the works real and where? BBS ads give a name, a number and often a network address; FidoNet nodelists and BBS lists of the time give the same with a date. An independent witness of the scene's geography. | sources discussion, 2026-10-09 | match ad text (text layer) with textfiles.com/bbs/BBSLISTS and archived nodelists | open |
| Q32 | How did graffiti photo packs (168 at textfiles, 1997–2000, mostly German crews) enter the art scene's channels? Same BBSes, same couriers, members shared with ANSI groups? | textfiles ingestion, field notes | NFO and DIZ of those packs (now ingested), greets and member lists, Demozoo groups | open |
| Q33 | Does a vision model recognize a subject drawn in characters (Calvin and Hobbes, a dragon, a face) as a viewer does by squinting? At which size does recognition appear, and does downsampling help as squinting does? | owner, 2026-10-09 | spike 0005: ten Calvin works found by title and text (`SMI-C&HT.ANS`, `PHN-CALV.ANS`, `TT-PG.ICE`…), blind, sizes from the cell grid to a thumbnail | open |
| Q20 | How alike are the works of one pack? Do packs have a house style, a template header or footer? | explorer | within-pack distances against between-pack | open |

## Hypotheses (to pre-register before a confirmatory test)

| Id | Hypothesis | Measure | Null model | Status |
| --- | --- | --- | --- | --- |
| H1 | Byte economy declines over time: files spend more bytes per visible cell as connections get faster. | bytes per ink cell; share of cursor-forward runs | permuted years within groups | open |
| H2 | The fall of shades from 1994 to 2004 happens within artists, not only by new artists replacing old ones. | shade share per artist over years | shuffled years within artists | open |
| H3 | Features v1 carry an author signal: nearest neighbours share the author more often than the same group, year and content kind would predict. | same-author rate among 12 nearest | neighbours drawn within group × year | explored (train): weak, 2.3% against 0.6% by chance and 14.2% knowing the group (works note); to retest with richer features |
| H4 | Formal novelties follow tool releases (rule 6): a new habit (wide canvas, iCE, 24-bit colour) appears in the packs after the editor that makes it easy. | first appearance and adoption curves | release dates shifted at random | open |
| H5 | Animation-like files peak in the mid-nineties and fall with the end of the BBS. | share of animated works (overwrites, clears) | permuted years | explored (train): the peak is 1990–93 (7.2%), not the mid-nineties; restate before testing |
| H6 | One-screen works compose for the 80×25 frame: their ink is centred and their fill higher than the first screen of long scrolls. | centre of mass, fill of rows 0–24 | same rows of scrolls | open |
| H8 | The golden age is real: across independent sources, artpacks per year peak in the mid-nineties, not only in 16colo. | artpacks per year in each source, overlap-corrected | each source's own curve, resampled | open |
| H7 | Groups keep a house palette: colour histograms are closer within a group than between groups of the same years. | distance of `fg_hist`/`bg_hist` | group labels permuted within year | open |

## Ideas (tools, measures, museum)

| Id | Idea | Why | Status |
| --- | --- | --- | --- |
| I1 | Content kind of each work: escape sequences or not, colours, block share; plain text art, coloured text art, colourless block art, ANSI | the extension does not say it (works note, constraint 1) | done: `works` v2, `content_kind` |
| I2 | Extract text runs from grids (letters and punctuation in rows) | search inside works, signatures (Q12), greetings, languages (Q10) | taken: text extractor v2 (`tm_analysis.text`, CP437 letters kept), `tm text`, table `text` of `works` v4, explorer search "words in the work". Short tags (`rs!`, two letters) still escape the three-character word rule |
| I3 | Decoder counts overwritten cells; keep frames of animations | the grid is not the work for animations (constraint 3) | counts done (decoder v3, `works` v3); frames for playback still open |
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
| I22 | Classify the lines of the text layer: greets, BBS ad, signature, title, prose, credits | Q12, Q25, the greets graph (I23) | open |
| I23 | A greets graph: who greets whom, by year, from `greets:` lines (3,728 train works hold the word) | R1 linkage, D5 graph, Q6 | open |
| I24 | Explorer header on a phone: the dataset note runs past the right edge | screenshot of the text search | open |
| I25 | Ingest the 331 textfiles.com artpacks that have no 16colo namesake, as a second source; compare all 3,956 by hash | Q21, Q26, corpus coverage | **taken**: 289 archives with files 16colo lacks ingested; hash comparison in the archives note |
| I26 | Resolve SAUCE author strings with Demozoo's nicks and aliases (165,502 nicks) | I20, H3, R1 | open |
| I27 | Wikidata identifiers on records of groups, tools and formats (CC0), for "see also" across languages | museum, authority control | open |
| I28 | An independent witness of how many packs were released per year: BBS file lists, art magazines' release lists, member lists in NFOs | H8, Q21 | open |
| I29 | Separate sampling (draw, frozen sample) from dataset building in `tm`: `tm.datasets` now does both | audit after D1 | **taken**: `tm.pilots` draws and freezes samples, `tm.datasets` builds |
| I30 | Import textfiles' descriptions (full group name, pack title, month) as assertions on the packs, signed with their source; they name groups that 16colo files only by tag | textfiles mirror | open |
| I31 | Extend the train/test split (`pack_split`) to packs of other archives: the hash rule does not depend on the source, but the views read 16colo only, so textfiles packs stay out of exploration | ingesting textfiles | open |
| I32 | A sample's guard checks the frame query's text, not its rows: a change in the data under the same query (a new source, a corrected artifact) goes unnoticed. Also hash the frame's rows at draw time | ingesting textfiles, D1 | open |
| I33 | Discmaster (discmaster.textfiles.com) indexes the files of the CD-ROMs on the Internet Archive; shareware and BBS CDs carry artpacks with the CD's release date. Search our hashes there: an independent, dated witness for Q21 and H8, and first-seen dates | sources discussion | open; hash search works (BLAKE3, JSON), first probe in the [register](sources/README.md) |
| I34 | The Internet Archive's `cdbbsarchive` collection (BBS CD-ROM images): artpacks as BBSes held them, dated by the disc | sources discussion | open |
| I35 | The Git history of github.com/sixteencolors/sixteencolors-archive: when each pack entered 16colo, and from where (answers part of Q26) | sources discussion | open |
| I36 | Usenet (`usenet-alt` on the Internet Archive; alt.ascii-art, alt.binaries.* and comp.bbs.* groups): ASCII art posted with a date and a sender, and release announcements of packs | sources discussion | open |
| I37 | Teletext Archive (teletextarchive.com): pages recovered from VHS tapes, a source for platform teletext (R6) beside teletextart.com | sources discussion | open |
| I38 | Today's scene on social networks and its own sites (Blocktronics, Mistigris, ANSI artists on Mastodon and Bluesky): where living artists can be asked for permission and testimony | sources discussion | open |
| I39 | Freeze the list of files seen as train then held out (the 382 of works v4 not in v5) beside the research program, so a confirmatory test can exclude them without rebuilding v4 | ADR 0018 | **taken**: `datasets/works/seen-then-test.yaml` |
| I40 | Near-duplicates beyond bytes, as a ladder: (1) same grid from other bytes (other escape codes, SAUCE added or removed): 932 extra files in works v5 already share a grid; (2) same grid but trailing SAUCE, comments, EOF padding; (3) cell similarity between grids of the same size (share of identical cells, tolerant of an edited signature or a recoloured line); (4) perceptual hash of the conservation rendering, for a work redrawn in another size or font; (5) the text layer and glyph histograms to find a work copied with changes. Each level is an `inferred` assertion `same_as`/`variant_of` signed `algo:`, never a merge | owner, 2026-10-09 | open |
| I41 | A white-background reading of the works, less dark to the visitor: a colour mapping as an `interpretation` profile with its recipe, never replacing the conservation or authentic renderings. Risk: inverting value breaks shading (░▒▓ read as ink on black) and the 16-colour palette's relations; test by content kind (text, blocks, coloured) and colour family before choosing (spike 0004) | owner, 2026-10-09 | open |
| I42 | A vision model as art critic: send the rendering (several sizes, PNG and JPEG) with or without context (title, group, year, text layer), and ask first for a description (subject, style, composition), then a commentary in the manner of a museum curator's lecture. Every output is `interpretation`, signed `algo:<model>@<version>`, with its prompt and image recipe. Rights: a work leaves our machines only with display rights (`can_display()`), so local open-weight models first. Measure against D1 descriptions written by hand, and on hallucinated subjects. Cost estimated 2026-10-09 (OpenRouter prices of that day, 107,944 distinct grids, ~1,500 tokens in and ~1,000 out per work, one pass): about $55 (DeepSeek v4.1 Flash, batch) to $345 (Qwen3.8 27B) and $700 (Claude Sonnet 5.5, batch); half a day to a day of wall time; the full protocol (sizes × contexts) multiplies it, so on a sample only | owner, 2026-10-09 | open |
| I43 | A museum of rooms with their own mood (gallery, release party, BBS, labels, Midnight, arcade, feeds borrowed from social apps), on the same works and rights: [museography proposal](museography.md), four questions to the owner | owner, 2026-10-09 ("c'est tristoune") | open |
| I19 | D1 sampling design: strata bounded by the mass, equal (or square-root) allocation per stratum so that thin years are over-represented, and each pack's inclusion weight recorded so that statistics can be reweighted to the corpus | owner: over-represent thin years | taken (roadmap step 6) |
| I18 | Detect the artist's handle in NFO and in-grid text and link it to SAUCE authors, with confidence | linkage R1 | open |

## Curiosities

| Id | Curiosity | From | Status |
| --- | --- | --- | --- |
| C1 | The earliest, longest, widest, most colourful, least filled works of 16colo: a cabinet of extremes | explorer sorts | open |
| C2 | The 64 KB cut download (`1994/itr-9401.zip`): what was the last file, the one lost? | field notes | open |
| C3 | Packs whose archive listing is a drawing (`TOTAL CHAOS`, 1993): how many groups did it, and did it spread? | field notes | open |
| C4 | Ninety-two archives are copies under another name: who renamed them, and when? | field notes | open |
| C6 | `DD-ICE.ICE` (pack dd-ice) is a ProTracker module, "agony intro", named like an iCE artwork; about 1,600 pictures, programs, archives and modules carry a SAUCE record of type ANSI. Which tool stamped them all? | decoder signatures | open |
| C7 | Ñ (0xA5) is by far the most drawn CP437 letter (about 130,000 cells in the train packs), then ÿ, ¢ and á: letters as texture, not as writing. Who drew with them, and since when? | glyph histograms, text v2 | open |
| C8 | The longest Wikipedia article on ANSI art is in Persian (31 KB, three times the English); the longest on the art scene is Korean, on the demoscene Armenian. Who wrote them, and is there an Iranian ANSI scene? | Wikipedia survey | open |
| C9 | 16colo, Demozoo, Defacto2, Blocktronics, Mistigris and PabloDraw have no Wikipedia article in any language checked; the artpack has 3. | Wikipedia survey | open |
| C10 | Black Maiden (Brazil) wrote Portuguese with CP437's ä and ö for ã and õ. Did other Brazilian groups share the habit, or use CP860 and look broken on CP437 screens? | D1 additions (maiden14) | open |
| C5 | A `.ANS` of 1996 with 605 rows of grey line drawing (`02-STEPS.ANS`, swap07): line art in ANSI, how common? | explorer | open |
