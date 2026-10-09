# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The grid: the one intermediate format every decoder produces and every renderer reads.

Grid v2 (ADR 0026): one grid for every system. A header names the system, the character set the
glyph numbers index, the palette the colour numbers index, and the font, all entries of the
registries in `corpus/` or SHA-256 of a font or palette the work carries. A cell holds native
values: the glyph's number in that character set, foreground and background as palette indexes,
attribute bits, the control code that occupies the cell when the screen shows something else
there, and `t`, the offset of the byte that last wrote the cell, which lets the site replay how
the work arrived. Characters struck over an earlier one in the same cell (a teleprinter, a
backspace) are kept as further layers, bottom first.

A PC grid that uses nothing beyond grid v1 (`PC_VGA` header, blink as the only attribute, no
control, no layer) keeps grid v1's digest, so that a new decoder version that changes nothing
in the cells keeps every measure and rendering keyed by it valid.
"""

from __future__ import annotations

import hashlib
import json
import struct
from dataclasses import asdict, dataclass, field
from types import MappingProxyType
from typing import Final

import pyarrow as pa
import pyarrow.parquet as pq

GRID_VERSION: Final = 2

# Attribute bits: a fixed registry, extended only by appending (ADR 0026).
BLINK: Final = 1 << 0
UNDERLINE: Final = 1 << 1
INVERSE: Final = 1 << 2
CONCEAL: Final = 1 << 3
DOUBLE_HEIGHT_TOP: Final = 1 << 4
DOUBLE_HEIGHT_BOTTOM: Final = 1 << 5
DOUBLE_WIDTH: Final = 1 << 6
WIDE_LEAD: Final = 1 << 7
WIDE_TRAIL: Final = 1 << 8
BOLD: Final = 1 << 9
ATTRIBUTES: Final = MappingProxyType(
    {
        "blink": BLINK,
        "underline": UNDERLINE,
        "inverse": INVERSE,
        "conceal": CONCEAL,
        "double_height_top": DOUBLE_HEIGHT_TOP,
        "double_height_bottom": DOUBLE_HEIGHT_BOTTOM,
        "double_width": DOUBLE_WIDTH,
        "wide_lead": WIDE_LEAD,
        "wide_trail": WIDE_TRAIL,
        "bold": BOLD,
    }
)

U8: Final = 0xFF
U16: Final = 0xFFFF
NO_CONTROL: Final = 0xFFFF_FFFF  # in the digest, a cell without control

CELL_COLUMNS = ("row", "col", "layer", "glyph", "fg", "bg", "attrs", "control", "t")
V1_CELL = struct.Struct("<HHHBBBI")  # row, col, codepoint, fg, bg, blink, t
V2_CELL = struct.Struct("<IHBIHHHII")  # row, col, layer, glyph, fg, bg, attrs, control, t
V2_TAG = b"tm-grid/2\n"


@dataclass(frozen=True)
class Header:
    """What the numbers of the cells mean: names of `corpus/` registry entries, or the SHA-256 of
    a font or palette the work carries (charset `custom:<font sha256>` when its glyphs have no
    known meaning)."""

    system: str
    charset: str
    palette: str
    font: str
    cell_w: int
    cell_h: int


PC_VGA = Header("pc-vga", "cp437", "vga16", "ibm-vga-8x16", 8, 16)


@dataclass(frozen=True)
class Cell:
    glyph: int
    fg: int
    bg: int
    t: int
    attrs: int = 0
    control: int | None = None

    @property
    def blink(self) -> bool:
        return bool(self.attrs & BLINK)


@dataclass(frozen=True)
class Grid:
    cols: int
    rows: int
    cells: dict[tuple[int, int], Cell]
    header: Header = PC_VGA
    strikes: dict[tuple[int, int], tuple[Cell, ...]] = field(
        default_factory=dict[tuple[int, int], tuple[Cell, ...]]
    )  # layers 1 and up, where a character was struck over another

    def cell(self, row: int, col: int) -> Cell | None:
        """The written cell at (row, col), bottom layer, or None where nothing was written."""
        return self.cells.get((row, col))

    def layers(self) -> list[tuple[int, int, int, Cell]]:
        """Every written cell as (row, col, layer, cell), in position then layer order."""
        found = [(row, col, 0, cell) for (row, col), cell in self.cells.items()]
        for (row, col), struck in self.strikes.items():
            found.extend((row, col, layer, cell) for layer, cell in enumerate(struck, start=1))
        return sorted(found, key=lambda item: item[:3])

    def digest(self) -> str:
        """SHA-256 of a canonical serialization: independent of any file format or library."""
        if self.fits_v1():
            sha = hashlib.sha256(struct.pack("<HH", self.cols, self.rows))
            for (row, col), cell in sorted(self.cells.items()):
                sha.update(V1_CELL.pack(row, col, cell.glyph, cell.fg, cell.bg, cell.blink, cell.t))
            return sha.hexdigest()
        sha = hashlib.sha256(V2_TAG)
        sha.update(json.dumps(asdict(self.header), sort_keys=True).encode())
        sha.update(struct.pack("<II", self.cols, self.rows))
        for row, col, layer, cell in self.layers():
            control = NO_CONTROL if cell.control is None else cell.control
            sha.update(
                V2_CELL.pack(
                    row, col, layer, cell.glyph, cell.fg, cell.bg, cell.attrs, control, cell.t
                )
            )
        return sha.hexdigest()

    def fits_v1(self) -> bool:
        """Whether grid v1 could hold this grid exactly."""
        return (
            self.header == PC_VGA
            and not self.strikes
            and self.cols <= U16
            and self.rows <= U16
            and all(
                c.attrs & ~BLINK == 0 and c.control is None and c.glyph <= U16 and c.fg <= U8
                and c.bg <= U8
                for c in self.cells.values()
            )
        )  # fmt: skip


def to_table(grid: Grid) -> pa.Table:
    """One row per written cell and layer, ordered by position, the header in the metadata."""
    ordered = grid.layers()
    cells = [cell for *_, cell in ordered]
    columns = {
        "row": pa.array([item[0] for item in ordered], pa.uint32()),
        "col": pa.array([item[1] for item in ordered], pa.uint16()),
        "layer": pa.array([item[2] for item in ordered], pa.uint8()),
        "glyph": pa.array([c.glyph for c in cells], pa.uint32()),
        "fg": pa.array([c.fg for c in cells], pa.uint16()),
        "bg": pa.array([c.bg for c in cells], pa.uint16()),
        "attrs": pa.array([c.attrs for c in cells], pa.uint16()),
        "control": pa.array([c.control for c in cells], pa.uint16()),
        "t": pa.array([c.t for c in cells], pa.uint32()),
    }
    metadata = {
        b"grid_version": str(GRID_VERSION).encode(),
        b"cols": str(grid.cols).encode(),
        b"rows": str(grid.rows).encode(),
        **{key.encode(): str(value).encode() for key, value in asdict(grid.header).items()},
    }
    # pyarrow-stubs leave a few parameters of these functions untyped; ours are all typed.
    table = pa.table(columns)  # pyright: ignore[reportUnknownMemberType]
    return table.replace_schema_metadata(metadata)


def from_table(table: pa.Table) -> Grid:
    metadata = {
        key.decode(): value.decode() for key, value in (table.schema.metadata or {}).items()
    }
    if metadata.get("grid_version") != str(GRID_VERSION):
        raise ValueError(f"not a grid v{GRID_VERSION}: {metadata.get('grid_version', 'v1')}")
    header = Header(
        metadata["system"],
        metadata["charset"],
        metadata["palette"],
        metadata["font"],
        int(metadata["cell_w"]),
        int(metadata["cell_h"]),
    )
    cells: dict[tuple[int, int], Cell] = {}
    struck: dict[tuple[int, int], list[Cell]] = {}
    rows = zip(*(table.column(name).to_pylist() for name in CELL_COLUMNS), strict=True)
    for row, col, layer, glyph, fg, bg, attrs, control, t in rows:
        cell = Cell(glyph, fg, bg, t, attrs, control)
        if layer == 0:
            cells[(row, col)] = cell
        else:
            struck.setdefault((row, col), []).append(cell)
    strikes = {pos: tuple(layers) for pos, layers in struck.items()}
    return Grid(int(metadata["cols"]), int(metadata["rows"]), cells, header, strikes)


def to_parquet(grid: Grid) -> bytes:
    sink = pa.BufferOutputStream()
    pq.write_table(to_table(grid), sink, compression="zstd")  # pyright: ignore[reportUnknownMemberType]
    return sink.getvalue().to_pybytes()


def from_parquet(data: bytes) -> Grid:
    return from_table(pq.read_table(pa.BufferReader(data)))  # pyright: ignore[reportUnknownMemberType]
