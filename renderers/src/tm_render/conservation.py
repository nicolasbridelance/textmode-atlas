# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Conservation rendering: the grid drawn as a PNG, cell by cell, with no interpolation (ADR 0010).

Each rendering comes with its recipe, enough to draw it again and check the result:
`pixels_sha256` (SHA-256 of the RGB pixels) is the reproducibility key, and is directly comparable
with any other renderer's output decoded to RGB, ansilove's included.
"""

from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass
from functools import lru_cache
from importlib.metadata import version
from pathlib import Path
from typing import Any, Literal

from PIL import Image

from tm_render.grid import PC_VGA, Cell, Grid
from tm_render.sauce import Sauce
from tm_render.versions import RENDERER_VERSION

GLYPHS = 256
GLYPH_HEIGHT = 16
GLYPH_WIDTH = 8
LINE_DRAWING = range(0xC0, 0xE0)  # glyphs whose 8th column is repeated into the 9th
BRIGHT = 8
BLANK = Cell(glyph=0x20, fg=7, bg=0, t=0)
MAX_SCALE = 8

VGA_PALETTE = (
    (0x00, 0x00, 0x00), (0x00, 0x00, 0xAA), (0x00, 0xAA, 0x00), (0x00, 0xAA, 0xAA),
    (0xAA, 0x00, 0x00), (0xAA, 0x00, 0xAA), (0xAA, 0x55, 0x00), (0xAA, 0xAA, 0xAA),
    (0x55, 0x55, 0x55), (0x55, 0x55, 0xFF), (0x55, 0xFF, 0x55), (0x55, 0xFF, 0xFF),
    (0xFF, 0x55, 0x55), (0xFF, 0x55, 0xFF), (0xFF, 0xFF, 0x55), (0xFF, 0xFF, 0xFF),
)  # fmt: skip

LetterSpacing = Literal[8, 9]
HighBackground = Literal["blink", "ice"]


@dataclass(frozen=True)
class BitmapFont:
    """A raw `.f16` font: 256 glyphs of 16 rows, one byte per row, leftmost pixel in the top bit."""

    name: str
    data: bytes

    def __post_init__(self) -> None:
        expected = GLYPHS * GLYPH_HEIGHT
        if len(self.data) != expected:
            raise ValueError(f"font {self.name}: {len(self.data)} bytes, expected {expected}")

    @classmethod
    def load(cls, path: Path) -> BitmapFont:
        return cls(path.name, path.read_bytes())

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest()

    def row(self, glyph: int, y: int) -> int:
        return self.data[glyph * GLYPH_HEIGHT + y]


@dataclass(frozen=True)
class Settings:
    """What changes the pixels. Names follow the rendering profiles in `corpus/profiles/`."""

    letter_spacing: LetterSpacing = 8
    high_bg: HighBackground = "blink"
    scale: int = 1

    def __post_init__(self) -> None:
        if not 1 <= self.scale <= MAX_SCALE:
            raise ValueError(f"scale {self.scale}: must be an integer from 1 to {MAX_SCALE}")

    @classmethod
    def from_sauce(cls, sauce: Sauce | None, scale: int = 1) -> Settings:
        """The file's own hints, as ansilove `-S` reads them, except the aspect stretch."""
        if sauce is None:
            return cls(scale=scale)
        return cls(
            letter_spacing=9 if sauce.letter_spacing == "9px" else 8,
            high_bg="ice" if sauce.ice_colors else "blink",
            scale=scale,
        )


@dataclass(frozen=True)
class Rendering:
    png: bytes
    recipe: dict[str, Any]


def render(grid: Grid, font: BitmapFont, settings: Settings) -> Rendering:
    if grid.header != PC_VGA:
        raise ValueError(f"the conservation renderer draws PC VGA grids, not {grid.header}")
    image = _draw(grid, font, settings)
    png = _encode(image)
    recipe = {
        "renderer": "tm_render",
        "renderer_version": RENDERER_VERSION,
        "encoder": f"Pillow {version('pillow')}",
        "grid_sha256": grid.digest(),
        "font": {"file": font.name, "sha256": font.sha256},
        "palette": "vga",
        "letter_spacing": settings.letter_spacing,
        "high_bg": settings.high_bg,
        "blink_phase": "visible",
        "scale": settings.scale,
        "interpolation": "none",
        "width": image.width,
        "height": image.height,
        "pixels_sha256": pixels_sha256(image),
        "output_sha256": hashlib.sha256(png).hexdigest(),
    }
    return Rendering(png, recipe)


def pixels_sha256(image: Image.Image) -> str:
    """SHA-256 of the image as 8-bit RGB rows: independent of the file format and its encoder."""
    return hashlib.sha256(image.convert("RGB").tobytes()).hexdigest()


def _draw(grid: Grid, font: BitmapFont, settings: Settings) -> Image.Image:
    scale = settings.scale
    lines: list[bytes] = []
    for row in range(grid.rows):
        cells = [_colours(grid.cell(row, col) or BLANK, settings) for col in range(grid.cols)]
        for y in range(GLYPH_HEIGHT):
            line = b"".join(_glyph_row(font, settings, colours, y) for colours in cells)
            lines.extend([line] * scale)
    width = grid.cols * settings.letter_spacing * scale
    image = Image.frombytes("P", (width, len(lines)), b"".join(lines))
    image.putpalette([channel for colour in VGA_PALETTE for channel in colour])
    return image


def _colours(cell: Cell, settings: Settings) -> tuple[int, int, int]:
    """In iCE mode the blink bit selects a bright background; otherwise blink is drawn lit."""
    bg = cell.bg + BRIGHT if settings.high_bg == "ice" and cell.blink else cell.bg
    return cell.glyph, cell.fg, bg


@lru_cache(maxsize=65536)
def _glyph_row(
    font: BitmapFont, settings: Settings, colours: tuple[int, int, int], y: int
) -> bytes:
    glyph, fg, bg = colours
    bits = font.row(glyph, y)
    pixels = [fg if bits & (0x80 >> x) else bg for x in range(GLYPH_WIDTH)]
    if settings.letter_spacing > GLYPH_WIDTH:
        pixels.append(pixels[-1] if glyph in LINE_DRAWING else bg)
    return bytes(index for index in pixels for _ in range(settings.scale))


def _encode(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=False, compress_level=9)
    return buffer.getvalue()
