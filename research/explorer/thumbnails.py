# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Thumbnails of the explorer's wall (leads I47).

Most works are long portraits: an 80-column ANSI of 200 rows shows its logo, or an empty first
screen, and nothing of the rest. Three ways to make a card from a rendering:

- `screen`: the first screen, as before;
- `best`: the screen with the most ink, the window of rows that differ most from black;
- `whole`: the whole work scaled into the card, a tall work folded into columns;
- `icon`: the best screen at half a card's width, with no corner: a node of the graph.

`screen` and `best` add the whole work in the card's right corner, seen from afar and folded
the same way, with the window outlined on it, when the work is taller than the window.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

CARD_RATIO = 320 / 200  # width / height of a card, as the wall draws it
CARD_WIDTH = 320
BAND = 16  # rows of pixels per text row (VGA 8×16)
INSET_SHARE = 0.22  # widest the corner view may be, as a share of the card width
INSET_MARGIN = 3
MAX_COLUMNS = 40
FRAME = (85, 255, 255)  # bright cyan, the explorer's accent in VGA
BACKDROP = (0, 0, 0)
MODES = ("screen", "best", "whole", "icon")
ICON_WIDTH = 160  # the best screen, small and bare, for the graph's nodes


def window_rows(width: int) -> int:
    """Rows of text that fill a card at the work's width (25 at 80 columns of 8 px)."""
    return max(1, round(width / CARD_RATIO / BAND))


def ink_per_row(image: Image.Image) -> np.ndarray:
    """Share of non-black pixels in each text row."""
    pixels = np.asarray(image.convert("L"))
    rows = pixels.shape[0] // BAND
    bands = pixels[: rows * BAND].reshape(rows, BAND, -1)
    return (bands > 0).mean(axis=(1, 2))


def best_window(ink: np.ndarray, size: int) -> int:
    """First text row of the `size` consecutive rows with the most ink; the earliest on ties."""
    if len(ink) <= size:
        return 0
    sums = np.convolve(ink, np.ones(size), mode="valid")
    return int(np.argmax(sums))


def thumbnail(image: Image.Image, mode: str) -> Image.Image:
    """A card for the wall from the work's rendering."""
    image = image.convert("RGB")
    if mode == "whole":
        return _contain(image)
    size = window_rows(image.width)
    top = best_window(ink_per_row(image), size) if mode in ("best", "icon") else 0
    box = (0, top * BAND, image.width, min(image.height, (top + size) * BAND))
    if mode == "icon":
        return _scale(image.crop(box), ICON_WIDTH / image.width)
    card = _scale(image.crop(box), CARD_WIDTH / image.width)
    if image.height > box[3] - box[1]:
        _corner(card, image, box)
    return card


def _scale(image: Image.Image, factor: float) -> Image.Image:
    size = (max(1, round(image.width * factor)), max(1, round(image.height * factor)))
    return image.resize(size, Image.Resampling.BOX)


def fold(width: int, height: int, box_width: float, box_height: float) -> tuple[float, int]:
    """Scale and number of columns that show a `width` × `height` work largest in the box, the
    work cut into columns read as a newspaper (one column for a work that is not tall)."""
    best = (0.0, 1)
    for columns in range(1, MAX_COLUMNS + 1):
        factor = min(box_width / (columns * width), columns * box_height / height, 1.0)
        if factor > best[0]:
            best = (factor, columns)
    return best


def _folded(image: Image.Image, factor: float, columns: int, height: int) -> Image.Image:
    small = _scale(image, factor)
    folded = Image.new("RGB", (columns * small.width, min(small.height, height)), BACKDROP)
    for column in range(columns):
        part = small.crop((0, column * height, small.width, (column + 1) * height))
        folded.paste(part, (column * small.width, 0))
    return folded


def _contain(image: Image.Image) -> Image.Image:
    height = round(CARD_WIDTH / CARD_RATIO)
    factor, columns = fold(image.width, image.height, CARD_WIDTH, height)
    small = _folded(image, factor, columns, height)
    card = Image.new("RGB", (CARD_WIDTH, height), BACKDROP)
    card.paste(small, ((CARD_WIDTH - small.width) // 2, (height - small.height) // 2))
    return card


def _corner(card: Image.Image, image: Image.Image, box: tuple[int, int, int, int]) -> None:
    """Paste the whole work, small and folded, in the card's right corner, with the window
    outlined on it."""
    room = card.height - 2 * INSET_MARGIN
    factor, columns = fold(image.width, image.height, card.width * INSET_SHARE, room)
    small = _folded(image, factor, columns, room)
    left = card.width - small.width - INSET_MARGIN
    card.paste(BACKDROP, (left - 1, INSET_MARGIN - 1, card.width, small.height + INSET_MARGIN + 1))
    card.paste(small, (left, INSET_MARGIN))
    column_width = small.width // columns
    top, bottom = (round(y * factor) for y in (box[1], box[3]))
    draw = ImageDraw.Draw(card)
    for column in range(top // room, min(columns, bottom // room + 1)):
        x = left + column * column_width
        y0 = max(top - column * room, 0) + INSET_MARGIN
        y1 = min(bottom - column * room, small.height) + INSET_MARGIN
        draw.rectangle((x - 1, y0 - 1, x + column_width, max(y1, y0 + 1)), outline=FRAME)
