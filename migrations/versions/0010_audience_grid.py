# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The audience grid in the database: its vocabularies, content ratings, each work's level.

ADR 0020. The vocabularies copy `corpus/ratings/grid.yaml` (version 1); a test fails when they
differ. A rating says that a file shows a descriptor at a level, or that it does not (`present`
false: a reviewer's rejection). Ratings are append-only, like assertions: a review supersedes,
never erases.

Revision ID: 0010
Revises: 0009
"""

from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None

UPGRADE = r"""
create table audience_level (
  code     text primary key,
  min_age  integer,             -- null: withheld, never shown
  rank     integer not null unique
);
insert into audience_level (code, min_age, rank) values
  ('3', 3, 0), ('7', 7, 1), ('12', 12, 2), ('16', 16, 3), ('18', 18, 4), ('withheld', null, 5);

create table content_descriptor (
  code  text primary key,
  kind  text not null check (kind in ('descriptor', 'notice')),
  unique (code, kind)
);
insert into content_descriptor (code, kind) values
  ('violence', 'descriptor'), ('fear', 'descriptor'), ('sexual', 'descriptor'),
  ('language', 'descriptor'), ('drugs', 'descriptor'), ('discrimination', 'descriptor'),
  ('crime', 'descriptor'), ('real_people', 'descriptor'), ('flashing', 'notice');

-- The degrees each descriptor has: language stops at 16, sexual goes to withheld.
create table descriptor_level (
  descriptor  text not null references content_descriptor,
  level       text not null references audience_level,
  primary key (descriptor, level)
);
insert into descriptor_level (descriptor, level) values
  ('violence', '7'), ('violence', '12'), ('violence', '16'), ('violence', '18'),
  ('fear', '7'), ('fear', '12'), ('fear', '16'),
  ('sexual', '12'), ('sexual', '16'), ('sexual', '18'), ('sexual', 'withheld'),
  ('language', '12'), ('language', '16'),
  ('drugs', '12'), ('drugs', '16'), ('drugs', '18'),
  ('discrimination', '16'), ('discrimination', '18'), ('discrimination', 'withheld'),
  ('crime', '12'), ('crime', '16'), ('crime', 'withheld'),
  ('real_people', '12'), ('real_people', '16'), ('real_people', '18'),
  ('real_people', 'withheld');

-- A program infers, a named reviewer reviews, the artist declares (grid rule 3).
create table content_rating (
  id             uuid primary key default gen_random_uuid(),
  sha256         char(64) not null references artifact,
  descriptor     text not null,
  kind           text not null,
  present        boolean not null default true,
  level          text,
  grid_version   integer not null check (grid_version >= 1),
  nature         text not null check (nature in ('inferred', 'reviewed', 'declared')),
  asserted_by    text not null check (asserted_by ~ '^(human|algo|identity):.+'),
  evidence_note  text,
  asserted_at    timestamptz not null default now(),
  superseded_by  uuid references content_rating,
  foreign key (descriptor, kind) references content_descriptor (code, kind),
  foreign key (descriptor, level) references descriptor_level (descriptor, level),
  -- a present descriptor has a level, a notice never has one, an absent one neither
  check ((kind = 'descriptor' and present) = (level is not null)),
  check (nature <> 'inferred' or asserted_by like 'algo:%'),
  check (nature <> 'reviewed' or asserted_by like 'human:%'),
  check (nature <> 'declared' or asserted_by like 'identity:%')
);
create index content_rating_sha256 on content_rating (sha256) where superseded_by is null;

create function content_rating_append_only() returns trigger language plpgsql as $$
begin
  if tg_op = 'DELETE' then
    raise exception 'content_rating is append-only: delete forbidden';
  end if;
  if old.superseded_by is not null
     or (to_jsonb(new) - 'superseded_by') <> (to_jsonb(old) - 'superseded_by') then
    raise exception 'content_rating is append-only: only setting superseded_by is allowed';
  end if;
  return new;
end $$;
create trigger content_rating_append_only before update or delete on content_rating
  for each row execute function content_rating_append_only();

-- A file's level: the highest among its current, present descriptors (grid rule 1). Its
-- notices are listed beside it. A file with no current rating has no row: not rated yet.
create view work_audience as
select r.sha256,
  coalesce(
    (array_agg(l.code order by l.rank desc) filter (where l.code is not null))[1], '3'
  ) as level,
  array_agg(distinct r.descriptor order by r.descriptor)
    filter (where r.present and r.kind = 'descriptor') as descriptors,
  array_agg(distinct r.descriptor order by r.descriptor)
    filter (where r.present and r.kind = 'notice') as notices,
  bool_or(r.nature = 'inferred' and r.present) as has_unreviewed
from content_rating r
left join audience_level l on l.code = r.level and r.present
where r.superseded_by is null
group by r.sha256;
"""

DOWNGRADE = r"""
drop view if exists work_audience;
drop trigger if exists content_rating_append_only on content_rating;
drop function if exists content_rating_append_only;
drop table if exists content_rating;
drop table if exists descriptor_level;
drop table if exists content_descriptor;
drop table if exists audience_level;
"""


def upgrade() -> None:
    op.execute(UPGRADE)


def downgrade() -> None:
    op.execute(DOWNGRADE)
