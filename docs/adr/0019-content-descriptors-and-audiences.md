<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0019. Describe sensitive content, and decide audiences on the server

- Status: **Proposed**. It needs the owner's decision, and the lawyer's review of the legal
  points marked "to verify"
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

1. **Content descriptors are assertions.** A work can carry descriptors from a closed
   vocabulary taken from PEGI's: `violence`, `fear` (horror, gore), `sexual`, `nudity`,
   `discrimination` (hate), `drugs`, `language`, `crime` (warez, carding, phreaking). Each is an
   assertion with `nature` and `asserted_by` (invariant 4):
   - `inferred` by an `algo:` (keywords in the text layer, file names, NFO, later a vision
     model, I42);
   - `asserted` by a named reviewer (`human:`), who can confirm or reject an inferred one;
   - `declared` by the artist, who can describe their own work.

   Nothing is deleted. A rejection is a new assertion, so the history of how a work was judged
   stays visible.
2. **An audience is computed on the server, next to `can_display()`.** A function `audience()`
   maps a work's descriptors to a class: `all`, `16` or `18`. Like `can_display()`, it is applied
   by `tm export` and by the API, never by the frontend, and it is held at full branch coverage.
   Until a human has confirmed or rejected an `inferred` descriptor, it counts as present.
3. **A class of its own: `withheld`.** A work that may be illegal to show is never exported,
   whatever its rights. It stays in the archive with its metadata, for a decision by the owner
   and the lawyer. This covers sexual content that involves or may involve minors (in French law,
   drawings may also fall under it; to verify), and content that the lawyer finds unlawful to
   publish even in an archival context.
4. **Rooms read the audience** (museography proposal):
   - feeds, swipe, arcade and kiosk mode show `all` only;
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
