# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The grid: the one intermediate format every decoder produces and every renderer reads.

A cell holds a code point in the artifact's character set, a foreground and a background in VGA
attribute order (0 black, 1 blue, 2 green, 3 cyan, 4 red, 5 magenta, 6 brown, 7 grey, +8 bright),
the blink bit, and `t`: the offset of the byte that last wrote the cell, which lets the site
replay how the work arrived.
"""

from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass

import pyarrow as pa
import pyarrow.parquet as pq

CELL_COLUMNS = ("row", "col", "codepoint", "fg", "bg", "blink", "t")
CELL_FORMAT = struct.Struct("<HHHBBBI")  # row, col, codepoint, fg, bg, blink, t


@dataclass(frozen=True)
class Cell:
    codepoint: int
    fg: int
    bg: int
    blink: bool
    t: int


@dataclass(frozen=True)
class Grid:
    cols: int
    rows: int
    cells: dict[tuple[int, int], Cell]

    def cell(self, row: int, col: int) -> Cell | None:
        """The written cell at (row, col), or None where nothing was written."""
        return self.cells.get((row, col))

    def digest(self) -> str:
        """SHA-256 of a canonical serialization: independent of any file format or library."""
        sha = hashlib.sha256(struct.pack("<HH", self.cols, self.rows))
        for (row, col), cell in sorted(self.cells.items()):
            sha.update(
                CELL_FORMAT.pack(row, col, cell.codepoint, cell.fg, cell.bg, cell.blink, cell.t)
            )
        return sha.hexdigest()


def to_table(grid: Grid) -> pa.Table:
    """One row per written cell, ordered by position, with the canvas size in the metadata."""
    ordered = sorted(grid.cells.items())
    columns = {
        "row": pa.array([pos[0] for pos, _ in ordered], pa.uint16()),
        "col": pa.array([pos[1] for pos, _ in ordered], pa.uint16()),
        "codepoint": pa.array([c.codepoint for _, c in ordered], pa.uint16()),
        "fg": pa.array([c.fg for _, c in ordered], pa.uint8()),
        "bg": pa.array([c.bg for _, c in ordered], pa.uint8()),
        "blink": pa.array([c.blink for _, c in ordered], pa.bool_()),
        "t": pa.array([c.t for _, c in ordered], pa.uint32()),
    }
    metadata = {b"cols": str(grid.cols).encode(), b"rows": str(grid.rows).encode()}
    # pyarrow-stubs leave a few parameters of these functions untyped; ours are all typed.
    table = pa.table(columns)  # pyright: ignore[reportUnknownMemberType]
    return table.replace_schema_metadata(metadata)


def from_table(table: pa.Table) -> Grid:
    metadata = table.schema.metadata or {}
    rows = zip(*(table.column(name).to_pylist() for name in CELL_COLUMNS), strict=True)
    cells = {
        (row, col): Cell(codepoint, fg, bg, blink, t)
        for row, col, codepoint, fg, bg, blink, t in rows
    }
    return Grid(int(metadata[b"cols"]), int(metadata[b"rows"]), cells)


def to_parquet(grid: Grid) -> bytes:
    sink = pa.BufferOutputStream()
    pq.write_table(to_table(grid), sink, compression="zstd")  # pyright: ignore[reportUnknownMemberType]
    return sink.getvalue().to_pybytes()


def from_parquet(data: bytes) -> Grid:
    return from_table(pq.read_table(pa.BufferReader(data)))  # pyright: ignore[reportUnknownMemberType]
