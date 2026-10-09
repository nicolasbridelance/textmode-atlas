# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Split the files a scene archive holds loose, by their directory on its site (ADR 0024).

Revision ID: 0014
Revises: 0013
"""

from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None

PACKED = r"""
select m.sha256,
  case when bool_and(p.split = 'train') then 'train' else 'test' end as split,
  count(distinct p.pack_sha256)::int as packs,
  array_agg(distinct p.archive order by p.archive) as archives
from set_member m
join pack_split p on p.set_work_id = m.set_work_id
group by m.sha256
"""

UPGRADE = rf"""
-- A loose file is a single work's artifact that no pack holds. Its split comes from the hash of
-- `<archive>:<directory>`, with the threshold of the packs: one directory, one side.
create or replace view work_split as
{PACKED}
union all
select a.sha256,
  case when get_byte(sha256(convert_to(
    s.name || ':' || coalesce(substring(a.source_path from '^(.*)/[^/]*$'), ''), 'UTF8')), 0) < 52
  then 'test' else 'train' end as split,
  0 as packs,
  array[s.name] as archives
from artifact a
join version v on v.id = a.version_id
join work w on w.id = v.work_id and w.kind = 'single'
join source s on s.id = a.source_id and s.kind = 'archive'
where not exists (select 1 from set_member m where m.sha256 = a.sha256);
"""

DOWNGRADE = f"create or replace view work_split as {PACKED};"


def upgrade() -> None:
    op.execute(UPGRADE)


def downgrade() -> None:
    op.execute(DOWNGRADE)
