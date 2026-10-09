-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors
-- SPDX-License-Identifier: CC0-1.0
--
-- Text layer of the decoded grids of the train packs, one row per line that holds a word.
select t.sha256, l.row, l.text
from text_layer t
join work_split s on s.sha256 = t.sha256 and s.split = 'train'
join decoding d on d.sha256 = t.sha256 and d.decoder_version = :decoder_version
  and d.grid_sha256 = t.grid_sha256
cross join lateral unnest(t.line_rows, t.lines) as l(row, text)
where t.extractor_version = :text_version
