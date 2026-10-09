<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# 0027 — One museum for exploration and research

Status: Accepted, at the owner's explicit request, 2026-10-09.

## Decision

The collection browser, nearest-work constellation, scientific publications and work
screen are rooms of one museum. Research progressively enriches the same work record;
there is no separate visitor product called the research explorer. Existing scientific
datasets, reproducible pipelines and train/test separation remain independent of the UI.

The Svelte museum owns the navigation, localized collection and shared work screen.
Its local Python host reads the existing works/6 and graph/2 datasets and private derived
storage, serving the built museum and its data from one origin. `just explore` remains a
compatibility alias for this museum. The existing WebGL constellation is retained as a
room and opens works in the shared screen.

Source, conservation, documented evidence and interpretation stay distinct inside each
record. Vision-model readings require an `algo:` author, model identity, input hash,
method and uncertainty; absent readings are never invented. No model is invoked by
opening a page. Local interpretation inputs remain outside Git.

## Boundaries

One interface does not grant publication rights. The live host applies `can_display()`
and the audience grid to records, grids, images, text and graph nodes. Metadata-only
records remain accessible without their files; withdrawn/withheld works are absent.
Public static hosting continues to consume gated exports and does not include private
datasets or S3 credentials. Publishing further scientific/vision data requires its
normal provenance and rights checks, not a second interface.

## Consequences

The phone's existing local URL opens the same museum. Existing gallery controls,
metadata/text search, feature ordering, neighbours and scientific graph survive.
Scientific reports remain dated observations of their stated dataset versions.
Future analyses extend the museum's interpretation contract and publications room.
