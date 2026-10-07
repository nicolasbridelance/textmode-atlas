<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0007. Mechanize code and commit rules

- Status: Accepted
- Date: 2026-10-07
- Deciders: Nicolas Bridelance (rules), Claude (tooling)

## Context

`docs/vibe-coding-rules.md` sets code craft and repository hygiene rules, and separates what a
tool can decide from what needs judgment. Rules repeated in prompts cost context every session
and are applied unevenly.

## Decision

- Tools enforce what is decidable, blocking `just check` and CI: ruff and ESLint (complexity ≤ 8,
  nesting, magic numbers, print/console, commented-out code, TODO without issue link), vulture,
  deptry and knip (unused code and dependencies), jscpd (duplication).
- Commits follow Conventional Commits, checked by a `commit-msg` hook and in CI; a functional
  commit and its pruning are separate commits.
- `CLAUDE.md` keeps only what needs judgment, and the post-commit protocol.

## Alternatives considered

- **Rules in prompts only**: uneven, expensive in context.
- **Commitlint (Node)**: one more toolchain for a 40-line check.

## Consequences

- False positives are handled by configuration in the repository, with a reason.
- pnpm's minimum release age policy is kept for the same reason: supply-chain safety by default.
