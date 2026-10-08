# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path

import pytest
from tm_analysis.features import Features, extract
from tm_render.ansi import decode
from tm_render.grid import Cell, Grid

HORIZON = Path(__file__).resolve().parents[2] / "tests" / "golden" / "ansi" / "horizon.ans"
# Features of the golden artifact, pinned: a change of value must come with a new version.
HORIZON_DIGEST = "c7e75c1d55637346b1689927c6d08c50a9fa76df8a32b604744c326e6dff40ec"
BLOCK, HALF, SHADE, BOX, SPACE = 0xDB, 0xDC, 0xB1, 0xC4, 0x20
GREY, RED, BLUE = 7, 4, 1


def grid(cols: int, rows: int, cells: dict[tuple[int, int], int], **colour: int) -> Grid:
    """A grid whose cells are written in reading order, grey on black unless told otherwise."""
    fg, bg = colour.get("fg", GREY), colour.get("bg", 0)
    return Grid(
        cols,
        rows,
        {pos: Cell(cp, fg, bg, False, pos[0] * cols + pos[1]) for pos, cp in cells.items()},
    )


def digest(features: Features) -> str:
    payload = json.dumps(dataclasses.asdict(features), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def test_an_empty_canvas_has_neutral_measures() -> None:
    features = extract(Grid(80, 1, {}))
    assert (features.cells, features.fill_ratio, features.glyph_entropy) == (0, 0.0, 0.0)
    assert (features.center_row, features.center_col) == (0.5, 0.5)
    assert (features.symmetry_h, features.n_colors, features.draw_order) == (0.0, 0, 1.0)


def test_spaces_count_as_ink_only_when_painted() -> None:
    plain = extract(grid(4, 1, {(0, 0): SPACE, (0, 1): BLOCK}))
    painted = extract(grid(4, 1, {(0, 0): SPACE, (0, 1): BLOCK}, bg=BLUE))
    assert plain.fill_ratio == pytest.approx(1 / 4)
    assert painted.fill_ratio == pytest.approx(2 / 4)


def test_a_glyph_in_its_background_colour_shows_nothing() -> None:
    assert extract(grid(2, 1, {(0, 0): BLOCK}, fg=0)).fill_ratio == 0.0


def test_centre_of_mass_and_symmetry() -> None:
    corner = extract(grid(5, 5, {(4, 4): BLOCK}))
    assert (corner.center_row, corner.center_col) == (1.0, 1.0)
    arch = extract(grid(5, 2, {(0, 0): BLOCK, (0, 4): BLOCK, (1, 0): BLOCK, (1, 4): BLOCK}))
    assert arch.symmetry_h == 1.0
    stair = extract(grid(3, 3, {(0, 0): BLOCK, (1, 1): BLOCK, (2, 2): BLOCK, (0, 1): BLOCK}))
    assert 0.0 < stair.symmetry_h < 1.0


def test_glyph_classes_and_entropy() -> None:
    cells = {(0, 0): BLOCK, (0, 1): HALF, (0, 2): SHADE, (0, 3): BOX, (0, 4): ord("A")}
    cells |= {(0, 5): ord("!"), (0, 6): 0x01}
    features = extract(grid(8, 1, cells))
    shares = [
        features.class_block,
        features.class_half_block,
        features.class_shade,
        features.class_box,
        features.class_alphanumeric,
        features.class_punctuation,
        features.class_other,
    ]
    assert shares == pytest.approx([1 / 7] * 7)
    assert features.glyph_entropy == pytest.approx(2.807, abs=1e-3)  # log2(7)
    assert sum(features.glyph_hist) == len(cells)


def test_bigrams_are_horizontal_pairs_most_frequent_first() -> None:
    cells = {(0, c): cp for c, cp in enumerate([BLOCK, HALF, BLOCK, HALF, SHADE])}
    features = extract(grid(5, 1, cells))
    assert features.bigram_codes[0] == BLOCK * 256 + HALF
    assert features.bigram_counts[:2] == [2, 1]


def test_colours_and_bright_backgrounds() -> None:
    cells = {
        (0, 0): Cell(BLOCK, RED, 0, False, 0),
        (0, 1): Cell(ord("A"), GREY, BLUE, True, 1),
        (0, 2): Cell(SPACE, GREY, BLUE, True, 2),
    }
    features = extract(Grid(3, 1, cells))
    assert features.n_colors == len({RED, GREY, 0, BLUE})
    assert features.fg_hist[RED] == features.fg_hist[GREY] == 1
    assert features.bg_hist[BLUE] == 2
    assert features.high_bg_ratio == pytest.approx(2 / 3)
    assert features.fg_bg_pairs == 2


def test_a_typed_screen_is_linear_and_a_drawn_one_is_not() -> None:
    typed = extract(grid(3, 2, {(r, c): BLOCK for r in range(2) for c in range(3)}))
    assert (typed.cursor_jumps, typed.draw_order) == (0.0, 1.0)
    backwards = {(0, c): Cell(BLOCK, GREY, 0, False, 2 - c) for c in range(3)}
    drawn = extract(Grid(3, 1, backwards))
    assert (drawn.cursor_jumps, drawn.draw_order) == (1.0, -1.0)


def test_the_golden_artifact_gives_the_pinned_features() -> None:
    features = extract(decode(HORIZON.read_bytes()).grid)
    assert digest(features) == digest(extract(decode(HORIZON.read_bytes()).grid))
    assert digest(features) == HORIZON_DIGEST, f'pin "{digest(features)}"'
