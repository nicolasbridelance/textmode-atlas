# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Decoding of stored originals into grids, one `decoding` row per artifact and decoder version.

An unreadable file is a result, not a crash: it gets a row with a classified error. The grid goes
to the derived bucket (ADR 0011), under a key that follows the row's primary key. Run twice, it
decodes nothing the second time.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Connection, Row, text
from tm_render.ansi import DecodeError, decode
from tm_render.grid import Grid, from_parquet, to_parquet
from tm_render.versions import DECODER_VERSION

from tm.storage import IntegrityError, ObjectStore, get_original, grid_key

DECODER = "tm_render.ansi"


@dataclass(frozen=True)
class Decoded:
    """The outcome, without the grid: a run over the corpus must not hold every grid."""

    path: str
    sha256: str
    error_class: str | None
    cols: int | None = None
    rows: int | None = None
    grid_sha256: str | None = None


def decode_pending(conn: Connection, originals: ObjectStore, derived: ObjectStore) -> list[Decoded]:
    """Decode every pending artifact in one transaction (tests, small runs)."""
    return [decode_artifact(conn, originals, derived, a) for a in pending_artifacts(conn)]


def pending_artifacts(conn: Connection) -> Sequence[Row[Any]]:
    """ANSI artifacts with no result yet for the current decoder version."""
    return conn.execute(
        text(
            "select a.sha256, a.source_path from artifact a where a.format = 'ansi'"
            " and not exists (select 1 from decoding d where d.sha256 = a.sha256"
            " and d.decoder = :decoder and d.decoder_version = :version)"
            " order by a.source_path, a.sha256"
        ),
        {"decoder": DECODER, "version": DECODER_VERSION},
    ).all()


def decode_artifact(
    conn: Connection,
    originals: ObjectStore,
    derived: ObjectStore,
    artifact: Row[Any],
) -> Decoded:
    sha256, path = artifact.sha256, artifact.source_path
    row = {"sha256": sha256, "decoder": DECODER, "version": DECODER_VERSION}
    try:
        grid = decode(get_original(originals, sha256)).grid
    except DecodeError as err:
        conn.execute(
            text(
                "insert into decoding (sha256, decoder, decoder_version, status, error_class)"
                " values (:sha256, :decoder, :version, 'error', :error_class)"
            ),
            {**row, "error_class": err.kind},
        )
        return Decoded(path, sha256, err.kind, None)
    _put_grid(derived, grid_key(sha256, DECODER, DECODER_VERSION), grid)
    conn.execute(
        text(
            "insert into decoding (sha256, decoder, decoder_version, status, grid_sha256, cols,"
            " rows) values (:sha256, :decoder, :version, 'ok', :grid_sha256, :cols, :rows)"
        ),
        {**row, "grid_sha256": grid.digest(), "cols": grid.cols, "rows": grid.rows},
    )
    return Decoded(path, sha256, None, grid.cols, grid.rows, grid.digest())


def _put_grid(store: ObjectStore, key: str, grid: Grid) -> None:
    """Write the grid once; an object already there must hold the same grid."""
    if store.exists(key):
        if from_parquet(store.get(key)).digest() != grid.digest():
            raise IntegrityError(f"object {key} holds a different grid: the decoder is not stable")
        return
    store.put(key, to_parquet(grid), "application/vnd.apache.parquet")
