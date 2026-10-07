# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Test database: a blank PostgreSQL database per session, migrated by Alembic."""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Connection, create_engine, make_url, text

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def db_url() -> Iterator[str]:
    base = os.environ.get("TM_DATABASE_URL")
    if not base:
        pytest.skip("TM_DATABASE_URL not set: database tests skipped")
    name = f"tm_test_{uuid.uuid4().hex[:8]}"
    admin = create_engine(base, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'create database "{name}"'))
    url = make_url(base).set(database=name).render_as_string(hide_password=False)
    engine = create_engine(url)
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    with engine.begin() as conn:
        cfg.attributes["connection"] = conn
        command.upgrade(cfg, "head")
    engine.dispose()
    yield url
    with admin.connect() as conn:
        conn.execute(text(f'drop database "{name}" with (force)'))
    admin.dispose()


@pytest.fixture
def db(db_url: str) -> Iterator[Connection]:
    """Connection inside a transaction rolled back at the end of the test."""
    engine = create_engine(db_url)
    with engine.connect() as conn:
        trans = conn.begin()
        yield conn
        trans.rollback()
    engine.dispose()
