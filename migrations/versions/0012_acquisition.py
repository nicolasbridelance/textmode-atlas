# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Where and when every original was fetched (ADR 0021): acquisitions, append-only.

A file fetched from two addresses has two rows. Files inside an archive inherit its rows through
`set_member`; `artifact_provenance` lists both.

Revision ID: 0012
Revises: 0011
"""

from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None

UPGRADE = r"""
create table acquisition (
  id               uuid primary key default gen_random_uuid(),
  sha256           char(64) not null references artifact,
  source_id        uuid not null references source,
  url              text not null check (url ~ '^(https?|rsync|ftp|file)://'),
  method           text not null check (method in ('rsync', 'http', 'manual')),
  retrieved_at     timestamptz,
  retrieved_basis  text not null
                     check (retrieved_basis in ('recorded', 'file_mtime', 'mirror_run', 'unknown')),
  remote           jsonb not null default '{}',  -- Last-Modified, ETag, remote file date
  recorded_at      timestamptz not null default now(),
  recorded_by      text not null check (recorded_by ~ '^(human|algo):.+'),
  unique (sha256, url, retrieved_at),
  check ((retrieved_basis = 'unknown') = (retrieved_at is null))
);
create index acquisition_sha256 on acquisition (sha256);

create function acquisition_append_only() returns trigger language plpgsql as $$
begin
  raise exception 'acquisition is append-only: % forbidden', lower(tg_op);
end $$;
create trigger acquisition_append_only before update or delete on acquisition
  for each row execute function acquisition_append_only();

-- Every artifact's acquisitions: its own, and those of every archive it was extracted from.
create view artifact_provenance as
select q.sha256, null::char(64) as via_archive, null::text as path_in_archive,
  q.url, q.method, q.retrieved_at, q.retrieved_basis, q.remote, s.name as source
from acquisition q
join source s on s.id = q.source_id
union all
select m.sha256, q.sha256, m.path, q.url, q.method, q.retrieved_at, q.retrieved_basis,
  q.remote, s.name
from set_member m
join version v on v.work_id = m.set_work_id
join artifact pa on pa.version_id = v.id
join acquisition q on q.sha256 = pa.sha256
join source s on s.id = q.source_id;
"""

DOWNGRADE = r"""
drop view if exists artifact_provenance;
drop trigger if exists acquisition_append_only on acquisition;
drop function if exists acquisition_append_only;
drop table if exists acquisition;
"""


def upgrade() -> None:
    op.execute(UPGRADE)


def downgrade() -> None:
    op.execute(DOWNGRADE)
