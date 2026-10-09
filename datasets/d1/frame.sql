-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors
-- SPDX-License-Identifier: CC0-1.0
--
-- Sampling frame of D1 (ADR 0017): the train packs of 16colo whose archive was read whole, one
-- row per pack. `era` is the stratum, bounded by the mass of packs (works note, constraint 2;
-- archives note); `dominant_kind` and `members` order the packs inside a stratum, so that the
-- systematic draw spreads over content and size.
with packs as (
  select a.sha256 as pack_sha256, w.id as set_work_id, w.title as pack,
    extract(year from v.date_min)::int as year
  from pack_split p
  join artifact a on a.sha256 = p.pack_sha256
  join version v on v.id = a.version_id
  join work w on w.id = v.work_id
  join expansion e on e.sha256 = a.sha256 and e.status = 'ok'
  where p.split = 'train' and v.date_min is not null
),
kinds as (
  select m.set_work_id,
    case
      when f.class_block + f.class_half_block + f.class_shade >= 0.25
        then case when f.n_colors > 2 then 'coloured_blocks' else 'blocks' end
      else case when f.n_colors > 2 then 'coloured_text' else 'text' end
    end as kind
  from set_member m
  join decoding d on d.sha256 = m.sha256 and d.decoder_version = :decoder_version
  join features f on f.sha256 = m.sha256 and f.extractor_version = :features_version
    and f.grid_sha256 = d.grid_sha256
  where f.n_colors > 0
),
dominant as (
  select distinct on (set_work_id) set_work_id, kind
  from (select set_work_id, kind, count(*) as n from kinds group by 1, 2) k
  order by set_work_id, n desc, kind
)
select
  p.pack_sha256,
  p.pack,
  p.year,
  case
    when p.year <= 1993 then '1990-93'
    when p.year <= 1995 then '1994-95'
    when p.year <= 1997 then '1996-97'
    when p.year <= 1999 then '1998-99'
    when p.year <= 2004 then '2000-04'
    when p.year <= 2012 then '2005-12'
    else '2013-26'
  end as era,
  coalesce(d.kind, 'none') as dominant_kind,
  (select count(*) from set_member m where m.set_work_id = p.set_work_id)::int as members
from packs p
left join dominant d on d.set_work_id = p.set_work_id
