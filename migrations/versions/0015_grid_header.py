# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""What a decoding produced, and which system and character set its grid declares (ADR 0026).

Revision ID: 0015
Revises: 0014
"""

from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None

UPGRADE = r"""
-- Kept beside the object so that a query picks grids without opening them. Every grid written
-- before grid v2 is a PC VGA grid in code page 437.
alter table decoding
  add column document_kind text check (document_kind in ('grid', 'vector', 'text')),
  add column system text,
  add column charset text;
update decoding set document_kind = 'grid', system = 'pc-vga', charset = 'cp437'
  where status = 'ok';
alter table decoding
  add constraint decoding_document_when_ok check ((status = 'ok') = (document_kind is not null)),
  add constraint decoding_system_of_a_document check ((document_kind is null) = (system is null)),
  add constraint decoding_charset_of_a_grid check (document_kind <> 'grid' or charset is not null);
create index decoding_system on decoding (system, charset) where status = 'ok';
"""

DOWNGRADE = r"""
drop index if exists decoding_system;
alter table decoding drop column if exists charset, drop column if exists system,
  drop column if exists document_kind;
"""


def upgrade() -> None:
    op.execute(UPGRADE)


def downgrade() -> None:
    op.execute(DOWNGRADE)
