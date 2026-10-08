# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from sqlalchemy import Connection, text
from stores import Stores
from tm.archives import Expanded
from tm.packs import ingest_pack, pack_archives
from tm.rights import Privacy, Rights, can_display
from tm.storage import get_original, sha256_hex

HORIZON = (Path(__file__).resolve().parents[2] / "tests/golden/ansi/horizon.ans").read_bytes()
# Same SAUCE record, other content: art that only its SAUCE record identifies.
LOGO = b"\x1b[1;36mLOGO" + HORIZON[len(b"\x1b[1;36mLOGO") :]
MEMBERS = {
    "HORIZON.ANS": HORIZON,
    "DEMO.NFO": b"demo pack 1995\r\n",
    "TUNE.XM": b"Extended Module: \x00\x01",
    "LOGO.GR": LOGO,
    "SUB/FILE_ID.DIZ": b"demo95 - 5 files\r\n",
}

pytestmark = pytest.mark.db


class Shown:
    def __init__(self, rights: Rights) -> None:
        self.rights = rights
        self.privacy = Privacy()


def make_pack(path: Path, members: dict[str, bytes]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("SUB/", b"")
        for name, data in members.items():
            archive.writestr(name, data)
    return path


def rows(db: Connection, sql: str) -> list[tuple[object, ...]]:
    return [tuple(row) for row in db.execute(text(sql)).all()]


def test_pack_archives_lists_archives_in_order(tmp_path: Path) -> None:
    for name in ("1995/b.zip", "1995/a.RAR", "1995/notes.txt", "1996/c.zip"):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_bytes(b"x")
    found = pack_archives([tmp_path / "1995", tmp_path / "1996" / "c.zip"])
    assert [p.relative_to(tmp_path).as_posix() for p in found] == [
        "1995/a.RAR",
        "1995/b.zip",
        "1996/c.zip",
    ]


def test_a_pack_is_a_set_of_stored_members(db: Connection, stores: Stores, tmp_path: Path) -> None:
    pack = make_pack(tmp_path / "1995" / "demo95.zip", MEMBERS)
    result = ingest_pack(db, stores.originals, pack)
    assert (result.path, result.new, result.members, result.error_class) == (
        "1995/demo95.zip",
        True,
        5,
        None,
    )
    assert get_original(stores.originals, result.sha256) == pack.read_bytes()
    for data in MEMBERS.values():
        assert get_original(stores.originals, sha256_hex(data)) == data
    assert rows(
        db,
        "select w.kind, w.title, v.date_min::text, v.date_max::text, v.date_basis, a.format"
        " from artifact a join version v on v.id = a.version_id join work w on w.id = v.work_id"
        " where w.kind = 'set'",
    ) == [("set", "demo95", "1995-01-01", "1995-12-31", "pack", "zip")]
    assert rows(
        db,
        "select m.position, m.path, a.format, a.charset, w.title from set_member m"
        " join artifact a on a.sha256 = m.sha256 left join version v on v.id = a.version_id"
        " left join work w on w.id = v.work_id order by m.position",
    ) == [
        (0, "HORIZON.ANS", "ansi", "cp437", "Horizon"),
        (1, "DEMO.NFO", "nfo", "cp437", None),
        (2, "TUNE.XM", "xm", None, None),
        (3, "LOGO.GR", "ansi", "cp437", "Horizon"),
        (4, "SUB/FILE_ID.DIZ", "diz", "cp437", None),
    ]
    paths = rows(db, "select source_path from artifact where format = 'nfo'")
    assert paths == [("1995/demo95.zip/DEMO.NFO",)]


def test_every_work_of_a_pack_may_be_shown_as_released(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    ingest_pack(db, stores.originals, make_pack(tmp_path / "1995" / "demo95.zip", MEMBERS))
    works = db.execute(text("select rights from work")).scalars().all()
    assert len(works) == 3  # the set and its two art files
    for raw in works:
        rights = Rights.model_validate(raw)
        assert str(rights.scene_publication.url) == "https://16colo.rs/pack/demo95/"  # type: ignore[union-attr]
        assert can_display(Shown(rights)) == "file"


def test_ingesting_a_pack_again_changes_nothing(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    pack = make_pack(tmp_path / "1995" / "demo95.zip", MEMBERS)
    ingest_pack(db, stores.originals, pack)
    before = rows(db, "select (select count(*) from artifact), (select count(*) from set_member)")
    again = ingest_pack(db, stores.originals, pack)
    assert (again.new, again.members) == (False, 0)
    assert rows(
        db, "select (select count(*) from artifact), (select count(*) from set_member)"
    ) == (before)


def test_a_file_in_two_packs_is_one_artifact(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    ingest_pack(db, stores.originals, make_pack(tmp_path / "1995" / "a.zip", MEMBERS))
    other = {"HORIZON.ANS": HORIZON, "OTHER.NFO": b"another pack\r\n"}
    ingest_pack(db, stores.originals, make_pack(tmp_path / "1996" / "b.zip", other))
    sha = sha256_hex(HORIZON)
    assert rows(db, f"select count(*) from artifact where sha256 = '{sha}'") == [(1,)]
    assert rows(db, f"select count(*) from set_member where sha256 = '{sha}'") == [(2,)]
    assert rows(db, "select count(*) from work where kind = 'single'") == [(2,)]


def test_an_archive_that_cannot_be_read_is_still_recorded(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    rar = tmp_path / "1994" / "old.rar"
    rar.parent.mkdir(parents=True)
    rar.write_bytes(b"Rar!\x1a\x07\x00 damaged")
    result = ingest_pack(db, stores.originals, rar)
    assert (result.error_class, result.members) == ("bad_archive", 0)
    assert get_original(stores.originals, result.sha256) == rar.read_bytes()
    assert rows(db, "select format, source_path from artifact") == [("rar", "1994/old.rar")]
    assert rows(db, "select count(*) from set_member") == [(0,)]
    assert rows(db, "select status, error_class from expansion") == [("error", "bad_archive")]


def test_unreadable_members_are_named_not_recorded(
    db: Connection, stores: Stores, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pack = make_pack(tmp_path / "1993" / "imploded.zip", MEMBERS)
    readable = [(name, data) for name, data in MEMBERS.items() if name != "TUNE.XM"]
    monkeypatch.setattr("tm.packs.expand", lambda _path, _format: Expanded(readable, ["TUNE.XM"]))
    result = ingest_pack(db, stores.originals, pack)
    assert (result.members, result.unreadable) == (4, ["TUNE.XM"])
    assert rows(db, "select count(*) from artifact where format = 'xm'") == [(0,)]
    assert rows(db, "select status, unreadable from expansion") == [("partial", ["TUNE.XM"])]


def test_a_pack_outside_a_year_directory_is_undated(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    result = ingest_pack(db, stores.originals, make_pack(tmp_path / "loose.zip", MEMBERS))
    assert result.path == "loose.zip"
    assert rows(db, "select distinct date_min, date_basis from version") == [(None, None)]


def test_a_later_run_adds_the_members_an_earlier_one_could_not_read(
    db: Connection, stores: Stores, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pack = make_pack(tmp_path / "1993" / "imploded.zip", MEMBERS)
    readable = [(name, data) for name, data in MEMBERS.items() if name != "TUNE.XM"]
    with monkeypatch.context() as patched:
        patched.setattr("tm.packs.expand", lambda _p, _f: Expanded(readable, ["TUNE.XM"]))
        ingest_pack(db, stores.originals, pack)
    again = ingest_pack(db, stores.originals, pack)
    assert (again.new, again.members, again.unreadable) == (False, 1, [])
    assert rows(db, "select position, path from set_member where path = 'TUNE.XM'") == [
        (2, "TUNE.XM")
    ]
    assert rows(db, "select count(*) from work where kind = 'set'") == [(1,)]
    assert rows(db, "select status, unreadable from expansion") == [("ok", [])]


def test_a_pack_first_met_inside_another_becomes_a_set(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    inner = make_pack(tmp_path / "1996" / "inner.zip", {"HORIZON.ANS": HORIZON})
    outer = make_pack(tmp_path / "1997" / "outer.zip", {"INNER.ZIP": inner.read_bytes()})
    ingest_pack(db, stores.originals, outer)
    result = ingest_pack(db, stores.originals, inner)
    assert (result.new, result.members) == (True, 1)
    assert rows(
        db,
        "select w.title, a.source_path from artifact a join version v on v.id = a.version_id"
        f" join work w on w.id = v.work_id where a.sha256 = '{result.sha256}'",
    ) == [("inner", "1997/outer.zip/INNER.ZIP")]


def test_art_signed_with_a_group_extension_is_found_by_its_content(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    files = {
        "BW-INF.MIR": b"\x1b[0;1;34m Mirage \x1b[0m\r\n\x1a",
        "LOADER.EXE": b"MZ\x00\x00\x1b[1;31mcoloured message\x00",
        "INFO.NFO": b"\x1b[1mansi nfo\x1b[0m\r\n",
    }
    ingest_pack(db, stores.originals, make_pack(tmp_path / "1992" / "mirage01.zip", files))
    assert rows(
        db,
        "select m.path, a.format, v.id is not null from set_member m"
        " join artifact a on a.sha256 = m.sha256 left join version v on v.id = a.version_id"
        " order by m.position",
    ) == [("BW-INF.MIR", "ansi", True), ("LOADER.EXE", "exe", False), ("INFO.NFO", "nfo", False)]


def test_an_entry_listed_twice_is_one_member(
    db: Connection, stores: Stores, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pack = make_pack(tmp_path / "2004" / "twice.zip", MEMBERS)
    listed_twice = [("CRO.NFO", b"nfo\r\n"), ("CRO.NFO", b"nfo\r\n")]
    monkeypatch.setattr("tm.packs.expand", lambda _p, _f: Expanded(listed_twice, []))
    result = ingest_pack(db, stores.originals, pack)
    assert result.members == 1
    assert rows(db, "select path, position from set_member") == [("CRO.NFO", 0)]
