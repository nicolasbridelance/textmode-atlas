# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Stratified systematic sampling, for pilot datasets drawn from a frame (ADR 0017).

Within each stratum the units are sorted by the frame's order columns, then every k-th unit is
taken from a random start, k = N / n. Sorting first spreads the sample over the order columns
without making more strata (implicit stratification). Each drawn unit has inclusion probability
n / N in its stratum and keeps the weight N / n, so statistics can be reweighted to the frame.
The start is drawn from the seed and the stratum's name: the same frame and seed give the same
sample, and a stratum's draw does not change when another stratum changes.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Drawn:
    unit: str
    stratum: str
    frame_size: int  # N: units of the stratum in the frame
    drawn: int  # n: units drawn from it
    weight: float  # N / n


def draw(
    frame: Sequence[Mapping[str, Any]],
    *,
    unit: str,
    stratum: str,
    order: Sequence[str],
    per_stratum: int,
    seed: int,
) -> list[Drawn]:
    """Draw `per_stratum` units from each stratum of `frame`, or all of a smaller stratum."""
    if per_stratum < 1:
        raise ValueError(f"per_stratum must be at least 1, not {per_stratum}")
    strata: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in frame:
        strata[str(row[stratum])].append(row)
    sample: list[Drawn] = []
    for name in sorted(strata):
        rows = sorted(strata[name], key=lambda r: (*(_sortable(r[c]) for c in order), r[unit]))
        size, n = len(rows), min(per_stratum, len(rows))
        start = random.Random(f"{seed}:{name}").random() * size / n
        picks = [rows[math.floor(start + i * size / n)] for i in range(n)]
        sample.extend(Drawn(str(r[unit]), name, size, n, size / n) for r in picks)
    return sample


def _sortable(value: Any) -> tuple[bool, Any]:
    """Nulls last, and never compared with a value."""
    return (value is None, value if value is not None else 0)
