<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0033. The texts of a pack are works: NFO, FILE_ID.DIZ and text files

- Status: Accepted
- Date: 2026-10-10
- Deciders: Nicolas Bridelance ("Mais oui ! Bien sûr ! Il faut tout valoriser correctement"),
  on Claude's proposal (autonomous mode, ADR 0008)
- Amends: the ingestion of packs and loose files (`tm.packs`, `tm.loose`); applies ADR 0030
- Relates to: leads I99 (held is not shown), I100 (NFO and DIZ are not works)

## Context

Ingestion makes a `single` work of every art member of a pack (ANSI, ASCII, XBin…) and keeps
the other members as artifacts only. NFO, FILE_ID.DIZ and `.txt` files fell on the wrong side:
on 2026-10-10 the corpus held 5,662 NFO, 5,850 DIZ and 10,653 text files with no work, so no
decoding, no rendering and no place in the collection. Yet ADR 0030 puts NFO, DIZ, readme files
and member lists in scope, and the foundation document counts the NFO among the arts of the
character. The practices registry (ADR 0031) counted the NFO practice as held while no visitor
could see one.

They are CP437 text, the format the ASCII decoder already reads. Many are drawn: an NFO's
header logo, a DIZ's box, a member list framed in block characters.

## Decision

1. **A text member is a work.** A pack member or a loose file named `.nfo`, `.diz`, `.txt` or
   `.lit` becomes a `single` work, unless its bytes are binary (a signature, or a NUL byte). Its
   format stays `nfo`, `diz` or `text`: the use that distinguishes it from art (ADR 0030) is
   kept, and the collection can filter by it.
2. **Same rights and dates as the art beside it.** In a pack, the pack's scene publication
   (ADR 0009) and dating; loose, the archive's URL and the SAUCE date.
3. **Decoded like ASCII.** `tm decode` reads `nfo`, `diz` and `text` with the CP437 decoder, so
   rendering, features, text layer and datasets follow with no special case.
4. **Files already held are promoted** by `tm ingest documents`, idempotent: each text artifact
   with no work gets one, with the rights and dating of its first pack, or of its archive when
   loose. Originals are not touched (invariant 1).

## Consequences

- About 22,000 works enter the collection; they must be rendered, measured and published in the
  next `works` dataset.
- The EDA's art counts (`ART` in `tm.eda.chapters`) do not include documents: art and documents
  stay distinct in the figures, as the foundation document asks.
- Long documents (member lists, walkthroughs) will need a reading mode beside the framed grid
  (I101); until then they are shown as grids like the rest.
- A `.txt` may be anything a group put in a pack: news, a greeting, a poem, a list. They are the
  scene's own paperwork and are shown as such.
