<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0005. Take the reference VGA font from libansilove

- Status: Accepted
- Date: 2026-10-07
- Deciders: Claude, approved by Nicolas Bridelance

## Context

Rendering needs the IBM VGA 8×16 ROM font as raw bitmaps. The rendering report recommends VileR's
Ultimate Oldschool PC Font Pack (CC BY-SA 4.0), but its download page is behind a captcha. The
foundation document chooses ansilove as the conservation renderer.

## Decision

Extract `font_pc_80x25` from libansilove's sources (BSD-2-Clause) with
`scripts/font_from_c_header.py` into `corpus/fonts/ibm-vga-8x16.f16`. Profiles reference it by
SHA-256.

## Alternatives considered

- **VileR's pack**: the most thorough collection, needed later for other video cards; not
  reachable automatically today.
- **Linux console fonts**: unclear provenance and licenses.

## Consequences

- The museum's renderings and ansilove's start from the same glyphs, which makes comparisons
  meaningful.
- It reproduces hardware quirks (the lower half block is 9 rows high).
