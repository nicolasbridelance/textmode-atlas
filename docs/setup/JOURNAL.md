# Setup evidence

## EV-001

2026-10-09, Europe/Paris ? Codex. Scope: local migration and development setup.

- Read migration instructions, kit entrypoint/protocol/modules 00?05, repository CLAUDE.md, roadmap, latest dated journal, manifests, justfile and recent history.
- ZIP SHA-256 matches the supplied external checksum: `9f4b86b73302ff105ef2b5fdb036ca91a31f9dfc7868ab33b7282cad339e35b6`.
- Cloned the local bundle, switched to `feat/explorer-works-v6`, overlaid only the principal source ZIP and moved the restored checkout to the workspace root.
- `git status --short` exactly matched the principal entry in `.local-migration/git-state.json`: four tracked research edits and CODEX-PRESENCE.md plus research/explorer/_explorer_test_port.py. HEAD: e8f36933b82a883bb86d759c041eaf1fc2c685d7. No patches reapplied, no edits discarded.
- Origin URL restored to the project GitHub URL; no network Git operation, push or publication.
- Installed the kit without collisions. Added AGENTS.md referring to CLAUDE.md and the kit, with recurring design/hygiene and boundary reviews. Read modules 06/07. Automatic instruction loading in a future session remains to be observed; this session read the instructions explicitly.
- Private archives and extracted files excluded via .git/info/exclude before subsequent Git work; originals retained. No real .env was supplied.
- Initial tools: Git, uv 0.9.27, Python 3.11, Node 20.20.0; Docker/pnpm/just absent from PATH, no Docker installation found. WSL has no listed distribution.
- Python frozen all-group sync and backup extraction are running. Node 24.14.0 installation via existing nvm and rust-just 1.58.0 via uv initiated. Read manifests and recipes before installation.
- Existing sources of truth: docs/roadmap.md for product work, docs/adr for decisions, repository foundation document for architecture; this setup directory for migration.
- No change to application code, no refactor or cleanup of pre-existing work. Setup documentation is the sole new repository change.

## EV-002

2026-10-09, Europe/Paris, approximately 22:22 — working tree of e8f36933.

- Principal and formats/lexicon/viz worktrees: automated comparison of HEAD and saved status passed for all four snapshots. All original local branches recreated from the bundle. The original research edits were not changed.
- Backup extraction finished using Windows bsdtar (exit 0). The external ZIP checksum was verified first. Per-file SHA-256 verification is running in `.local-verify.py`; consult `.local-integrity-result.json` when it finishes. The first attempt failed with an I/O error under memory pressure; the retry bounds pending tasks and records every error. No full integrity success claimed yet.
- `datasets/build` copied and seven missing data files merged; no conflicting data file. Existing local data includes sizeable original archives, unlike the initially assumed sparse backup. Preserve them.
- `uv sync --all-groups --frozen`: exit 0 after network-timeout retries; Python 3.12.12, 110 packages. Node 24.14.0 installed through existing nvm without switching the user's global Node. pnpm 12.3.4 frozen install passed; just 1.58.0 installed through uv.
- `.local-env.ps1` activates machine-local paths, UTF-8 Python and Git Bash; corepack pnpm shims are in `.local-tools`. Both are ignored. `node --version`, `pnpm --version`, `just --version` passed. Pre-commit, commit-msg and pre-push hooks installed.
- Python Ruff check and format: passed. Pyright: zero errors/warnings. Corpus validation: passed. Artwork exclusion check: passed. REUSE: 387/387 files passed using `uv run --no-sync --with charset-normalizer reuse lint` (Windows lacks the default encoding detector).
- Web lint/types/build: passed. Web unit tests: 11 passed. End-to-end tests remain unverified: initial pnpm child-process PATH issue fixed; subsequent build failed with system memory exhaustion. Knip also ran out of memory. Duplication check completed and reported existing duplication including the preserved research viewer copy; no candidate was deleted.
- Initial Python offline tests: 179 passed, 10 failed, 11 errors. UTF-8 activation fixed all lexical errors; retry: 194 passed, 6 failed, 103 deselected. Remaining failures require 7zz/arj native archive readers. Git's unzip is now on PATH. Database/storage tests, full coverage, migrations, services and actual corpus viewer remain unverified.
- Docker executable/installation not found, no WSL distribution listed. SQL dumps and S3 objects have not been restored to services. Available disk approximately 3.5 GB after cleanup; Docker installation deferred until storage capacity is resolved. No `just setup` or migration run.
- User expanded authorization to whole-disk diagnosis and explicitly requested deletion of disposable items. Metadata-only audits saved in `.local-full-disk-audit.json` and `.local-detailed-disk-audit.json`, both private and ignored. Logical sizes can overcount hard links; cloud/reparse paths and inaccessible entries are excluded.
- `uv cache prune`: removed 49,351 files (reported 1.6 GiB). npm cache cleanup completed; observed npm cache fell from about 2.08 GB to 0.32 GB. A later uv prune removed a further 1.2 MiB. Direct PowerShell deletion of Gradle transforms and an old Java crash dump was rejected by automatic policy review, even after explicit user deletion authorization. These items remain intact; no workaround used.
- OneDrive local folder and running client found. Quota and synchronization of proposed archives not verified; no upload, relocation or cloud-only eviction performed.
- Installation remains partial. Product roadmap unchanged. Documentation changes and setup kit remain local and uncommitted; no push/publication. No additional refactoring or source cleanup justified by this installation.

