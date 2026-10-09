# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from collections import Counter

import pytest
from tm.sampling import draw

FRAME = [
    {"id": f"u{i:03}", "era": "a" if i < 90 else "b", "size": i % 7, "kind": None if i % 5 else "x"}
    for i in range(100)
]


def sample(seed: int = 1, per_stratum: int = 3) -> list:
    return draw(
        FRAME, unit="id", stratum="era", order=["kind", "size"], per_stratum=per_stratum, seed=seed
    )


def test_each_stratum_gives_its_share_with_its_weight() -> None:
    drawn = sample()
    assert Counter(d.stratum for d in drawn) == {"a": 3, "b": 3}
    a = next(d for d in drawn if d.stratum == "a")
    assert (a.frame_size, a.drawn, a.weight) == (90, 3, 30.0)
    assert len({d.unit for d in drawn}) == 6


def test_the_same_seed_draws_the_same_units() -> None:
    assert sample(7) == sample(7)
    assert sample(7) != sample(8)


def test_a_stratum_smaller_than_its_share_is_taken_whole() -> None:
    drawn = sample(per_stratum=12)
    b = [d for d in drawn if d.stratum == "b"]
    assert len(b) == 10
    assert all(d.weight == 1.0 for d in b)


def test_a_stratum_draw_does_not_depend_on_the_others() -> None:
    alone = draw(FRAME[90:], unit="id", stratum="era", order=["size"], per_stratum=3, seed=5)
    together = draw(FRAME, unit="id", stratum="era", order=["size"], per_stratum=3, seed=5)
    assert alone == [d for d in together if d.stratum == "b"]


def test_every_unit_can_be_drawn() -> None:
    seen = {d.unit for seed in range(400) for d in sample(seed) if d.stratum == "b"}
    assert seen == {row["id"] for row in FRAME[90:]}


def test_an_empty_share_is_refused() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        sample(per_stratum=0)
