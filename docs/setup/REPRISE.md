# Setup checkpoint

2026-10-09, Europe/Paris — local development ready; broader installation audit remains partial.

Branch fix/windows-restoration, based on e8f36933. Functional commits: 65a77d0 (Windows archive handling and stable file order), 9ca145a (preserved explorer/graph v6 changes). Setup documentation commit follows. Temporary coordination and port-copy files are preserved through local Git exclusions; private backups remain excluded.

Integrity: 172,150 backup files verified, 172,070 derived S3 objects verified. PostgreSQL migration 0015 (head), 127,077 works; Demozoo database exists, contents unchecked. Do not repeat SQL import or delete tables.

Activate . ./.local-env.ps1. Database commands work with 127.0.0.1 in TM_DATABASE_URL; localhost stalled during inspection. Explorer at http://127.0.0.1:8737 remains running. Wall/search/detail/graph and keyboard Enter/Escape inspected on desktop/mobile. Existing mobile dataset-note overflow remains.

Validation (EV-005): Linux just check exit 0, 304 Python tests, 100% coverage for display/audience/export rules, 11 web unit tests; 5 e2e tests and production build pass. Hygiene passes; migration duplication is intentional. Native Windows: 303 passed, 1 ARJ test deselected; arj absent. NanaZip console exists but project reader remains 7zz.

Temporary textmode-atlas-validation container holds isolated /tmp/checkrepo and Linux tools; stopped after use, retained for reproducibility. No service/storage deletion. Public bucket restoration and full access/security/legal/accessibility audit are still open; no publication compliance claim.

GitHub main matched e8f36933 at last fetch. Feature upstreams were deleted; preserved local worktrees remain independent. Branch push awaits explicit owner response; no push or publication yet. Next product work follows docs/roadmap.md. See JOURNAL.md#ev-005 for commands and limits.
