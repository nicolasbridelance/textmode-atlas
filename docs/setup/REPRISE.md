# Setup checkpoint

2026-10-10, Europe/Paris — local development ready; broader installation audit remains partial.

Branch feat/unified-museum, first functional commit e1b28b9 (baseline e8f36933), followed by the locally recorded discovery integration (EV-009). The owner requested one museum for exploration and scientific/vision interpretation. Pinterest/Instagram/Tinder and the presentation workshop are restored, with one navigation and one collection. Latest code is running and validated; hygiene passes. No push or main merge. Next product work: reviewed interpretation authoring/model evaluation, following docs/roadmap.md. Temporary coordination files and private backups remain excluded.

Integrity: 172,150 backup files verified, 172,070 derived S3 objects verified. PostgreSQL migration 0015 (head), 127,077 works; Demozoo database exists, contents unchecked. Do not repeat SQL import or delete tables.

Activate . ./.local/env.ps1 (machine-local files are gathered under .local/, see LOCAL-WINDOWS.md). Database commands work with 127.0.0.1 in TM_DATABASE_URL; localhost stalled during inspection. Unified museum at http://127.0.0.1:8737 remains running; `just museum` rebuilds and starts it (`just explore` alias). Restart after rights/audience changes. Collection, shared work, measures, locale switch, graph and publications inspected on desktop/mobile. Collection has no horizontal overflow at 390px. See docs/unified-museum.md for contracts and limits.

Validation (EV-008/009): Linux just check exit 0, 311 Python tests, 100% critical policy branch coverage, 26 web unit tests; final navigation checks and production build pass, 22 e2e tests pass. Real-corpus EN/FR discovery paths have one navigation, no mobile overflow and zero browser errors. HTTP checks deny metadata-only PNG/grid/text. Existing Vitest shutdown warning and migration duplication remain. Previous native Windows baseline: 303 passed, 1 ARJ test deselected; arj absent. NanaZip console exists but project reader remains 7zz.

Temporary textmode-atlas-validation container holds isolated /tmp/checkrepo and Linux tools; retained for reproducibility. No service/storage deletion. Public bucket restoration and full access/security/legal/accessibility audit are still open; no publication compliance claim.

GitHub main matched e8f36933 at last fetch. Earlier cleanup is published as origin/fix/windows-restoration through ea620a4; the unified museum is local, not pushed or merged. Preserved local worktrees remain independent. Next product work follows docs/roadmap.md, particularly reviewed model readings/authoring, not a separate viewer. See EV-005/006/008 in JOURNAL.md.

Machine-local Wi-Fi access enabled at owner request (EV-007) now serves the unified museum (EV-008). Keep its process running. Rooms and API return HTTP 200 through the existing forward. Exact address, firewall/forwarding evidence and reversible scripts are private files under .local/scripts and .local/evidence. Phone-side acceptance remains open. No model calls, new paid services or private-data publication.
