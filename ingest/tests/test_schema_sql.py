# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Invariants carried by the database: every constraint has a test that makes it fail."""

from __future__ import annotations

import pytest
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError

pytestmark = pytest.mark.db

SHA = "a" * 64
IDS = {
    "identity": "00000000-0000-0000-0000-000000000001",
    "work": "00000000-0000-0000-0000-000000000002",
}


def insert_artifact(db: Connection, sha: str = SHA) -> None:
    db.execute(text("insert into artifact (sha256, bytes) values (:s, 10)"), {"s": sha})


def assertion(db: Connection, **overrides: object) -> str:
    row: dict[str, object] = {
        "subject_type": "identity",
        "subject_id": IDS["identity"],
        "relation": "created",
        "object_type": "work",
        "object_id": IDS["work"],
        "nature": "testified",
        "evidence": None,
        "asserted_by": "human:tester",
        "role": None,
    }
    row.update(overrides)
    return str(
        db.execute(
            text(
                "insert into assertion (subject_type, subject_id, relation, object_type,"
                " object_id, nature, evidence, asserted_by, role) values (:subject_type,"
                " :subject_id, :relation, :object_type, :object_id, :nature, :evidence,"
                " :asserted_by, :role) returning id"
            ),
            row,
        ).scalar_one()
    )


def fails(db: Connection, match: str, fn: object) -> None:
    savepoint = db.begin_nested()
    with pytest.raises(DBAPIError, match=match):
        fn()  # type: ignore[operator]
    savepoint.rollback()


def test_inferred_requires_algo(db: Connection) -> None:
    fails(db, "check", lambda: assertion(db, nature="inferred"))
    assertion(db, nature="inferred", asserted_by="algo:resonance@0.1")


def test_documented_requires_evidence(db: Connection) -> None:
    fails(db, "check", lambda: assertion(db, nature="documented"))
    insert_artifact(db)
    assertion(db, nature="documented", evidence=SHA)


def test_asserted_by_has_a_kind(db: Connection) -> None:
    fails(db, "check", lambda: assertion(db, asserted_by="nicolas"))


def test_had_role_requires_role(db: Connection) -> None:
    fails(db, "check", lambda: assertion(db, relation="had_role"))
    assertion(db, relation="had_role", role="sysop", object_type="place")


def test_assertion_is_append_only(db: Connection) -> None:
    old = assertion(db)
    new = assertion(db, asserted_by="human:corrector")
    fails(
        db,
        "append-only",
        lambda: db.execute(
            text("update assertion set relation = 'references' where id = :i"), {"i": old}
        ),
    )
    fails(
        db,
        "append-only",
        lambda: db.execute(text("delete from assertion where id = :i"), {"i": old}),
    )
    db.execute(text("update assertion set superseded_by = :n where id = :o"), {"n": new, "o": old})
    fails(
        db,
        "append-only",
        lambda: db.execute(
            text("update assertion set superseded_by = null where id = :o"), {"o": old}
        ),
    )
    active = db.execute(text("select count(*) from edge_testified")).scalar_one()
    assert active == 1


def test_artifact_is_immutable(db: Connection) -> None:
    insert_artifact(db)
    db.execute(text("update artifact set format = 'ans' where sha256 = :s"), {"s": SHA})
    fails(
        db,
        "immutable",
        lambda: db.execute(text("update artifact set bytes = 11 where sha256 = :s"), {"s": SHA}),
    )
    fails(
        db,
        "delete forbidden",
        lambda: db.execute(text("delete from artifact where sha256 = :s"), {"s": SHA}),
    )


def test_artifact_hash_format(db: Connection) -> None:
    fails(db, "check", lambda: insert_artifact(db, "A" * 64))


def test_decoding_is_grid_or_classified_error(db: Connection) -> None:
    insert_artifact(db)
    sql = text(
        "insert into decoding (sha256, decoder, decoder_version, status, error_class,"
        " grid_sha256, document_kind, system, charset)"
        " values (:s, 'ansi', :v, :st, :e, :g, :k, :sys, :cs)"
    )
    grid = {"k": "grid", "sys": "pc-vga", "cs": "cp437"}
    none = {"k": None, "sys": None, "cs": None}
    fails(
        db,
        "check",
        lambda: db.execute(sql, {"s": SHA, "v": "1", "st": "error", "e": None, "g": None, **none}),
    )
    fails(
        db,
        "check",
        lambda: db.execute(sql, {"s": SHA, "v": "2", "st": "ok", "e": None, "g": None, **grid}),
    )
    db.execute(sql, {"s": SHA, "v": "3", "st": "error", "e": "truncated", "g": None, **none})
    db.execute(sql, {"s": SHA, "v": "4", "st": "ok", "e": None, "g": "b" * 64, **grid})


