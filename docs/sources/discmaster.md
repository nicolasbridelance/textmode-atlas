<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Source note: Discmaster

M0 note: access, limits and terms, checked at the source on 2026-10-09.

## What it is

[discmaster.textfiles.com](https://discmaster.textfiles.com/), "experimental": the files of
selected Internet Archive items (CD-ROMs, floppy disks, FTP site captures) extracted, identified
by [dexvert](https://github.com/Sembiance/dexvert) and searchable. Each file keeps the date it
carried on its disc or site. Contact: sysop@textfiles.com (textfiles.com, Jason Scott's).

## What it holds (its home page, 2026-10-09)

1,883,127,002 files from 43,856 items, 126.8 TiB; 518,961,860 text files, 52,242,712 archives.

## Access

- Search by BLAKE3 of a file's bytes, JSON output:
  `https://discmaster.textfiles.com/search?b3sum=<hex>&outputAs=json`. The answer is a list of
  copies, each with `itemid`, `fileid` (path inside the item, starting with the item's name),
  `filename`, `size`, `ts` (the file's date there), `b3sum` and dexvert's identification.
- No API documentation, no bulk dump. One request per file.
- `scripts/discmaster_witness.py` asks for every pack archive the museum holds, one request a
  second with our User-Agent, and keeps the answers in `data/discmaster/witnesses.jsonl`
  (local, never in Git).

## Terms

- None stated. The home page: "no cookies and no tracking and only errors and hit/search counts
  are logged."
- The files are the Internet Archive's items; Discmaster is a view of them. We keep only where
  and when a copy sits, never the files: no artwork comes from it.

## How the museum uses it

- **A witness, not a source of works.** A byte-identical copy of a pack on a shareware CD-ROM or
  an FTP capture says the pack existed there, at the date the file carries, independently of
  16colo's lineage (Q21, H8, lead I33). Dates are file dates on the medium: a copy can be later
  than the release, rarely earlier, so they bound the release from above.
- First probe: `acid-50a.zip` on `ftp.sunet.se`, 1996-10-13 ([register](README.md)).
- Later, the same search for single works (members), on a sample: works travelled outside packs.
