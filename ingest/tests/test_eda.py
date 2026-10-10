# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The live exploration (ADR 0028): its statistics, and its chapters on a small database."""

from __future__ import annotations

from pathlib import Path

import pytest
from packs_on_disk import HORIZON, ingest
from sqlalchemy import Connection, create_engine, text
from stores import Stores
from tm import features
from tm.decode import decode_pending
from tm.eda import fingerprint, snapshot
from tm.eda.stats import Kind, agreement, group_agreement_test, histogram, kitagawa

PLAIN = b"Just words, typed in grey on black.\r\n" * 3


def test_agreement_counts_the_majority_of_each_group() -> None:
    assert agreement([[True, True, False], [False]]) == 3 / 4
    assert agreement([]) == 0.0


def test_groups_that_decide_together_beat_the_permutation_null() -> None:
    together = [[True] * 6, [False] * 6] * 10
    test = group_agreement_test(together, draws=200)
    assert test.observed == 1.0
    assert test.q95 < test.observed
    assert test.p < 0.01


def test_groups_that_do_not_matter_stay_within_the_null() -> None:
    mixed = [[True, False, True, False]] * 20
    test = group_agreement_test(mixed, draws=200)
    assert test.observed <= test.q95
    assert test.p > 0.05


def test_the_permutation_is_reproducible() -> None:
    groups = [[True, False, False], [True, True, False, True]]
    assert group_agreement_test(groups, 50).null == group_agreement_test(groups, 50).null


def test_kitagawa_parts_add_up_to_the_change_of_the_mean() -> None:
    before = {"blocks": Kind(0.9, 0.3), "text": Kind(0.1, 0.0)}
    after = {"blocks": Kind(0.5, 0.25), "text": Kind(0.5, 0.0)}
    split = kitagawa(before, after)
    assert split["total"] == pytest.approx(0.5 * 0.25 - 0.9 * 0.3)
    assert split["within"] + split["composition"] == pytest.approx(split["total"])
    assert abs(split["composition"]) > abs(split["within"])


def test_kitagawa_puts_a_new_kind_in_the_composition() -> None:
    split = kitagawa({"blocks": Kind(1.0, 0.2)}, {"blocks": Kind(0.5, 0.2), "text": Kind(0.5, 0)})
    assert split["within"] == pytest.approx(0)
    assert split["composition"] == pytest.approx(-0.1)


def test_histogram_closes_the_last_bin() -> None:
    assert histogram([0, 0.1, 0.5, 1.0, 1.5], 0, 1, 2) == [2, 2]


@pytest.fixture
def corpus(db: Connection, stores: Stores, tmp_path: Path) -> None:
    ingest(db, stores, tmp_path / "1995" / "demo95.zip", {"HORIZON.ANS": HORIZON}, "train")
    ingest(db, stores, tmp_path / "1996" / "words96.zip", {"WORDS.ASC": PLAIN}, "train")
    decode_pending(db, stores.originals, stores.derived)
    for row in features.pending_features(db):
        features.extract_artifact(db, stores.derived, row)


@pytest.mark.db
@pytest.mark.usefixtures("corpus")
def test_the_snapshot_reads_the_database_as_it_is(db: Connection) -> None:
    found = snapshot(db)
    contents = found["chapters"]["contents"]
    assert contents["funnel"]["art"] == 2
    assert contents["funnel"]["packs"] == 2
    assert contents["checks"]["every_work_decoded"]["holds"]
    years = {y["year"]: y for y in found["chapters"]["peak"]["years"]}
    assert set(years) == {1995, 1996}
    eras = {e["era"] for e in found["chapters"]["revival"]["eras"]}
    assert eras == {"1994-95", "1996-97"}  # train packs, measured


@pytest.mark.db
@pytest.mark.usefixtures("corpus")
def test_a_withdrawn_work_is_counted_nowhere(db: Connection) -> None:
    db.execute(
        text(
            """update work set privacy = '{"withdrawn": true}' where kind = 'single'"""
            " and id = (select v.work_id from artifact a join version v on v.id = a.version_id"
            " where a.source_path like '%HORIZON.ANS')"
        )
    )
    found = snapshot(db)
    assert found["hidden"] == 1
    assert found["chapters"]["contents"]["funnel"]["art"] == 1
    assert [y["year"] for y in found["chapters"]["peak"]["years"]] == [1996]
    assert {e["era"] for e in found["chapters"]["revival"]["eras"]} == {"1996-97"}


@pytest.mark.db
def test_the_fingerprint_moves_with_a_write(db_url: str) -> None:
    engine = create_engine(db_url, isolation_level="AUTOCOMMIT")  # statistics count commits
    with engine.connect() as conn:
        before = fingerprint(conn)
        conn.execute(text("insert into source (kind, name) values ('manual', 'eda-test')"))
        conn.execute(text("delete from source where name = 'eda-test'"))
        conn.execute(text("select pg_stat_force_next_flush()"))
        conn.execute(text("select pg_stat_clear_snapshot()"))
        assert fingerprint(conn) != before
    engine.dispose()
