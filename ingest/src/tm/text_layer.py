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
from tm_render.grid import from_parquet
from tm_render.versions import DECODER_VERSION

from tm.decode import DECODER
from tm.shards import EVERYTHING, Shard, condition
from tm.storage import IntegrityError, ObjectStore, grid_key


def pending_text(conn: Connection, shard: Shard = EVERYTHING) -> Sequence[Row[Any]]:
    """Grids of the current decoder with no text layer from the current extractor yet."""
    return conn.execute(
        text(
            "select d.sha256, a.source_path, d.grid_sha256 from decoding d"
            " join artifact a on a.sha256 = d.sha256"
            " where d.status = 'ok' and d.decoder = :decoder"
            " and d.decoder_version = :decoder_version"
            " and not exists (select 1 from text_layer t where t.sha256 = d.sha256"
            " and t.extractor_version = :version)"
            f"{condition('d.sha256')} order by a.source_path, d.sha256"
        ),
        {
            "decoder": DECODER,
            "decoder_version": DECODER_VERSION,
            "version": TEXT_VERSION,
            **shard.params(),
        },
    ).all()


def read_artifact(conn: Connection, derived: ObjectStore, row: Row[Any]) -> list[TextLine]:
    grid = from_parquet(derived.get(grid_key(row.sha256, DECODER, DECODER_VERSION)))
    if grid.digest() != row.grid_sha256:
        raise IntegrityError(f"grid of {row.sha256} does not match its decoding row")
    lines = text_lines(grid)
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
