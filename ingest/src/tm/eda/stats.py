# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The few statistics the exploration needs, small enough to read in one sitting.

A permutation test asks how often chance alone would give a value at least as large as the one
observed; a Kitagawa decomposition splits a change of mean into what changed inside each kind
and what came from the mix of kinds changing.
"""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

SEED = 20261010  # every permutation of the exploration draws from this seed
QUANTILE = 0.95


def agreement(groups: Sequence[Sequence[bool]]) -> float:
    """Share of items that make the same choice as the majority of their group."""
    total = sum(len(g) for g in groups)
    if not total:
        return 0.0
    return sum(max(sum(g), len(g) - sum(g)) for g in groups) / total


@dataclass(frozen=True)
class Permutation:
    observed: float
    null: list[float]  # sorted

    @property
    def mean(self) -> float:
        return sum(self.null) / len(self.null)

    @property
    def q95(self) -> float:
        return self.null[min(len(self.null) - 1, int(QUANTILE * len(self.null)))]

    @property
    def p(self) -> float:
        """One-sided, with the observed value counted among the draws (never exactly 0)."""
        return (1 + sum(x >= self.observed for x in self.null)) / (1 + len(self.null))


def group_agreement_test(groups: Sequence[Sequence[bool]], draws: int = 2000) -> Permutation:
    """Agreement within groups, against the same choices shuffled across groups of the same
    sizes: if groups did not matter, where an item sits would not change its choice."""
    pooled = [x for g in groups for x in g]
    sizes = [len(g) for g in groups]
    rng = random.Random(SEED)
    null: list[float] = []
    for _ in range(draws):
        rng.shuffle(pooled)
        cuts = iter(pooled)
        null.append(agreement([[next(cuts) for _ in range(n)] for n in sizes]))
    return Permutation(agreement(groups), sorted(null))


@dataclass(frozen=True)
class Kind:
    """One kind in one period: its share of the items and the mean of the measure within it."""

    share: float
    mean: float


def kitagawa(before: Mapping[str, Kind], after: Mapping[str, Kind]) -> dict[str, float]:
    """Change of the overall mean, split into `within` (each kind's mean moved) and
    `composition` (the mix of kinds moved); the two parts add up to `total`."""
    within = composition = 0.0
    for name in before.keys() | after.keys():
        a, b = before.get(name, Kind(0.0, 0.0)), after.get(name, Kind(0.0, 0.0))
        mean_a = a.mean if a.share else b.mean  # a kind absent on one side moves the mix only
        mean_b = b.mean if b.share else a.mean
        within += (mean_b - mean_a) * (a.share + b.share) / 2
        composition += (b.share - a.share) * (mean_a + mean_b) / 2
    return {"total": within + composition, "within": within, "composition": composition}


def histogram(values: Sequence[float], low: float, high: float, bins: int) -> list[int]:
    """Counts in `bins` equal bins from `low` to `high`, the last one closed."""
    counts = [0] * bins
    width = (high - low) / bins
    for value in values:
        if low <= value <= high:
            counts[min(bins - 1, int((value - low) / width))] += 1
    return counts


def quantile(ordered: Sequence[float], q: float) -> float:
    """The `q` quantile of sorted values, interpolated as PostgreSQL's `percentile_cont`."""
    if not ordered:
        return 0.0
    at = q * (len(ordered) - 1)
    low = int(at)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (at - low)


def lorenz(sizes: Sequence[int], points: int = 40) -> list[tuple[float, float]]:
    """The Lorenz curve of `sizes`: for the smallest share x of the groups, the share y of
    the total they hold, sampled at about `points` places from (0, 0) to (1, 1)."""
    ordered = sorted(sizes)
    total = sum(ordered)
    if not total:
        return [(0.0, 0.0), (1.0, 1.0)]
    curve = [(0.0, 0.0)]
    held = 0
    step = max(1, len(ordered) // points)
    for i, size in enumerate(ordered, 1):
        held += size
        if i % step == 0 or i == len(ordered):
            curve.append((i / len(ordered), held / total))
    return curve


def gini(sizes: Sequence[int]) -> float:
    """0 when every group holds as much, towards 1 when one holds everything."""
    ordered = sorted(sizes)
    total, n = sum(ordered), len(ordered)
    if not total:
        return 0.0
    weighted = sum((2 * i - n - 1) * size for i, size in enumerate(ordered, 1))
    return weighted / (n * total)
