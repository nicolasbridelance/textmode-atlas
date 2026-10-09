<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Source note: teletext art

M0 note: access, limits and terms of the teletext sources, checked at the source on 2026-10-09
(leads I54, I55, I56, I60). One note for several small sources, because the question they share
matters more than any one of them: **does the page survive as a file, or only as a picture?**

## What the museum already holds

16colo's `mist1116` (Mistigris, November 2016) carries 12 teletext pages by Illarterate as
files: 11 `.EP1` (a page format of teletext editors, which one to confirm) and one `.TTI`
(`MISTFAX16.TTI`). Teletext was not absent from the corpus (I54): it came into a PC artpack.
No decoder reads them yet (M5).

## Sources

| Source | What it is | Pages as files? | Measured 2026-10-09 | robots.txt | Terms |
| --- | --- | --- | --- | --- | --- |
| **edit.tf** | Online teletext editor; `edit.tf/#<data>` carries the whole page in the URL | **yes, the URL is the page** | Demozoo: 20 full `edit.tf/#…` links (8 as downloads); 5 short links on `s.edit.tf`, whose host **no longer resolves**: lost unless the Internet Archive kept the redirect | GitHub Pages, none | none stated |
| **Demozoo / scene.org** | Teletext compo entries | mostly: 95 zips (contents not listed), 2 `.tti`, 1 `.t42`; also 12 `.png` and 12 `.txt`, 2 videos | 127 files on scene.org ([scene-org.md](scene-org.md)) | — | as scene.org |
| **teletextart.co.uk** (TARL, Teletext Art Research Lab, Dan Farrimond) | Artists, block parties (Cambridge 2016–2022, Wigan 2018, Teletext50), knowledge base, podcast; links to the archives | **a few**: 12 zips among 1,087 media (FlashParty entries 2021–2025, YLE40, Mistigris anniversary 2019, MIST templates); the rest images (766 PNG, 205 JPEG, 96 GIF) | WordPress API `wp/v2/media`: 1,087 items listed, uploads 2016–2026 | `/wp-admin/` only | none stated; no license on the page |
| **teletextart.com** (MUTA, Museum of Teletext Art; International Teletext Art Festival) | Exhibitions broadcast on real teletext services (YLE, ORF), 2012–2026; early Norwegian teletext art of 1979 (NRK, Arild Boman) | **no**: 276 media listed, all images (269 GIF) | 433 counted by the API, 276 returned | `/wp/wp-admin/` only | none stated |
| **teletextarchaeologist.org** (Jason Robertson) | Broadcast pages recovered from domestic VHS since 2012, plus pages saved with PC decoder cards; tape donations | not on this site: it links to an archive viewer at `archive.teletextarchaeologist.org`, which **no longer resolves** | 57 media | `/wp-admin/` only | none stated |
| **teletextarchive.com** | Recovered broadcast pages | unknown | not examined further | **`Disallow: /` for all** | — |
| **zxnet.co.uk** (Alistair Buxton, teletext recovery and tools) | Recovery software, resources | unknown | not examined further | **`Disallow: /` for all** | — |

## What follows

- **Files are rare.** Teletext art lives mostly as screenshots, on the festival and lab sites as
  in Demozoo (field note, 2026-10-09). The files the museum can keep: the 127 scene.org entries,
  the 20 edit.tf pages, the dozen TARL zips, the Mistigris pack it already has.
- **Broadcast pages are another collection.** VHS recoveries are broadcast teletext (news,
  sport, broadcasters' graphic artists), not scene art. Two sites close their whole content to
  robots; they are not fetched. If the museum ever shows broadcast teletext design, it starts with
  a letter to Jason Robertson and Alistair Buxton.
- **Artists to credit.** TARL and MUTA list artists by name with biographies: the best credit
  source for teletext, better than file names. Reading their pages by hand is fine; nothing is
  republished without asking (TARL contact page; MUTA contact page).
- **Screenshots to pages** (I60) could draw on MUTA's 269 GIFs, if they are clean renderings
  of the 40 × 25 grid (not checked): a test set, once the owner and an ADR agree.
