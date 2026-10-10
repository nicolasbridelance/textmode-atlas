<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0006. What can plain rules and offline tools read in the words of the works?

- Date: 2026-10-10 · Time box: 3 h · Time spent: about 3 h
- Branch: spike/0006-reading-the-words (kept locally until the step 15 ADR, then deleted)

## Question

Roadmap step 15 (leads I51, I22, I23, Q10, Q25) asks for a reading of the words inside the works:
zones, line classes, entities, languages. Before writing its ADR: how far do cheap, offline,
explainable methods go on the text layer we already have, where do they fail, and what must the
production design plan for (cleaning, evaluation, ambiguity)? Exploratory, train packs only
(research programme, rule 3).

## Method

- Data: text layer v2 of dataset `works` v6 (decoder `tm_render.ansi@5`, train packs):
  970,841 lines with a word, in 79,309 of 86,700 decoded files. Years are filing years.
- **Cleaning**: each line split into segments at three spaces or more (the extractor's run
  separator); a segment is kept when at least 60% of its non-space characters sit in plausible
  words (two letters or more, a vowel, not one repeated letter). Kept: 721,586 lines; 443,398 hold
  four words or more, in 51,147 files.
- **Language**: lingua 2 (offline n-gram models), restricted to 28 Latin-script languages. Per
  file: clean lines of three words or more, joined, when they total fifteen words (32,220
  files). Per line: clean lines of six words or more.
- **Phone numbers**: candidates by a pattern that admits the scene's disguises (o/O for 0,
  i/I/l for 1, letters or X in place of digits); dates set apart; North American shape
  (`[1-]AAA-EEE-NNNN`) read first, then numbers written with `+`; place from libphonenumber's
  offline geocoder.
- **Line classes**: regular expressions for greets headers, BBS vocabulary, credits
  (`ansi by`, `font by`…), member vocabulary, pack information, contact, URL and e-mail.
- **Greets**: a section opens on a greets header and runs over the following rows (gap of two
  rows at most, twelve rows at most); names are the items of comma, slash, ampersand or "and"
  lists, cleaned of decoration and stop words.
- **Checking**: samples drawn by hash, read by Claude (not a human gold set): 40 phone readings,
  60 greeted names, 40 URL or e-mail lines, and four files per language.

## Findings

**Cleaning is required and works.** A quarter of the lines with a "word" are drawing (`$$$`,
`888`, `iiil`), and many lines mix a border with text. Segment cleaning keeps the text and drops
the drawing in every sampled case; it loses tokens without a vowel (`BBS`, `TRSI` alone) and
very short tags, which the rules read on the raw line instead.

**Phone numbers: reliable, and the best first entity.** 10,584 readings (3,600 distinct numbers)
in 5,990 files, plus 2,503 deliberately masked numbers and 2,534 left unresolved. 39 of 40 sampled
readings are real numbers; the place is wrong in two or three, where codes collide: `972` is
Dallas and Israel, `649` the Turks and Caicos and Auckland (`+64 9`), `+7 095` an old Moscow code.
NANP numbers dominate (US 7,937 readings, Canada 2,086); numbers written without `+` outside
North America mostly stay unresolved, as do trunk prefixes (`+49 (0) 30…`). Area codes have been
split since the 1990s: the geocoder's current place is a lead, not a fact.

**Phones go, the internet comes, and they cross in 1996.** Share of decoded files per filing year
that hold at least one phone number (read or masked), against a URL or e-mail address:

| Year | Files | Phone | URL or e-mail | Greets section | Credit line |
| --- | --- | --- | --- | --- | --- |
| 1990 | 260 | 54.2% | 0.0% | 0.0% | 9.2% |
| 1992 | 1,403 | 29.2% | 0.1% | 0.4% | 24.8% |
| 1993 | 3,534 | 20.4% | 0.4% | 4.1% | 23.6% |
| 1994 | 8,384 | 19.3% | 2.3% | 10.4% | 26.4% |
| 1995 | 11,619 | 12.2% | 5.6% | 9.6% | 21.6% |
| 1996 | 14,993 | 6.7% | 9.6% | 10.0% | 19.9% |
| 1997 | 13,178 | 2.9% | 12.5% | 7.8% | 15.2% |
| 1998 | 7,500 | 2.0% | 14.1% | 6.3% | 14.3% |
| 2000 | 2,438 | 0.5% | 15.4% | 4.5% | 10.7% |
| 2005+ | 8,854 | 1.7% | 11.3% | 5.3% | 12.9% |

