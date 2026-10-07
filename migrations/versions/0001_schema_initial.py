# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Initial schema: works, files, actors, assertions, rights, gaps, cartels.

The invariants of the foundation document are carried by constraints and triggers, so that no
code path can bypass them.

Revision ID: 0001
Revises:
"""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

UPGRADE = r"""
create extension if not exists vector;

-- Acquisition sources (16colo.rs, Demozoo, an author's deposit…). Required by
-- artifact.source_id.
create table source (
  id          uuid primary key default gen_random_uuid(),
  kind        text not null check (kind in ('archive','api','deposit','manual','golden')),
  name        text not null unique,
  url         text,
  terms_note  text,
  created_at  timestamptz not null default now()
);

create table work (
  id        uuid primary key default gen_random_uuid(),
  kind      text not null check (kind in ('single','set')),  -- set = pack, disk, BBS
  title     text,
  usage     text[] not null default '{}',
  system    text[] not null default '{}',
  scene     text[] not null default '{}',
  channel   text[] not null default '{}',
  function  text[] not null default '{}',
  rights    jsonb not null default '{}',   -- validated by tm.rights.Rights
  privacy   jsonb not null default '{}',   -- validated by tm.rights.Privacy
  created_at timestamptz not null default now()
);
create index work_system_idx  on work using gin (system);
create index work_channel_idx on work using gin (channel);

create table version (
  id         uuid primary key default gen_random_uuid(),
  work_id    uuid not null references work,
  label      text,
  date_min   date,
  date_max   date,
  date_basis text check (date_basis in ('sauce','pack','mtime','testimony')),
  behavior   text not null check (behavior in
               ('static','animated','interactive','generative','performative')),
  check (date_min is null or date_max is null or date_min <= date_max)
);

create table artifact (
  sha256      char(64) primary key check (sha256 ~ '^[0-9a-f]{64}$'),
  version_id  uuid references version,
  bytes       bigint not null check (bytes >= 0),
  format      text,
  charset     text,
  cols        int check (cols > 0),
  rows        int check (rows > 0),
  sauce       jsonb,
  source_id   uuid references source,
  source_path text,
  acquired_at timestamptz not null default now()
);

create table set_member (
  set_work_id uuid references work,
  sha256      char(64) not null references artifact,
  path        text not null,
  position    int not null,
  primary key (set_work_id, path)
);

-- Decoding outcome of each artifact: a grid or a classified error, never nothing.
create table decoding (
  sha256          char(64) not null references artifact,
  decoder         text not null,
  decoder_version text not null,
  status          text not null check (status in ('ok','error')),
  error_class     text,
  grid_sha256     char(64),
  cols            int,
  rows            int,
  decoded_at      timestamptz not null default now(),
  primary key (sha256, decoder, decoder_version),
  check ((status = 'ok') = (grid_sha256 is not null)),
  check ((status = 'error') = (error_class is not null))
);

create table representation (
  id            uuid primary key default gen_random_uuid(),
  sha256        char(64) not null references artifact,
  level         text not null check (level in ('authentic','conservation','interpretation')),
  profile       text,
  recipe        jsonb not null,
  output_sha256 char(64) not null,
  created_at    timestamptz not null default now(),
  check (level <> 'authentic' or profile is not null)
);

create table trace (
  id       uuid primary key default gen_random_uuid(),
  work_id  uuid not null references work,
  kind     text not null check (kind in ('log','capture','recording','testimony')),
  sha256   char(64) references artifact,
  note     text
);

-- Actors. The handle is the public entity; the civil person never leaves the database.
create table identity (
  id      uuid primary key default gen_random_uuid(),
  handle  text not null,
  aliases text[] not null default '{}'
);

create table person (
  id           uuid primary key default gen_random_uuid(),
  identity_ids uuid[] not null default '{}',
  consent      text not null default 'none' check (consent in ('none','self_declared'))
);

create table collective (
  id   uuid primary key default gen_random_uuid(),
  name text not null
);

create table place (
  id   uuid primary key default gen_random_uuid(),
  kind text not null check (kind in ('bbs','newsgroup','ftp','irc','demoparty','web','other')),
  name text not null,
  meta jsonb not null default '{}'
);

create table tool (
  id       uuid primary key default gen_random_uuid(),
  name     text not null,
  version  text,
  released date,
  features text[] not null default '{}'
);

-- The graph: a single, append-only table.
create table assertion (
  id            uuid primary key default gen_random_uuid(),
  subject_type  text not null check (subject_type in
                  ('identity','work','collective','place','tool')),
  subject_id    uuid not null,
  relation      text not null check (relation in (
                  'created','member_of','collaborated_with','released_in','references',
                  'made_for','made_with','distributed_by','competed_with','moved_to',
                  'had_role','similar_to')),
  object_type   text not null check (object_type in
                  ('identity','work','collective','place','tool')),
  object_id     uuid not null,
  -- for had_role: artist, coder, sysop, courier, packer, faq_author, archivist
  role          text,
  date_min      date,
  date_max      date,
  nature        text not null check (nature in ('documented','testified','inferred')),
  evidence      char(64) references artifact,
  evidence_note text,
  confidence    real check (confidence between 0 and 1),
  asserted_by   text not null check (asserted_by ~ '^(human|algo):.+'),
  asserted_at   timestamptz not null default now(),
  superseded_by uuid references assertion,
  check (nature <> 'inferred' or asserted_by like 'algo:%'),
  check (nature <> 'documented' or evidence is not null),
  check (relation <> 'had_role' or role is not null),
  check (date_min is null or date_max is null or date_min <= date_max),
  check (superseded_by is null or superseded_by <> id)
);
create index assertion_subject_idx on assertion (subject_type, subject_id)
  where superseded_by is null;
create index assertion_object_idx on assertion (object_type, object_id)
  where superseded_by is null;

-- Append-only: the only allowed change is setting superseded_by (from null to a value).
create function assertion_append_only() returns trigger language plpgsql as $$
begin
  if tg_op = 'DELETE' then
    raise exception 'assertion is append-only: delete forbidden';
  end if;
  if old.superseded_by is not null
     or new.superseded_by is null
     or (to_jsonb(new) - 'superseded_by') <> (to_jsonb(old) - 'superseded_by') then
    raise exception 'assertion is append-only: only setting superseded_by is allowed';
  end if;
  return new;
end $$;
create trigger assertion_append_only before update or delete on assertion
  for each row execute function assertion_append_only();

-- An artifact describes an immutable original: its hash, size and acquisition date never change,
-- and it never disappears.
create function artifact_immutable() returns trigger language plpgsql as $$
begin
  if tg_op = 'DELETE' then
    raise exception 'artifact: delete forbidden (withdrawal goes through privacy.withdrawn)';
  end if;
  if new.sha256 <> old.sha256 or new.bytes <> old.bytes or new.acquired_at <> old.acquired_at then
    raise exception 'artifact: hash, size and acquisition date are immutable';
  end if;
  return new;
end $$;
create trigger artifact_immutable before update or delete on artifact
  for each row execute function artifact_immutable();

create view edge_documented as
  select * from assertion where nature = 'documented' and superseded_by is null;
create view edge_testified as
  select * from assertion where nature = 'testified' and superseded_by is null;
create view edge_inferred as
  select * from assertion where nature = 'inferred' and superseded_by is null;

-- Known but lost: every statistic publishes its coverage rate.
create table lost_item (
  id            uuid primary key default gen_random_uuid(),
  kind          text not null check (kind in ('pack','bbs','work','issue','other')),
  name          text not null,
  scene         text[] not null default '{}',
  date_min      date,
  date_max      date,
  known_from    text not null,   -- where we learn it existed (NFO, list, testimony)
  evidence      char(64) references artifact,
  asserted_by   text not null check (asserted_by ~ '^(human|algo):.+'),
  found_as      uuid references work   -- set if the item is found again
);

-- Moderation queue: claim, correct, testify, withdraw.
create table ticket (
  id         uuid primary key default gen_random_uuid(),
  work_id    uuid references work,
  action     text not null check (action in ('claim','correct','testify','withdraw')),
  payload    jsonb not null default '{}',
  status     text not null default 'open' check (status in ('open','accepted','rejected')),
  created_at timestamptz not null default now(),
  closed_at  timestamptz,
  closed_by  text check (closed_by ~ '^human:.+')
);

-- Cartels: the museum's texts about a work, one row per language. Work titles are not
-- translated. A translation points to its source; a machine translation is signed 'algo:' and is
-- an interpretation, displayed as such.
create table cartel (
  id              uuid primary key default gen_random_uuid(),
  work_id         uuid not null references work,
  lang            text not null check (lang ~ '^[a-z]{2,3}(-[A-Z][a-z]{3})?(-[A-Z]{2})?$'),
  body            text not null,
  written_by      text not null check (written_by ~ '^(human|algo):.+'),
  translated_from uuid references cartel,
  created_at      timestamptz not null default now(),
  superseded_by   uuid references cartel
);
create unique index cartel_current_idx on cartel (work_id, lang) where superseded_by is null;
"""

DOWNGRADE = r"""
drop table if exists cartel, ticket, lost_item cascade;
drop view if exists edge_inferred, edge_testified, edge_documented;
drop table if exists assertion, tool, place, collective, person, identity, trace,
  representation, decoding, set_member, artifact, version, work, source cascade;
drop function if exists assertion_append_only, artifact_immutable;
"""


def upgrade() -> None:
    op.execute(UPGRADE)


def downgrade() -> None:
    op.execute(DOWNGRADE)
