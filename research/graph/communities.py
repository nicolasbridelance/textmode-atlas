# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""What each community of the nearest-works graph looks like: archetype and variability.

For every community of the graph build (`just graph`), in the same profile space as the
neighbours (`tm_analysis.neighbours`):

- **profile**: how far the community's mean stands from the corpus mean on each measure, in
  standard deviations; the largest gaps make a descriptive **name** ("half blocks · magenta ·
  dense"). The name is computed, so it is signed `algo:` (invariant 8) until a person names it;
- **archetype**: the work nearest the community's centre, then the four next nearest (typical);
- **spread**: mean distance of the works to the centre, against the same for the corpus;
- **axis of variation**: the first principal component inside the community, what it opposes
  ("letters ↔ blocks"), the share of variance it carries, and works at both ends (2nd and 98th
  percentiles, so that outliers do not speak for the community).

Writes `communities.json` next to the graph. Exploratory, train packs only.

    uv run --group research python research/graph/communities.py   # or: just graph
"""

from __future__ import annotations

import collections
import json
import logging
from typing import Any

import duckdb
import numpy as np
from build import OUT as GRAPH  # next to this file: the graph build this names
from build import ROOT
from tm_analysis.neighbours import COLOURS, PROFILE, profile

NAMER = "algo:graph-communities@1"
TYPICAL = 5
ENDS = 2
LOW, HIGH = 2, 98  # percentiles of the axis where its ends are taken
NAME_PARTS = 3
STRONG = 0.5  # standard deviations: below this, a measure does not describe the community
LOADING = 0.25  # weight of a measure on the axis for it to be named

# What a high value of each dimension looks like, in words; then what a low one looks like.
WORDS: dict[str, tuple[str, str]] = {
    "fill_ratio": ("dense", "airy"),
    "glyph_entropy": ("many glyphs", "few glyphs"),
    "class_block": ("full blocks", "no full blocks"),
    "class_half_block": ("half blocks", "no half blocks"),
    "class_shade": ("shades", "no shades"),
    "class_box": ("box lines", "no box lines"),
    "class_alphanumeric": ("letters", "no letters"),
    "class_punctuation": ("punctuation", "no punctuation"),
    "class_other": ("odd glyphs", "no odd glyphs"),
    "high_bg_ratio": ("bright backgrounds", "dark backgrounds"),
    "symmetry_h": ("mirrored", "asymmetric"),
    "symmetry_v": ("mirrored top to bottom", "unbalanced top to bottom"),
    "draw_order": ("drawn out of order", "drawn line by line"),
    "center_row": ("weight low", "weight high"),
    "center_col": ("weight right", "weight left"),
}
VGA = (
    "black", "blue", "green", "cyan", "red", "magenta", "brown", "light grey", "dark grey",
    "bright blue", "bright green", "bright cyan", "bright red", "bright magenta", "yellow", "white",
)  # fmt: skip
# VGA's dark and bright twins, named together when a community holds both.
FAMILIES = {
    "blue": "blues", "green": "greens", "cyan": "cyans", "red": "reds", "magenta": "magentas",
    "brown": "yellows", "yellow": "yellows", "light grey": "greys", "white": "greys",
    "dark grey": "greys", "black": "greys",
}  # fmt: skip
DIMENSIONS = [*PROFILE, *(f"fg_{name}" for name in VGA)]

log = logging.getLogger(__name__)


def words(dimension: str, sign: float) -> str:
    if dimension.startswith("fg_"):
        colour = dimension[3:]
        return colour if sign > 0 else f"no {colour}"
    high, low = WORDS[dimension]
    return high if sign > 0 else low


def name_of(gaps: np.ndarray) -> str:
    """The strongest gaps in words; a colour and its bright twin, both present, make a family."""
    order = [i for i in np.argsort(-np.abs(gaps)) if abs(gaps[i]) >= STRONG]
    parts: list[str] = []
    for i in order:
        part = words(DIMENSIONS[i], gaps[i])
        family = FAMILIES.get(part.removeprefix("bright "))
        twin = next(
            (p for p in parts if family and FAMILIES.get(p.removeprefix("bright ")) == family), None
        )
        if twin:
            parts[parts.index(twin)] = family
        elif part not in parts:
            parts.append(part)
        if len(parts) == NAME_PARTS:
            break
    return " · ".join(parts) or "the middle of the corpus"


def axis(points: np.ndarray, shas: list[str]) -> dict[str, Any]:
    """The first principal component inside the community, and works at both of its ends."""
    centred = points - points.mean(axis=0)
    _, singular, vt = np.linalg.svd(centred, full_matrices=False)
    loadings = vt[0]
    scores = centred @ loadings
    named = [i for i in np.argsort(-np.abs(loadings)) if abs(loadings[i]) >= LOADING][:NAME_PARTS]
    low = [words(DIMENSIONS[i], -loadings[i]) for i in named]
    high = [words(DIMENSIONS[i], loadings[i]) for i in named]
    order = np.argsort(scores)
    at = {p: int(np.percentile(np.arange(len(order)), p)) for p in (LOW, HIGH)}
    return {
        "variance_share": round(float(singular[0] ** 2 / (singular**2).sum()), 3),
        "from": " · ".join(low),
        "to": " · ".join(high),
        "from_works": [shas[i] for i in order[at[LOW] : at[LOW] + ENDS]],
        "to_works": [shas[i] for i in order[max(at[HIGH] - ENDS + 1, 0) : at[HIGH] + 1]],
    }


def describe(
    community: int, members: np.ndarray, matrix: np.ndarray, meta: list[tuple[Any, ...]]
) -> dict[str, Any]:
    shas = [meta[i][0] for i in members]
    points = matrix[members]
    centre = points.mean(axis=0)
    distance = np.linalg.norm(points - centre, axis=1)
    typical = np.argsort(distance)[:TYPICAL]
    gaps = centre  # the corpus mean is 0 and its deviation 1 in every dimension
    years = [meta[i][1] for i in members if meta[i][1]]
    counted = collections.Counter
    return {
        "community": community,
        "works": len(members),
        "name": name_of(gaps),
        "named_by": NAMER,
        "profile": {DIMENSIONS[i]: round(float(gaps[i]), 2) for i in np.argsort(-np.abs(gaps))[:8]},
        "archetype": shas[typical[0]],
        "typical": [shas[i] for i in typical[1:]],
        "spread": round(float(distance.mean()), 3),
        "axis": axis(points, shas),
        "years": [int(np.percentile(years, p)) for p in (10, 25, 50, 75, 90)] if years else None,
        "kinds": dict(counted(meta[i][2] for i in members).most_common(3)),
        "groups": [g for g, _ in counted(meta[i][3] for i in members if meta[i][3]).most_common(5)],
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    manifest = json.loads((GRAPH / "manifest.json").read_text())
    works = ROOT / "datasets" / "build" / "works" / str(manifest["works"]["version"])
    columns = ", ".join(f"f.{name}" for name in PROFILE)
    rows = (
        duckdb.connect()
        .execute(
            f"select n.sha256, w.year, w.content_kind, lower(trim(w.sauce_group)), n.community,"
            f" {columns}, f.fg_hist from '{GRAPH / 'nodes.parquet'}' n"
            f" join '{works / 'works.parquet'}' w using (sha256)"
            f" join '{works / 'features.parquet'}' f using (sha256) order by n.sha256"
        )
        .fetchall()
    )
    first = 5
    matrix = profile([r[first:-1] for r in rows], [r[-1] for r in rows])
    assert matrix.shape[1] == len(PROFILE) + COLOURS
    membership = np.array([r[4] for r in rows])
    corpus_spread = float(np.linalg.norm(matrix, axis=1).mean())
    found = [
        describe(c, np.flatnonzero(membership == c), matrix, rows)
        for c in range(membership.max() + 1)
    ]
    out = {
        "graph": manifest["version"],
        "corpus_spread": round(corpus_spread, 3),
        "communities": found,
    }
    (GRAPH / "communities.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    for c in found:
        log.info("%2d %6d %-55s spread %.2f  %s ↔ %s", c["community"], c["works"], c["name"],
                 c["spread"], c["axis"]["from"], c["axis"]["to"])  # fmt: skip


if __name__ == "__main__":
    main()
