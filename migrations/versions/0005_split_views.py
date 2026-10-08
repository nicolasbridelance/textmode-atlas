# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Split views: which 16colo packs and works exploration may read (research program, rule 3).

Revision ID: 0005
Revises: 0004
"""

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

UPGRADE = r"""
-- A pack is `test` when the first byte of its archive's SHA-256 is below 52: about one pack in
-- five, fixed before anyone looked at the grids. Exploration reads `train` only.
create view pack_split as
select a.sha256 as pack_sha256, w.id as set_work_id,
  case when get_byte(decode(a.sha256, 'hex'), 0) < 52 then 'test' else 'train' end as split
from work w
join version v on v.work_id = w.id
join artifact a on a.version_id = v.id
join source s on s.id = a.source_id and s.name = '16colo'
where w.kind = 'set';

-- A file is `train` only when every pack that holds it is: a file shared with a test pack is
-- test, or it would let the test packs be seen through another door.
create view work_split as
select m.sha256,
  case when bool_and(p.split = 'train') then 'train' else 'test' end as split,
  count(distinct p.pack_sha256)::int as packs
from set_member m
join pack_split p on p.set_work_id = m.set_work_id
group by m.sha256;
"""

DOWNGRADE = r"""
drop view if exists work_split;
drop view if exists pack_split;
"""


def upgrade() -> None:
    op.execute(UPGRADE)


def downgrade() -> None:
    op.execute(DOWNGRADE)
