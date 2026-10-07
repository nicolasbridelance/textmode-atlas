<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0010. Render conservation PNGs from the grid; ansilove is the reference

- Status: Accepted
- Date: 2026-10-07
- Deciders: Claude (autonomous mode, ADR 0008); Nicolas Bridelance reviews afterwards

## Context

The foundation document named ansilove, pinned, as the renderer of conservation PNGs for ANSI,
XBIN and ASCII. Since then the pipeline has settled on one intermediate format, the grid: the
site draws works from it, features are computed on it, the timed replay reads its write offsets.
ansilove does not read our grid; it decodes the raw bytes again, with its own decoder.

Spike [0001](../spikes/0001-ansilove-parity.md) drew PNGs from our grid and compared them with
ansilove on 122 files: 96 of the 99 files in the VGA font are identical pixel for pixel (iCE,
blink, 8 and 9 px). The rest are a decoder gap on our side (PabloDraw 24-bit colour) and an
ansilove defect (the SAUCE record drawn as art when no EOF byte precedes it).

## Decision

`tm_render` draws conservation PNGs from the grid: the font named by the profile, integer scale,
no interpolation, 9th column for C0–DF, background from the profile (blink or iCE). The recipe
names `tm_render` and its version, the grid and font digests, and the PNG digest. ansilove stays
pinned in the development image as a reference: parity on the golden artifacts is checked in CI.

## Alternatives considered

- **ansilove for the PNG, the grid for everything else**: two decoders read the same bytes, so
  the downloaded image and the work on screen can disagree, and a decoding fix lands in one of
  them only. It also inherits ansilove's defects, and its SAUCE aspect stretch, which
  interpolates.
- **Patch libansilove to read our grid**: a fork of C code to maintain, for a drawing step that
  is about a hundred lines of Python.

## Consequences

- One decoding for the site, the analysis and the PNG: what is downloaded is what is shown, and
  every decoder fix reaches all three.
- The museum owns the correctness of its renderer; ansilove parity on the golden artifacts and
  spot checks on real packs (files kept local) are the guard.
- Recipes no longer depend on the container digest for rendering; they depend on the
  `tm_render` version and on the font and grid digests, all recorded.
- Systems without an ansilove reference (PETSCII, teletext…) follow the same path, as the
  foundation document already planned.
- The foundation document is amended in the same change (technical choices, recipe example).
