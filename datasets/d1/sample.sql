-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors
-- SPDX-License-Identifier: CC0-1.0
--
-- The sample as sample.yaml froze it: one row per pack, its stratum, how it was selected, its
-- inclusion weight, and why a pack was added by hand.
select unit as pack_sha256, stratum, selection, weight, reason from sample
