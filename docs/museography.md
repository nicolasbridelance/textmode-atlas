<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Museography: rooms, games and feeds

Status: **proposal for discussion**, 2026-10-09, at the owner's request ("c'est tristoune";
"je veux du festif, du tiers-lieu, de la scène indé, les côtés sombres, du ludique, des
interfaces façon Tinder, Insta, X"). Nothing here is decided. Once the owner has chosen, the
foundation document's visit section and the READMEs change first, then the work screen
(roadmap step 8).

## Why the current picture feels sad

The foundation document describes one way of visiting: a work alone on black, drawn at modem
speed, with three to five ways out, and walks written by named people. Each piece is right.
But together they describe a white cube painted black: a quiet, solemn place for one viewer at a
time.

The scene was not like that. It was loud, social and competitive. It was funny and often
offensive. People released packs every month, greeted each other and dissed each other, ran
BBSes, held parties and votes. Its art was made to be downloaded, shared and talked about, at
night, by teenagers. A museum that only offers slow looking keeps the art and loses the scene.

Slow looking stays: it is one room. The proposal is a museum of several **rooms**, each with its
own mood. They all show the same works, read the same data and obey the same rights. The visitor
picks a room at the door, as at a club night with several floors.

## What the corpus already gives (works v5, train packs)

Every room below is fed by data we hold or can extract. Nothing is invented for effect.

| Material | What we hold now | Used by |
| --- | --- | --- |
| The stream of bytes, cell by cell (`t`) | every decoded grid | modem playback, "guess it before it arrives" |
| Packs as releases, with year, group tag, NFO, DIZ | 3,668 packs; 4,786 groups and 9,698 authors as signed in SAUCE | release party, labels, discographies |
| Music shipped inside the packs | 2,849 tracker modules (MOD, S3M, XM, IT) | release party, listening corner |
| The words in the works | 909,508 lines; 6,077 works with greets; 12,182 that mention a BBS, a node or a sysop | the scene's social network, BBS room |
| Animations | 419 works with a third or more of their cells redrawn | the projection room |
| Measures of style | features v1 for 84,104 works; nearest neighbours | swipe, matches, "your style" |
| Broken and unreadable files | 15,350 classified decoding errors (most are formats not decoded yet; some are truncated or corrupt files) | the damaged-works room |
| Lost works | the `lost_item` table, empty today; NFO lists name files nobody holds | the ghost gallery |
| The graffiti photo packs | 168 packs at textfiles.com (field notes) | the scene's edges |

## The rooms

### 1. The gallery (slow looking): the current vision, kept

This is the work alone on black, drawn at modem speed, with zoom down to the cell and three to
five ways out. It becomes the quiet room, the one you return to. Nothing changes in it.

### 2. Release party (festive)

A pack is released the way it was in 1996, as an event.

- **The drop.** A countdown, then the pack opens. The NFO scrolls, a module from the pack plays,
  and the works arrive at modem speed, several at once, like a full file area being downloaded.
- **The compo.** Two works of the same month side by side; the room votes, as at a party. The
  results are anonymous and aggregated per pair, and never presented as a ranking of artists.
- **The month's releases.** What else came out that month, in every archive: the scene as a
  calendar of parties.
- **Shared screen.** Several visitors join one room, the playback is synchronized, and the
  station plays in the background. A watch party without accounts: a room has a link, and
  nobody has a profile.

### 3. The BBS (the third place)

The museum also opens as a bulletin board, because the BBS was the scene's third place.

- A guest login, ANSI menus drawn from the corpus's own BBS ads, and a "who's online" that only
  counts.
- **A oneliner wall**, where visitors leave one line in the BBS manner. It is moderated, and it
  is the only text visitors write.
- **Door games** (see the games below).
- **On site.** A kiosk mode for a café, a hackerspace, a library or a festival: a full-screen
  loop that works offline, a projection mode for an "ANSI night", and a drawing workshop where
  people draw their own ANSI in the browser. People drawing is welcome; a model drawing is not
  (invariant 9).

### 4. The labels (the independent scene)

Groups were labels and packs were albums. This room borrows from the record shop and from
Bandcamp:

- a **pack page** like an album page: the files as a tracklist, the NFO as liner notes, the
  credits as signed, the music;
- a **discography** for each group, month after month, with members joining and leaving as
  their NFOs list them;
- **who greeted whom**, as a map of friendships and rivalries drawn from the greets (I23);
- **best-of lists** made by named people (artists, sysops, historians), the walks of the
  foundation document in a record-shop voice;
- **the edges of the scene**: the graffiti crews that released photo packs, the music groups,
  the ASCII purists. The scene was never only ANSI.

### 5. Midnight (dark, creepy)

The scene drew skulls, demons and gore, and lived next to warez and phreaking. A rough count:
about 9,000 works hold a word of death, blood or hell. This room shows that side, and frames it.

- **Opening hours.** It opens only between midnight and 4 a.m., visitor's local time (a joke
  the BBS era would have liked; also reachable by a door code).
- **The horror wall**: skulls, monsters and the occult, at modem speed, with a low hum.
- **The ghost gallery**: works known only from an NFO list or a description, shown as empty
  frames with their cartel ("this file is listed in a pack's NFO; nobody holds it"). It is
  fed by `lost_item`, and the museum is honest about its gaps.
