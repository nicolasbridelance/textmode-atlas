# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
import importlib.util
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "thumbnails", ROOT / "research" / "explorer" / "thumbnails.py"
)
assert spec
assert spec.loader
thumbnails = importlib.util.module_from_spec(spec)
spec.loader.exec_module(thumbnails)

WIDTH = 640  # 80 columns of 8 px
ROWS = 100


def portrait(inked: range) -> Image.Image:
    """A black 80×100 work whose text rows `inked` are white."""
    pixels = np.zeros((ROWS * 16, WIDTH, 3), dtype=np.uint8)
    pixels[inked.start * 16 : inked.stop * 16] = 255
    return Image.fromarray(pixels)


def test_a_card_holds_25_rows_at_80_columns() -> None:
    assert thumbnails.window_rows(WIDTH) == 25


def test_best_window_finds_the_ink() -> None:
    ink = thumbnails.ink_per_row(portrait(range(60, 80)))
    assert thumbnails.best_window(ink, 25) in range(55, 61)


def test_best_window_prefers_the_top_on_ties() -> None:
    assert thumbnails.best_window(np.zeros(ROWS), 25) == 0


def test_every_mode_makes_a_card_of_the_wall_width() -> None:
    for mode in ("screen", "best", "whole"):
        card = thumbnails.thumbnail(portrait(range(60, 80)), mode)
        assert card.width == thumbnails.CARD_WIDTH


def test_an_icon_is_the_best_screen_small_and_bare() -> None:
    icon = thumbnails.thumbnail(portrait(range(60, 80)), "icon")
    assert icon.size == (thumbnails.ICON_WIDTH, 100)
    assert np.asarray(icon).mean() > 255 * 0.7  # the window found the 20 white rows of 25


def test_the_corner_shows_the_whole_work_on_the_right() -> None:
    card = np.asarray(thumbnails.thumbnail(portrait(range(0, 0)), "screen"))
    left, right = card[:, :200].max(), card[:, -40:].max()
    assert left == 0  # the first screen is black
    assert right > 0  # the window's outline is drawn in the corner


def test_a_work_that_fits_has_no_corner() -> None:
    short = Image.new("RGB", (WIDTH, 16 * 10))
    card = np.asarray(thumbnails.thumbnail(short, "best"))
    assert card.max() == 0


def test_a_tall_work_is_folded_into_columns() -> None:
    assert thumbnails.fold(WIDTH, 16 * 25, 320, 200)[1] == 1
    factor, columns = thumbnails.fold(WIDTH, 16 * 5000, 320, 200)
    assert columns > 1
    assert factor * WIDTH * columns <= 320


def test_a_whole_card_of_a_tall_work_fills_more_than_a_line() -> None:
    tall = np.full((5000 * 16, WIDTH, 3), 255, dtype=np.uint8)
    card = np.asarray(thumbnails.thumbnail(Image.fromarray(tall), "whole"))
    assert (card[100].max(axis=1) > 0).sum() > thumbnails.CARD_WIDTH // 2
