# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: CC0-1.0
"""Compose `horizon.ans`, the project's first golden artifact.

A work made for the museum by Claude, dedicated to the public domain (CC0). It is not scene art
and is never presented as such; it exists so that decoders and renderers have a reference whose
rights are clear. Run: `uv run python tests/golden/ansi/horizon.py`.

Two layers, as ANSI artists work: a pixel layer drawn with half blocks (two pixels per cell,
upper and lower), and a glyph layer for textures (shades, stars, waves). In VGA blink mode a
cell can show one bright colour at most: the foreground.
"""

from __future__ import annotations

import random
import struct
from dataclasses import dataclass, field
from pathlib import Path

WIDTH, HEIGHT = 80, 40
ESC = "\x1b["
FULL, UPPER, LOWER = 0xDB, 0xDF, 0xDC
LIGHT, MEDIUM, DARK = 0xB0, 0xB1, 0xB2
BLACK, BLUE, GREEN, CYAN, RED, MAGENTA, BROWN, GREY = range(8)
DGREY, LBLUE, LGREEN, LCYAN, LRED, LMAGENTA, YELLOW, WHITE = range(8, 16)
# Colours above are numbered as the VGA attribute byte does; SGR codes use another order.
SGR_ORDER = [0, 4, 2, 6, 1, 5, 3, 7]

