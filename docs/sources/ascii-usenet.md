<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Source note: ASCII art outside the group scene

M0 note: access, limits and terms, checked at the source on 2026-10-09. The ASCII art of
Usenet and the early web, made by individuals rather than groups, mostly signed with initials,
and older than most of the corpus. Three sources, one of them usable in bulk.

## Internet Archive: Giganews captures of Usenet

Item [`usenet-alt.ascii-art`](https://archive.org/details/usenet-alt.ascii-art) ("contributed
courtesy of giganews.com. These captures omit most binary posts"), public since 2014-03-07, and
the `rec.arts.ascii` file of item `usenet-rec.arts`.

| File | Size (gzip) | Messages |
| --- | --- | --- |
| `alt.ascii-art.20140611.mbox.gz` | 21.0 MB | 13,785, from 2003-06 to 2015 |
| `alt.ascii-art.animation.20140307.mbox.gz` | 3.1 MB | |
| `alt.ascii-art.endless-blabla.20140417.mbox.gz` | 0.2 MB | |
| `rec.arts.ascii.20140321.mbox.gz` (in `usenet-rec.arts`) | 2.4 MB | |

Each mbox comes with a `.csv.gz` index (date, message id, from, groups, subject). Messages in
`alt.ascii-art` per year: 2,141 in 2003, 3,468 in 2004, then 2,377, 2,207, 1,099, 795, 854, 468,
146 and fewer after 2010. Subjects carry the group's own tags: `[PIC]` 336, `[FAQ]` 87, `[DIS]`
26, `[ANN]` 21, `[REQ]` 15. **The 1990s are missing**: Giganews' retention starts in 2003.

Terms: none stated on the item; Internet Archive's terms apply. About 27 MB in all: fits on disk.

## asciiart.eu (Injosoft AB, Sweden)

- **Usenet archive** ([archives/usenet](https://www.asciiart.eu/archives/usenet)): 128,008
  messages, 43,471 threads, October 1993 to June 2013: `alt.ascii-art` 108,528 (1993–2013),
  `rec.arts.ascii` 8,668 (1994–2013), `de.alt.rec.ascii-art` 6,434 (2000–2010),
  `alt.ascii-art.animation` 4,297 (1994–2013), `alt.ascii-art.endless-blabla` 81. "Mirrored from
  publicly available historic Usenet archives", "the raw material is kept unchanged"; which
  archives is not said. Ten times the Internet Archive's count, and the only copy of the 1990s
  found so far (lead I65). Posters are grouped across aliases (9,234 poster pages); email
  addresses masked; `X-No-Archive` messages excluded; removal on request.
- **Galleries**: the classic ASCII art collections, by subject.
- **Access**: HTML pages; [sitemap-usenet.xml](https://www.asciiart.eu/sitemap-usenet.xml)
  lists 47,823 URLs; [llms.txt](https://www.asciiart.eu/llms.txt). No dump. robots.txt allows
  everything but the drawing app and the Usenet search.
- **Terms** ([terms-of-use](https://www.asciiart.eu/terms-of-use)): no "data mining, data
  harvesting, data extracting, scraping"; no mirroring "any substantial portion"; viewing,
  printing and sharing single works for personal, non-commercial use; "The ASCII artworks and
  messages belong to their original authors"; keep the artist's initials. Citation asked as
  "ASCII Art Archive (asciiart.eu)" with a link.
- **For the museum: no bulk fetch.** Single pages read by hand for research; for the Usenet
  archive, ask Injosoft where the 1993–2002 messages came from, then go to that source, or ask
  for an export (lead I65).

## chris.com (Christopher Johnson's ASCII Art Collection)

One of the first large web collections of ASCII art (from the mid-1990s), sorted by subject with
artists' initials kept. The live site now answers with a SiteGround captcha page. The Wayback
Machine holds 2,550 distinct URLs under `chris.com/ascii/`, captured from 1997 (most in 1999–2000,
2010 and 2016). asciiart.eu's galleries are generally said to descend from it; its terms do not
say so (claimed, not checked).

Wayback captures are a witness of what was online and when; the works stay their authors'. A
collection of that kind would be taken page by page from the Wayback Machine at a slow rate,
after an ADR on web-collected ASCII, because its works have no packs, groups or release dates.

## Privacy (invariant 7)

Usenet headers carry real names and email addresses next to handles and initials. In the raw
mbox they are the original, kept unchanged in storage; **nothing from `From:` reaches the public
API or the site**, and linking a poster's name to a handle is never published. asciiart.eu
already masks addresses and groups aliases; the museum does neither in public.
