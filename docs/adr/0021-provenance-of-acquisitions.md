<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0021. Record where and when every original was fetched, and carry it into what we publish

- Status: Accepted
- Date: 2026-10-09
- Deciders: Nicolas Bridelance (owner: "watermarquer tout ce qui passe entre nos mains avec un
  tag de la provenance, fichier récupéré à telle adresse à tel moment, pour créditer et aussi en
  waiver de notre côté"), written by Claude
- Relates to: invariant 1 (an original is never modified), ADR 0009 (credit, withdrawal)

## Context

An artifact records its first source and a path in it (`artifact.source_id`,
`source_path`). It does not record the address it was fetched from, nor when. And a file met
through several archives keeps only the first one: the textfiles copy of a 16colo pack, byte
for byte the same, leaves no trace. The owner wants every file that passes through our hands
to say where it was found and when. That serves two purposes: to credit the archive, and to
show our good faith (we took it from this public place, at this time, under its terms).

A watermark in the file itself is ruled out. An original is never modified (invariant 1), its
hash is its identity, and a mark in the pixels of a rendering would alter the work it shows.

## Decision

1. **An `acquisition` table, append-only.** One row each time a file is fetched from an
   address, with:
   - the file's SHA-256 and the source;
   - the exact URL;
   - the method (`rsync`, `http`, `manual`);
   - the retrieval time, and what that time rests on: `recorded` when the fetch wrote it,
     `file_mtime` when it was read from the local copy's date afterwards, `mirror_run` when only
     the end of a mirroring run is known;
   - what the server said of the file (`Last-Modified`, `ETag`, the remote file date kept by
     rsync).

   The same file fetched from two archives has two rows, so a copy is a second witness, not a
   lost fact. Rows are never updated nor deleted.
2. **The files inside an archive inherit its acquisitions**, through `set_member`: "extracted
   from `acid-50a.zip`, fetched from … at …". The view `artifact_provenance` gives them, for
   every artifact, direct or inherited.
3. **Fetching records itself from now on.** The mirror scripts write the time and the server's
   headers as they fetch (`acquisitions.tsv` beside the mirror), and `tm ingest acquisitions`
   loads such a file. The 16colo mirror of 2026-10-08 and the textfiles mirror of 2026-10-09
   are loaded after the fact, with their basis said honestly (`mirror_run`, `file_mtime`).
4. **What we publish carries it** (with `tm export`, roadmap step 7), never inside an original:
   - the record JSON of a work lists its provenance, credit and withdrawal link;
   - every PNG we publish carries them in its text chunks (XMP), which do not change a pixel;
   - the HTTP responses of the public bucket link to the record (`Link: rel="describedby"`);
   - a public register of the SHA-256 of every published file, so any copy can be recognised
     without a mark.

## Consequences

- Credit and withdrawal requests can name the archive and the date a file came from.
- A remote date kept by rsync (16colo's file dates) is a fact about the archive, and a lead for
  its history (when a pack entered 16colo, Q26).
- Retrieval times before this ADR are approximate, and say so in their basis.
