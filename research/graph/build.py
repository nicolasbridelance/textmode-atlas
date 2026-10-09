# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The nearest-works graph of the train packs (roadmap step 12, leads I48): build it once.

Reads the `works` dataset (train packs only), takes each measured work's 10 nearest works by
`tm_analysis.neighbours`, finds communities with Leiden (modularity, fixed seed) on the graph
without directions, lays the works out in two dimensions with UMAP on those same neighbours
(fixed seed), and writes `datasets/build/graph/<version>/`:

- `edges.parquet`: source, target, rank (1 = nearest), distance;
- `nodes.parquet`: sha256, in-degree (how often the work is someone's neighbour), community,
  and the position `x`, `y` for the graph explorer;
- `manifest.json`: the works dataset and the versions it was built from, and the SHA-256 of
  each file.

Exploratory: the study is [neighbours.md](../exploration/neighbours.md).

    uv run --group research python research/graph/build.py   # or: just graph
"""

from __future__ import annotations

import hashlib
import json
import logging
import random
from pathlib import Path

import duckdb
import igraph as ig
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import umap
from tm_analysis.neighbours import PROFILE, nearest, profile
from tm_analysis.versions import NEIGHBOURS_VERSION

ROOT = Path(__file__).resolve().parents[2]
WORKS = ROOT / "datasets" / "build" / "works" / "6"
VERSION = "2"  # of this graph build: k, the community and layout methods and their seeds
OUT = ROOT / "datasets" / "build" / "graph" / VERSION
K = 10
SEED = 20261009
MIN_DIST = 0.05  # how tightly UMAP packs close works: islands with some air inside

log = logging.getLogger(__name__)


def measured(db: duckdb.DuckDBPyConnection) -> tuple[list[str], np.ndarray]:
    columns = ", ".join(f"f.{name}" for name in PROFILE)
    rows = db.execute(
        f"select sha256, {columns}, f.fg_hist from '{WORKS / 'works.parquet'}' w"
        f" join '{WORKS / 'features.parquet'}' f using (sha256)"
        " where f.fill_ratio is not null order by sha256"
    ).fetchall()
    shas = [row[0] for row in rows]
    return shas, profile([row[1:-1] for row in rows], [row[-1] for row in rows])


def communities(count: int, sources: np.ndarray, targets: np.ndarray) -> list[int]:
    random.seed(SEED)  # igraph's Leiden draws from Python's generator
    graph = ig.Graph(n=count, edges=list(zip(sources, targets, strict=True)))
    graph.simplify()  # a pair of mutual neighbours is one tie
    found = graph.community_leiden(objective_function="modularity", n_iterations=-1)
    # Number communities by size, largest first, so that names do not depend on the run.
    order = {old: new for new, old in enumerate(np.argsort(-np.bincount(found.membership)))}
    return [order[c] for c in found.membership]


def layout(indexes: np.ndarray, distances: np.ndarray) -> np.ndarray:
    """Positions from the neighbours already found: UMAP wants each work first in its own row."""
    count = len(indexes)
    own = np.arange(count)[:, None]
    knn = (np.hstack([own, indexes]), np.hstack([np.zeros((count, 1)), distances]))
    reducer = umap.UMAP(
        n_neighbors=K + 1, min_dist=MIN_DIST, precomputed_knn=(*knn, None), random_state=SEED
    )
    return np.asarray(reducer.fit_transform(np.zeros((count, 1))), dtype=np.float32)


def write(name: str, table: pa.Table) -> dict[str, object]:
    path = OUT / name
    pq.write_table(table, path)
    return {"file": name, "rows": table.num_rows, "sha256": _sha256(path)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    shas, matrix = measured(duckdb.connect())
    indexes, distances = nearest(matrix, K)
    count = len(shas)
    sources = np.repeat(np.arange(count), K)
    targets = indexes.ravel()
    membership = communities(count, sources, targets)
    positions = layout(indexes, distances)
    OUT.mkdir(parents=True, exist_ok=True)
    edges = pa.table(
        {
            "source": pa.array([shas[i] for i in sources]),
            "target": pa.array([shas[i] for i in targets]),
            "rank": pa.array(np.tile(np.arange(1, K + 1), count), pa.int8()),
            "distance": pa.array(distances.ravel(), pa.float32()),
        }
    )
    nodes = pa.table(
        {
            "sha256": shas,
            "in_degree": pa.array(np.bincount(targets, minlength=count), pa.int32()),
            "community": pa.array(membership, pa.int32()),
            "x": pa.array(positions[:, 0]),
            "y": pa.array(positions[:, 1]),
        }
    )
    works = json.loads((WORKS / "manifest.json").read_text())
    manifest = {
        "name": "graph",
        "version": VERSION,
        "works": {"version": works["version"], "manifest_sha256": _sha256(WORKS / "manifest.json")},
        "neighbours": NEIGHBOURS_VERSION,
        "k": K,
        "communities": {"method": "leiden-modularity", "seed": SEED},
        "layout": {"method": "umap", "min_dist": MIN_DIST, "seed": SEED},
        "tables": {"edges": write("edges.parquet", edges), "nodes": write("nodes.parquet", nodes)},
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    log.info("%d works, %d edges, %d communities", count, edges.num_rows, max(membership) + 1)


if __name__ == "__main__":
    main()
