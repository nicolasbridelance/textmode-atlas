<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0002. Build on the target architecture from the first line

- Status: Accepted
- Date: 2026-10-07
- Deciders: Nicolas Bridelance

## Context

The first visible deliverable (one work on screen) could be reached faster with a standalone
page that decodes ANSI in the browser. Everything built that way would have to be redone: the
foundation document puts decoding in the Python pipeline, display rights in `tm export`, files
in a public bucket.

## Decision

Every piece is built where and how the foundation document places it, even for a proof of
concept. The site reads grids exported by the Python pipeline; it never decodes ANSI itself.
Exploration that must not follow this rule happens in spikes (0001).

## Alternatives considered

- **Quick standalone prototype, rebuilt later**: faster to the first image, but the rebuild is
  certain and the prototype tends to survive.

## Consequences

- The first image on screen comes later, after decoder, storage and export exist.
- No work is ever thrown away, and the invariants hold from the start.
