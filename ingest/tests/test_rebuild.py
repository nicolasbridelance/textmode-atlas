# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import Connection, text
from stores import Stores
from tm.decode import DECODER
from tm.rebuild import rebuild_grids, rebuild_renderings
from tm.render import render_pending
from tm.storage import grid_key, original_key, rendering_key
from tm_render.conservation import BitmapFont
from tm_render.versions import DECODER_VERSION

pytestmark = pytest.mark.db

FONT = BitmapFont.load(Path(__file__).resolve().parents[2] / "corpus/fonts/ibm-vga-8x16.f16")


def test_a_lost_grid_and_rendering_are_made_again_the_same(
    db: Connection, stores: Stores, horizon: str
) -> None:
    render_pending(db, stores.derived, FONT, 1)
    output = db.execute(text("select output_sha256 from representation")).scalar_one()
    grid, png = grid_key(horizon, DECODER, DECODER_VERSION), rendering_key(output)
    kept = stores.derived.get(grid), stores.derived.get(png)
    stores.derived.delete(grid)
    stores.derived.delete(png)  # what the move of 2026-10-09 left behind

    grids = rebuild_grids(db, stores.originals, stores.derived)
    renderings = rebuild_renderings(db, stores.derived, FONT)

    assert (grids.rebuilt, grids.different, renderings.rebuilt, renderings.different) == (
        1,
        [],
        1,
        [],
    )
    assert (stores.derived.get(grid), stores.derived.get(png)) == kept
    assert rebuild_grids(db, stores.originals, stores.derived).rebuilt == 0


def test_without_its_original_a_grid_stays_missing(
    db: Connection, stores: Stores, horizon: str
) -> None:
    stores.derived.delete(grid_key(horizon, DECODER, DECODER_VERSION))
    stores.originals.delete(original_key(horizon))
    assert rebuild_grids(db, stores.originals, stores.derived).no_source == 1
    assert rebuild_renderings(db, stores.derived, FONT).no_source == 0  # none was drawn


def test_a_grid_that_comes_out_different_is_not_stored(
    db: Connection, stores: Stores, horizon: str
) -> None:
    stores.derived.delete(grid_key(horizon, DECODER, DECODER_VERSION))
    db.execute(text("alter table decoding disable trigger all"))
    db.execute(text("update decoding set grid_sha256 = repeat('0', 64)"))
    rebuilt = rebuild_grids(db, stores.originals, stores.derived)
    assert (rebuilt.rebuilt, rebuilt.different) == (0, [horizon])
    assert not stores.derived.exists(grid_key(horizon, DECODER, DECODER_VERSION))
