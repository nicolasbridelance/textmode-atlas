<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0030. Screens and documents of text-mode computing enter the corpus, beside the art

- Status: Accepted
- Date: 2026-10-10
- Deciders: Claude (autonomous mode, ADR 0008), at the owner's request ("enrichir les corpus …
  en particulier : OS, logiciels, splash screens, games, minitel, soluces, nfo, readme, manuels,
  man, warez, cracks"); Nicolas Bridelance reviews afterwards. The legal points below wait for
  him and the lawyer.
- Amends: foundation document, "Pratiques voisines" and milestone M5
- Relates to: ADR 0009 (show what the scene released), 0020 (audience grid), 0024 (loose files),
  0026 (one grid for every system)

## Context

The corpus holds art made as art: the packs of 16colo and textfiles.com, and soon textfiles'
loose ANSI, ASCII, RTTY and VT100 (ADR 0024). The foundation document already puts NFO, FAQ,
games and the Minitel in the scope of M5, and lists neighbouring practices. It does not name
the rest of what a text-mode screen showed: the operating system, the programs and their
splash and quit screens, the games, the documents that came with them (readme, manuals, man
pages, walkthroughs), and the warez scene that wrote the NFO and drew the cracktros. The owner
asked for all of it.

These are the same material: cells of one character set, one palette, one font. The art scene
grew out of them (the NFO, the BBS screen, the door game), borrowed from them (box drawing from
interfaces, ASCII headers from FAQs) and was read on them. Without them the museum shows the art
cut off from the screens around it, and research cannot ask what made art art (Q16, I54).

They are also different in three ways that matter here:

- **Most are not art**, and existing measurements were made on art. Mixing them in would move
  every figure the research room shows.
- **Many exist only while a program runs.** An OS prompt, a word processor's menu, a game
  screen are not files; they are states of video memory. Some were saved as files: DOOM's
  `ENDOOM` lump is a raw 80 × 25 text-mode dump (the BIN layout, character and attribute
  pairs), ZZT boards are files, Minitel pages are `.vdt` byte streams.
- **Rights are not the scene's.** ADR 0009 covers what the scene released. An operating system,
  a commercial program or a game belongs to its publisher; a cracked copy of it is an
  infringing copy.

## Decision

1. **Scope.** "Le caractère comme matière" covers every screen and document made of character
   cells, art or not. Three families enter as collections:
   - **screens**: operating systems, program interfaces, splash and quit screens, text-mode
     games (ZZT, roguelikes, BBS door games), Minitel and videotex pages;
   - **documents**: NFO and FILE_ID.DIZ, readme files, manuals and on-line documentation,
     man pages, walkthroughs, hints and FAQs;
   - **the warez scene**: NFO, applications and member lists, courier lists, texts on cracking,
     cracktros and BBS adverts.
2. **Usage says what a work is.** Each work carries `work.usage` (already in the schema:
   `image`, `interface`, `tool`, `world`, …; `document` is added for texts read rather than
   looked at) and `work.channel`. Datasets and the research room keep art only by default,
   with the filter written in their definition, so existing results stay comparable; a study
   that crosses families says so.
3. **How each enters.**
   - Text documents: artifacts with a text layer, `single` works of usage `document`, by the
     loose-files rule of ADR 0024 (split by directory).
   - Screens saved as files (BIN and B800 dumps, `ENDOOM`, ZZT boards, `.vdt` pages): decoded
     into grid v2 (ADR 0026), one decoder per format, after grid v2 lands.
   - Screens that exist only in a running program: a capture, recorded as a `trace` of kind
     `capture` with its recipe (emulator and version, program hash, keystrokes, moment), the
     grid read from video memory rather than from pixels. A spike measures how before any code.
4. **Never stored:** a cracked program, a crack, patch, trainer or key generator, or a commercial
   program its publisher did not release freely. Such a file may be recorded by name, size and
   hash when a document refers to it, never kept. Cracktros, NFO and the scene's own texts are
   the scene's releases and follow ADR 0009 like the art. Freeware, shareware released for
   distribution, free software and public domain programs may be stored as originals.
5. **Shown only with a right.** Screens and documents of software published outside the scene
   (operating systems, commercial programs and games, their manuals) are not covered by ADR 0009:
   `can_display()` refuses them until the owner and the lawyer decide (short quotation, publisher
   permission, or records only). Free-licensed documents (BSD and GNU man pages, FreeDOS) are
   shown under their licence, with its notice. Every work, whatever its family, is rated on the
   audience grid (ADR 0020); textfiles' sections on drugs, anarchy and sex are not part of this
   decision.
6. **Order.** Sources that are files come first, measured in the [source register](../sources/README.md#screens-and-documents-of-text-mode-computing-adr-0030):
   textfiles.com's sections (piracy, adventure, games, computers, programming), man pages,
   `ENDOOM` screens, ZZT worlds, then Minitel pages once a bulk source is found (I57), then
   captures.

## Consequences

- The corpus gains a family that is mostly text and mostly not art. The text layer, spike 0006's
  readings and the per-line ADR of step 15 apply to it as they are; NFO credit extraction (M4)
  finds its main material here.
- Every dataset definition and research reading states its usage filter. Works without a usage
  are art (everything ingested before this ADR).
- The BIN decoder, today `unsupported_format`, gains a second reason to exist: video memory
  dumps.
- Display of third-party software screens waits for a legal decision; records, grids and
  research can proceed meanwhile in the private bucket.
- The roadmap gains a step after step 19; nothing before it moves.

## Alternatives considered

- **A separate collection outside the corpus.** Rejected: the same decoders, grids and
  measurements apply, and the comparison art / not art is the point.
- **Wait for M5.** Rejected for the files that are already text: the pipeline reads them today.
  Screens that need decoders or captures do wait for grid v2.
- **Store cracks and commercial programs privately, never shown.** Rejected: holding an
  infringing copy is the act the law forbids, shown or not, and the museum has no use for the
  bytes beyond what their hash and the documents say.
