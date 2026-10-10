<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0032. Excerpts: the museum takes the textual artwork where it finds it, credited, withdrawable

- Status: Accepted
- Date: 2026-10-10
- Deciders: Nicolas Bridelance (owner: "une signature sur un forum de l'époque, c'est aussi
  possible de l'intégrer … on peut prendre notre appareil photo et aller prendre les photos
  nous-mêmes … nous ne copions pas les œuvres en entier, juste des artworks textuels, en
  créditant les auteurs, avec la possibilité de take down"); written by Claude
- Amends: ADR 0009 (what may be shown), ADR 0030 points 4 and 5, ADR 0031 (ways of holding);
  foundation document, display rule. The lawyer's review before M4 covers this ADR too.

## Context

ADR 0009 shows what the scene released and a scene archive still holds. ADR 0030 held back
screens and documents of software published outside the scene, and ADR 0031 left the web era
(forums, personal pages, Usenet, captures in the Wayback Machine) as `record` holdings: a
description and a link. Character art is text: it turns up anywhere, in a forum signature, a
game's manual, a splash screen of abandonware, a page saved by the Wayback Machine. Waiting for
someone to have archived it as a file means most of it will never enter the museum.

A photographer of graffiti does not wait for a pack of photographs: he takes his own. The
museum can do the same with text: cut out the artwork, and only the artwork, from where it
sits, and say exactly where it was cut from.

## Decision

1. **A new way of holding: `excerpt`.** The museum's own capture of a textual artwork found
   inside something larger: lines of a web page or a post, a screen of a program, the ASCII
   header of a manual. The excerpt is the original the museum stores, write-once; the larger
   thing is never stored whole.
2. **An excerpt says where it was taken.** Its record names the page or file it was cut from
   (a live URL or a Wayback Machine capture, with its date), how it was cut (lines, a
   selector, a screen and a moment), when, and the credit: the author as signed, or "unknown".
   The recipe is precise enough to cut it again from the same capture (invariant 3).
3. **Shown, credited, withdrawable.** `can_display()` shows a work that is:
   - released by the scene and held by a scene archive (ADR 0009);
   - under a licence its author gave, or in the public domain (the licence is shown with it);
   - an excerpt with its credit and its source (this ADR).
   Withdrawal on request still wins over every case; the takedown address is on every record.
4. **Never the whole work of someone else.** Programs, games, manuals and pages are not stored
   whole unless the scene released them freely (ADR 0009) or a licence allows it; ADR 0030's
   ban on cracked and commercial programs stands. Abandonware sites (Abandonware France, formerly
   Lost Treasures FR, and others) are places to look and to cut from, not sources to mirror.
5. **Audiences apply** (ADR 0020): an excerpt is rated like any work.

## Consequences

- `Rights` gains `excerpt` (source URL, capture date, how it was cut, credit); the display
  policy has three ways to say yes, each tested; `rights.py` stays at full branch coverage.
- `tm acquire` takes excerpts: it fetches the page, cuts the lines the manifest names, stores
  only the cut, and records the fetch of the page.
- The registry's practices gain `excerpt` as a way of holding; most practices of the web era,
  of games and of software screens can now be held, not only recorded.
- Each excerpt depends on a page that may disappear; the Wayback capture, when there is one, is
  the stable reference.

## Alternatives considered

- **Records only for anything not archived as a file.** Rejected by the owner: the museum would
  miss most of the art outside the scene archives.
- **Store the whole page or program privately, show the excerpt.** Rejected: holding someone
  else's whole work is what the museum promised not to do; the recipe and the capture's URL are
  enough to check the cut.
