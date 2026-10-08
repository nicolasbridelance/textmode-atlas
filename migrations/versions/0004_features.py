# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Features: the measurements of each decoded grid, by extractor version (ADR 0016).

Revision ID: 0004
Revises: 0003
"""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

UPGRADE = r"""
-- One row per grid and extractor version. The grid is named by its digest, so a row says which
-- grid it measured; datasets publish these rows as features.parquet.
create table features (
  sha256             char(64) not null references artifact,
  extractor_version  text not null,
  grid_sha256        char(64) not null,
  cols               integer not null check (cols > 0),
  rows               integer not null check (rows > 0),
  cells              integer not null check (cells >= 0),
  fill_ratio         double precision not null check (fill_ratio between 0 and 1),
  center_row         double precision not null,
  center_col         double precision not null,
  symmetry_h         double precision not null check (symmetry_h between 0 and 1),
  symmetry_v         double precision not null check (symmetry_v between 0 and 1),
  glyph_hist         integer[] not null check (cardinality(glyph_hist) = 256),
  glyph_entropy      double precision not null check (glyph_entropy >= 0),
  class_block        double precision not null,
  class_half_block   double precision not null,
  class_shade        double precision not null,
  class_box          double precision not null,
  class_alphanumeric double precision not null,
  class_punctuation  double precision not null,
  class_other        double precision not null,
  bigram_codes       integer[] not null,
  bigram_counts      integer[] not null,
  n_colors           integer not null check (n_colors between 0 and 16),
  fg_hist            integer[] not null check (cardinality(fg_hist) = 16),
  bg_hist            integer[] not null check (cardinality(bg_hist) = 8),
  high_bg_ratio      double precision not null check (high_bg_ratio between 0 and 1),
  fg_bg_pairs        integer not null check (fg_bg_pairs >= 0),
  cursor_jumps       double precision not null check (cursor_jumps between 0 and 1),
  draw_order         double precision not null check (draw_order between -1 and 1),
  extracted_at       timestamptz not null default now(),
  primary key (sha256, extractor_version),
  check (cardinality(bigram_codes) = cardinality(bigram_counts))
);
"""

DOWNGRADE = r"""
drop table if exists features;
"""


def upgrade() -> None:
    op.execute(UPGRADE)


def downgrade() -> None:
    op.execute(DOWNGRADE)