def test_a_decoded_document_says_its_kind_system_and_charset(db: Connection) -> None:
    """ADR 0026: a query picks grids by system without opening them."""
    insert_artifact(db)
    sql = text(
        "insert into decoding (sha256, decoder, decoder_version, status, grid_sha256,"
        " document_kind, system, charset) values (:s, 'x', :v, 'ok', :g, :k, :sys, :cs)"
    )
    ok = {"s": SHA, "g": "b" * 64}
    for version, kind, system, charset in [
        ("1", None, None, None),  # an ok decoding without a document kind
        ("2", "grid", None, "cp437"),  # a document without a system
        ("3", "grid", "pc-vga", None),  # a grid without a charset
        ("4", "image", "pc-vga", "cp437"),  # not a kind of document
    ]:
        values = {**ok, "v": version, "k": kind, "sys": system, "cs": charset}
        fails(db, "check", lambda values=values: db.execute(sql, values))
    db.execute(sql, {**ok, "v": "5", "k": "vector", "sys": "pc-vga", "cs": None})
    db.execute(sql, {**ok, "v": "6", "k": "grid", "sys": "c64", "cs": "petscii-upper"})


def test_expansion_says_why_a_pack_is_empty_or_partial(db: Connection) -> None:
    insert_artifact(db)
    sql = text(
        "insert into expansion (sha256, status, error_class, unreadable)"
        " values (:s, :st, :e, cast(:u as text[]))"
    )
    for status, error_class, unreadable in [
        ("error", None, []),
        ("ok", "bad_archive", []),
        ("partial", None, []),
        ("ok", None, ["TUNE.XM"]),
    ]:
        values = {"s": SHA, "st": status, "e": error_class, "u": unreadable}
        fails(db, "check", lambda values=values: db.execute(sql, values))
    db.execute(sql, {"s": SHA, "st": "partial", "e": None, "u": ["TUNE.XM"]})


def test_features_histograms_have_their_size(db: Connection) -> None:
    insert_artifact(db)
    sql = text(
        "insert into features (sha256, extractor_version, grid_sha256, cols, rows, cells,"
        " fill_ratio, center_row, center_col, symmetry_h, symmetry_v, glyph_hist, glyph_entropy,"
        " class_block, class_half_block, class_shade, class_box, class_alphanumeric,"
        " class_punctuation, class_other, bigram_codes, bigram_counts, n_colors, fg_hist,"
        " bg_hist, high_bg_ratio, fg_bg_pairs, cursor_jumps, draw_order) values (:s, :v,"
        " :s, 80, 1, 0, 0, 0.5, 0.5, 0, 0, cast(:glyphs as integer[]), 0, 0, 0, 0, 0, 0, 0, 0,"
        " '{}', :counts, 0, cast(:fg as integer[]), cast(:bg as integer[]), 0, 0, 0, 1)"
    )
    good = {"s": SHA, "glyphs": [0] * 256, "counts": [], "fg": [0] * 16, "bg": [0] * 8}
    for version, wrong in enumerate(
        [{"glyphs": [0] * 255}, {"fg": [0] * 8}, {"bg": [0] * 16}, {"counts": [1]}]
    ):
        values = {**good, **wrong, "v": str(version)}
        fails(db, "check", lambda values=values: db.execute(sql, values))
    db.execute(sql, {**good, "v": "ok"})


def test_text_layer_rows_and_lines_go_together(db: Connection) -> None:
    insert_artifact(db)
    sql = text(
        "insert into text_layer (sha256, extractor_version, grid_sha256, line_rows, lines)"
        " values (:s, :v, :s, cast(:rows as integer[]), cast(:lines as text[]))"
    )
    fails(db, "check", lambda: db.execute(sql, {"s": SHA, "v": "1", "rows": [0], "lines": []}))
    db.execute(sql, {"s": SHA, "v": "1", "rows": [0], "lines": ["rs^mdn"]})


def test_authentic_representation_needs_profile(db: Connection) -> None:
    insert_artifact(db)
    sql = text(
        "insert into representation (sha256, level, profile, recipe, output_sha256)"
        " values (:s, :l, :p, '{}', :o)"
    )
    fails(
        db, "check", lambda: db.execute(sql, {"s": SHA, "l": "authentic", "p": None, "o": "c" * 64})
    )
    db.execute(sql, {"s": SHA, "l": "authentic", "p": "pc-vga-bbs-1994", "o": "c" * 64})


def insert_work(db: Connection) -> str:
    return str(
        db.execute(text("insert into work (kind) values ('single') returning id")).scalar_one()
    )


def test_cartel_one_current_text_per_language(db: Connection) -> None:
    work = insert_work(db)
    sql = text(
        "insert into cartel (work_id, lang, body, written_by, translated_from)"
        " values (:w, :l, :b, :by, :src) returning id"
    )
    fr = db.execute(
        sql, {"w": work, "l": "fr", "b": "Un ciel.", "by": "human:curator", "src": None}
    ).scalar_one()
    db.execute(sql, {"w": work, "l": "en", "b": "A sky.", "by": "algo:translate@1", "src": fr})
    fails(
        db,
        "duplicate key",
        lambda: db.execute(
            sql, {"w": work, "l": "fr", "b": "Autre.", "by": "human:curator", "src": None}
        ),
    )
    fails(
        db,
        "check",
        lambda: db.execute(
            sql, {"w": work, "l": "French", "b": "x", "by": "human:curator", "src": None}
        ),
    )
    fails(
        db,
        "check",
        lambda: db.execute(sql, {"w": work, "l": "de", "b": "x", "by": "deepl", "src": fr}),
    )
