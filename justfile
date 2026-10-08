# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
#
# Project commands. `just --list` shows them all.

set dotenv-load

# List commands
default:
    @just --list

# Set everything up: dependencies, services, schema, storage
setup:
    test -f .env || cp .env.example .env
    uv sync --all-groups
    pnpm install
    pnpm --filter museum exec playwright install --with-deps chromium-headless-shell
    just services
    just migrate
    uv run tm dev storage-init
    just hooks

# Install git hooks: fast checks on commit, message rules, full check on push
hooks:
    uv run pre-commit install

# Start PostgreSQL and Garage, and wait until they are ready
services:
    #!/usr/bin/env bash
    set -euo pipefail
    if command -v docker >/dev/null; then exec docker compose up -d --wait; fi
    # Inside the dev container, compose has already started them next to it
    for _ in $(seq 60); do
        pg_isready -q -d "${TM_DATABASE_URL/+psycopg/}" \
            && curl -fs -o /dev/null "$TM_GARAGE_ADMIN_URL/health" && exit 0
        sleep 1
    done
    echo "services unreachable: $TM_DATABASE_URL, $TM_GARAGE_ADMIN_URL" >&2
    exit 1

# Apply database migrations
migrate:
    uv run alembic upgrade head

# Everything CI checks
check: lint typecheck test corpus licenses no-artworks unused duplicates web-check

lint:
    uv run ruff check .
    uv run ruff format --check .

typecheck:
    uv run pyright

# Python tests with coverage; `rights.py` must stay at 100% branch coverage
test *args:
    uv run pytest --cov --cov-report=term-missing {{args}}
    uv run coverage report --include='ingest/src/tm/rights.py' --fail-under=100

corpus:
    uv run tm corpus check

licenses:
    uv run reuse lint

no-artworks:
    uv run python scripts/check_no_artworks.py

# Unused code and dependencies (Python and TypeScript)
unused:
    uv run vulture
    for package in ingest renderers analysis api; do (cd $package && uv run deptry .); done
    pnpm run hygiene:unused

# Copy-pasted blocks
duplicates:
    pnpm run hygiene:duplicates

# ansilove draws every golden artifact with the recorded pixels (ADR 0010); needs ansilove
parity:
    uv run --frozen python scripts/check_ansilove_parity.py

# Post-commit pruning candidates (report only; see CLAUDE.md, post-commit protocol)
hygiene: unused duplicates
    @echo "── TODO / FIXME (each must link an issue)"
    @git grep -n -E "(TODO|FIXME)[(:]" -- . ':!docs' ':!*.lock' ':!pnpm-lock.yaml' || echo "none"
    @echo "── Skipped or expected-to-fail tests"
    @git grep -n -E "pytest\.skip|mark\.skip|xfail|\.skip\(" -- '*.py' '*.ts' || echo "none"
    @echo "── Scaffolding leftovers"
    @git ls-files | grep -E "_v[0-9]+\.|\.spike\.|\.tmp\.|\.bak$|_old\." || echo "none"

# Site: lint, types, tests
web-check:
    pnpm --filter museum lint
    pnpm --filter museum check
    pnpm --filter museum test

# Run the site in development mode
web:
    pnpm --filter museum dev --host

# Screenshots of the built site (desktop, mobile, every locale) into apps/museum/test-results/
shots *paths:
    pnpm --filter museum run build
    pnpm --filter museum run screenshots {{paths}}

# Research notebooks (marimo)
notebook path="research":
    uv run --group research marimo edit {{path}}
