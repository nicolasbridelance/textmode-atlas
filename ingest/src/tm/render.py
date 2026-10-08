# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Conservation renderings of decoded grids: one PNG and one `representation` row each.

The PNG goes to the derived bucket (ADR 0011), addressed by its digest; the row holds the recipe
that draws it again (invariant 3). A grid already rendered by the current renderer version, at
the same scale and with the same font, is skipped.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Connection, Row, text
from tm_render.conservation import BitmapFont, Settings, render
from tm_render.grid import from_parquet
from tm_render.sauce import Sauce
from tm_render.versions import DECODER_VERSION, RENDERER_VERSION

from tm.decode import DECODER
from tm.storage import IntegrityError, ObjectStore, grid_key, rendering_key, sha256_hex

LEVEL = "conservation"


@dataclass(frozen=True)
class Rendered:
    path: str
    sha256: str
    recipe: dict[str, Any]


def render_pending(
    conn: Connection, derived: ObjectStore, font: BitmapFont, scale: int
) -> list[Rendered]:
    """Render every decoded grid that has no conservation rendering with these settings yet."""
    pending = conn.execute(
        text(
            "select a.sha256, a.source_path, a.sauce, d.grid_sha256 from decoding d"
            " join artifact a on a.sha256 = d.sha256"
            " where d.status = 'ok' and d.decoder = :decoder"
            " and d.decoder_version = :decoder_version"
            " and not exists (select 1 from representation r where r.sha256 = d.sha256"
            " and r.level = :level and r.recipe->>'renderer_version' = :renderer_version"
            " and r.recipe->>'grid_sha256' = d.grid_sha256"
            " and (r.recipe->>'scale')::int = :scale and r.recipe#>>'{font,sha256}' = :font)"
            " order by a.source_path, a.sha256"
        ),
        {
            "decoder": DECODER,
            "decoder_version": DECODER_VERSION,
            "level": LEVEL,
            "renderer_version": RENDERER_VERSION,
            "scale": scale,
            "font": font.sha256,
        },
    ).all()
    return [_render_one(conn, derived, font, scale, row) for row in pending]


def _render_one(
    conn: Connection, derived: ObjectStore, font: BitmapFont, scale: int, row: Row[Any]
) -> Rendered:
    grid = from_parquet(derived.get(grid_key(row.sha256, DECODER, DECODER_VERSION)))
    if grid.digest() != row.grid_sha256:
        raise IntegrityError(f"grid of {row.sha256} does not match its decoding row")
    rendering = render(grid, font, Settings.from_sauce(_sauce(row.sauce), scale))
    _put_rendering(derived, rendering.png)
    conn.execute(
        text(
            "insert into representation (sha256, level, recipe, output_sha256)"
            " values (:sha256, :level, cast(:recipe as jsonb), :output_sha256)"
        ),
        {
            "sha256": row.sha256,
            "level": LEVEL,
            "recipe": json.dumps(rendering.recipe, sort_keys=True),
            "output_sha256": rendering.recipe["output_sha256"],
        },
    )
    return Rendered(row.source_path, row.sha256, rendering.recipe)


def _sauce(record: dict[str, Any] | None) -> Sauce | None:
    """The SAUCE record as `tm ingest` stored it (JSON), back as the reader's dataclass."""
    if record is None:
        return None
    fields: dict[str, Any] = {**record, "comments": tuple(record["comments"])}
    return Sauce(**fields)


def _put_rendering(store: ObjectStore, png: bytes) -> None:
    key = rendering_key(sha256_hex(png))
    if store.exists(key):
        if sha256_hex(store.get(key)) != sha256_hex(png):
            raise IntegrityError(f"object {key} does not match its hash")
        return
    store.put(key, png, "image/png")
