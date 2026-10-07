<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Golden artifacts

Works made for the project and dedicated to the public domain (CC0). They are the only artworks
in the repository. Each is rendered on every build; output hashes must not change.

`renderings.json` records, for each one, the SHA-256 of the RGB pixels of its conservation
rendering (settings from its SAUCE record, scale 1). The test suite checks that `tm_render`
reproduces them; `just parity`, run in the development image by CI, checks that the pinned
ansilove draws the same pixels (ADR 0010). A change to either is a deliberate update of this file.

They are made by Claude for the museum's tests and showcase. They are not scene art and are
never presented as such.

| File | What it exercises | Made with |
| --- | --- | --- |
| `ansi/horizon.ans` | 80 columns, 40 rows, SAUCE record (9px, blink mode), full rows without CR LF, half-block pixels with two colours per cell, shade gradients, CP437 punctuation | `ansi/horizon.py` (fixed seed: regenerating gives the same bytes) |
