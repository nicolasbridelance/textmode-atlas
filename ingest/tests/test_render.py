# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
from PIL import Image
from sqlalchemy import Connection, text
from stores import Stores
from tm.decode import DECODER, decode_pending
from tm.ingest import ingest_golden
from tm.render import render_pending
from tm.storage import IntegrityError, grid_key, rendering_key
from tm_render.conservation import BitmapFont, pixels_sha256
from tm_render.grid import Grid, to_parquet
from tm_render.versions import DECODER_VERSION, RENDERER_VERSION

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "tests" / "golden"
PINNED = json.loads((GOLDEN / "renderings.json").read_text())
FONT = BitmapFont.load(ROOT / "corpus" / "fonts" / "ibm-vga-8x16.f16")

pytestmark = pytest.mark.db


def decoded(db: Connection, stores: Stores, root: Path = GOLDEN) -> str:
    sha = ingest_golden(db, stores.originals, root)[0].sha256
    decode_pending(db, stores.originals, stores.derived)
    return sha


def test_the_whole_chain_draws_the_pinned_pixels(db: Connection, stores: Stores) -> None:
    sha = decoded(db, stores)
    [item] = render_pending(db, stores.derived, FONT, scale=1)
    assert item.path == "ansi/horizon.ans"
    assert item.recipe["pixels_sha256"] == PINNED["ansi/horizon.ans"]["pixels_sha256"]
    png = stores.derived.get(rendering_key(item.recipe["output_sha256"]))
    assert pixels_sha256(Image.open(io.BytesIO(png))) == item.recipe["pixels_sha256"]
    row = db.execute(text("select * from representation where sha256 = :s"), {"s": sha}).one()
    assert (row.level, row.profile, row.output_sha256) == (
        "conservation",
        None,
        item.recipe["output_sha256"],
    )
    assert row.recipe["renderer_version"] == RENDERER_VERSION
    assert (row.recipe["letter_spacing"], row.recipe["high_bg"]) == (9, "blink")


def test_render_is_idempotent(db: Connection, stores: Stores) -> None:
    decoded(db, stores)
    assert len(render_pending(db, stores.derived, FONT, scale=1)) == 1
    assert render_pending(db, stores.derived, FONT, scale=1) == []
    assert db.execute(text("select count(*) from representation")).scalar_one() == 1


def test_another_scale_is_another_rendering(db: Connection, stores: Stores) -> None:
    decoded(db, stores)
    render_pending(db, stores.derived, FONT, scale=1)
    [item] = render_pending(db, stores.derived, FONT, scale=2)
    assert (item.recipe["scale"], item.recipe["width"]) == (2, 2 * 80 * 9)


def test_a_failed_decoding_is_not_rendered(db: Connection, stores: Stores, tmp_path: Path) -> None:
    root = tmp_path / "golden"
    root.mkdir()
    (root / "empty.ans").write_bytes(b"")
    decoded(db, stores, root)
    assert render_pending(db, stores.derived, FONT, scale=1) == []


def test_a_grid_that_differs_from_its_decoding_row_stops_the_run(
    db: Connection, stores: Stores
) -> None:
    sha = decoded(db, stores)
    key = grid_key(sha, DECODER, DECODER_VERSION)
    stores.derived.put(key, to_parquet(Grid(80, 1, {})))
    with pytest.raises(IntegrityError, match="does not match its decoding row"):
        render_pending(db, stores.derived, FONT, scale=1)


def test_an_altered_png_stops_the_run(db: Connection, stores: Stores) -> None:
    decoded(db, stores)
    [item] = render_pending(db, stores.derived, FONT, scale=1)
    key = rendering_key(item.recipe["output_sha256"])
    db.execute(text("delete from representation"))
    stores.derived.put(key, b"not a png")
    with pytest.raises(IntegrityError, match="does not match its hash"):
        render_pending(db, stores.derived, FONT, scale=1)
