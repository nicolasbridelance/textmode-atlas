# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Feature extractor v1: measurements of a grid, never of its pixels (foundation document,
"Pipeline d'analyse").

Four families: geometry, glyphs, colour, sequence. Every measure is a pure function of the grid,
so the same grid always gives the same numbers (invariant 3). Colours are VGA attributes as the
grid stores them: `fg` 0–15, `bg` 0–7, and the blink bit, which iCE files draw as a bright
background.

A cell *shows ink* when it is not black on black: a visible glyph whose colour differs from its
background, or any non-black background. Spaces painted with a background are ink: ANSI artists
drew with them.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import chain
from typing import TypedDict

import numpy as np
from numpy.typing import NDArray
from tm_render.grid import Grid

# Code points that draw no pixel in CP437: NUL, space, non-breaking space.
BLANK = frozenset({0x00, 0x20, 0xFF})
FULL_BLOCK = 0xDB
HALF_BLOCKS = frozenset({0xDC, 0xDD, 0xDE, 0xDF})
SHADES = frozenset({0xB0, 0xB1, 0xB2})
BOX_DRAWING = frozenset(range(0xB3, 0xDB))  # single and double lines, B3–DA
# ASCII letters and digits, and the accented letters of CP437 (80–9A, A0–A5).
ALPHANUMERIC = frozenset(
    chain(
        range(0x30, 0x3A),
        range(0x41, 0x5B),
        range(0x61, 0x7B),
        range(0x80, 0x9B),
        range(0xA0, 0xA6),
    )
)
PUNCTUATION = frozenset(range(0x21, 0x7F)) - ALPHANUMERIC
GLYPH_CLASSES: dict[str, frozenset[int]] = {
    "block": frozenset({FULL_BLOCK}),
    "half_block": HALF_BLOCKS,
    "shade": SHADES,
    "box": BOX_DRAWING,
    "alphanumeric": ALPHANUMERIC,
    "punctuation": PUNCTUATION,
}
CODEPOINTS = 256
FG_COLOURS = 16
BG_COLOURS = 8
TOP_BIGRAMS = 16


@dataclass(frozen=True)
class Features:
    # Geometry
    cols: int
    rows: int
    cells: int  # written cells
    fill_ratio: float  # cells showing ink / canvas cells
    center_row: float  # centre of mass of the ink, 0 top, 1 bottom
    center_col: float  # 0 left, 1 right
    symmetry_h: float  # ink mask against its left–right mirror, in its bounding box (Jaccard)
    symmetry_v: float  # against its top–bottom mirror
    # Glyphs
    glyph_hist: list[int]  # written cells by code point, 256 entries
    glyph_entropy: float  # Shannon entropy in bits of the visible glyphs
    class_block: float  # share of visible glyphs in each class
    class_half_block: float
    class_shade: float
    class_box: float
    class_alphanumeric: float
    class_punctuation: float
    class_other: float
    bigram_codes: list[int]  # most frequent horizontal pairs of visible glyphs, left * 256 + right
    bigram_counts: list[int]
    # Colour
    n_colors: int  # distinct colours seen: glyph foregrounds and backgrounds of ink cells
    fg_hist: list[int]  # visible glyphs by foreground, 16 entries
    bg_hist: list[int]  # ink cells by background, 8 entries
    high_bg_ratio: float  # ink cells with the blink bit: a bright background under iCE
    fg_bg_pairs: int  # distinct (foreground, background) pairs among visible glyphs
    # Sequence (from `t`, the offset of the byte that last wrote each cell)
    cursor_jumps: float  # share of writes, in byte order, that do not follow the previous one
    draw_order: float  # Spearman correlation of byte order with reading order; 1 = linear


class _Glyphs(TypedDict):
    glyph_hist: list[int]
    glyph_entropy: float
    class_block: float
    class_half_block: float
    class_shade: float
    class_box: float
    class_alphanumeric: float
    class_punctuation: float
    class_other: float
    bigram_codes: list[int]
    bigram_counts: list[int]


class _Colours(TypedDict):
    n_colors: int
    fg_hist: list[int]
    bg_hist: list[int]
    high_bg_ratio: float
    fg_bg_pairs: int


class _Sequence(TypedDict):
    cursor_jumps: float
    draw_order: float


@dataclass(frozen=True)
class _Arrays:
    row: NDArray[np.int64]
    col: NDArray[np.int64]
    codepoint: NDArray[np.int64]
    fg: NDArray[np.int64]
    bg: NDArray[np.int64]
    blink: NDArray[np.bool_]
    t: NDArray[np.int64]

    @classmethod
    def of(cls, grid: Grid) -> _Arrays:
        ordered = sorted(grid.cells.items())

        def column(values: list[int]) -> NDArray[np.int64]:
            return np.array(values, dtype=np.int64)

        return cls(
            row=column([r for (r, _), _ in ordered]),
            col=column([c for (_, c), _ in ordered]),
            codepoint=column([cell.glyph for _, cell in ordered]),
            fg=column([cell.fg for _, cell in ordered]),
            bg=column([cell.bg for _, cell in ordered]),
            blink=np.array([cell.blink for _, cell in ordered], dtype=np.bool_),
            t=column([cell.t for _, cell in ordered]),
        )