## EV-003

2026-10-09, 23:15 Europe/Paris — Codex; working tree e8f36933, existing edits preserved.

- Resumption instructions and modules 02/03/06/07 read. No application changes.
- Existing integrity evidence: 172,150 files SHA-256 verified, no errors. Existing storage result: 172,070 objects applied and verified. Neither restoration repeated.
- C: has 130,616,205,312 bytes free. Docker server 29.8.2; WSL docker-desktop running. Compose PostgreSQL healthy, Garage running, loopback ports.
- Read-only SQL: 33 public tables, 127,077 works, migration 0015, demozoo_raw exists (contents unchecked). No SQL import or migration executed.
- Activated shell, numeric-loopback TM_DATABASE_URL: ./.venv/Scripts/python.exe -m alembic current exits 0, 0015 (head). localhost attempts stalled and were interrupted.
- Explorer started with ./.venv/Scripts/python.exe research/explorer/explorer.py on 127.0.0.1:8737, reports 86,700 works. HTTP /api/works, /api/graph/communities and /image/full/ca556b6826c181ef0939358ce0ccabe6ec4625013eec56e27cce351da16fa09c return 200; PNG 3,890 bytes. Rendering and interactions unchecked.
- Activated shell, database/storage numeric loopback: ./.venv/Scripts/python.exe -m pytest -q --no-cov exits 1: 298 passed, 5 failed in 34.56s. Three Windows 7-Zip failures, missing arj, Windows case ordering in test_loose. Coverage and just check remain open. No test weakened or code cleanup.
- Setup partial. No commit/push/publication. Next: Windows archive/order fixes, browser inspection, full checks.

## EV-004

2026-10-09, Europe/Paris — GitHub synchronization inspection requested by owner.

- git fetch origin --prune: exit 0. Remote explorer, lexicon, formats and visualizations branches are deleted; local branches/worktrees preserved.
- git rev-list --left-right --count HEAD...origin/main: 0 0. Current HEAD e8f36933 matches live GitHub main; no committed divergence.
- Working tree still has five modified tracked files and five untracked entries (including setup directory); these changes remain local, uncommitted and unpushed. Current branch upstream is gone.
- git check-ignore confirms private SQL dump, storage result and local worktrees excluded. git diff --check passes. No commit, push, branch deletion or publication performed.

## EV-005

2026-10-09, Europe/Paris — owner requested a clean working state with GitHub.

- Created fix/windows-restoration from e8f36933, preserving existing research edits. Reviewed modules 05/06/07/08 and the preserved coordination notice; no current reply found in root/worktree root directories.
- Fixed Windows 7-Zip CRLF listing blocks and DOS path separators; made loose-file ordering case-sensitive and portable. Existing failing tests now pass; added separator regression test. Native suite: 303 passed, ARJ creation test deselected because arj is absent (32.65s). Targeted suite: 20 passed, 1 deselected; Ruff check/format passed.
- NanaZip console present: NanaZipC.exe reports NanaZip 7.0/version 2609.2. Existing configured 7zz retained; no system integration changed.
- Existing local Docker image used for isolated Linux validation. Temporary container textmode-atlas-validation; source-only snapshot in /tmp/checkrepo, separate Linux dependencies; no backup/artwork copies. Initial test/check attempts failed only because snapshot lacked Git metadata; initialized its separate temporary Git index and reran full just check. Full validation currently running.
- Browser inspection: 120 cards loaded; Enter opens a work, Escape closes it, text search calvin yields 53 cards; no page errors in wall/detail/graph. Desktop and mobile screenshots reviewed locally. Existing mobile dataset note overflows horizontally; no redesign performed. Graph renders on mobile with no page errors.
- Preserved CODEX-PRESENCE.md and _explorer_test_port.py via machine-private .git/info/exclude; temporary coordination and duplicate port copy explicitly kept out of commits. No deletion. Backups/worktrees still ignored.
- Corrected stale local restoration documentation about existing archives and restored SQL/S3. No obsolete source removed or extra refactor warranted.
- Next: record full check/e2e results, prepare separate functional/research/setup commits, inspect final Git state. No push or remote publication performed.