# 5×5 pixel letters for the logo.
LETTERS = {
    "T": ["#####", "..#..", "..#..", "..#..", "..#.."],
    "E": ["#####", "#....", "####.", "#....", "#####"],
    "X": ["#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "####."],
}


@dataclass
class Cell:
    char: int = 0x20
    fg: int = GREY
    bg: int = BLACK


@dataclass
class Canvas:
    cells: list[list[Cell]] = field(
        default_factory=lambda: [[Cell() for _ in range(WIDTH)] for _ in range(HEIGHT)]
    )
    # Pixel layer: None where transparent (the glyph layer shows through).
    pixels: list[list[int | None]] = field(
        default_factory=lambda: [[None] * WIDTH for _ in range(HEIGHT * 2)]
    )

    def glyph(self, row: int, col: int, char: int, fg: int, bg: int = BLACK) -> None:
        if 0 <= row < HEIGHT and 0 <= col < WIDTH:
            self.cells[row][col] = Cell(char, fg, bg)

    def text(self, row: int, col: int, text: str, fg: int) -> None:
        for offset, char in enumerate(text.encode("cp437")):
            self.glyph(row, col + offset, char, fg)

    def pixel(self, y: int, x: int, colour: int) -> None:
        if 0 <= y < HEIGHT * 2 and 0 <= x < WIDTH:
            self.pixels[y][x] = colour

    def flatten(self) -> list[list[Cell]]:
        return [[self._merge(row, col) for col in range(WIDTH)] for row in range(HEIGHT)]

    def _merge(self, row: int, col: int) -> Cell:
        upper, lower = self.pixels[row * 2][col], self.pixels[row * 2 + 1][col]
        under = self.cells[row][col]
        if upper is None and lower is None:
            return under
        return half_block(upper, lower, under.bg)


def half_block(upper: int | None, lower: int | None, background: int) -> Cell:
    """One cell showing two stacked pixels; a missing pixel shows the background colour."""
    top = background if upper is None else upper
    bottom = background if lower is None else lower
    if top == bottom:
        return Cell(FULL, top) if top >= 8 else Cell(0x20, GREY, top)
    if bottom < 8:
        return Cell(UPPER, top, bottom)
    if top < 8:
        return Cell(LOWER, bottom, top)
    return Cell(UPPER, top, bottom - 8)  # two bright pixels: darken the lower one


SKY_RAMP = [BLACK, BLUE, MAGENTA, RED, BROWN]
SHADES = [0x20, LIGHT, MEDIUM, DARK]
FIRST_GLOW_ROW = 9


def sky(canvas: Canvas, last_row: int) -> None:
    """Night above; toward the horizon, one shade step per row, as ANSI gradients are drawn."""
    for row in range(last_row + 1):
        step = max(0, row - FIRST_GLOW_ROW)
        index, shade = min(step // 4, len(SKY_RAMP) - 2), step % 4
        char, fg, bg = SHADES[shade], SKY_RAMP[index + 1], SKY_RAMP[index]
        if step >= (len(SKY_RAMP) - 1) * 4:
            char, fg, bg = 0x20, GREY, SKY_RAMP[-1]
        for col in range(WIDTH):
            canvas.glyph(row, col, char, fg, bg)


def stars(canvas: Canvas, rng: random.Random) -> None:
    for _ in range(70):
        row, col = rng.randrange(0, FIRST_GLOW_ROW), rng.randrange(WIDTH)
        char, fg = rng.choice([(0xFA, GREY), (0xFA, WHITE), (0xF9, LCYAN), (0x2A, WHITE)])
        canvas.glyph(row, col, char, fg)


def logo(canvas: Canvas, word: str, top: int) -> None:
    gradient = [WHITE, WHITE, LCYAN, LCYAN, CYAN]
    width = len(word) * 6 - 1
    left = (WIDTH - width) // 2
    for index, letter in enumerate(word):
        for y, line in enumerate(LETTERS[letter]):
            for x, mark in enumerate(line):
                if mark == "#":
                    canvas.pixel(top + y, left + index * 6 + x, gradient[y])


MOON_SEAS = [
    (-3, -1),
    (-3, 0),
    (-2, -2),
    (-2, -1),
    (-2, 0),
    (-1, -1),
    (0, 2),
    (1, 1),
    (1, 2),
    (1, 3),
    (2, 2),
    (2, -3),
    (3, -2),
]


def moon(canvas: Canvas, centre_y: int, centre_x: int, radius: int) -> None:
    """A full moon with irregular darker seas. Half-block pixels are nearly square."""
    for y in range(centre_y - radius, centre_y + radius + 1):
        for x in range(centre_x - radius, centre_x + radius + 1):
            dy, dx = y - centre_y, x - centre_x
            if dx * dx + dy * dy <= radius * radius + 1:
                canvas.pixel(y, x, GREY if (dy, dx) in MOON_SEAS else WHITE)


def ridge(rng: random.Random, base: int, roughness: float) -> list[int]:
    """Midpoint displacement: a mountain line, one height per column (in pixels)."""
    heights = [float(base)] * (WIDTH + 1)
    step, scale = WIDTH, roughness
    while step > 1:
        half = step // 2
        for left in range(0, WIDTH, step):
            right = min(left + step, WIDTH)
            heights[left + half] = (heights[left] + heights[right]) / 2 + rng.uniform(-scale, scale)
        step, scale = half, scale * 0.55
    return [round(h) for h in heights[:WIDTH]]


def mountains(canvas: Canvas, rng: random.Random, horizon: int) -> None:
    for base, roughness, colour in [(horizon - 9, 8.0, BLUE), (horizon - 4, 5.0, BLACK)]:
        for x, top in enumerate(ridge(rng, base, roughness)):
            for y in range(top, horizon):
                canvas.pixel(y, x, colour)


def sea(canvas: Canvas, rng: random.Random, first_row: int, moon_col: int) -> None:
    """Waves that carry the glow near the horizon, and the moon's path on the water."""
    last_row = HEIGHT - 4
    for row in range(first_row, last_row + 1):
        distance = row - first_row
        tint = [RED, MAGENTA, MAGENTA, BLUE][min(distance, 3)]
        for col in range(WIDTH):
            if rng.random() < 0.22 - distance * 0.012:
                canvas.glyph(row, col, rng.choice([0xF7, 0x7E]), tint)
        spread = 1 + distance
        for col in range(moon_col - spread, moon_col + spread + 1):
            if rng.random() < 0.75 - distance * 0.07:
                canvas.glyph(
                    row, col, rng.choice([0xC4, 0xCD, 0xFA]), WHITE if distance < 3 else GREY
                )


def horizon_line(canvas: Canvas, y: int, centre_x: int) -> None:
    """Brightest under the glow, fading to the edges."""
    for x in range(WIDTH):
        distance = abs(x - centre_x)
        canvas.pixel(y, x, YELLOW if distance < 8 else LRED if distance < 26 else RED)


def signature(canvas: Canvas) -> None:
    canvas.text(HEIGHT - 2, 2, "horizon", DGREY)
    canvas.text(HEIGHT - 2, 46, "made by claude for textmode-atlas", DGREY)
    canvas.text(HEIGHT - 1, 2, "tm!", LBLUE)
    canvas.text(HEIGHT - 1, 63, "cc0 \u00b7 2026", DGREY)


def compose() -> list[list[Cell]]:
    rng = random.Random(1994)  # fixed seed: the artifact is reproducible
    canvas = Canvas()
    horizon = 50
    sky(canvas, last_row=horizon // 2)
    stars(canvas, rng)
    logo(canvas, "TEXTMODE", top=3)
    canvas.text(7, 31, "\u00b7  a t l a s  \u00b7", LCYAN)
    moon(canvas, centre_y=20, centre_x=63, radius=5)
    mountains(canvas, rng, horizon)
    horizon_line(canvas, horizon, centre_x=30)
    sea(canvas, rng, first_row=horizon // 2 + 1, moon_col=63)
    signature(canvas)
    return canvas.flatten()


def sgr(cell: Cell) -> str:
    bold = ";1" if cell.fg >= 8 else ""
    return f"{ESC}0{bold};{30 + SGR_ORDER[cell.fg % 8]};{40 + SGR_ORDER[cell.bg]}m"


def encode(rows: list[list[Cell]]) -> bytes:
    """ANSI as editors save it: row by row, colour changes only, CR LF unless the row is full."""
    out = bytearray(f"{ESC}0m".encode())
    current: Cell | None = None
    for row in rows:
        end = len(row)
        while end and row[end - 1].char == 0x20 and row[end - 1].bg == BLACK:
            end -= 1
        for cell in row[:end]:
            if current is None or (cell.fg, cell.bg) != (current.fg, current.bg):
                out += sgr(cell).encode()
                current = cell
            out.append(cell.char)
        if end < WIDTH:
            out += f"{ESC}0m\r\n".encode()
            current = None
    out += f"{ESC}0m".encode()
    return bytes(out)


def sauce(file_size: int, rows: int) -> bytes:
    """SAUCE 00 record: title, author, group, date, ANSi type, 80 columns, blink mode, 9px VGA."""

    def field_text(value: str, size: int) -> bytes:
        return value.encode("cp437").ljust(size, b" ")

    flags = 0b0000_0100  # letter spacing 9px, legacy aspect not set, blink mode
    return (
        b"SAUCE00"
        + field_text("Horizon", 35)
        + field_text("claude", 20)
        + field_text("textmode-atlas", 20)
        + b"20261007"
        + struct.pack("<IBBHHHHBB", file_size, 1, 1, WIDTH, rows, 0, 0, 0, flags)
        + b"IBM VGA".ljust(22, b"\0")
    )


def main() -> None:
    rows = compose()
    body = encode(rows)
    record = sauce(len(body), len(rows))
    assert len(record) == 128
    Path(__file__).with_name("horizon.ans").write_bytes(body + b"\x1a" + record)


if __name__ == "__main__":
    main()
