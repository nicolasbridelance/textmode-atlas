# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""SAUCE problems: the evidence for which a decoder set a file's SAUCE numbers aside.

Revision ID: 0003
Revises: 0002
"""

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

UPGRADE = r"""
-- Empty when the record is absent or coherent. Otherwise the decoder used none of its numbers
-- (width, flags), and the file waits for a reading that restores them; artifact.sauce keeps the
-- record as written.
alter table decoding add column sauce_problems text[] not null default '{}';
"""

DOWNGRADE = r"""
alter table decoding drop column if exists sauce_problems;
"""


def upgrade() -> None:
    op.execute(UPGRADE)


def downgrade() -> None:
    op.execute(DOWNGRADE)
