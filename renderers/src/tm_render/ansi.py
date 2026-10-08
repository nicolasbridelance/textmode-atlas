# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""ANSI / CP437 decoder: bytes as MS-DOS ANSI.SYS and BBS terminals interpreted them.

Supported: SGR colours and attributes, cursor positioning and movement, save / restore, screen
and line erasure, CR, LF, TAB, and the DOS end-of-file byte. Other control sequences are skipped
and counted. Text wraps at the canvas width; the canvas grows downward as far as the art goes.

The decoder never raises on content: unreadable input yields a `DecodeError` with a class.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from tm_render.grid import Cell, Grid
from tm_render.sauce import Sauce, split
from tm_render.signatures import binary_format

DEFAULT_WIDTH = 80
MAX_ROWS = 10_000  # far beyond any real artwork; stops runaway cursor movement
ESC, CSI_START = 0x1B, ord("[")
CR, LF, TAB = 0x0D, 0x0A, 0x09
TAB_STOP = 8
DEFAULT_FG, DEFAULT_BG = 7, 0
BRIGHT = 8
# SGR colour index (0 black, 1 red, 2 green, 3 yellow, 4 blue…) → VGA attribute order.
SGR_TO_VGA = (0, 4, 2, 6, 1, 5, 3, 7)
SGR_FG, SGR_BG = range(30, 38), range(40, 48)
# SGR attributes other than colours: code → (state field, value).
SGR_ATTRIBUTES: dict[int, tuple[str, object]] = {
    1: ("bold", True),
    5: ("blink", True),
    7: ("inverse", True),
    22: ("bold", False),
    25: ("blink", False),
    27: ("inverse", False),
    39: ("fg", DEFAULT_FG),
    49: ("bg", DEFAULT_BG),
}
ERASE_ALL = 2
ERASE_TO_START = 1
# A control sequence ends with a byte in this range (ECMA-48 "final byte").
FINAL_BYTES = range(0x40, 0x7F)


class DecodeError(Exception):
    """A classified decoding failure: `kind` is stored in the `decoding` table."""

    def __init__(self, kind: str, detail: str) -> None:
        super().__init__(f"{kind}: {detail}")
        self.kind = kind


@dataclass(frozen=True)
class Stream:
    """How the bytes drew the grid, which the final grid cannot say: an animation redraws."""

    writes: int  # characters put on the canvas
    overwrites: int  # writes on a position already written, even if erased since
    clears: int  # whole-screen erasures (ESC[2J)


@dataclass
class Decoded:
    grid: Grid
    sauce: Sauce | None
    skipped_sequences: int
    sauce_problems: tuple[str, ...] = ()
    stream: Stream = Stream(0, 0, 0)


@dataclass
class _State:
    width: int
    row: int = 0
    col: int = 0
    fg: int = DEFAULT_FG
    bg: int = DEFAULT_BG
    bold: bool = False
    blink: bool = False
    inverse: bool = False
    saved: tuple[int, int] = (0, 0)
    skipped: int = 0
    cells: dict[tuple[int, int], Cell] = field(default_factory=lambda: {})
    max_row: int = 0
    writes: int = 0
    clears: int = 0
    written: set[tuple[int, int]] = field(default_factory=set[tuple[int, int]])

    def put(self, codepoint: int, offset: int) -> None:
        self.writes += 1
        self.written.add((self.row, self.col))
        fg, bg = (self.bg, self.fg) if self.inverse else (self.fg, self.bg)
        self.cells[(self.row, self.col)] = Cell(
            codepoint, fg + (BRIGHT if self.bold else 0), bg, self.blink, offset
        )
        self.max_row = max(self.max_row, self.row)
        self.col += 1
        if self.col >= self.width:  # ANSI.SYS wraps at once: a CR LF after a full row adds one
            self.newline()

    def newline(self) -> None:
        self.row += 1
        self.col = 0
        if self.row >= MAX_ROWS:
            raise DecodeError("too_large", f"more than {MAX_ROWS} rows")

    def move_to(self, row: int, col: int) -> None:
        self.row = max(0, min(row, MAX_ROWS - 1))
        self.col = max(0, min(col, self.width - 1))


