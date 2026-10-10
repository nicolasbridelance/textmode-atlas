# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Draw again the derived objects the database records but the store lacks: grids and
conservation renderings.

The machine moved on 2026-10-09 without about a quarter of the derived objects. Their rows hold
what they were (a grid's digest, a rendering's recipe and output digest), so each is made again
from its source, the original or the grid, and stored only if it is the same object, byte for
byte: a rebuild is also a test of invariant 3. One that comes out different is counted, not
stored, and keeps its row. Run twice, the second run finds nothing missing.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import Connection, Row, text
from tm_render.ansi import DecodeError, decode
from tm_render.conservation import BitmapFont, Settings, render
from tm_render.versions import DECODER_VERSION, RENDERER_VERSION

from tm.decode import DECODER, put_grid
from tm.grids import stored_grid
from tm.shards import EVERYTHING, Shard, condition
from tm.storage import (
    IntegrityError,
    ObjectStore,
    get_original,
    grid_key,
    original_key,
    rendering_key,
)


@dataclass
class Rebuilt:
    rebuilt: int = 0
    no_source: int = 0  # the original, or the grid, is missing too
    different: list[str] = field(default_factory=list[str])  # came out other than recorded


def rebuild_grids(
    conn: Connection, originals: ObjectStore, derived: ObjectStore, shard: Shard = EVERYTHING
) -> Rebuilt:
    """Decode again every original whose grid at the current decoder version is missing."""
    rows = conn.execute(
        text(
            "select sha256, grid_sha256 from decoding where status = 'ok' and decoder = :decoder"
            f" and decoder_version = :version{condition('sha256')} order by sha256"
        ),
        {"decoder": DECODER, "version": DECODER_VERSION, **shard.params()},
    ).all()
    result = Rebuilt()
    for row in rows:
        key = grid_key(row.sha256, DECODER, DECODER_VERSION)
        if derived.exists(key):
            continue
        if not originals.exists(original_key(row.sha256)):
            result.no_source += 1
            continue
        try:
            grid = decode(get_original(originals, row.sha256)).grid
        except DecodeError:
            result.different.append(row.sha256)
            continue
        if grid.digest() != row.grid_sha256:
            result.different.append(row.sha256)
            continue
        put_grid(derived, key, grid)
        result.rebuilt += 1
    return result


def rebuild_renderings(
    conn: Connection, derived: ObjectStore, font: BitmapFont, shard: Shard = EVERYTHING
) -> Rebuilt:
    """Draw again every conservation rendering of this renderer and font whose PNG is missing."""
    result = Rebuilt()
    for row in _renderings(conn, font, shard):
        if derived.exists(rendering_key(row.output_sha256)):
            continue
        recipe = row.recipe
        if not derived.exists(grid_key(row.sha256, DECODER, DECODER_VERSION)):
            result.no_source += 1
            continue
        try:
            grid = stored_grid(derived, row.sha256, recipe["grid_sha256"])
        except IntegrityError:
            result.different.append(row.sha256)
            continue
        settings = Settings(
            letter_spacing=recipe["letter_spacing"],
            high_bg=recipe["high_bg"],
            scale=recipe["scale"],
        )
        rendering = render(grid, font, settings)
        if rendering.recipe["output_sha256"] != row.output_sha256:
            result.different.append(row.sha256)
            continue
        derived.put(rendering_key(row.output_sha256), rendering.png, "image/png")
        result.rebuilt += 1
    return result


def _renderings(conn: Connection, font: BitmapFont, shard: Shard) -> Sequence[Row[Any]]:
    return conn.execute(
        text(
            "select sha256, recipe, output_sha256 from representation"
            " where level = 'conservation' and recipe->>'renderer_version' = :renderer_version"
            " and recipe#>>'{font,sha256}' = :font"
            f"{condition('sha256')} order by sha256"
        ),
        {"renderer_version": RENDERER_VERSION, "font": font.sha256, **shard.params()},
    ).all()
