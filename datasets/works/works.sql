-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors
-- SPDX-License-Identifier: CC0-1.0
--
-- One row per art file of the train packs (view work_split), whatever its format. A file in
-- several packs is placed in the earliest one (by year, then path), and `packs` says how many
-- hold it. SAUCE fields are as recorded; `sauce_problems` says when the decoder set them aside.
--
-- `content_kind` says what the grid holds, since the extension does not (works note): text or
-- blocks (a quarter of the visible glyphs or more are █▄▀▌▐░▒▓; the share is bimodal, with its
-- trough between 10% and 35%), coloured or not (more than two colours: plain text is grey on
-- black). Null when the grid was not measured.
with placed as (
  select distinct on (m.sha256)
    m.sha256, p.pack_sha256, pa.source_path as pack_path, w.title as pack,
    extract(year from v.date_min)::int as year, m.path
  from set_member m
  join pack_split p on p.set_work_id = m.set_work_id
  join work w on w.id = p.set_work_id
  join version v on v.work_id = w.id
  join artifact pa on pa.sha256 = p.pack_sha256
  order by m.sha256, year nulls last, pa.source_path, m.path
)
select
  a.sha256,
  pl.pack_sha256,
  pl.pack,
  pl.year,
  pl.path,
  s.packs,
  a.format,
  a.bytes,
  a.sauce ->> 'title' as sauce_title,
  a.sauce ->> 'author' as sauce_author,
  a.sauce ->> 'group' as sauce_group,
  a.sauce ->> 'date' as sauce_date,
  (a.sauce ->> 'width')::int as sauce_width,
  ((a.sauce ->> 'flags')::int & 1) = 1 as sauce_ice,
  nullif(a.sauce ->> 'font', '') as sauce_font,
  d.status as decoding,
  d.error_class as decoding_error,
  d.cols,
  d.rows,
  d.sauce_problems,
  d.grid_sha256,
  r.output_sha256 as rendering_sha256,
  case
    when f.sha256 is null then null
    when f.n_colors = 0 then 'empty'
    when f.class_block + f.class_half_block + f.class_shade >= 0.25
      then case when f.n_colors > 2 then 'coloured_blocks' else 'blocks' end
    else case when f.n_colors > 2 then 'coloured_text' else 'text' end
  end as content_kind
from work_split s
join placed pl on pl.sha256 = s.sha256
join artifact a on a.sha256 = s.sha256
join version av on av.id = a.version_id
join work aw on aw.id = av.work_id and aw.kind = 'single'
-- Each art file has one decoder at the current version: the ANSI decoder, or `none` for a
-- format no decoder reads yet (error `unsupported_format`).
left join decoding d on d.sha256 = a.sha256 and d.decoder_version = :decoder_version
left join features f on f.sha256 = a.sha256 and f.extractor_version = :features_version
  and f.grid_sha256 = d.grid_sha256
left join lateral (
  select output_sha256 from representation r
  where r.sha256 = a.sha256 and r.level = 'conservation'
    and r.recipe ->> 'renderer_version' = :renderer_version
    and r.recipe ->> 'grid_sha256' = d.grid_sha256 and (r.recipe ->> 'scale')::int = 1
  order by r.created_at desc, r.output_sha256 limit 1
) r on true
where s.split = 'train'
