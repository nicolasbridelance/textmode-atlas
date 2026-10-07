<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
<p align="center">
  <img src="docs/assets/horizon.png" width="720"
       alt="An ANSI artwork: the word TEXTMODE in white and cyan block letters over a starry night, a full moon, a dusk glow drawn in blue, magenta and red shades, dark mountains, and a sea carrying the moon's path. Signed: horizon, made by claude for textmode-atlas, cc0 2026.">
</p>

<p align="center">
  <em>Horizon</em> — 80 × 40 characters, code page 437, VGA palette. Made by Claude for the museum's tests; CC0.
</p>

# textmode-atlas

*[Lire en français](README.fr.md)*

[![ci](https://github.com/nicolasbridelance/textmode-atlas/actions/workflows/ci.yml/badge.svg)](https://github.com/nicolasbridelance/textmode-atlas/actions/workflows/ci.yml)

**The Digital Museum of Character Arts.** ANSI and ASCII art, PETSCII, ATASCII, teletext, Minitel,
NFO files, Usenet, and every art whose material is the character.

These works were born on screens. Shown at the right size, with the right font and palette, an
ANSI is not a reproduction: it is the work. The museum shows them that way, one at a time, and
keeps a research database that says where each one comes from and what it is linked to.

The project is dedicated to the people who made the textmode scene.

## What a visit will feel like

- **One work, full screen, on black.** No grid of thumbnails, no account, no pop-up.
- **Drawn at modem speed.** The work appears line by line at 2,400 baud, the way it reached a
  BBS caller in 1994. Space shows it at once.
- **Down to the character.** Zoom until you see which glyph and which two colours make each
  cell: how it was done.
- **Somewhere to go next.** Each work offers three to five exits: the next one in its pack,
  another by the same artist, the closest in style, a rival group's answer, what came out
  elsewhere that month.
- **Tours** of 12 to 20 works written by named people, and the scene's own radio stations
  playing along.

## Where it stands

Under construction, in the open. The repository runs on its target architecture: content-
addressed storage, a database whose invariants are enforced by constraints, a static bilingual
site. The first work screen is being built now. Follow along in the
[roadmap](docs/roadmap.md) and the [session journal](docs/journal/).

## How it works

```
source → acquisition → hash → grid → features → renderings → export → site
```

- **Originals are never modified.** Every file is stored once, addressed by its SHA-256.
- **The grid is the pivot.** Each work is decoded once into cells (character, colours, the byte
  that wrote it); the browser draws the work from that grid, sharp at any scale.
- **Every link has an origin.** "Who made this, with whom, for whom" lives in a single
  append-only table: each relation says who asserts it and on what evidence. A computation is
  never shown as a fact.
- **Research reads the corpus as a whole.** Credits, greetings and BBS adverts become links;
  style, novelty and the spread of techniques are measured, with pre-registered questions and
  published coverage. See the [research programme](docs/research-program.md).

## Credit, and the right to leave

The museum shows what the scene itself released for free distribution, credited as signed, with
a link to the archive that holds it. Every work carries **"Is this yours? Withdraw or claim."**
A withdrawal is immediate and asks for no justification: write to **ennead.studio@gmail.com** or
see [TAKEDOWN.md](TAKEDOWN.md). Handles stay handles: no link to a civil identity without
consent. Nothing is sold, and no model is trained to imitate anyone.

## Licenses

| Content | License |
| --- | --- |
| Code | [Apache-2.0](LICENSES/Apache-2.0.txt) |
| Metadata, assertions, features, rendering profiles | [CC0 1.0](LICENSES/CC0-1.0.txt) |
| Texts: documentation, cartels, tours | [CC BY 4.0](LICENSES/CC-BY-4.0.txt) |
| Works and testimonies | **no license is granted by the project**: they belong to their authors and are not in this repository |

Every file declares its license following [REUSE](https://reuse.software/). The only works in
the repository are the project's own CC0 reference pieces, like the one above.

## Languages

The repository is in English. The museum is multilingual: everything a visitor reads exists at
least in English and French, and other languages are welcome. Work titles are never translated.

## Getting started

In GitHub Codespaces the development container sets everything up. Locally you need Docker,
[`uv`](https://docs.astral.sh/uv/), [`just`](https://just.systems/) and Node 24 with `pnpm`:

```sh
just setup     # dependencies, services, migrations, storage, git hooks
just check     # everything CI checks
just --list    # other commands
```

## Read more

- [Foundation document](docs/Le%20caractère%20comme%20matière%20—%20document%20de%20fondation.md)
  (French): the specification, its invariants and milestones.
- [Research programme](docs/research-program.md) and [roadmap](docs/roadmap.md).
- [Architecture decisions](docs/adr/) and [spikes](docs/spikes/).
- [CONTRIBUTING.md](CONTRIBUTING.md): how to contribute, and the four prohibitions.
