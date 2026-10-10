<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Agent instructions

Read `CLAUDE.md` for repository conventions and invariants. Its Claude-specific
commit attribution applies to Claude; use truthful attribution for other agents.

For installation and resumption, read `METS_TOI_BIEN.md`, then follow
`docs/setup/PROTOCOLE.md`. Maintain `docs/setup/CHECKLIST.md`,
`docs/setup/JOURNAL.md` and `docs/setup/REPRISE.md` with actual evidence.
Read the relevant setup modules before each action. Before code changes and
validation, apply module 06; after stabilization, apply module 07. Preserve
existing work and documented intentional debt. Use the repository's stricter
cleanup threshold when applicable. Track changes in the existing task or journal.
For UI changes, apply module 08 and inspect rendering and interactions.
For integrations, costs, contracts, access, security and legal questions, apply
modules 09–14 respectively; available capabilities do not authorize publication,
paid services, changes to remote access, or disclosure of private backups.

## Local migration

The baseline is `feat/explorer-works-v6` at
`e8f36933b82a883bb86d759c041eaf1fc2c685d7`, with preserved research edits.
Do not run `just setup` or `just migrate` before restoring the SQL dump.
Do not commit migration archives, dumps, storage objects or original artworks.
Machine-private files are excluded through `.git/info/exclude`.
Python 3.12 and frozen uv dependencies are required; Node >=24 and pnpm 12.3.4
are the web requirements. `just check` is the full validation command.
The offline research explorer uses `datasets/build/works/7` and private derived
S3 objects, listens on 127.0.0.1:8737, and is started with `just explore`.
See the setup checkpoint for commands actually verified on this machine.
