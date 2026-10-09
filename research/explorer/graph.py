# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""What the graph page of the explorer reads (roadmap step 13, leads I49).

The nearest-works graph build (`just graph`): positions, communities and edges, with the
metadata a node shows, and each work's ink colour. Payloads are made once, at the first
request, and kept: the graph does not change while the explorer runs.
"""

from __future__ import annotations

import json
from functools import cached_property
from pathlib import Path
from typing import Any

import duckdb
import numpy as np

# VGA's 16 colours; black is left out of a work's ink, since most works are drawn on it.
VGA = np.array(
    [
        [0, 0, 0], [0, 0, 170], [0, 170, 0], [0, 170, 170], [170, 0, 0], [170, 0, 170],
        [170, 85, 0], [170, 170, 170], [85, 85, 85], [85, 85, 255], [85, 255, 85],
        [85, 255, 255], [255, 85, 85], [255, 85, 255], [255, 255, 85], [255, 255, 255],
    ],
    dtype=np.float64,
)  # fmt: skip
INK_FLOOR = 60  # the darkest ink a node may have, so that it still glows on black


class Graph:
    def __init__(self, build: Path, works: Path) -> None:
        self.build = build
        self.works = works

    @staticmethod
    def exists(build: Path) -> bool:
        return (build / "nodes.parquet").exists()

    def _rows(self) -> list[tuple[Any, ...]]:
        return (
            duckdb.connect()
            .execute(
                "select n.sha256, n.x, n.y, n.community, n.in_degree, w.year, w.content_kind,"
                " w.sauce_group, w.sauce_author, w.pack, w.path, w.archive, w.sauce_title,"
                " f.fg_hist"
                f" from '{self.build / 'nodes.parquet'}' n"
                f" join '{self.works / 'works.parquet'}' w using (sha256)"
                f" join '{self.works / 'features.parquet'}' f using (sha256)"
                " order by n.sha256"
            )
            .fetchall()
        )

    @cached_property
    def nodes(self) -> bytes:
        """Columns of every node as JSON: one list per field, in the order of the edges."""
        rows = self._rows()
        columns = list(zip(*rows, strict=True))
        ink = _ink(np.array(columns[13], dtype=np.float64))
        names = ["sha256", "x", "y", "community", "in_degree", "year", "kind", "group",
                 "author", "pack", "path", "archive", "title"]  # fmt: skip
        payload: dict[str, Any] = {name: list(columns[i]) for i, name in enumerate(names)}
        payload["ink"] = ink.ravel().tolist()
        return json.dumps(payload, separators=(",", ":")).encode()

    @cached_property
    def edges(self) -> bytes:
        """Every edge as two little-endian uint32 node indexes, source then target, by source and
        then rank: the first edge of each work goes to its nearest."""
        db = duckdb.connect()
        db.execute(
            "create table idx as select sha256, row_number() over (order by sha256) - 1 as i"
            f" from '{self.build / 'nodes.parquet'}'"
        )
        pairs = db.execute(
            f"select s.i, t.i from '{self.build / 'edges.parquet'}' e"
            " join idx s on s.sha256 = e.source join idx t on t.sha256 = e.target"
            " order by s.i, e.rank"
        ).fetchnumpy()
        stacked = np.column_stack([pairs["i"], pairs["i_1"]]).astype("<u4")
        return stacked.tobytes()

    @cached_property
    def communities(self) -> bytes:
        return (self.build / "communities.json").read_bytes()


def _ink(fg_hist: np.ndarray) -> np.ndarray:
    """The colour a work is drawn in: its foreground colours mixed by cell count, black left
    out, brightened to a floor so that a dark work still shows."""
    weights = fg_hist[:, 1:]
    totals = np.maximum(weights.sum(axis=1, keepdims=True), 1)
    mixed = weights @ VGA[1:] / totals
    peak = np.maximum(mixed.max(axis=1, keepdims=True), 1)
    scaled = np.where(peak < INK_FLOOR, mixed * INK_FLOOR / peak, mixed)
    return np.clip(np.rint(scaled), 0, 255).astype(np.uint8)
