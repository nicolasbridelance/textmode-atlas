# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Decoded grids as the extractors read them: from the derived bucket, checked against their
decoding row, and the ones an extractor version has not read yet."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from sqlalchemy import Connection, Row, text
from tm_render.grid import Grid, from_parquet
from tm_render.versions import DECODER_VERSION

from tm.decode import DECODER
from tm.shards import EVERYTHING, Shard, condition
from tm.storage import IntegrityError, ObjectStore, grid_key

# Tables with one row per grid and extractor version: (sha256, extractor_version, …).
ExtractorTable = Literal["features", "text_layer"]


def stored_grid(derived: ObjectStore, sha256: str, grid_sha256: str) -> Grid:
    """The current decoder's grid of an artifact, refused if it is not the one its row names."""
    grid = from_parquet(derived.get(grid_key(sha256, DECODER, DECODER_VERSION)))
    if grid.digest() != grid_sha256:
        raise IntegrityError(f"grid of {sha256} does not match its decoding row")
    return grid


def pending_grids(
    conn: Connection, table: ExtractorTable, version: str, shard: Shard = EVERYTHING
) -> Sequence[Row[Any]]:
    """Grids of the current decoder with no row in `table` from extractor `version` yet."""
    return conn.execute(
        text(
            "select d.sha256, a.source_path, d.grid_sha256 from decoding d"
            " join artifact a on a.sha256 = d.sha256"
            " where d.status = 'ok' and d.decoder = :decoder"
            " and d.decoder_version = :decoder_version"
            f" and not exists (select 1 from {table} x where x.sha256 = d.sha256"
            " and x.extractor_version = :version)"
            f"{condition('d.sha256')} order by a.source_path, d.sha256"
        ),
        {
            "decoder": DECODER,
            "decoder_version": DECODER_VERSION,
            "version": version,
            **shard.params(),
        },
    ).all()
