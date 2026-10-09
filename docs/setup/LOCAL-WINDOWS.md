<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Windows migration

Private backup: `.local-migration/`; original ZIP is retained at the root.
Its SHA-256 is `9f4b86b73302ff105ef2b5fdb036ca91a31f9dfc7868ab33b7282cad339e35b6`.
The bundle and source snapshot restored the principal branch exactly, including
four tracked edits and two untracked research files. Other snapshots must remain
separate from this branch. No patches were reapplied.

Use `uv sync --all-groups --frozen` for Python dependencies. Native commands in
`justfile` require the Git Bash shell for POSIX recipes. Do not run the aggregate
setup or migration recipe before SQL restoration.

On this machine, run `. ./.local-env.ps1` in PowerShell to select the installed
Node 24 and pnpm shims, the Python virtual environment and UTF-8 defaults.
Read `JOURNAL.md` and `REPRISE.md` for current checks and remaining work.

PostgreSQL/pgvector and Garage are defined in `compose.yaml`; Docker is required
for that environment. Node 20 does not satisfy the web manifest. Do not replace
the storage engine or publish private research data to work around missing tools.

The migration backup omits most original archives and the public bucket. Existing
local archives were discovered separately and must be preserved. The restored
derived bucket supports the unified museum's local host; it does not restore
public exports. Preserve the source ZIP and dumps until local verification is complete.

## Scope, interfaces and risks

The foundation document and `CLAUDE.md` remain authoritative. Python workspaces
`ingest`, `renderers`, `analysis` and `api` produce versioned grids and datasets;
`apps/museum` consumes public exports or its local host's gated records. That host
consumes works/6, graph/2 and derived S3 objects; `just museum` (alias `just explore`)
serves collection, constellation and research together. See [the museum contract](../unified-museum.md).
SQL contracts live in Alembic migrations;
grid contracts and audience/display permissions have repository tests.

The principal workspace and all three restored worktrees match their saved
HEAD and pre-existing changes. They are independent; no snapshot was layered
onto another branch. Product priorities remain in `docs/roadmap.md`.

Private migration archives, SQL dumps and derived objects stay local and outside
Git. Source integrity is mandatory and originals are never rewritten. Public
distribution still requires the existing credit, rights and audience gates.
No external integration was activated and no account access changed. Connector
tools available to the agent are not project dependencies or publication consent.

The running Compose services bind to loopback. SQL is restored at migration 0015
and the derived S3 restoration has verified 172,070 objects. Agent
filesystem access is broad; GitHub protections and cloud access are unverified.
The principal risks are accidental backup publication, storage exhaustion,
overwriting pre-existing edits and migrating before dump restoration. Exclusions,
snapshot comparison, retained backups and the restoration sequence address these
risks; the owner remains responsible for access and retention decisions.

No new paid service or CI run is requested. Local disk and download use are real;
agent, existing cloud and CI billing are unknown, with no financial audit claimed.
No budget is inferred from quotas. Legal applicability, operational ownership,
retention and accessibility certification remain unassessed for publication.
The local setup does not change licenses, grant artwork rights or claim compliance.

UI sources are the museum Svelte components/localized messages and the retained
constellation runtime. Priority tasks are text search, graph navigation and work display.
Rendering, keyboard, focus and responsive checks require a running local museum;
reading these sources does not satisfy those checks.
