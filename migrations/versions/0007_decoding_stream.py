# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Decoding stream: how the bytes drew the grid (writes, overwrites, screen clears).

Revision ID: 0007
Revises: 0006
"""

from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None

UPGRADE = r"""
-- The grid keeps the last state of each cell; an animation redraws. Null for errors, and for
-- rows of decoder versions that did not count.
alter table decoding
  add column writes integer check (writes >= 0),
  add column overwrites integer check (overwrites between 0 and writes),
  add column clears integer check (clears >= 0);
"""

DOWNGRADE = r"""
alter table decoding drop column if exists writes, drop column if exists overwrites,
  drop column if exists clears;
"""


def upgrade() -> None:
    op.execute(UPGRADE)


def downgrade() -> None:
    op.execute(DOWNGRADE)
