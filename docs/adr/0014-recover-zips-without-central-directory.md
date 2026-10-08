<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0014. Recover ZIP archives without a central directory with 7-Zip, checked by our CRC

- Status: Accepted
- Date: 2026-10-08
- Deciders: Claude (autonomous mode, ADR 0008); Nicolas Bridelance reviews afterwards
- Extends: [0013](0013-archive-readers-for-artpacks.md), which kept ZIP away from 7-Zip

## Context

After ingesting all of 16colo (5,858 archives), six ZIP archives could not be opened at all.
Python's `zipfile` needs the central directory at the end of the file; four of them have none
Info-ZIP can find either (`1994/itr-9401.zip` is exactly 65,536 bytes: a download cut at 64 KB),
and Python rejects the directory of a fifth (`1997/silk0197.zip`) that Info-ZIP can list. The
sixth, `2025/test.php00.zip`, is 20 bytes and not an archive.

A ZIP also records each member in a local header before its data, with the member's size and
CRC-32. 7-Zip 23.01 lists and extracts members from those headers when the central directory is
missing. On the five archives it recovers 151 members; in each truncated archive only the last
member, the one the cut went through, stays unreadable.

ADR 0013 kept ZIP away from 7-Zip because 7-Zip misread one of three test archives with PKZIP
1.x methods. That risk is about trusting 7-Zip's bytes, not about using it.

## Decision

When Python cannot open a ZIP, `tm.archives` lists it with `7zz l -slt -tzip`, extracts it with
`7zz x -tzip`, and keeps a member only if its size and CRC-32 match the local header, computed by
us as for Info-ZIP. Members that fail, or that 7-Zip does not write, are named as unreadable. If
7-Zip lists no member, the archive stays a `bad_archive` error.

The order for ZIP becomes: Python; Info-ZIP for members Python cannot decompress; 7-Zip for
archives Python cannot open.

## Alternatives considered

- **Leave them as errors**: five packs of 1994–2004 lost for a missing index, while their bytes
  are there.
- **Rebuild the central directory** (`zip -FF`) and read the repaired copy: one more tool, and
  it writes a new archive, which then needs its own checks; the original must stay untouched
  anyway.
- **Parse local headers in Python**: possible, but it would reimplement what Info-ZIP and 7-Zip
  already do, including PKZIP 1.x methods that Python cannot decompress.

## Consequences

- Five more packs have their files; 7-Zip's output is never trusted without our CRC check, so
  the reason of ADR 0013 still holds.
- Ingestion must run again on those packs: `tm ingest pack` completes them (ADR 0013 reruns).
- A member whose local header is wrong or missing is still lost; that is the archive's state, and
  `expansion` records it.
