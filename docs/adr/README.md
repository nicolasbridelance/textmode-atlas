<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Architecture decision records

One file per decision that is hard to reverse, has real alternatives, or departs from the
[foundation document](../Le%20caractère%20comme%20matière%20—%20document%20de%20fondation.md).
The foundation document says *what* the system is; an ADR says *why*, and what was rejected.

- File: `NNNN-short-title.md`, numbered in order, never renumbered.
- Status: `Proposed` → `Accepted` (by the project owner), later `Superseded by NNNN` or
  `Deprecated`. An accepted ADR is not rewritten: a change of mind is a new ADR that supersedes it.
- A decision that comes out of a [spike](../spikes/) cites the spike report.

## Template

```markdown
# NNNN. Title in the imperative

- Status: Proposed | Accepted | Superseded by NNNN
- Date: YYYY-MM-DD
- Deciders: …

## Context
The forces at play, facts first.

## Decision
What we do.

## Alternatives considered
Each option, and why it lost.

## Consequences
What becomes easier, what becomes harder, what we must now do.
```

## Index

| ADR | Decision | Status |
| --- | --- | --- |
| [0001](0001-record-decisions-and-spikes.md) | Record decisions as ADRs, explore with time-boxed spikes | Accepted |
| [0002](0002-target-architecture-from-the-first-line.md) | Build on the target architecture from the first line | Accepted |
| [0003](0003-garage-for-local-object-storage.md) | Use Garage for local S3 storage | Accepted |
| [0004](0004-english-repository-multilingual-museum.md) | English repository, multilingual museum | Accepted |
| [0005](0005-reference-font-from-libansilove.md) | Take the reference VGA font from libansilove | Accepted |
| [0006](0006-display-requires-permission.md) | Show a file only with permission; metadata otherwise | Superseded by 0009 |
| [0007](0007-mechanize-code-and-commit-rules.md) | Mechanize code and commit rules | Accepted |
| [0008](0008-autonomous-development.md) | Develop in autonomous mode: green CI is the merge gate | Accepted |
| [0009](0009-show-what-the-scene-released.md) | Show what the scene released freely, credit it, withdraw on request | Accepted |
