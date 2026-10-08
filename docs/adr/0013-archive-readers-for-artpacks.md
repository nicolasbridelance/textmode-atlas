<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0013. Read artpack archives with Python, Info-ZIP, 7-Zip and arj, checked by CRC

- Status: Accepted
- Date: 2026-10-08
- Deciders: Claude (autonomous mode, ADR 0008); Nicolas Bridelance reviews afterwards

## Context

`tm ingest pack` stores each pack archive and every file inside it (foundation document, "Trois
points d'usage"). The files must come out byte for byte: their SHA-256 is their identity, and the
grid, the features and the credits all start from them.

The 16colo mirror (measured 2026-10-08 on the 5,215 archives downloaded by then, 1990–2010; see
[source note](../sources/16colo.md)) holds:

- ZIP: 94 % of the packs. Python's `zipfile` reads deflate and stored members, but not the
  PKZIP 1.x methods (shrink, implode): 864 members in 32 packs, 12 of the 295 packs of
  1990–1993. Early packs are rare and matter for the history; losing them biases every count.
- RAR: about 6 % (296 so far).
- LHA / LZH (15) and ARJ (8).

Readers tried on these files:

| Reader | ZIP shrink / implode | RAR | LHA / LZH | ARJ |
| --- | --- | --- | --- | --- |
| Python `zipfile` | no | no | no | no |
| Info-ZIP `unzip` 6.00 (Debian) | 3 / 3 archives tested, CRC checked | | | |
| 7-Zip 23.01, official build (`7zz`) | 2 / 3 | 293 / 294 | 14 / 15 | 1 / 8 |
| 7-Zip 16.02, Debian `p7zip` | 3 / 3 | "unsupported method" (no RAR codec) | | |
| `unar` 1.10.1 | wrong bytes: 155 of 236 files of one archive fail their CRC | fails | | |
| `bsdtar` (libarchive 3.6.2) | | 8 / 285 | 9 / 15 | unrecognized |
| `arj` (GPL, Debian) | | | | 8 / 8 |

## Decision

`tm.archives.expand()` reads a pack archive into its files, in archive order:

- **ZIP**: Python `zipfile`. Members it cannot read are extracted by Info-ZIP `unzip` and kept
  only if their size and CRC-32 match the archive's own record.
- **RAR, LHA, LZH**: the official 7-Zip console build, version 23.01, pinned by SHA-256.
- **ARJ**: `arj`.
- Tools write DOS names as raw bytes; names that are not UTF-8 are read as CP437, as Python reads
  ZIP names.
- A file that cannot be read is named in the result, never guessed. An archive that cannot be
  opened is still stored and recorded, with a classified error (`bad_archive`).

The three tools are installed by `scripts/install-archive-readers.sh`, run by the development
image and by the CI job that runs the tests.

## Alternatives considered

- **One reader for everything** (`unar`, `bsdtar`, Debian `7z`): none covers the corpus, and
  `unar` returned wrong bytes without failing, the worst outcome for an archive.
- **RARLAB `unrar`**: non-free and RAR only; 7-Zip's RAR decoder comes from the same code and is
  distributed under LGPL with the unRAR restriction, which forbids writing RAR archives, not
  reading them.
- **Skip what Python cannot read**: simplest, but it removes the oldest packs first.

## Consequences

- The extracted bytes do not depend on the tool: ZIP members are checked against the archive's
  CRC by us, the other formats by the tools themselves, and a file's identity is its SHA-256.
  The tool versions therefore do not enter any recipe.
- Three external programs in the image and in CI; `missing_reader` names the one absent.
- 7-Zip's license file is installed with the binary, as its terms require.
- Archives that no reader opens stay countable: they are artifacts with no `set_member` rows.
- The one ZIP 7-Zip misreads is read by Info-ZIP, which is why ZIP never goes to 7-Zip.
