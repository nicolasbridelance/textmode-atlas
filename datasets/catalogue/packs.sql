-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors
-- SPDX-License-Identifier: CC0-1.0
--
-- One row per 16colo pack archive. The split is drawn from the archive's hash: about one pack
-- in five (first byte below 52) is held out for testing, the same pack every build.
select
  a.sha256 as pack_sha256,
  w.title as pack,
  a.source_path as path,
  extract(year from v.date_min)::int as year,
  a.format as archive_format,
  a.bytes,
  e.status as expansion,
  e.error_class as expansion_error,
  coalesce(cardinality(e.unreadable), 0) as unreadable,
  (select count(*) from set_member m where m.set_work_id = w.id)::int as members,
  case when get_byte(decode(a.sha256, 'hex'), 0) < 52 then 'test' else 'train' end as split
from work w
join version v on v.work_id = w.id
join artifact a on a.version_id = v.id
join source s on s.id = a.source_id and s.name = '16colo'
left join expansion e on e.sha256 = a.sha256
where w.kind = 'set'
