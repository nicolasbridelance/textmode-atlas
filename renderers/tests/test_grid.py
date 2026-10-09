# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
import hashlib
import struct
from dataclasses import replace
from pathlib import Path

import pytest
from tm_render.ansi import decode
from tm_render.grid import (
    BLINK,
    DOUBLE_HEIGHT_TOP,
    PC_VGA,
    Cell,
    Grid,
    Header,
    from_parquet,
    from_table,
    to_parquet,
    to_table,
)

GOLDEN = Path(__file__).resolve().parents[2] / "tests" / "golden" / "ansi" / "horizon.ans"
TELETEXT = Header("teletext", "teletext-g0-en", "teletext8", "saa5050", 12, 20)
# Horizon's grid digest under grid v1, before ADR 0026: grid v2 must keep it.
# Recorded by decoder v4 in `decoding.grid_sha256`, 2026-10-09.
HORIZON_V1 = "2b72558a1d23805fed14dc6269381aa2d625e9ef86879d89b261e89023999244"


def v1_digest(grid: Grid) -> str:
    """Grid v1's serialization, written out again here so that the test does not trust the code."""
    sha = hashlib.sha256(struct.pack("<HH", grid.cols, grid.rows))
    for (row, col), c in sorted(grid.cells.items()):
        sha.update(struct.pack("<HHHBBBI", row, col, c.glyph, c.fg, c.bg, c.blink, c.t))
    return sha.hexdigest()


def test_parquet_round_trip() -> None:
    grid = decode(GOLDEN.read_bytes()).grid
    again = from_parquet(to_parquet(grid))
    assert again == grid
    assert again.digest() == grid.digest()


def test_empty_grid_round_trip() -> None:
    grid = Grid(80, 1, {})
    assert from_parquet(to_parquet(grid)) == grid


def test_a_pc_grid_keeps_its_grid_v1_digest() -> None:
    grid = decode(GOLDEN.read_bytes()).grid
    assert grid.fits_v1()
    assert grid.digest() == v1_digest(grid) == HORIZON_V1


def test_anything_beyond_grid_v1_changes_the_digest() -> None:
    grid = Grid(2, 1, {(0, 0): Cell(0x41, 7, 0, 0, BLINK)})
    variants = [
        replace(grid, header=TELETEXT),
        replace(grid, cells={(0, 0): Cell(0x41, 7, 0, 0, DOUBLE_HEIGHT_TOP)}),
        replace(grid, cells={(0, 0): Cell(0x41, 7, 0, 0, BLINK, control=0x11)}),
        replace(grid, strikes={(0, 0): (Cell(0x5F, 7, 0, 1),)}),
        replace(grid, cells={(0, 0): Cell(0x41, 300, 0, 0, BLINK)}),
    ]
    digests = {grid.digest(), *(variant.digest() for variant in variants)}
    assert len(digests) == len(variants) + 1
    assert not any(variant.fits_v1() for variant in variants)


def test_layers_controls_and_header_survive_parquet() -> None:
    grid = Grid(
        40,
        2,
        {(0, 0): Cell(0x20, 7, 0, 0, control=0x11), (1, 3): Cell(0x7F, 2, 0, 9, DOUBLE_HEIGHT_TOP)},
        TELETEXT,
        {(1, 3): (Cell(0x2D, 2, 0, 10), Cell(0x7C, 2, 0, 11))},
    )
    again = from_parquet(to_parquet(grid))
    assert again == grid
    assert again.digest() == grid.digest()
    assert [item[:3] for item in grid.layers()] == [(0, 0, 0), (1, 3, 0), (1, 3, 1), (1, 3, 2)]


def test_the_header_travels_in_the_parquet_metadata() -> None:
    metadata = to_table(Grid(1, 1, {}, TELETEXT)).schema.metadata
    assert metadata[b"grid_version"] == b"2"
    assert (metadata[b"system"], metadata[b"charset"]) == (b"teletext", b"teletext-g0-en")
    assert PC_VGA.charset == "cp437"


def test_a_grid_v1_table_is_refused() -> None:
    v1 = to_table(Grid(1, 1, {})).replace_schema_metadata({b"cols": b"1", b"rows": b"1"})
    with pytest.raises(ValueError, match="not a grid v2"):
        from_table(v1)
