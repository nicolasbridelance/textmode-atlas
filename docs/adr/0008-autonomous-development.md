<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0008. Develop in autonomous mode: green CI is the merge gate

- Status: Accepted
- Date: 2026-10-07
- Deciders: Nicolas Bridelance

## Context

Claude builds the repository over many sessions. Waiting for a human review on every pull
request would make the owner a bottleneck; the owner delegates construction and asks to be told
what is needed from him.

## Decision

- Claude opens its own pull requests and merges them once every CI job is green. The owner
  reviews afterwards when he wishes; a problem found later is fixed by a new pull request.
- CI is therefore the gate: every rule that can be checked must be checked there (0007).
- Claude asks the owner only for what needs a person: accounts and access, secrets, contacts
  with third parties, legal or financial decisions, spending.
- Anything that leaves the repository on the owner's behalf (messages to artists, archives or
  radios, publication of works, payments) is prepared by Claude and sent by the owner.

## Alternatives considered

- **Required human review on `main`**: safer per change, but blocks the work between sessions.

## Consequences

- Branch protection on `main` requires the CI checks, not a review (to be configured by the
  owner: the Codespaces token cannot change repository settings).
- The journal and the roadmap are how the owner follows the work.
