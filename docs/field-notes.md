<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Field notes

What building the museum teaches about the scene: habits found in the files, gaps in the record,
traces of how the art travelled. Each entry is dated, says how it was found and where the
evidence is, so that it can be checked, and later told.

This is a quarry, not a publication. Visitor stories, cartels and data stories draw from it,
are localized (`en`, `fr`) and checked again before they are shown. Measurements here describe
the files we hold; they are not claims about the whole scene (see the coverage notes in each
entry).

Add an entry whenever the work turns up something worth telling (CLAUDE.md, "During the
session"). Newest first.

## 2026-10-09 — What the works say in letters

**Early ANSI talked about BBSes.** Nine ANSI in ten hold at least one row of words. Among the
ANSI of 1990–93, 44% use the vocabulary of a board (sysop, node, baud, running, bbs, call); 25%
in 1994–96, 11% in 1997–99, 7% in 2000–04, and 12% again after 2005, perhaps the retro boards.
The art was first an advertisement for a place to call. Greets (`greets`, `greetings`,
`hellos`) peak in 1994–96, at 9%. *Evidence: text layer v1 of the train packs (`works` v4,
table `text`), marker words matched on whole words, 2026-10-09. Rough: `call` is a common word,
and an ad drawn in blocks is not text to the extractor. Story: from the board's door to the
artist's signature.*

**The scene's letters were CP437's.** CP437 has é, ü, ñ, but no ã or õ: a Brazilian ANSI could
not write `não` on a standard VGA screen, and one writes `näo`, borrowing the German ä, beside
`soh` for `só`. Polish texts in the packs drop their diacritics (`juz`, `sie`). Ñ, the most
drawn accented letter by far, is mostly texture, not Spanish. Writing in another language than
English stays under 1% of the ANSI of every era, by a rough count of function words (two
distinct ones per work); found: German, Brazilian Portuguese, Polish, Swedish, Dutch, French,
Spanish. *Evidence: glyph histograms of features v1 (codes 0x80–0xA5 in 8.5% of
measured works, 130,000 cells of Ñ) and text layer v2 of the train packs, 2026-10-09. Open:
Q10, Q24, C7.*

## 2026-10-08 — Pictures signed as ANSI

**Some packs signed every file, pictures and music included.** About 1,600 files of 16colo that
are not text carry a SAUCE record that calls them ANSI: 662 JPEG and 505 GIF pictures, 142
programs, 115 ZIP archives, 81 Scream Tracker and 22 ProTracker modules, PCX, BMP and IFF
images. Most date from 1994–98 and come from many groups (iNSOMNiA, BLACK MAiDEN, Union, CiA,
Mistigris…). A tool that appended SAUCE records to a whole pack must have set the type to
Character/ANSI whatever the file was: the record became a signature of the group, not a
description of the file. One module, `DD-ICE.ICE` ("agony intro"), even bears an artwork's
extension. *How found: ANSI files named `.JPG` decoded as grey noise in the explorer; their first
bytes were JPEG and GIF signatures. Evidence: decoder version 4, error `binary_content`;
`artifact.sauce` (data type 1, file type 1) of those files.*

## 2026-10-08 — First look at the grids

**The nineties drew with eight backgrounds.** VGA text mode can show sixteen background colours
if the blink bit is given up (iCE colours), and the SAUCE record has a flag for it. Before 1998
the flag is almost never set, which could have meant that editors did not write it. The grids
say otherwise: in the train packs of 1994–99, only 1–2% of ANSI works use the blink bit under
ink at all, and the raw files hold no other way of asking for a bright background
(`ESC[100–107m`, `ESC[?33h`) in a sample of 3,000. Artists worked within eight backgrounds, as
the BBS terminals of their readers would show them, blinking otherwise. Sixteen backgrounds
became common only after 2013 (22% of works). *How found: feature `high_bg_ratio` against the
SAUCE flag, then a byte scan of the originals. Evidence: research/exploration/works.md; dataset
`works` v1.*

**"ASCII" files were often coloured.** In 1994–99, a third of the files the scene named `.ASC`
contain ANSI colour codes, and about a quarter are drawn in more than two colours: the
extension named a style of drawing (with letters and punctuation), not the absence of colour.
After 2000 the same extension often holds colourless block art. *How found: fixed sample of
600 `.ASC` files of the train packs, colours measured on the grid and escape sequences on the
bytes. Evidence: research/exploration/works.md.*

## 2026-10-08 — Widths that were not widths

**A broken SAUCE record is a tool's fingerprint.** 568 ANSI and ASCII files carry a SAUCE
record whose binary fields cannot be true (ADR 0015); 138 of them declared widths of 8,224 to
30,061 columns. 96% date from 1995 to 1999, and the faults come in families, each tied to a few
groups:

- *Text running over the numbers.* 84 files of cnc and Damage (1995), taura productions (1996)
  and Polyester (1997) have, after the group, the text `-EnCrYptEd by iLL`, which overruns the
  date, the size and the types. Four groups, two years, one signature: probably one tool, or one
  person's tool, passed from group to group. Who or what "iLL" was is not known yet.
- *A record shifted by one byte.* RiSE (1995, 28 files) wrote an author field of 21 bytes
  instead of 20; every later field slides, and 80 columns reads as 20,480. MOZiCART's packs of
  1996 show the same shift.
- *Spaces where zeros belong.* .boogiE%Woogie., rune, sHADe, atb, BAFH and others (1995–2003)
  padded the binary fields with spaces, as a text editor would: 80 columns reads `0x2050`, the
  size `0x2020…`.

The art in these files is intact; only the 128-byte record is wrong. Drawn at the declared width,
a whole screen fell onto one row, which is how the fault showed. *How found: grids of 16colo
sorted by width, after the whole corpus was decoded; raw records read byte by byte. Evidence:
`decoding.sauce_problems` (decoder version 2); `artifact.sauce` of `1997/poly0197.zip`,
`1995/rise0395.zip`, `1996/bdp-0396.zip`.*

## 2026-10-08 — Ingesting all of 16colo

**Some packs survive only as cut downloads.** Four ZIP packs of the mirror end before their
central directory, the index a ZIP keeps at its end: `1994/itr-9401.zip` stops at exactly
65,536 bytes, a transfer cut at 64 KB; `1994/id-1194.zip`, `1995/ioa-1295.zip` and
`2004/mxt-pack17.zip` stop inside their last file. The copy that reached the archive is the one
that broke, and no complete one has been found. Every member before the cut is intact (checked
by CRC); the last one is lost. *Evidence: ADR 0014; `expansion` rows of those packs.*

**Packs drew in their own file listing.** 1,541 files of the mirror are empty, in 377 packs.
730 of them, in 207 packs from 1993 to 2004, have names made of blocks, lines and dots: shown
in archive order, as a BBS file lister or `pkunzip -v` would, they draw. `1993/chs-0893.zip`
spells its logo over five empty files (` ▄▄`, `▀██▀██▀▀`, ` ██ ██▄▄`, ` ██────┐`, ` │TOTAL│`,
` │CHAOS`) and then section headers (`∙■ANSI■∙`, `∙■VGA■∙`, `∙■INFO■∙`); `1994/wbl-0694.zip`
alternates `-·ANSI·-`, `-·VGA·-`, `-·MODS·-` with blank names. The archive itself was a canvas,
read before any file was opened. A museum that shows only the files loses it: the listing
should be shown as the pack's first page. *Evidence: dataset `catalogue` v1, `files` with
`bytes = 0`, by archive position; research/exploration/catalogue.md.*

**A tool's default became the most common group name.** In SAUCE records, the group most often
named is `READ THE INI FILE`: 1,874 art files in 167 packs, 1994 to 1998, most in 1995 (WiCKED
packs, for instance `1995/wkd-0695.zip`). The authors are filled in; the group is the
placeholder of a SAUCE-writing tool that nobody configured. The font field likewise carries
`SAUCE-ADDER V1.4` on 92 files. Which tool wrote them is not established. Metadata inside the
file is evidence of the tools as much as of the artists. *Evidence: dataset `catalogue` v1,
`sauce_group` and `sauce_font`; research/exploration/catalogue.md.*

**The same pack, released under several names.** 92 archives of the 16colo mirror are
byte-for-byte copies of another one: 91 packs exist in two or three files. In 30 cases only the
case of the name differs (`2002/017-Athanasia.zip`, `2002/017-athanasia.zip`); in 56 the name
itself changes, often the group tag or the punctuation (`1997/go!-#000.zip`, `1997/go-000.zip`;
`2004/mx-pack12.zip`, `2004/mxt-pack12.zip`; `1997/plf-0197.zip`, `1997/plf_0197.zip`). Five
are filed under two years (`1993/die-pk5.zip` and `1994/die-pk5.zip`; `1997/cia52.zip` and
`1998/ciapak52.zip`): a pack that circulated across a new year, or a dating hesitation of the
archive. Packs travelled under the names each BBS or FTP site gave them, and the archive kept
several of those names. The museum stores one artifact and dates it from the first name met,
so for those five the year is uncertain by one. *Evidence: `sha256sum` of every archive of the
mirror against the 5,766 sets the ingestion recorded from 5,858 archives.*

**A pack can hold the same file twice in one archive.** `2004/cro-dskmg0604-nomp3.rar` lists
`cro-dskmg0604-nomp3/cro.nfo` twice, with the same size, date and CRC, among 255 entries; it
also has a `cro.nfo` at its root. The packer most likely added the folder's NFO twice when
building the archive. Nothing is lost, but a tool that expects one entry per name stops: the
museum's ingestion did, after 5,200 packs. How often this happens in the rest of the mirror is
not measured yet. *Evidence: `7zz l -slt` on the archive; PR fixing `tm.packs`.*

## 2026-10-08 — Pack ingestion and the 16colo mirror

**Before SAUCE, groups signed their files with the extension.** In 1990–1993 packs, files named
`.MIR` (Mirage), `.SDA`, `.LTD`, `.TRI`, `.BAD` are ANSI art: 924 of 929 contain ANSI escape
sequences. Nothing in the name says "ANSI"; the group's tag took the place of the format. The
SAUCE record, which states the format, the author and the group inside the file, appears in
1994. Recognizing art by its content found 2,739 ANSI files of 1990–1993 that extension and
SAUCE missed. *Evidence: local ingestion of the 304 packs of 1990–1993; `tm.packs._art_format`;
PR #36. Story: how a signature moved from the file name into the file.*

**The scene wrote its typography into file names.** A 1994 pack (`1994/ac!-05l.lha`) names its
music `íCE-sTATION-zEBRA.Mo!`, using the CP437 letter `í` for the "i" of iCE; a 1992 pack
(`1992/ace-r2.zip`) has `A∙C∙E.ANS` with CP437 middle dots. The stylized spelling of group
names (lower-case first letter, accented i) reached the 8.3 file name. Today's tools mangle
these names unless told the files are DOS. *Evidence: ADR 0013, `tm.archives._dos_name`.*

**The oldest packs use compression nobody reads any more.** 32 packs of the mirror, none after
2002 and 12 of the 295 packs of 1990–1993, hold files compressed with PKZIP 1.x methods (shrink, implode). Python
cannot read them; one popular extractor (`unar` 1.10.1) returned wrong bytes for 155 of 236
files of one archive without failing. Only Info-ZIP read them all correctly. Keeping the early
years readable is an active effort. *Evidence: ADR 0013.*

**About one pack in eighteen is a RAR, and three formats from BBS days survive.** 321 RAR, 15
LHA / LZH and 8 ARJ archives among 5,860; 7-Zip's official build reads the RAR files that free
readers do not. *Evidence: ADR 0013; rsync listing of `archive-pack`.*

**Artpacks carried music and pictures, and those outweigh the art.** In the extracted packs,
MP3 files are 27 % of the bytes and JPEG 24 %; all the textmode files together (about 127,000)
weigh about 1 GB of 12.2 GB, 8 KB on average. 16colo's own PNG renders of the art (19.6 GB)
weigh more than everything in the packs. *Evidence: rsync listing of `pack`, source note.
Story: what a "pack" was, beyond the drawings.*

**The archive is a portrait of the mid-1990s.** 3,224 of the 5,485 packs date from 1993–1997;
2005–2012 hold 88 together, then releases pick up again from 2013 (390 packs to 2026). A sample
drawn at random from the whole catalogue would be a sample of 1995–1996. *Evidence: API v1
`/year/`, source note. Coverage: 16colo only; the decline may partly be one of archiving.*

**Six packs are deliberately withheld.** The mirror refuses `1997/root05.zip`,
`2000/bongo.zip`, `2000/plenty.zip`, `2004/aclv5.zip`, `2005/cphart15.zip` and
`2011/cph.artpack.24.back.in.business.2011.zip` ("Permission denied"); the forum mentions packs
kept from download on purpose. Why each is withheld is not recorded here and should be asked,
not guessed. *Evidence: `data/16colo/rsync.log`, 2026-10-08.*

**The same file travels between packs.** In 1990–1993 alone, 741 files appear in two packs or
more: logos, info files, and 16colo's yearly collections (`1990.zip`, `1991.zip`…) that gather
loose files. Identity by hash links every appearance. *Evidence: `set_member` rows after local
ingestion. Story: re-releases, and which works circulated most.*

**An early ANSI is about one screen.** The 7,225 ANSI files of 1990–1993 are all 80 columns
wide; half are 29 rows or fewer, nine in ten 120 rows or fewer, the longest 2,749 rows.
*Evidence: `decoding` rows after local decoding. Coverage: 1990–1993 only.*

**16colo's tags are hand-curated metadata, unevenly spread.** Artists, groups and content tags
(`logo`, `memberlist`, `infofile`, `ansimation`, `ripscrip`, `teletext`, `wide`…) were added by
people; Mistigris alone has 14,141 tagged files. They describe where curators worked, not the
make-up of the archive. *Evidence: 16colo tag page, noted by the owner.*

**The archive holds more archives than it lists packs.** The mirror has 5,862 pack archives;
the API counts 5,485 packs. Not explained yet. *Evidence: source note.*

## 2026-10-07 — Spike 0001, ansilove parity

**SAUCE heights often count one row too many.** Many files declare a height that includes the
CR LF ending the last line; the drawn canvas ends one row earlier. *Evidence: spike 0001.*

**Without its EOF byte, the SAUCE record is drawn as art.** When no 0x1A byte precedes the
record, ansilove prints the metadata at the bottom of the image. *Evidence: spike 0001.*

**Choosing by hand skews the sample.** Of five packs picked "almost at random" for the spike,
three date from 2014. *Evidence: spike 0001 corpus; the reason D1 is drawn by stratum.*
