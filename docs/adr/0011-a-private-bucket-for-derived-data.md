<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0011. Keep derived data in a third, private bucket

- Status: Accepted
- Date: 2026-10-08
- Deciders: Claude (autonomous mode, ADR 0008); Nicolas Bridelance reviews afterwards

## Context

The foundation document names two buckets: the originals (private, write-once, versioned, kept in
three copies) and the public files, filled by `tm export` with what `can_display()` allows.

`tm decode` now produces a grid (Parquet) for every artifact, and `tm render` will produce PNGs.
They must live somewhere, and neither bucket fits:

- They are not originals. They are computed, and can be computed again: the grid from the
  original and the decoder version, the PNG from the grid and its recipe (invariant 3). The
  originals bucket is the museum's irreplaceable part, with versioning and three copies; filling
  it with data that can be rebuilt makes every copy larger and blurs what "write-once" protects.
- They cannot go to the public bucket as such. Analysis needs the grid of every work, including
  the ones we may not show (`metadata` or `none`). A private grid in a public bucket would break
  invariant 6.

The Parquet bytes are also not a stable identity: the same grid written by two versions of
pyarrow may differ byte for byte. The stable identity is the grid digest (`Grid.digest()`), which
the `decoding` table already records.

## Decision

Three buckets:

| Bucket | Holds | Access | Policy |
| --- | --- | --- | --- |
| `tm-originals` | originals, `sha256/ab/cd/<sha256>` | private | write-once, versioned, three copies |
| `tm-derived` | grids, later renderings and features | private | rebuildable: not replicated, may be emptied and rebuilt |
| `tm-public` | what `tm export` copies from `tm-derived`, after `can_display()` | public, behind the CDN | a withdrawal deletes and purges |

A grid is stored at `grids/<sha[:2]>/<sha[2:4]>/<sha>/<decoder>@<decoder_version>.parquet`,
where `<sha>` is the artifact's hash: the key follows the primary key of the `decoding` row, not
the file content. Writing is idempotent. When the object already exists, `tm decode` reads it
back and compares its grid digest with the one it just computed; a difference stops the run with
an integrity error, since the same decoder version must give the same grid.

`tm export` reads from `tm-derived` and writes to `tm-public`. Nothing reaches `tm-public` by any
other path.

## Alternatives considered

- **A `grids/` prefix in `tm-originals`** (the first idea): one bucket fewer to declare, but
  rebuildable data would be versioned and copied three times like irreplaceable data, and a
  lifecycle rule meant for derived files would sit one prefix away from the originals.
- **A private prefix in `tm-public`**: one misconfigured policy or CDN rule would publish works
  we may not show. Invariant 6 should not depend on a prefix.
- **Grids in PostgreSQL** (`bytea`): the grid is already a table of cells; but the database is
  backed up daily and grows with every decoder version, for data that is cheap to rebuild.
- **Address the file by its content hash**: Parquet output is not byte-stable across library
  versions, so the same grid would get several keys.

## Consequences

- One more bucket in `tm dev storage-init`, in the settings (`TM_DERIVED_BUCKET`) and, from M4,
  in OpenTofu.
- Losing `tm-derived` costs time, not data: `tm decode` and `tm render` rebuild it.
- Backups cover originals and the database only.
- A new decoder version writes new keys beside the old ones; old grids stay until an explicit
  cleanup.
- The foundation document is amended in the same change (architecture, hosting table, backups).
