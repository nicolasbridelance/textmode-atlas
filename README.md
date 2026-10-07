<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# textmode-atlas

*[Lire en français](README.fr.md)*

**Digital Museum of Character Arts**: ANSI, ASCII, PETSCII, ATASCII, teletext, Minitel, NFO,
Usenet, and every art whose material is the character. A museum that shows one work at a time,
the way it appeared on screen, and a research database that keeps the origin of every fact.

The project is dedicated to the people who made the textmode scene.

## What this repository contains, and under which license

| Content | License |
| --- | --- |
| Code | [Apache-2.0](LICENSES/Apache-2.0.txt) |
| Metadata, assertions, features, rendering profiles | [CC0 1.0](LICENSES/CC0-1.0.txt) |
| Texts: documentation, cartels, tours | [CC BY 4.0](LICENSES/CC-BY-4.0.txt) |
| Works and testimonies | **no license is granted by the project**: they belong to their authors and are not in this repository |

Every file declares its license following the [REUSE](https://reuse.software/) convention (SPDX
header or `REUSE.toml`). The only works in the repository are the golden artifacts in
`tests/golden/`, made for the project and dedicated to the public domain (CC0).

Is a work yours, and would you like it withdrawn, credited differently, or shown? See
[TAKEDOWN.md](TAKEDOWN.md). Withdrawals are applied with no justification asked.

## Languages

The repository is written in English. The museum is multilingual: everything a visitor reads
(interface, cartels, tours, collection titles) exists at least in English and French, and other
languages are welcome. Work titles are never translated. Machine translations are marked as such.

## Getting started

In GitHub Codespaces, the development container sets everything up. Locally you need Docker,
[`uv`](https://docs.astral.sh/uv/), [`just`](https://just.systems/) and Node 24 with `pnpm`:

```sh
just setup     # dependencies, services, migrations, storage
just check     # everything CI checks
just --list    # other commands
uv run tm --help
```

## Where to read

- [Foundation document](docs/Le%20caractère%20comme%20matière%20—%20document%20de%20fondation.md)
  (French): the specification, its invariants and milestones.
- [docs/research/](docs/research/) (French): preliminary reports — leads to verify, not sources.
- [CONTRIBUTING.md](CONTRIBUTING.md): how to contribute, and the four prohibitions.
