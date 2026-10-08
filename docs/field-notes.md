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
