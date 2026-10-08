# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import Connection, text
from tm.ingest import golden_files, ingest_golden
from tm.rights import Privacy, Rights, can_display
from tm.storage import LocalStore, get_original

GOLDEN = Path(__file__).resolve().parents[2] / "tests" / "golden"
HORIZON = GOLDEN / "ansi" / "horizon.ans"

pytestmark = pytest.mark.db


class Shown:
    def __init__(self, rights: Rights) -> None:
        self.rights = rights
        self.privacy = Privacy()


def count(db: Connection, table: str) -> int:
    return int(db.execute(text(f"select count(*) from {table}")).scalar_one())


def test_golden_files_finds_horizon() -> None:
    assert HORIZON in golden_files(GOLDEN)


def test_ingest_records_source_work_version_and_artifact(db: Connection, tmp_path: Path) -> None:
    store = LocalStore(tmp_path)
    [item] = ingest_golden(db, store, GOLDEN)
    assert item.path == "ansi/horizon.ans"
    assert item.new
    assert get_original(store, item.sha256) == HORIZON.read_bytes()
    row = db.execute(
        text(
            "select a.format, a.charset, a.bytes, a.source_path, a.sauce->>'author' as author,"
            " s.kind, w.title, v.date_min, v.date_basis, v.behavior"
            " from artifact a join source s on s.id = a.source_id"
            " join version v on v.id = a.version_id join work w on w.id = v.work_id"
            " where a.sha256 = :sha"
        ),
        {"sha": item.sha256},
    ).one()
    assert (row.format, row.charset, row.bytes) == ("ansi", "cp437", len(HORIZON.read_bytes()))
    assert (row.source_path, row.author, row.kind) == ("ansi/horizon.ans", "claude", "golden")
    assert (row.title, row.date_basis, row.behavior) == ("Horizon", "sauce", "static")
    assert row.date_min.isoformat() == "2026-10-07"


def test_ingest_is_idempotent(db: Connection, tmp_path: Path) -> None:
    store = LocalStore(tmp_path)
    ingest_golden(db, store, GOLDEN)
    before = {t: count(db, t) for t in ("source", "work", "version", "artifact")}
    [again] = ingest_golden(db, store, GOLDEN)
    assert not again.new
    assert {t: count(db, t) for t in before} == before


def test_ingested_work_may_be_displayed(db: Connection, tmp_path: Path) -> None:
    ingest_golden(db, LocalStore(tmp_path), GOLDEN)
    rights = db.execute(text("select rights from work")).scalar_one()
    parsed = Rights.model_validate(rights)
    assert parsed.license == "CC0-1.0"
    assert can_display(Shown(parsed)) == "file"


def test_a_file_without_sauce_falls_back_to_its_name(db: Connection, tmp_path: Path) -> None:
    root = tmp_path / "golden"
    root.mkdir()
    (root / "plain.ans").write_bytes(b"hello\r\n")
    ingest_golden(db, LocalStore(tmp_path / "store"), root)
    row = db.execute(
        text(
            "select w.title, a.sauce is null as no_sauce, v.date_basis from artifact a"
            " join version v on v.id = a.version_id join work w on w.id = v.work_id"
        )
    ).one()
    assert (row.title, row.no_sauce, row.date_basis) == ("plain", True, None)


def test_an_impossible_sauce_date_is_not_recorded(db: Connection, tmp_path: Path) -> None:
    data = HORIZON.read_bytes()
    index = data.rindex(b"20261007")
    root = tmp_path / "golden"
    root.mkdir()
    (root / "odd.ans").write_bytes(data[:index] + b"20269999" + data[index + 8 :])
    ingest_golden(db, LocalStore(tmp_path / "store"), root)
    row = db.execute(text("select date_min, date_basis from version")).one()
    assert (row.date_min, row.date_basis) == (None, None)
