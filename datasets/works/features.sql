-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors
-- SPDX-License-Identifier: CC0-1.0
--
-- Extractor features of the decoded grids of the train packs, one row per art file.
select f.sha256, f.cols, f.rows, f.cells, f.fill_ratio, f.center_row, f.center_col,
  f.symmetry_h, f.symmetry_v, f.glyph_hist, f.glyph_entropy, f.class_block, f.class_half_block,
  f.class_shade, f.class_box, f.class_alphanumeric, f.class_punctuation, f.class_other,
  f.bigram_codes, f.bigram_counts, f.n_colors, f.fg_hist, f.bg_hist, f.high_bg_ratio,
  f.fg_bg_pairs, f.cursor_jumps, f.draw_order
from features f
join work_split s on s.sha256 = f.sha256 and s.split = 'train'
join decoding d on d.sha256 = f.sha256 and d.decoder_version = :decoder_version
  and d.grid_sha256 = f.grid_sha256
where f.extractor_version = :features_version
