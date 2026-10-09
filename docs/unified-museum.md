<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# One museum, progressively enriched

The collection, constellation, scientific reports and work screen share one museum
navigation and one work identity ([ADR 0027](adr/0027-one-museum-for-exploration-and-research.md)).
Exploration enriches this museum rather than producing a second visitor application.

Run `just museum` after activating the restored development environment. This builds
the Svelte site and starts its local Python host on 127.0.0.1:8737. `just explore`
is a compatibility alias. The existing machine-local Wi-Fi forwarding still works.

## Rooms and records

- `/fr/explore` and `/explore` (English; `/en/…` redirects there): the collection, metadata and decoded-text search,
  archive/year/format/kind filters, feature ordering and rendering choices.
  Its `view=pinterest`, `view=instagram` and `view=tinder` layouts share the same
  gated corpus and browser-local selection; `view=grid` is the compact gallery,
  while legacy `view=relations` URLs still show metadata relationships. The single
  header directly links the three discovery modes, Collection, Constellation and
  Research. There is no second layout menu or separate research collection switch.
  All open the same work screen.
  Chance: without a chosen order the collection is shuffled by `seed` (default
  `explorer`, so first visits agree); "Reshuffle" writes a new seed in the URL, so a
  shuffle can be shared. "A work at random" asks `/api/surprise?<filters>&seed=` for
  one decoded work whose files may be shown, within the current filters.
- `/fr/constellation` and `/constellation`: the scientific graph, its communities,
  neighbourhoods and existing interactive views. Selecting a work opens the shared screen.
- `/fr/research` and `/research`: existing dated reports and research programme.
  Source documents retain their original language and dataset scope.
- `/fr/work?w=<sha256>` and its English equivalent: conservation, credit, audience,
  withdrawal, measured features, computed neighbours and signed readings.

The live host reads `datasets/build/works/6`, `datasets/build/graph/2`, PostgreSQL
rights/audience records and private derived S3 objects. Neither originals nor those
private inputs become web build assets or Git files. Rights and audience are enforced
on the server; withheld/withdrawn records are absent, metadata-only and adult records
do not expose files. Restart the host after rights or audience changes: its policy
snapshot is loaded at startup. Existing public static deployment still reads gated
exports; its collection fallback searches the exported visit list. The full live
scientific graph requires the local API. The graph retains its pinned deck.gl CDN
dependency, so that room needs network access on first load.

## Interpretations

Local readings are JSON arrays in the ignored path
`datasets/build/interpretations/1/<artifact-sha256>.json`. Each reading has an `id`,
`title`, `body`, `locale` (`en` or `fr`), `kind` (`explanation`, `science`, `vision`),
`nature`, `asserted_by`, `method`, `input_sha256`, `sources` and `uncertainty`.
Its level is always `interpretation`. Inferred readings require an `algo:` author.
Vision readings additionally require a model identifier, prompt SHA-256 and input
rendering SHA-256, and cannot claim to be documented facts. The acquired-work hash
must match the record being enriched. Invalid readings are rejected.

Opening a page never invokes a model. No vision judgements have been invented or
generated for this consolidation. Future research and model runs can supply validated
readings to these same records; authoring workflows and public interpretation exports
remain future work. Existing reports are observations, not retroactively rewritten
results. Filtered graph views label their original training-graph statistics.

The shared canvas is used for grids supported by compact format v1; other decoded
formats use the existing conservation PNG. This preserves their visibility without
pretending that all formats already support cell inspection.

The preserved presentation workshop also belongs to the shared screen: persistent
dark/light/system theme, background/frame, pixel interpretations, comparison and
PNG/recipe export. Its source and limitations are in [the workshop](presentation-workshop.md)
and [experiments](presentation-experiments.md), also readable in the research room.
These pixel rules are labelled interpretations and do not invoke vision models.
