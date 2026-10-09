# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
import io
from pathlib import Path

import pytest
from conftest import SauceRecord
from PIL import Image
from tm_render.ansi import decode
from tm_render.conservation import VGA_PALETTE, BitmapFont, Settings, render
from tm_render.grid import BLINK, Cell, Grid

FULL_BLOCK, LOWER_HALF_BLOCK, LETTER_A = 0xDB, 0xDC, 0x41
FONT = BitmapFont.load(Path(__file__).resolve().parents[2] / "corpus/fonts/ibm-vga-8x16.f16")
BLUE, RED, BRIGHT_RED, WHITE = 1, 4, 12, 15


def pixels(grid: Grid, settings: Settings) -> Image.Image:
    return Image.open(io.BytesIO(render(grid, FONT, settings).png)).convert("RGB")


def one_cell(codepoint: int, fg: int = WHITE, bg: int = 0, blink: bool = False) -> Grid:
    return Grid(1, 1, {(0, 0): Cell(codepoint, fg, bg, 0, BLINK if blink else 0)})


def test_cell_size_and_integer_scale() -> None:
    assert pixels(one_cell(LETTER_A), Settings()).size == (8, 16)
    assert pixels(one_cell(LETTER_A), Settings(letter_spacing=9, scale=3)).size == (27, 48)


def test_scale_repeats_pixels_without_interpolation() -> None:
    small = pixels(one_cell(LETTER_A), Settings())
    large = pixels(one_cell(LETTER_A), Settings(scale=2))
    for y in range(16):
        for x in range(8):
            assert large.getpixel((2 * x + 1, 2 * y + 1)) == small.getpixel((x, y))


def test_ninth_column_repeats_line_drawing_glyphs_only() -> None:
    nine = Settings(letter_spacing=9)
    assert pixels(one_cell(FULL_BLOCK), nine).getpixel((8, 0)) == VGA_PALETTE[WHITE]
    assert pixels(one_cell(LETTER_A, bg=BLUE), nine).getpixel((8, 8)) == VGA_PALETTE[BLUE]


def test_blink_bit_is_a_bright_background_in_ice_mode() -> None:
    cell = one_cell(LOWER_HALF_BLOCK, bg=RED, blink=True)
    assert pixels(cell, Settings(high_bg="ice")).getpixel((0, 0)) == VGA_PALETTE[BRIGHT_RED]
    assert pixels(cell, Settings(high_bg="blink")).getpixel((0, 0)) == VGA_PALETTE[RED]


def test_blinking_text_is_drawn_in_its_lit_phase() -> None:
    lit = pixels(one_cell(FULL_BLOCK, blink=True), Settings(high_bg="blink"))
    assert lit.getpixel((4, 8)) == VGA_PALETTE[WHITE]


def test_unwritten_cells_are_black() -> None:
    grid = Grid(2, 1, {(0, 0): Cell(FULL_BLOCK, WHITE, 0, 0)})
    image = pixels(grid, Settings())
    assert image.crop((8, 0, 16, 16)).getcolors() == [(8 * 16, VGA_PALETTE[0])]


def test_settings_from_sauce(sauce_record: SauceRecord) -> None:
    assert Settings.from_sauce(None) == Settings(letter_spacing=8, high_bg="blink")
    sauce = decode(b"x\x1a" + sauce_record(flags=0b0000_0101)).sauce
    assert Settings.from_sauce(sauce, scale=2) == Settings(9, "ice", 2)


def test_invalid_scale_and_font_fail_fast() -> None:
    with pytest.raises(ValueError, match="scale 0"):
        Settings(scale=0)
    with pytest.raises(ValueError, match="expected 4096"):
        BitmapFont("short.f16", b"\0" * 10)


def test_recipe_describes_the_rendering() -> None:
    grid = one_cell(LETTER_A)
    recipe = render(grid, FONT, Settings(letter_spacing=9, scale=2)).recipe
    assert recipe["renderer"] == "tm_render"
    assert recipe["grid_sha256"] == grid.digest()
    assert recipe["font"] == {"file": "ibm-vga-8x16.f16", "sha256": FONT.sha256}
    assert (recipe["width"], recipe["height"], recipe["scale"]) == (18, 32, 2)
    assert recipe["interpolation"] == "none"