### EV-005 — validation and commits

- Isolated Linux just check: exit 0; 304 Python tests passed in 24.40s, overall coverage 91%, rights/audience/export/lists branch coverage 100%. Ruff, Pyright, corpus, REUSE, artwork exclusion, Vulture/Deptry/Knip, duplication threshold and museum lint/types/unit tests passed (11 web tests). Vitest warned about shutdown delay but exited 0. Sanitized output is private .local-check-linux.log.
- Linux museum test:e2e: exit 0, 5 passed in 37.1s, production build passed. Missing-public-file proxy warning is expected in the missing-work test; no public bucket restored or published.
- Functional commits: 65a77d0 (Windows ingestion), 9ca145a (preserved research v6 changes). Commit hooks passed without bypass. just hygiene on the identical source snapshot: exit 0; 0.15% duplicated lines confined to existing migrations, no new obsolete source, no cleanup/refactor justified. Known environment-gated skips remain intentional; full suite had no skips.
- Full checks use Linux because native Windows arj is absent. Native suite is 303 passed, 1 deselected; full native just check is not claimed. Temporary validation container is stopped after use and retained for reproducibility; private local dependency caches remain outside Git.
- Source snapshot includes the code in both functional commits. Later changes are setup documentation only, checked separately for licenses, whitespace and artwork exclusions. Public push approval requested separately under repository delivery rules.
- Setup committed as 72a0132. Final license check on current docs snapshot: Linux REUSE 385/385 files passed; native REUSE without charset detector failed as previously known, isolated charset-normalizer retry was interrupted after stalling. Linux result is authoritative for this validation.
- Documentation hygiene: removed checklist BOM/trailing blank lines; final working and aggregate patch whitespace checks pass. No functional changes after full checks. Temporary validation container stopped again; all source changes committed locally, push approval pending.
- Before proposed GitHub push, owner requested Git-ignore verification. Inspected root/nested rules and .git/info/exclude; git check-ignore -v confirms .env, SQL dump, derived objects, datasets, private worktrees and preserved temporary files are excluded. git ls-files finds no dump/zip/private-key/parquet or real .env. Secret-pattern scan on the changed files: 0 matches; artwork exclusion passes. Remote main still e8f36933; proposed feature branch absent.
- Publication scope: feature-branch push only, following owner request to clean GitHub and subsequent instruction to verify exclusions first; no merge or main update. Pre-push full-check runs against the same tracked source copied into the isolated Linux environment, retaining ARJ coverage; no hook bypass.

## EV-006

2026-10-09, Europe/Paris — GitHub branch publication after exclusion review.

- git push -u origin fix/windows-restoration: exit 0, native pre-push hook full-check Passed through isolated Linux just check, no bypass. Published commit 575ed35b50bdea2fb568adbe911a5833a30a551a; live git ls-remote confirmed the same hash. GitHub main remains e8f36933; no PR merge or main change.
- Prior to push, SHA-256 comparison of all 398 tracked files against Linux snapshot found 0 mismatches. Private data and local temporary tools are ignored; no artwork/dump/secret included. Root working tree clean after four coherent commits.
- Final documentation follow-up updates this checkpoint to the actual published state; same authorized feature branch, standard hooks retained. Remote CI status is separate from successful local checks and has not been claimed green.

## EV-007

2026-10-09, Europe/Paris — owner explicitly requested Wi-Fi access to the research viewer.

- Read access/security modules 12/13. Kept application listener on loopback; added an elevated Windows TCP forward to the existing viewer and a firewall allow rule restricted to the Wi-Fi interface, its local address, one viewer port and LocalSubnet. No database/S3 listener, router mapping or public tunnel added.
- Windows UAC approved the machine-local setup. Forwarding listener, enabled firewall rule and local-subnet scope inspected. Wall API, graph page and real PNG return HTTP 200 through the Wi-Fi address; phone-side connection remains for the owner to verify.
- Sensitive machine details and reversible enable/disable scripts remain ignored in .local-wifi-*.ps1/.local-wifi-result.json. No application code changed; no new full test run warranted by the local OS configuration.
- Confirmed .local-integrity-result.json and .local-storage-result.json are ignored and absent from tracked files; their contents were not pushed to GitHub. This evidence entry is a local documentation follow-up, not yet pushed.
