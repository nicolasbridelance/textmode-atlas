<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0031. A museum of every character art: a registry of practices, one representative first

- Status: Accepted
- Date: 2026-10-10
- Deciders: Claude (autonomous mode, ADR 0008), at the owner's request ("le périmètre est encore
  plus large que ça ! le but c'est le musée des arts du caractère, notre fonds est loin d'être
  complet ou même représentatif ou même d'avoir un représentant de chaque"); Nicolas Bridelance
  reviews afterwards
- Amends: foundation document, "Pratiques voisines" (Jacquard and punched cards are no longer
  out of scope); extends ADR 0030
- Relates to: lead I54 (a representative of every practice Wikipedia names), the
  [cartography report](../research/01_cartographie.md), the [source register](../sources/README.md)

## Context

The museum is a museum of the character arts: every practice that makes an image, a space, a
sound or a poem out of characters, on screens, paper, tape or air. Its holdings are one scene:
PC ANSI and ASCII of the artpacks, plus what textfiles.com kept beside them. Of the practices
the cartography report, the foundation document, ADR 0030 and the Wikipedia survey name, most
have no work at all (I54). Nothing lists them in one place, so nothing says what is missing.

Depth in one scene and silence on the others misrepresents the art. A museum can be honest
about a gap only if it knows its gaps.

## Decision

1. **A registry of practices**, `corpus/practices.yaml`, validated by `tm corpus check` like the
   other registries: each practice with a code, a label in every required locale, a family, the
   ways the museum can hold it, the candidate sources, the leads that concern it, and the
   artifact that represents it once one is held (its SHA-256 and its path at the source).
2. **Ways of holding**, from the most to the least direct: `file` (a digital original),
   `capture` (a screen read from a running program, with its recipe), `reproduction` (a scan or
   photograph of a physical object, level `conservation` with no digital original, as the
   foundation document already says of typewriter art), `record` (a description and a link,
   when no copy may be held or none exists).
3. **Breadth first.** The next acquisitions aim at one representative of each practice before
   more of any practice already held. A practice is held when a representative is named; a
   practice with only `record` is listed as such, never hidden.
4. **Representativeness is measured, not claimed.** Once each practice has a representative,
   the registry is joined to the database to count works per practice; the museum shows these
   counts with the gaps, and research datasets say which practices they cover.
5. **Nothing leaves the scope by being far.** Ancestors (Jacquard looms, punched cards,
   cross-stitch, mosaics, calligrams, micrography) enter as `reproduction` or `record`, as the
   museum's first rooms of history; ADR 0009, 0030 and the audience grid apply to every family.

## Consequences

- The registry starts with about eighty practices in fifteen families; most are not held.
- Every new source note says which practices it brings; every ingestion that brings a first
  representative updates the registry in the same pull request.
- A visitor-facing page of the practices, held or not, becomes possible from the registry
  (a room of the museum, after the owner's choices on the museography proposal).
- `record` and `reproduction` need fields the schema does not have yet (a work with no file);
  they come with the first such work, by migration.

## Alternatives considered

- **Keep the practices as prose in the foundation document.** Rejected: prose cannot be joined
  to the database, and it did not show the gaps.
- **Depth first in each scene, then the next.** Rejected by the owner's request: the museum would
  stay a museum of one scene for years.
