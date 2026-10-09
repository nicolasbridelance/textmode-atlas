<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Source note: Wikipedia and Wikidata

Checked 2026-10-09 through the MediaWiki API: language links of 29 English articles, the size
of each article in each of the 70 languages that have one, keyword searches in 22 Wikipedias,
and the English categories "Artscene", "Artscene groups", "ASCII art", "Demoscene",
"Demogroups", "Bulletin board systems".

## What it is for the museum

- **Context, not evidence.** Wikipedia is secondary; claims about the scene go back to their
  sources (research program). Its articles are what visitors already read: the museum links to
  them, in the visitor's language when one exists.
- **Identifiers.** Wikidata items (CC0) name groups, tools, formats and code pages across
  languages and across other databases. They are the cheapest authority control for a record's
  "see also": ACiD Productions is Q289820, ANSI art Q2623363, artpack Q713860, Code page 437
  Q1105757, TheDraw Q12403260.

## Coverage of the subject (article size in thousands of bytes of wikitext)

| Topic (en title) | Languages | en | fr | Longest |
| --- | --- | --- | --- | --- |
| Teletext | 49 | 56.1 | 6.0 | ja 141.6 |
| ASCII art | 44 | 58.8 | 19.7 | en 58.8 |
| Bulletin board system | 40 | 54.7 | 15.8 | el 84.6 |
| Minitel | 30 | 46.3 | 92.0 | fr 92.0 |
| Concrete poetry | 29 | 22.6 | 9.8 | pl 27.1 |
| Demoscene | 28 | 52.1 | 14.2 | hy 65.8 |
| .nfo | 19 | 11.7 | 2.3 | en 11.7 |
| Videotex | 19 | 45.2 | 30.5 | en 45.2 |
| Kaomoji | 17 | 15.8 | 0.1 | ja 34.1 |
| Code page 437 | 17 | 52.6 | 3.0 | en 52.6 |
| Text mode | 14 | 21.8 | 8.1 | en 21.8 |
| ACiD Productions | 11 | 8.5 | 2.5 | en 8.5 |
| ANSI art | 10 | 10.5 | 1.5 | fa 31.0 |
| Box-drawing characters | 9 | 21.4 | — | ja 31.2 |
| FIGlet | 9 | 9.7 | 5.4 | en 9.7 |
| Block Elements | 9 | 6.6 | 1.2 | ru 10.0 |
| Semigraphics | 8 | 22.3 | 11.6 | ru 27.9 |
| Warez scene | 7 | 18.5 | 10.0 | en 18.5 |
| Crack intro | 7 | 10.9 | 2.1 | en 10.9 |
| PETSCII | 7 | 79.0 | — | en 79.0 |
| Jason Scott | 4 | 18.0 | 3.1 | en 18.0 |
| Textfiles.com | 3 | 4.5 | 3.5 | en 4.5 |
| Artpack | 3 | 1.9 | — | de 1.9 |
| Scene.org | 3 | 18.0 | — | en 18.0 |
| Shift JIS art | 3 | 6.6 | — | en 6.6 |
| TheDraw | 3 | 6.3 | — | ru 8.5 |
| Computer art scene | 2 | 11.9 | — | ko 12.7 |
| ATASCII | 2 | 41.6 | — | en 41.6 |
| ICE Advertisements | 1 | 3.4 | — | en 3.4 |

ANSI art has articles in de, en, fa, fi, fr, ko, pl, ru, sv, uk. The French one is 1.5 KB.

## What it shows

- **The neighbours are better covered than the art.** Teletext (49 languages), ASCII art (44),
  BBS (40) and the demoscene (28) are everywhere; ANSI art has 10 articles, the artpack 3, the
  art scene 2. The pack, the unit of release of the whole scene, is nearly absent.
- **Where the long articles are.** The longest article on ANSI art is in Persian (31 KB, three
  times the English one); the longest on the art scene is in Korean; on the demoscene, in
  Armenian; on semigraphics, in Russian (Псевдографика, 28 KB), which matches the place of
  pseudographics in the post-Soviet scene (cartography). Who wrote them is a lead (C8).
- **Groups with an English article.** ACiD Productions, iCE Advertisements, Aces of ANSI Art,
  Blade, Creators of Intense Art, Dark Illustrated, Superior Art Creations, and a page "Minor
  artscene groups"; people: RaD Man, Jason Scott. In German: Black Maiden, Chemical Reaction;
  in Swedish: Dubmood; in Finnish: Rad Man, Superior Art Creations.
- **Absent everywhere checked:** 16colo / Sixteen Colors, Demozoo, Defacto2, Blocktronics,
  Mistigris, PabloDraw, ACiDDraw (mentioned only inside other articles), teletext art as a
  practice.

## Local copy (2026-10-09)

`scripts/fetch_wikipedia.py` fetched, into `data/wikipedia/2026-10-09/` (local, never in Git):

- **Seeds:** the 34 topics above (29 surveyed and five formats or tools) and the members of six
  English categories with one level of subcategories: 333 English articles.
- **Every language that has them:** 1,902 distinct articles in 126 languages, 16.7 MB of
  wikitext, each with its page id, revision id and timestamp. Most covered after English (321):
  German 98, French 97, Russian 79, Finnish 72, Spanish 70, Italian 61, Japanese 58, Chinese 54,
  Polish 52, Swedish 49, Ukrainian 48.
- **Wikidata:** the 323 items these articles point to, whole (labels in every language,
  statements, links to other databases).
- **Fetches:** 267 requests, each logged with its time, URL, status and the SHA-256 of the
  body. Wikidata answered `maxlag` several times in a row: the script waits up to a minute
  between tries.

What it is for: the nomenclature of roadmap step 16 (kinds, techniques, formats, tools, groups,
with Wikidata identifiers and labels in every language) and the "see also" of records (I27).

**People.** 42 of the items are people (`P31 = Q5`), and their articles often give a civil
name next to a handle. The copy is research material: nothing from it may link a handle to a
civil identity in anything the museum publishes (invariant 7). The nomenclature keeps groups,
tools, formats and techniques; people stay out of it.

## Access and terms

- API: `https://<lang>.wikipedia.org/w/api.php` and `https://www.wikidata.org/w/api.php`.
  Wikimedia answers 429 to a generic User-Agent: send `textmode-atlas/<version> (<repository
  URL>; research)`, one request at a time, and batch titles (up to 50 per query).
- Wikipedia text: CC BY-SA 4.0 (quoting needs attribution and share-alike; the museum links
  rather than copies). Wikidata: CC0.
