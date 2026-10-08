<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0012. Version decoders and renderers explicitly, and guard the version with a source digest

- Status: Accepted
- Date: 2026-10-08
- Deciders: Claude (autonomous mode, ADR 0008); Nicolas Bridelance reviews afterwards

## Context

A `decoding` row is keyed by artifact, decoder and `decoder_version`; a grid in the derived
bucket follows the same key (ADR 0011); a rendering recipe records `renderer_version`. Those
versions are what lets the museum tell a result produced by old code from one produced by current
code, and decode again when the code changed (invariant 3).

Until now both were the `tm-render` package version, which nobody bumps: it is still `0.0.0`.
A decoder fix would leave every existing row looking current, and `tm decode` would skip them.
The failure is silent, and it concerns the data every later step builds on.

## Decision

`tm_render.versions` holds two explicit strings, `DECODER_VERSION` and `RENDERER_VERSION`, whole
numbers as text ("1", "2"…). The `decoding` rows, grid keys and recipes use them, and the
package version is no longer used for this.

A test guards them. It computes a digest of the code each version covers, from the syntax tree
(so comments, docstrings and formatting do not count), and compares it with the digest pinned for
the declared version in the test file:

| Version | Covers |
| --- | --- |
| `DECODER_VERSION` | `ansi.py`, `sauce.py`, `grid.py` |
| `RENDERER_VERSION` | `conservation.py` |

Changing that code without a new version fails the test. The message says what to do: bump the
version, add the new digest to the pins, and keep the old entries as history. The test requires
the declared version to be the latest pinned one; it cannot see a history entry being edited, so
that stays a point for review: an old line should never change in a diff.

## Alternatives considered

- **Bump the package version by hand**: relies on someone remembering; the failure is silent, and
  it is exactly what happened.
- **Use a digest of the source as the version**: nothing to forget, but the value is opaque, not
  ordered, and every harmless edit creates new rows and new grids.
- **Rely on the golden artifacts alone** (their pinned pixels): they catch what Horizon
  exercises, not a change in a branch Horizon never reaches, such as PabloDraw colour.
- **Git commit of the build**: ties results to a commit rather than to behavior; two commits
  with the same decoder would produce two sets of rows.

## Consequences

- A decoder or renderer change needs a deliberate step: one line in `versions.py`, one in the
  pins. Reviewers see it in the diff.
- A change that only moves code around (renaming a local variable) also changes the syntax tree
  and asks for a bump: over-decoding is the safe direction, and it costs one run of `tm decode`.
- Results of an earlier version stay in the database and in `tm-derived`; the current version is
  the one `tm decode` and `tm render` look for.
- The pin test holds the history, so it stays an audit trail of what each version was.
