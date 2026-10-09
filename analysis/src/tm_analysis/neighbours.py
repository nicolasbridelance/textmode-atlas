# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Nearest works by features v1: a style profile per work, and its k nearest neighbours.

The profile is 15 measures of `features.py` and the 16 foreground colour shares, each
standardized over the works compared, so that no unit dominates. Distance is Euclidean. A work
is never its own neighbour; ties go to the lower index, so the result depends only on the input
order. Used by the corpus graph (roadmap steps 12–14).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

PROFILE = (
    "fill_ratio", "glyph_entropy", "class_block", "class_half_block", "class_shade", "class_box",
    "class_alphanumeric", "class_punctuation", "class_other", "high_bg_ratio", "symmetry_h",
    "symmetry_v", "draw_order", "center_row", "center_col",
)  # fmt: skip
COLOURS = 16
CHUNK = 2048  # rows of the distance matrix computed at once
NOISE = 1e-9  # keeps a constant column from dividing by zero


def profile(measures: Sequence[Sequence[float]], fg_hist: Sequence[Sequence[float]]) -> np.ndarray:
    """One standardized row per work: the measures of PROFILE, then colour shares."""
    values = np.asarray(measures, dtype=np.float64)
    colours = np.asarray(fg_hist, dtype=np.float64)
    if values.shape[1] != len(PROFILE) or colours.shape[1] != COLOURS:
        raise ValueError(f"expected {len(PROFILE)} measures and {COLOURS} colours per work")
    colours = colours / np.maximum(colours.sum(axis=1, keepdims=True), 1)
    matrix = np.hstack([values, colours])
    return (matrix - matrix.mean(axis=0)) / (matrix.std(axis=0) + NOISE)


def nearest(matrix: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """For each row, the indexes and distances of its `k` nearest other rows, nearest first."""
    count = len(matrix)
    k = min(k, count - 1)
    squares = (matrix**2).sum(axis=1)
    indexes = np.empty((count, k), dtype=np.int64)
    distances = np.empty((count, k), dtype=np.float64)
    for start in range(0, count, CHUNK):
        rows = slice(start, min(start + CHUNK, count))
        block = squares[rows, None] + squares[None, :] - 2 * matrix[rows] @ matrix.T
        block = np.sqrt(np.maximum(block, 0))
        block[np.arange(block.shape[0]), np.arange(rows.start, rows.stop)] = np.inf  # not itself
        for offset, row in enumerate(block):
            order = _smallest(row, k)
            indexes[start + offset] = order
            distances[start + offset] = row[order]
    return indexes, distances


def _smallest(row: np.ndarray, k: int) -> np.ndarray:
    """Indexes of the `k` smallest values, by value then index, without sorting the row."""
    threshold = np.partition(row, k - 1)[k - 1]
    candidates = np.flatnonzero(row <= threshold)  # every tie at the threshold, in index order
    return candidates[np.lexsort((candidates, row[candidates]))][:k]
