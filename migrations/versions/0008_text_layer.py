# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Text layer: the rows of each decoded grid that hold words, by extractor version (leads I2).

Revision ID: 0008
Revises: 0007
"""

from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None

UPGRADE = r"""
-- One row per grid and extractor version, even when the grid holds no text: the row says it was
-- read. `line_rows[i]` is the grid row of `lines[i]`; datasets publish one row per line.
create table text_layer (
  sha256            char(64) not null references artifact,
  extractor_version text not null,
  grid_sha256       char(64) not null,
  line_rows         integer[] not null,
  lines             text[] not null,
  extracted_at      timestamptz not null default now(),
  primary key (sha256, extractor_version),
  check (cardinality(line_rows) = cardinality(lines))
);
"""

DOWNGRADE = r"""
drop table if exists text_layer;
"""


def upgrade() -> None:
    op.execute(UPGRADE)


def downgrade() -> None:
    op.execute(DOWNGRADE)