def _sgr(state: _State, params: list[int]) -> None:
    for code in params or [0]:
        if code == 0:
            state.fg, state.bg, state.bold, state.blink, state.inverse = (
                DEFAULT_FG,
                DEFAULT_BG,
                False,
                False,
                False,
            )
        elif code in SGR_FG:
            state.fg = SGR_TO_VGA[code - SGR_FG.start]
        elif code in SGR_BG:
            state.bg = SGR_TO_VGA[code - SGR_BG.start]
        else:
            _sgr_attribute(state, code)


def _sgr_attribute(state: _State, code: int) -> None:
    if code in SGR_ATTRIBUTES:
        name, value = SGR_ATTRIBUTES[code]
        setattr(state, name, value)


def _first(params: list[int], default: int = 1) -> int:
    return params[0] if params and params[0] > 0 else default


def _position(state: _State, params: list[int]) -> None:
    row = _first(params)
    col = params[1] if len(params) > 1 and params[1] > 0 else 1
    state.move_to(row - 1, col - 1)


def _erase_display(state: _State, params: list[int]) -> None:
    if params and params[0] == ERASE_ALL:
        state.clears += 1
        state.cells.clear()
        state.move_to(0, 0)


def _erase_line(state: _State, params: list[int]) -> None:
    mode = params[0] if params else 0
    spans = {ERASE_TO_START: (0, state.col), ERASE_ALL: (0, state.width - 1)}
    first, last = spans.get(mode, (state.col, state.width - 1))
    for col in range(first, last + 1):
        state.cells.pop((state.row, col), None)


def _save(state: _State, params: list[int]) -> None:
    state.saved = (state.row, state.col)


def _restore(state: _State, params: list[int]) -> None:
    state.move_to(*state.saved)


_CSI: dict[str, Callable[[_State, list[int]], None]] = {
    "m": _sgr,
    "H": _position,
    "f": _position,
    "A": lambda s, p: s.move_to(s.row - _first(p), s.col),
    "B": lambda s, p: s.move_to(s.row + _first(p), s.col),
    "C": lambda s, p: s.move_to(s.row, s.col + _first(p)),
    "D": lambda s, p: s.move_to(s.row, s.col - _first(p)),
    "J": _erase_display,
    "K": _erase_line,
    "s": _save,
    "u": _restore,
}


def _parse_params(raw: bytes) -> list[int]:
    return [
        int(part) if part.isdigit() else 0
        for part in raw.decode("ascii", "replace").split(";")
        if part != ""
    ]


def _csi(state: _State, content: bytes, start: int) -> int:
    """Run the control sequence starting after `ESC [`; return the offset after it."""
    end = start
    while end < len(content) and content[end] not in FINAL_BYTES:
        end += 1
    if end >= len(content):
        return end  # truncated sequence at end of file: nothing to draw
    handler = _CSI.get(chr(content[end]))
    if handler is None or content[start:end].startswith(b"?"):
        state.skipped += 1
    else:
        handler(state, _parse_params(content[start:end]))
    return end + 1


def _control(state: _State, byte: int) -> bool:
    """Apply CR, LF or TAB; return False for any other byte."""
    if byte == CR:
        state.col = 0
    elif byte == LF:
        state.newline()
    elif byte == TAB:
        state.col = min(state.width - 1, (state.col // TAB_STOP + 1) * TAB_STOP)
    else:
        return False
    return True


def decode(data: bytes) -> Decoded:
    if binary := binary_format(data):
        raise DecodeError("binary_content", f"a {binary} file, not text")
    content, sauce = split(data)
    if not content:
        raise DecodeError("empty", "no content before the end of file")
    # A record with corrupt binary fields gives no width: its numbers are text or shifted bytes
    # (20,480 or 26,912 columns), and drawing at that width would put the art on one row.
    problems = sauce.problems(len(data)) if sauce else ()
    width = sauce.width if sauce and sauce.width and not problems else DEFAULT_WIDTH
    state = _State(width=width)
    offset = 0
    while offset < len(content):
        byte = content[offset]
        if byte == ESC and offset + 1 < len(content) and content[offset + 1] == CSI_START:
            offset = _csi(state, content, offset + 2)
            continue
        if not _control(state, byte):
            state.put(byte, offset)
        offset += 1
    # The canvas ends at the last written row, as ansilove draws it: SAUCE heights often count a
    # trailing CR LF as a row (spike 0001). The record itself stays in `Decoded.sauce`.
    grid = Grid(width, state.max_row + 1, dict(state.cells))
    stream = Stream(state.writes, state.writes - len(state.written), state.clears)
    return Decoded(grid, sauce, state.skipped, problems, stream)
