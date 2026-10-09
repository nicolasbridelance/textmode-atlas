<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0019. Describe sensitive content, and decide audiences on the server

- Status: **Proposed**. Points 1–3 of its first draft are decided in ADR 0020 (the grid);
  the rooms, the age check and the legal points marked "to verify" need the owner and the lawyer
- Date: 2026-10-09
- Deciders: Nicolas Bridelance, with the lawyer (roadmap, "Before M4"); drafted by Claude
- Relates to: ADR 0009 (what may be shown), the museography proposal (rooms, Midnight, feeds)

## Context

The owner asked about age ratings ("la question du PEGI") and about adult archives, such as the
Minitel rose: where they are, and how to tag them so that the museum keeps them and handles
them with care.

The scene was made largely by teenagers and was often transgressive. A rough keyword count over
the text layer of the train packs (works v5, 2026-10-09, false positives included) finds sexual
words in 2,880 works, drug words in 865, hate words in 216 and warez words in 4,175. The
titles and file names alone flag 114, 132, 23 and 173. The packs also hold about 3,000
photographs and pictures that we do not decode yet, some of them probably adult. Future sources
will add more: the Minitel's adult services (the "3615" messageries), adult BBS areas, and
Usenet's ASCII art. None of those is in the corpus yet, and no archive of Minitel pages has been
identified.

Today nothing marks this content. `can_display()` answers one question, whether the museum
may show the file (rights). Nothing answers the other one: to whom, and with what framing.

PEGI is the European rating for games. It does not apply to a website, but its descriptors are
a vocabulary people know. The arcade games, if they ever ship as store apps, would need an IARC
rating.

## Decision (proposed)

1. **Descriptors, levels and ratings: decided in [ADR 0020](0020-the-audience-grid.md).** The
   grid ([audience-grid.md](../audience-grid.md)) gives the levels 3, 7, 12, 16, 18 and
   `withheld`, eight descriptors and the rules. Ratings are append-only rows signed `algo:`,
   `human:` or `identity:`, and the database computes each file's level (`work_audience`).
2. **An audience is applied on the server, next to `can_display()`.** A function `audience()`
   reads `work_audience`. Like `can_display()`, it is applied by `tm export` and by the API,
   never by the frontend, and it is held at full branch coverage. A file no one has reviewed
   counts as 16 (grid rule 4).
3. **`withheld` is never exported**, whatever the rights. It stays in the archive with its
   metadata, for a decision by the owner and the lawyer. That covers sexual content that
   involves or may involve minors (in French law, drawings may also fall under it; to verify),
   and content that would be unlawful to publish even in an archive.
4. **Rooms read the audience** (museography proposal):
   - feeds, swipe and arcade show 12 and under; kiosk mode shows 7 and under unless its venue
     sets another level;
   - the gallery and the labels show `16` behind a content warning the visitor clicks through;
   - Midnight is `16` by default;
   - `18` is shown only after the age check the lawyer approves, and until then not at all
     (record and metadata only).
5. **Hateful works keep their place in the record, with a cartel.** A work tagged
   `discrimination` is never in a feed, a game or a recommendation. In the gallery it comes with
   a text written by a person that says what it is and why it is kept.
6. **Privacy holds.** A descriptor applies to a work, never to a person. `crime` on a warez
   work never links its handle to a civil identity (invariant 7).

## Consequences

- A schema change: descriptors as assertions (relation `has_descriptor`, object from the
  vocabulary), and `audience` in the exported record.
- A review queue: inferred descriptors go to D2 annotators by count, sexual and hate first.
- The keyword pass is cheap and runs on the text layer we hold. It over-flags ("crack", "acid"
  as a group name), which is acceptable, since a human clears false positives.
- Questions for the lawyer: the age check required in France for a site that shows some
  explicit works among many others (to verify); drawn sexual content and minors; hate speech in
  an archive; how to handle the scene's sexualized depictions of real people (celebrities,
  other sceners).
