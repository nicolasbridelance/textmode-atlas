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

from tm.grids import pending_grids, stored_grid
from tm.shards import EVERYTHING, Shard
from tm.storage import ObjectStore

COLUMNS = [field.name for field in dataclasses.fields(Features)]


def pending_features(conn: Connection, shard: Shard = EVERYTHING) -> Sequence[Row[Any]]:
    """Grids of the current decoder with no features from the current extractor yet."""
    return pending_grids(conn, "features", FEATURES_VERSION, shard)


def extract_artifact(conn: Connection, derived: ObjectStore, row: Row[Any]) -> Features:
    features = extract(stored_grid(derived, row.sha256, row.grid_sha256))
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
