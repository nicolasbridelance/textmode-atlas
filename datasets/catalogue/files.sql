-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors
-- SPDX-License-Identifier: CC0-1.0
--
-- One row per file in a 16colo pack: a file found in two packs has two rows, one artifact.
-- SAUCE fields are as recorded, unparsed: the date is the raw `YYYYMMDD` text.
select
  p.sha256 as pack_sha256,
  m.path,
  m.position,
  m.sha256,
  a.bytes,
  a.format,
  lower(substring(m.path from '\.([^./]+)$')) as extension,
  coalesce(fw.kind = 'single', false) as is_art,
  a.sauce is not null as has_sauce,
  a.sauce ->> 'title' as sauce_title,
  a.sauce ->> 'author' as sauce_author,
  a.sauce ->> 'group' as sauce_group,
  a.sauce ->> 'date' as sauce_date,
  (a.sauce ->> 'data_type')::int as sauce_data_type,
  (a.sauce ->> 'file_type')::int as sauce_file_type,
  (a.sauce ->> 'width')::int as sauce_width,
  (a.sauce ->> 'height')::int as sauce_height,
  (a.sauce ->> 'flags')::int as sauce_flags,
  nullif(a.sauce ->> 'font', '') as sauce_font,
  jsonb_array_length(a.sauce -> 'comments')::int as sauce_comment_lines,
  d.status as decoding,
  d.error_class as decoding_error,
  d.cols,
  d.rows
from set_member m
join version sv on sv.work_id = m.set_work_id
join artifact p on p.version_id = sv.id
join source s on s.id = p.source_id and s.name = '16colo'
join artifact a on a.sha256 = m.sha256
left join version fv on fv.id = a.version_id
left join work fw on fw.id = fv.work_id
left join decoding d
  on d.sha256 = a.sha256 and d.decoder = :decoder and d.decoder_version = :decoder_version
