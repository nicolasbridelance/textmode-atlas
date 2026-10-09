# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""work_audience says whether a person has rated the file (grid rule 4).

A file whose ratings all come from programs is not rated yet, whatever its level: a program
that no longer finds a descriptor does not make a work fit for every audience. `reviewed` is
true when a current rating was reviewed by a person or declared by the artist.

Revision ID: 0011
Revises: 0010
"""

from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None

VIEW = r"""
create or replace view work_audience as
select r.sha256,
  coalesce(
    (array_agg(l.code order by l.rank desc) filter (where l.code is not null))[1], '3'
  ) as level,
  array_agg(distinct r.descriptor order by r.descriptor)
    filter (where r.present and r.kind = 'descriptor') as descriptors,
  array_agg(distinct r.descriptor order by r.descriptor)
    filter (where r.present and r.kind = 'notice') as notices,
  bool_or(r.nature = 'inferred' and r.present) as has_unreviewed{reviewed}
from content_rating r
left join audience_level l on l.code = r.level and r.present
where r.superseded_by is null
group by r.sha256;
"""


def upgrade() -> None:
    op.execute(VIEW.format(reviewed=",\n  bool_or(r.nature <> 'inferred') as reviewed"))


def downgrade() -> None:
    op.execute("drop view work_audience;\n" + VIEW.format(reviewed=""))
