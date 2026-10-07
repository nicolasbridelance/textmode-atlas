# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Alembic: the database URL comes from `TM_DATABASE_URL`, never from a file in the repository.

Tests pass their own connection through `config.attributes["connection"]`.
"""

from alembic import context
from sqlalchemy import create_engine
from tm.config import settings


def run(connection) -> None:  # type: ignore[no-untyped-def]
    context.configure(connection=connection, transaction_per_migration=True)
    with context.begin_transaction():
        context.run_migrations()


given = context.config.attributes.get("connection")
if given is not None:
    run(given)
else:
    with create_engine(settings().database_url).connect() as connection:
        run(connection)
        connection.commit()
