# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The compact grid file the site reads (`grid.tmg`, ADR 0022): the whole canvas, row by row.

A 16-byte header, then 8 bytes per cell, little-endian, every cell of the canvas in row-major
order, written or not:

    header  magic "TMG1" | version u8 = 1 | flags u8 | cols u16 | rows u16 | reserved 6 bytes
    cell    codepoint u16 | fg u8 | bg u8 | t u32, where t = 0xFFFFFFFF for a cell never written

Header flags: bit 0, the high background is iCE (bright) rather than blink. A cell's blink bit
rides in the top bit of its `bg` byte. `t` lets the site replay the arrival of the work at modem
speed without ever reading ANSI: draw the cells in increasing `t`.
"""

from __future__ import annotations

import struct

from tm_render.grid import Cell, Grid

MAGIC = b"TMG1"
VERSION = 1
HEADER = struct.Struct("<4sBBHH6x")
CELL = struct.Struct("<HBBI")
NEVER = 0xFFFFFFFF
ICE = 0x01
BLINK = 0x80


def encode(grid: Grid, ice: bool) -> bytes:
    out = bytearray(HEADER.pack(MAGIC, VERSION, ICE if ice else 0, grid.cols, grid.rows))
    for row in range(grid.rows):
        for col in range(grid.cols):
            cell = grid.cell(row, col)
            if cell is None:
                out += CELL.pack(0, 0, 0, NEVER)
            else:
                bg = cell.bg | (BLINK if cell.blink else 0)
                out += CELL.pack(cell.codepoint, cell.fg, bg, cell.t)
    return bytes(out)


def decode(data: bytes) -> tuple[Grid, bool]:
    """The grid and its iCE flag; the inverse of `encode`, used by tests and tools."""
    magic, version, flags, cols, rows = HEADER.unpack_from(data)
    if magic != MAGIC or version != VERSION:
        raise ValueError(f"not a TMG{VERSION} file")
    cells: dict[tuple[int, int], Cell] = {}
    for index in range(cols * rows):
        codepoint, fg, bg, t = CELL.unpack_from(data, HEADER.size + index * CELL.size)
        if t != NEVER:
            cells[divmod(index, cols)] = Cell(codepoint, fg, bg & ~BLINK, bool(bg & BLINK), t)
    return Grid(cols, rows, cells), bool(flags & ICE)
