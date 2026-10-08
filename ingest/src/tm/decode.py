# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Decoding of stored originals into grids, one `decoding` row per artifact and decoder version.

Every art file gets a result. An unreadable file is a result, not a crash: it gets a row with a
classified error, and so does art in a format no decoder reads yet (`unsupported_format`, under
the decoder name `none`). ASCII goes through the ANSI decoder, as ansilove draws it: width from
SAUCE, else 80 columns. A SAUCE record with corrupt binary fields gives no width; the row names
the evidence (`sauce_problems`), which marks the file for a later reading that restores it. The
grid goes to the derived bucket (ADR 0011), under a key that follows
the row's primary key. Run twice, it decodes nothing the second time.
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
# Art formats the decoder reads; other art gets an `unsupported_format` row from NO_DECODER.
DECODED_FORMATS = ["ansi", "ascii"]
NO_DECODER = "none"


@dataclass(frozen=True)
class Decoded:
    """The outcome, without the grid: a run over the corpus must not hold every grid."""

    path: str
    sha256: str
    error_class: str | None
    cols: int | None = None
    rows: int | None = None
    grid_sha256: str | None = None
    sauce_problems: tuple[str, ...] = ()


def decode_pending(conn: Connection, originals: ObjectStore, derived: ObjectStore) -> list[Decoded]:
    """Decode every pending artifact in one transaction (tests, small runs)."""
    return [decode_artifact(conn, originals, derived, a) for a in pending_artifacts(conn)]


def pending_artifacts(conn: Connection) -> Sequence[Row[Any]]:
    """Art artifacts with no result yet from the decoder their format calls for, at the current
    decoder version."""
    return conn.execute(
        text(
            "select a.sha256, a.source_path, a.format from artifact a"
            " join version v on v.id = a.version_id"
            " join work w on w.id = v.work_id and w.kind = 'single'"
            " where not exists (select 1 from decoding d where d.sha256 = a.sha256"
            " and d.decoder_version = :version and d.decoder ="
            " case when a.format = any(:formats) then :decoder else :none end)"
            " order by a.source_path, a.sha256"
        ),
        {
            "decoder": DECODER,
            "none": NO_DECODER,
            "formats": DECODED_FORMATS,
            "version": DECODER_VERSION,
        },
    ).all()


def decode_artifact(
    conn: Connection,
    originals: ObjectStore,
    derived: ObjectStore,
    artifact: Row[Any],
) -> Decoded:
    sha256, path = artifact.sha256, artifact.source_path
    row = {"sha256": sha256, "decoder": DECODER, "version": DECODER_VERSION}
    if artifact.format not in DECODED_FORMATS:
        return _error(conn, {**row, "decoder": NO_DECODER}, path, "unsupported_format")
    try:
        decoded = decode(get_original(originals, sha256))
    except DecodeError as err:
        return _error(conn, row, path, err.kind)
    grid, problems = decoded.grid, decoded.sauce_problems
    _put_grid(derived, grid_key(sha256, DECODER, DECODER_VERSION), grid)
    conn.execute(
        text(
            "insert into decoding (sha256, decoder, decoder_version, status, grid_sha256, cols,"
            " rows, sauce_problems) values (:sha256, :decoder, :version, 'ok', :grid_sha256,"
            " :cols, :rows, :problems)"
        ),
        {
            **row,
            "grid_sha256": grid.digest(),
            "cols": grid.cols,
            "rows": grid.rows,
            "problems": list(problems),
        },
    )
    return Decoded(path, sha256, None, grid.cols, grid.rows, grid.digest(), problems)


def _error(conn: Connection, row: dict[str, str], path: str, error_class: str) -> Decoded:
    conn.execute(
        text(
            "insert into decoding (sha256, decoder, decoder_version, status, error_class)"
            " values (:sha256, :decoder, :version, 'error', :error_class)"
        ),
        {**row, "error_class": error_class},
    )
    return Decoded(path, row["sha256"], error_class)


def _put_grid(store: ObjectStore, key: str, grid: Grid) -> None:
    """Write the grid once; an object already there must hold the same grid."""
    if store.exists(key):
        if from_parquet(store.get(key)).digest() != grid.digest():
            raise IntegrityError(f"object {key} holds a different grid: the decoder is not stable")
        return
    store.put(key, to_parquet(grid), "application/vnd.apache.parquet")
