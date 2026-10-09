# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
import importlib.util
import sys
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPLORER = ROOT / "research" / "explorer"
sys.path.insert(0, str(EXPLORER))  # the host imports its neighbours by name
spec = importlib.util.spec_from_file_location("explorer", EXPLORER / "explorer.py")
assert spec
assert spec.loader
explorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(explorer)

SHOWN = [letter * 64 for letter in "abcdef"]
HIDDEN = "f" * 64  # metadata only: never drawn
UNDECODED = "e" * 64


@pytest.fixture
def db():
    con = duckdb.connect()
    con.execute(
        "create table w (sha256 varchar, year int, format varchar, content_kind varchar,"
        " archives varchar[], sauce_group varchar, sauce_author varchar, pack varchar,"
        " path varchar, decoding varchar)"
    )
    for i, sha in enumerate(SHOWN):
        con.execute(
            "insert into w values (?, ?, 'ansi', 'text', ['16colo'], 'g', 'a', 'p', 'f', ?)",
            [sha, 1996 if i % 2 else 1997, "error" if sha == UNDECODED else "ok"],
        )
    con.execute("create table visit_rules (sha256 varchar, shown varchar, level varchar)")
    for sha in SHOWN:
        con.execute(
            "insert into visit_rules values (?, ?, '12')",
            [sha, "metadata" if sha == HIDDEN else "files"],
        )
    return con


def test_a_seed_draws_the_same_work_again(db):
    first = explorer.surprise(db, {"seed": "abc234"})
    assert first == explorer.surprise(db, {"seed": "abc234"})
    assert first["seed"] == "abc234"


def test_draws_only_decoded_works_whose_files_may_be_shown(db):
    drawn = {explorer.surprise(db, {"seed": f"s{i}"})["sha256"] for i in range(40)}
    assert drawn <= set(SHOWN) - {HIDDEN, UNDECODED}
    assert len(drawn) > 1  # the seed does move the draw


def test_draws_within_the_filters_or_not_at_all(db):
    for i in range(10):
        found = explorer.surprise(db, {"seed": f"s{i}", "year": "1996"})
        assert found["sha256"] in {SHOWN[1], SHOWN[3]}
    assert explorer.surprise(db, {"seed": "x", "year": "1980"}) is None


def test_random_order_takes_the_seed_and_other_orders_do_not():
    assert explorer._order({"order": "random", "seed": "abc"}) == (
        explorer.ORDERS["random"],
        ["abc"],
    )
    assert explorer._order({})[1] == [explorer.DEFAULT_SEED]
    assert explorer._order({"order": "year"}) == (explorer.ORDERS["year"], [])


def test_a_seed_is_never_sql(db):
    with pytest.raises(ValueError, match="seed"):
        explorer.surprise(db, {"seed": "x' or 1=1 --"})
