# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Text layer of every decoded grid, one `text_layer` row per artifact and extractor version.

The grid is read from the derived bucket and checked against its decoding row before it is
read. A grid without words gets a row with no lines, so a second run reads nothing.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import Connection, Row, text
from tm_analysis.text import TextLine, text_lines
from tm_analysis.versions import TEXT_VERSION

from tm.grids import pending_grids, stored_grid
from tm.shards import EVERYTHING, Shard
from tm.storage import ObjectStore


def pending_text(conn: Connection, shard: Shard = EVERYTHING) -> Sequence[Row[Any]]:
    """Grids of the current decoder with no text layer from the current extractor yet."""
    return pending_grids(conn, "text_layer", TEXT_VERSION, shard)


def read_artifact(conn: Connection, derived: ObjectStore, row: Row[Any]) -> list[TextLine]:
    lines = text_lines(stored_grid(derived, row.sha256, row.grid_sha256))
    conn.execute(
        text(
            "insert into text_layer (sha256, extractor_version, grid_sha256, line_rows, lines)"
            " values (:sha256, :version, :grid_sha256, :line_rows, :lines)"
        ),
        {
            "sha256": row.sha256,
            "version": TEXT_VERSION,
            "grid_sha256": row.grid_sha256,
            "line_rows": [line.row for line in lines],
            "lines": [line.text for line in lines],
        },
    )
    return lines
