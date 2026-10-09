# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path

import pytest
from packs_on_disk import HORIZON, ingest
from sqlalchemy import Connection, text
from stores import Stores
from tm.audience import KEYWORDS, STREAM, rate_flashing, rate_words
from tm.decode import decode_pending
from tm.features import extract_artifact, pending_features
from tm.text_layer import pending_text, read_artifact

pytestmark = pytest.mark.db

SWEARING = b"\x1b[0;37mwhat the fuck, lamers\r\n"
BLINKING = b"\x1b[5;31mblinking skull\r\n"  # SGR 5: the blink bit, no iCE in SAUCE


def test_words_and_streams_give_ratings_to_review(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    files = {"SWEAR.ANS": SWEARING, "BLINK.ANS": BLINKING, "HORIZON.ANS": HORIZON}
    ingest(db, stores, tmp_path / "1995" / "a.zip", files)
    decode_pending(db, stores.originals, stores.derived)
    for row in pending_features(db):
        extract_artifact(db, stores.derived, row)
    for row in pending_text(db):
        read_artifact(db, stores.derived, row)
    found = rate_words(db)
    assert found == {("language", "16"): 1, ("fear", "12"): 1}
    assert rate_flashing(db) == 1
    rows = db.execute(
        text(
            "select a.source_path, r.descriptor, r.level, r.nature, r.asserted_by,"
            " r.evidence_note from content_rating r join artifact a using (sha256) order by 1, 2"
        )
    ).all()
    assert [tuple(r) for r in rows] == [
        ("1995/a.zip/BLINK.ANS", "fear", "12", "inferred", KEYWORDS, "words: skull"),
        ("1995/a.zip/BLINK.ANS", "flashing", None, "inferred", STREAM,
         "blinking cells outside iCE, or a third of the cells redrawn"),
        ("1995/a.zip/SWEAR.ANS", "language", "16", "inferred", KEYWORDS, "words: fuck"),
    ]  # fmt: skip
    assert rate_words(db) == {}  # a second run adds nothing
    assert rate_flashing(db) == 0
    level = "select a.source_path, w.level, w.has_unreviewed, w.reviewed from work_audience w"
    level += " join artifact a using (sha256) order by 1"
    assert [tuple(r) for r in db.execute(text(level))] == [
        ("1995/a.zip/BLINK.ANS", "12", True, False),
        ("1995/a.zip/SWEAR.ANS", "16", True, False),
    ]


def test_a_new_version_supersedes_the_earlier_one(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    ingest(db, stores, tmp_path / "1995" / "a.zip", {"SWEAR.ANS": SWEARING})
    decode_pending(db, stores.originals, stores.derived)
    for row in pending_text(db):
        read_artifact(db, stores.derived, row)
    sha = db.execute(text("select sha256 from artifact where source_path like '%SWEAR%'")).scalar()
    for descriptor, level in (("sexual", "18"), ("language", "12")):
        db.execute(
            text(
                "insert into content_rating (sha256, descriptor, kind, level, grid_version,"
                " nature, asserted_by) values (:s, :d, 'descriptor', :l, 1, 'inferred',"
                " 'algo:keywords@0')"
            ),
            {"s": sha, "d": descriptor, "l": level},
        )
    rate_words(db)
    current = db.execute(
        text(
            "select descriptor, present, level, asserted_by from content_rating"
            " where superseded_by is null order by 1"
        )
    ).all()
    assert [tuple(r) for r in current] == [
        ("language", True, "16", KEYWORDS),
        ("sexual", False, None, KEYWORDS),
    ]
