<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0015. Set aside SAUCE records whose binary fields are corrupt

- Status: Accepted
- Date: 2026-10-08
- Deciders: Claude (autonomous mode, ADR 0008); Nicolas Bridelance reviews afterwards
- Extends: [0012](0012-explicit-versions-for-decoders-and-renderers.md) (decoder version 2)

## Context

The decoder drew each file at its SAUCE width. After decoding all of 16colo, about 135 grids
had 8,224 to 30,061 columns. Their records begin with `SAUCE00`, but the binary fields that
follow are not numbers:

- **text overflowing into them**: `1997/poly0197.zip/EA_INK.ASC` has the group
  `Polyester` followed by `-EnCrYptEd by iLL`, which runs over the date, the size and the types
  (data type 98, file type 121: `b`, `y`);
- **a field one byte too long**: in `1995/rise0395.zip` and `1996/moz9604a.zip` the author
  takes 21 bytes, and every field after it is shifted; width `0x5000` is 80 in the wrong byte;
- **spaces as padding**: `1996/bdp-0396.zip` and `1995/quad0495.zip` fill the high bytes with
  `0x20`, so 80 columns read as `0x2050` = 8,272 and the size as `0x2020xxxx`.

At these widths the art lies on one or a few rows. A width cap would cut the real wide works:
about fifty grids of 260 to 2,660 columns, among them `2017/impure67.zip/us-train.ans`, whose
records are coherent.

## Decision

A record is set aside when it shows evidence that is impossible in a well-formed one:

- `type_out_of_spec`: a (data type, file type) pair that SAUCE v00.5 does not define;
- `size_exceeds_file`: an original size larger than the whole file the record ends.

The decoder then draws at the default width (80), and the renderer uses none of the record's
flags (iCE, letter spacing). The evidence is stored in `decoding.sauce_problems`; an empty
array means no record or a coherent one. `artifact.sauce` keeps the record as it was written.

The files set aside wait for an interpretive reading that restores the intended values (for
instance re-aligning a shifted record). That reading will be an assertion signed `algo:`, next
to the record, never in its place.

## Alternatives considered

- **Cap the width** (at 255 or 1,000 columns): cuts real wide works, and keeps the wrong width
  of corrupt records under the cap.
- **Require the size field to match the content exactly**: over a thousand ANSI and ASCII records
  with a valid type declare a size of zero, or one smaller than the file but not its content
  (written by tools that left it blank, or before a last edit); their width is right, and this
  test would throw it away.
- **Quarantine the works**: the art is intact, only the 128-byte record is wrong; excluding
  the works would lose them for a metadata fault.
- **Repair the record during decoding**: restoring is interpretation, and must be signed and
  separate from the source (invariants 2 and 5).

## Consequences

- Decoder version 2: every art file is decoded again, and the grids of version 1 stay under
  their own keys.
- Works set aside can be listed with `select … from decoding where cardinality(sauce_problems) > 0`.
- Where ansilove would trust such a record, our grid departs from it on purpose.
- The defects are traces of the tools and groups that wrote them, and are recorded as such in
  the field notes.
