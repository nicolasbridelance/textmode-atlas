# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Features of every decoded grid, one `features` row per artifact and extractor version.

The grid is read from the derived bucket and checked against its decoding row before it is
measured. Run twice, it measures nothing the second time; a new extractor version measures
everything again, beside the rows of the old one.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from typing import Any

from sqlalchemy import Connection, Row, text
from tm_analysis.features import Features, extract
from tm_analysis.versions import FEATURES_VERSION
from tm_render.grid import from_parquet
from tm_render.versions import DECODER_VERSION

from tm.decode import DECODER
from tm.shards import EVERYTHING, FILTER, Shard
from tm.storage import IntegrityError, ObjectStore, grid_key

COLUMNS = [field.name for field in dataclasses.fields(Features)]


def pending_features(conn: Connection, shard: Shard = EVERYTHING) -> Sequence[Row[Any]]:
    """Grids of the current decoder with no features from the current extractor yet."""
    return conn.execute(
        text(
            "select d.sha256, a.source_path, d.grid_sha256 from decoding d"
            " join artifact a on a.sha256 = d.sha256"
            " where d.status = 'ok' and d.decoder = :decoder"
            " and d.decoder_version = :decoder_version"
            " and not exists (select 1 from features f where f.sha256 = d.sha256"
            " and f.extractor_version = :version)"
            f"{FILTER} order by a.source_path, d.sha256"
        ),
        {
            "decoder": DECODER,
            "decoder_version": DECODER_VERSION,
            "version": FEATURES_VERSION,
            **shard.params(),
        },
    ).all()


def extract_artifact(conn: Connection, derived: ObjectStore, row: Row[Any]) -> Features:
    grid = from_parquet(derived.get(grid_key(row.sha256, DECODER, DECODER_VERSION)))
    if grid.digest() != row.grid_sha256:
        raise IntegrityError(f"grid of {row.sha256} does not match its decoding row")
    features = extract(grid)
    names = ", ".join(COLUMNS)
    values = ", ".join(f":{name}" for name in COLUMNS)
    conn.execute(
        text(
            f"insert into features (sha256, extractor_version, grid_sha256, {names})"
            f" values (:sha256, :version, :grid_sha256, {values})"
        ),
        {
            "sha256": row.sha256,
            "version": FEATURES_VERSION,
            "grid_sha256": row.grid_sha256,
            **dataclasses.asdict(features),
        },
    )
    return features
