# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The audience grid (ADR 0020): one source in corpus/ratings/grid.yaml, the same everywhere."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError
from tm.corpus import Grid, load_grid
from tm.ratings import written
from tm_render.conservation import BitmapFont

ROOT = Path(__file__).resolve().parents[2]
GRID = load_grid(ROOT / "corpus" / "ratings" / "grid.yaml")
SHA = "b" * 64


def test_published_files_are_current() -> None:
    font = BitmapFont.load(ROOT / "corpus" / "fonts" / "ibm-vga-8x16.f16")
    for path, content in written(GRID, font, ROOT / "corpus", ROOT / "docs").items():
        assert path.read_text(encoding="utf-8") == content, f"run `tm corpus ratings`: {path}"


def test_level_three_means_no_descriptor() -> None:
    raw = GRID.model_dump()
    raw["descriptors"][0]["levels"]["3"] = {"en": "x", "fr": "x"}
    with pytest.raises(ValidationError, match="level 3 means no descriptor"):
        Grid.model_validate(raw)


def test_levels_keep_their_order() -> None:
    raw = GRID.model_dump()
    raw["levels"] = list(reversed(raw["levels"]))
    with pytest.raises(ValidationError, match="in that order"):
        Grid.model_validate(raw)


@pytest.mark.db
def test_the_database_holds_the_grid(db: Connection) -> None:
    levels = db.execute(text("select code, min_age from audience_level order by rank")).all()
    assert [tuple(r) for r in levels] == [(lv.code, lv.min_age) for lv in GRID.levels]
    kinds = dict(db.execute(text("select code, kind from content_descriptor")).all())
    expected = {d.code: "descriptor" for d in GRID.descriptors}
    expected |= {n.code: "notice" for n in GRID.notices}
    assert kinds == expected
    degrees = set(db.execute(text("select descriptor, level from descriptor_level")).all())
    assert {tuple(r) for r in degrees} == {
        (d.code, level) for d in GRID.descriptors for level in d.levels
    }


def rate(db: Connection, **overrides: object) -> str:
    row: dict[str, object] = {
        "sha256": SHA,
        "descriptor": "violence",
        "kind": "descriptor",
        "present": True,
        "level": "12",
        "nature": "inferred",
        "asserted_by": "algo:keywords@1",
    }
    row.update(overrides)
    return str(
        db.execute(
            text(
                "insert into content_rating (sha256, descriptor, kind, present, level,"
                " grid_version, nature, asserted_by) values (:sha256, :descriptor, :kind,"
                " :present, :level, 1, :nature, :asserted_by) returning id"
            ),
            row,
        ).scalar_one()
    )


def fails(db: Connection, match: str, fn: object) -> None:
    savepoint = db.begin_nested()
    with pytest.raises(DBAPIError, match=match):
        fn()  # type: ignore[operator]
    savepoint.rollback()


@pytest.mark.db
def test_a_rating_follows_the_grid(db: Connection) -> None:
    db.execute(text("insert into artifact (sha256, bytes) values (:s, 10)"), {"s": SHA})
    fails(db, "foreign key", lambda: rate(db, descriptor="language", level="18"))
    fails(db, "check", lambda: rate(db, level=None))
    fails(db, "check", lambda: rate(db, descriptor="flashing", kind="notice"))
    fails(db, "check", lambda: rate(db, asserted_by="human:reviewer"))
    fails(db, "check", lambda: rate(db, nature="reviewed"))
    fails(db, "check", lambda: rate(db, nature="declared", asserted_by="human:x"))
    rate(db, descriptor="flashing", kind="notice", level=None)
    rate(db, nature="declared", asserted_by="identity:horizon")


@pytest.mark.db
def test_a_rating_is_append_only(db: Connection) -> None:
    db.execute(text("insert into artifact (sha256, bytes) values (:s, 10)"), {"s": SHA})
    first = rate(db)
    fails(db, "append-only", lambda: db.execute(text("delete from content_rating")))
    fails(
        db,
        "append-only",
        lambda: db.execute(text("update content_rating set level = '16'")),
    )
    second = rate(db, nature="reviewed", asserted_by="human:reviewer", level="16")
    db.execute(
        text("update content_rating set superseded_by = :s where id = :f"),
        {"s": second, "f": first},
    )


@pytest.mark.db
def test_a_work_takes_its_highest_current_level(db: Connection) -> None:
    db.execute(text("insert into artifact (sha256, bytes) values (:s, 10)"), {"s": SHA})
    inferred = rate(db, descriptor="sexual", level="18")
    rate(db, descriptor="fear", level="12")
    rate(db, descriptor="flashing", kind="notice", level=None)
    audience = "select level, descriptors, notices, has_unreviewed from work_audience"
    assert tuple(db.execute(text(audience)).one()) == (
        "18",
        ["fear", "sexual"],
        ["flashing"],
        True,
    )
    rejection = rate(
        db, descriptor="sexual", present=False, level=None, nature="reviewed",
        asserted_by="human:reviewer",
    )  # fmt: skip
    db.execute(
        text("update content_rating set superseded_by = :r where id = :i"),
        {"r": rejection, "i": inferred},
    )
    assert tuple(db.execute(text(audience)).one())[:2] == ("12", ["fear"])