DOS file names that look like domains (`edit.com`) are negligible (110 of 30,246 URL lines).
A file holds a number or not, whatever its length: the shares are not weighted by text.

**Masking rose as the boards closed.** Among numbers read or masked, the masked share goes from
7% (1992) to 12–13% (1993–96), 20% (1997–98) and 45% (1999), on small counts after 1997.
`PRI-VATE` and `XXX-XXXX` dominate; some masks speak (`NOT-OPEN`, `DiE-FEDS`). In about a quarter
of read numbers from 1992 to 1999 (16.6% overall), digits are written as letters (`9o9.685.o749`,
`6l3-83O-6964`).

**Language: English everywhere, a few dense pockets elsewhere.** Of 32,220 files with enough
text, 24,092 are English at confidence 0.9 or more; about 740 are in another language at that
confidence (Polish 215, German 132, Swedish 115, Spanish 93, French 39, Portuguese 29, Finnish
27, Dutch 24). The non-English share of decoded files rises from 0.1% (1993) to 3% (2000), then
falls back. Polish is concentrated in two groups, 1999–2003 (`l0p*`, `spr_*`): poems, dedications,
news. "Latin" (480 files) and "Tagalog" (170) are artefacts of handle lists and repeated menu
words; low-confidence results are lists, not languages. Line-level detection is noisier and
finds 989 "Turkish" lines in five files that are binary data decoded as text (`srg-0295`).

**Greets: the rules find the sections, not yet the names.** 8,599 sections in 6,846 files,
76,681 name mentions, 35,202 distinct strings. The most greeted strings are plausible (iCE 255
files, ACiD 225, PWA, Razor 1911, Napalm, CiA, Fire, Blade, Misfit, TRSI, Halaster, Lord Jazz),
but only about 31 of 60 sampled mentions are a person or group greeted. Failures: sections that
run into prose, `name - message` lines (`lord jazz - howz it going?`), headers that open no list
("hello everybody", "welcome"), past-member lists next to the greets, placeholders (`XXX`), and
generic words (`etc`, `well`, `thanks`).

**Credits and URLs read well by rule.** Sampled credit lines are credits in most cases (`ANSi by:
Living Death [iDENTiTY]`, `font by sq2(ice)`); 39 of 40 sampled URL or e-mail lines are real
addresses, one is a fake (`hq@Harlequin.vga.ansi`).

## Recommendation

1. **Write the step 15 ADR** with these choices:
   - a per-line reading table (cleaned text, segments, class labels, language with confidence,
     entities with spans), each reading versioned and signed `algo:<name>@<version>`, never a
     fact (invariant 5);
   - entities as `inferred` assertions only after an extractor has measured precision;
   - phone numbers first (precise, dated, placeable), then credits and URLs, then greets;
   - ambiguous readings kept as several candidates with the rule that produced each (`972`,
     `649`), not resolved silently.
2. **Greets need zones before names**: a section segmenter (where the list starts and stops,
   `name - message` lines) and a gold set before any graph (I23, Q37). A model-free approach
   is not enough for publication at 52% precision.
3. **Start D2 now**, small: 200 lines drawn from D1 across the classes above, labelled by a person
   (class, names, numbers), so that every extractor reports precision and recall (research
   programme, layer 1). Claude's reading in this spike is a pre-check, not D2.
4. **Filter binary files** before any text work: a file whose "text" is mostly high CP437 letters
   is not prose (`srg-0295`).
5. **Language at file level only**, confidence 0.9 or more, with the artefact languages (Latin,
   Tagalog) treated as "list or noise". Line level waits for a test on D2.
6. The 1996 crossing of phones and addresses is a candidate for pre-registration on the test
   packs (Q25), with a null model by permuted years within groups.
