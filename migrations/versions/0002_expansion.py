# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Expansion: what reading each pack archive gave, so that an empty or partial pack says why.

Revision ID: 0002
Revises: 0001
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

UPGRADE = r"""
-- Latest outcome of reading an archive: read whole, read but for named members, or a classified
-- error (no member could be listed). Rewritten by each run, which may read more than the last.
create table expansion (
  sha256      char(64) primary key references artifact,
  status      text not null check (status in ('ok','partial','error')),
  error_class text,
  unreadable  text[] not null default '{}',
  expanded_at timestamptz not null default now(),
  check ((status = 'error') = (error_class is not null)),
  check ((status = 'partial') = (cardinality(unreadable) > 0))
);
"""

DOWNGRADE = r"""
drop table if exists expansion;
"""


def upgrade() -> None:
    op.execute(UPGRADE)


def downgrade() -> None:
    op.execute(DOWNGRADE)
