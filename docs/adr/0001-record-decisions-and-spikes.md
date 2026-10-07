<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0001. Record decisions as ADRs, explore with time-boxed spikes

- Status: Accepted
- Date: 2026-10-07
- Deciders: Nicolas Bridelance, Claude

## Context

The project will be built over many sessions, by an agent whose memory does not carry over and,
later, by contributors. Decisions were scattered across the foundation document, the session
journal and commit messages: enough to know what happened, not to find why a choice was made or
what was rejected. Meanwhile, the rule "target architecture from the first line" (0002) forbids
throwaway prototypes, yet some questions can only be answered by trying.

## Decision

- Decisions that are hard to reverse, have real alternatives, or depart from the foundation
  document are recorded as ADRs in `docs/adr/`. The foundation document states the outcome and
  links the ADR.
- Unknowns that block a decision are explored in **spikes**: a written question, a time box, a
  `spike/NNNN-topic` branch that is never merged, and a report in `docs/spikes/`. The decision
  that follows is an ADR; the production code is written anew on a normal branch.

## Alternatives considered

- **Decisions only in the foundation document**: mixes the what and the why, and loses the
  rejected options. The document would grow into a history.
- **Decisions only in the journal**: chronological, hard to find, never marked superseded.
- **Prototype on feature branches**: experiment code drifts into production by inertia.

## Consequences

- One more file per significant decision; the index in `docs/adr/README.md` stays current.
- Spike code never reaches `main`; what it teaches does, through the report and the ADR.
