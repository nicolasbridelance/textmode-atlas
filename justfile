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
    just services
    just migrate
    uv run tm dev storage-init

# Start PostgreSQL and Garage, and wait until they are ready
services:
    docker compose up -d --wait

# Apply database migrations
migrate:
    uv run alembic upgrade head

# Everything CI checks
check: lint typecheck test corpus licenses no-artworks web-check

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

# Site: lint, types, tests
web-check:
    pnpm --filter museum lint
    pnpm --filter museum check
    pnpm --filter museum test

# Run the site in development mode
web:
    pnpm --filter museum dev --host

# Research notebooks (marimo)
notebook path="research":
    uv run --group research marimo edit {{path}}