def extract(grid: Grid) -> Features:
    a = _Arrays.of(grid)
    visible = ~np.isin(a.codepoint, list(BLANK)) & (a.fg != a.bg)
    ink = visible | (a.bg != 0)
    return Features(
        cols=grid.cols,
        rows=grid.rows,
        cells=len(a.t),
        fill_ratio=_ratio(int(ink.sum()), grid.cols * grid.rows),
        center_row=_center(a.row[ink], grid.rows),
        center_col=_center(a.col[ink], grid.cols),
        symmetry_h=_symmetry(a.row[ink], a.col[ink], axis="h"),
        symmetry_v=_symmetry(a.row[ink], a.col[ink], axis="v"),
        **_glyphs(a, visible),
        **_colours(a, visible, ink),
        **_sequence(a, grid.cols),
    )


def _ratio(part: int, whole: int) -> float:
    return part / whole if whole else 0.0


def _center(positions: NDArray[np.int64], extent: int) -> float:
    if not len(positions) or extent <= 1:
        return 0.5
    return float(positions.mean() / (extent - 1))


def _symmetry(row: NDArray[np.int64], col: NDArray[np.int64], axis: str) -> float:
    """Jaccard index of the ink positions and their mirror within the ink's bounding box."""
    if not len(row):
        return 0.0
    if axis == "h":
        mirrored = zip(row.tolist(), (col.min() + col.max() - col).tolist(), strict=True)
    else:
        mirrored = zip((row.min() + row.max() - row).tolist(), col.tolist(), strict=True)
    cells = set(zip(row.tolist(), col.tolist(), strict=True))
    mirror = set(mirrored)
    return len(cells & mirror) / len(cells | mirror)


def _glyphs(a: _Arrays, visible: NDArray[np.bool_]) -> _Glyphs:
    shown = a.codepoint[visible]
    counts = np.bincount(shown, minlength=CODEPOINTS) if len(shown) else np.zeros(CODEPOINTS)
    p = counts[counts > 0] / max(len(shown), 1)
    share = {
        name: _ratio(int(np.isin(shown, list(members)).sum()), len(shown))
        for name, members in GLYPH_CLASSES.items()
    }
    codes, bigram_counts = _bigrams(a, visible)
    return _Glyphs(
        glyph_hist=np.bincount(a.codepoint, minlength=CODEPOINTS).tolist(),
        glyph_entropy=float(-(p * np.log2(p)).sum()) + 0.0,
        class_block=share["block"],
        class_half_block=share["half_block"],
        class_shade=share["shade"],
        class_box=share["box"],
        class_alphanumeric=share["alphanumeric"],
        class_punctuation=share["punctuation"],
        class_other=max(0.0, 1.0 - sum(share.values())) if len(shown) else 0.0,
        bigram_codes=codes,
        bigram_counts=bigram_counts,
    )


def _bigrams(a: _Arrays, visible: NDArray[np.bool_]) -> tuple[list[int], list[int]]:
    """Pairs of visible glyphs side by side on a row, most frequent first, ties by code."""
    shown = {
        (r, c): cp
        for r, c, cp in zip(
            a.row[visible].tolist(),
            a.col[visible].tolist(),
            a.codepoint[visible].tolist(),
            strict=True,
        )
    }
    pairs = Counter(
        left * CODEPOINTS + right
        for (r, c), left in shown.items()
        if (right := shown.get((r, c + 1))) is not None
    )
    top = sorted(pairs.items(), key=lambda item: (-item[1], item[0]))[:TOP_BIGRAMS]
    return [code for code, _ in top], [count for _, count in top]


def _colours(a: _Arrays, visible: NDArray[np.bool_], ink: NDArray[np.bool_]) -> _Colours:
    fg, bg = a.fg[visible], a.bg[ink]
    seen = set(fg.tolist()) | set(bg.tolist())
    return _Colours(
        n_colors=len(seen),
        fg_hist=np.bincount(fg, minlength=FG_COLOURS).tolist(),
        bg_hist=np.bincount(bg, minlength=BG_COLOURS).tolist(),
        high_bg_ratio=_ratio(int(a.blink[ink].sum()), int(ink.sum())),
        fg_bg_pairs=len(set(zip(fg.tolist(), a.bg[visible].tolist(), strict=True))),
    )


def _sequence(a: _Arrays, cols: int) -> _Sequence:
    """How the cells arrived: in reading order (a typed screen) or in jumps (a drawn one)."""
    if len(a.t) < 2:  # noqa: PLR2004 - a sequence needs two writes
        return _Sequence(cursor_jumps=0.0, draw_order=1.0)
    order = np.argsort(a.t, kind="stable")
    position = (a.row * cols + a.col)[order]
    jumps = int((np.diff(position) != 1).sum())
    return _Sequence(
        cursor_jumps=jumps / (len(position) - 1),
        draw_order=_spearman(np.arange(len(position)), position),
    )


def _spearman(x: NDArray[np.int64], y: NDArray[np.int64]) -> float:
    rx, ry = _ranks(x), _ranks(y)
    sx, sy = rx.std(), ry.std()
    if sx == 0 or sy == 0:
        return 1.0
    rho = ((rx - rx.mean()) * (ry - ry.mean())).mean() / (sx * sy)
    return float(np.clip(rho, -1.0, 1.0))  # rounding can step just past ±1


def _ranks(values: NDArray[np.int64]) -> NDArray[np.float64]:
    ranks = np.empty(len(values), dtype=np.float64)
    ranks[np.argsort(values, kind="stable")] = np.arange(len(values), dtype=np.float64)
    return ranks