- **Damaged works**: files that do not decode, shown as what they are (truncated, corrupt,
  mislabelled), with the conservation note. Glitch, presented as a record and never as a style.
- **Dead lines**: BBS ads with their phone numbers. Click one and you hear a modem dial, then
  the tone of a number no longer in service.
- **Guardrails.** Content warnings, a "not tonight" door, and no glorification of the hateful
  works some packs contain: those stay in the collection as records, shown only with context
  and never in a feed. No person is linked to warez activity (privacy block, invariant 7).

### 6. The arcade (playful)

Games that teach how the art is made, with the scene's own pleasures (speed, guessing,
collecting):

- **Modem race**: a work arrives at 2400 baud, and you name what it is before it is complete.
  It uses the byte stream we already decode, and it is the slow looking of the BBS caller,
  turned into a game.
- **Guess the year**: a work, a slider from 1990 to 2026, and a score by the distance in years.
  A GeoGuessr of ANSI, fed by the dataset's years; the reveal shows the pack and its month.
- **Which glyph?**: zoom on a cell and pick the character and its two colours. It teaches the
  half block and the shade.
- **Squint**: a blur slider. At what point does a face appear? This connects to the
  vision-model study (Q33).
- **Open a pack**: an artpack is literally a pack. Open one as a booster and get five works,
  one of them rare (by our measures: an animation, a 9-pixel font, an unusual width), then keep
  your collection in the browser.
- **Find Calvin**: hidden subjects to find in a wall of works, fed by titles and the text
  layer.

### 7. Feeds: the social apps, borrowed

The scene had its own social network: greets were follows and mentions, disses were replies,
member lists were followers, BBS ads were profiles, and the monthly pack was the feed. Borrowing
today's interfaces explains that network in a language every visitor reads, which is the point.

| Today's interface | What it shows here | Built from |
| --- | --- | --- |
| **Tinder** (swipe) | Swipe works right or left. After 20, the museum shows "your style" (half blocks and magenta, like 1996) and a "match": the works nearest your taste | features v1, nearest neighbours; choices kept in the browser only |
| **Instagram** (stories, grid) | A pack as stories, tapping through its files, with the NFO as the first slide; a group's page as a profile grid, with its NFO as the bio and the greets it received as "followers" | packs, text layer, greets graph (I23) |
| **X / Twitter** (timeline) | "This day in 1996": the works and packs of a date as a timeline, greets as @mentions, a rival's answer as a quote post, BBS ads as "trending" | dated packs (month precision from Q30), greets, BBS ads |
| **TikTok / Reels** (vertical feed) | Modem-speed playback as a vertical feed, one work per screen, with the module playing | byte stream, modules |
| **Spotify Wrapped** | A recap of your visit: the years you liked, the glyph you saw most, your nearest group | the visitor's own session, in the browser |
| **Letterboxd** | Named curators' lists and short reviews | walks by named people |

We borrow the forms, not the business model.

- **Feeds end.** "You have seen the whole pack" is a real ending, and the way out leads to
  another room, not to more of the same.
- **No accounts, no tracking, no notifications.** What a visitor does stays in their browser.
  Aggregates (compo votes) are anonymous counts per pair of works.
- **Never a ranking of people.** Likes and matches are about works and styles, never about
  artists' worth.
- **Credit and withdrawal on every card.** A swipe card still carries the handle, the group,
  the pack, the source archive, and the "withdraw or claim" link (ADR 0009).

## Rules that hold in every room

- **Rights and identity.** `can_display()` decides what is shown, in every room; the frontend
  never decides it. Credit is shown as signed. No handle is linked to a civil identity.
- **Interpretation is marked.** A model's description (I42), a "your style" sentence or a match
  is labelled as computed (`interpretation`, `algo:`). A white-background or glitch view is an
  interpretation profile, never the work (I41).
- **No generated works.** No room makes art "in the style of" (invariant 9). Visitors may draw,
  as people.
- **Accessibility.** Every room works with a keyboard and a screen reader, honours reduced
  motion (no forced flashing; blink and animations can be paused), and states its colour
  contrast. Every room works on a phone.
- **Languages.** Everything a visitor reads exists in `en` and `fr` at least.

## What to build first

The first work screen (roadmap step 8) is room 1. The order below puts first what the data
already supports and what teaches the most about the art:

1. **Modem race** and **Which glyph?**: they need only the grid and the byte stream, and they
   test the canvas renderer of step 8 (spike 0002).
2. **Swipe**: it needs features and neighbours, which we hold already.
3. **Open a pack** and **the release party**: they need modules to play (radio and module
   playback, M0 and later).
4. **Feeds** and the **labels**: they need the greets graph (I23) and month dating (Q30).
5. **Midnight**: it needs content tags and a reviewed list for its warnings, which means
   people (D2 annotations).

## Questions for the owner

1. Rooms chosen at the door, or a single museum whose mood changes with the hour and the visitor's
   path?
2. Which social formats matter most to you: the swipe, the stories, or the timeline?
3. Midnight: how far into the offensive material may the museum go, with context?
4. On-site: is there a first venue (a third place, a festival, a library) to design the kiosk
   mode for?
