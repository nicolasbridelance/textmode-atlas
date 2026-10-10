# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

import pytest
from sqlalchemy import Connection, text
from stores import Stores
from tm.loose import ingest_loose, loose_files
from tm.packs import TEXTFILES, ingest_pack
from tm.storage import sha256_hex

HORIZON = (Path(__file__).resolve().parents[2] / "tests/golden/ansi/horizon.ans").read_bytes()
TEST_BELOW = 52

pytestmark = pytest.mark.db


def write(root: Path, path: str, data: bytes) -> Path:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target


def ingest_tree(db: Connection, stores: Stores, root: Path, tree: str, declared: str | None = None):
    return [
        ingest_loose(
            db, stores.originals, path, site_root=root, source=TEXTFILES, declared=declared
        )
        for path in loose_files([root / tree])
    ]


def rows(db: Connection, sql: str) -> list[tuple[object, ...]]:
    return [tuple(row) for row in db.execute(text(sql)).all()]


def expected_split(directory: str) -> str:
    first = hashlib.sha256(f"textfiles:{directory}".encode()).digest()[0]
    return "test" if first < TEST_BELOW else "train"


def test_loose_files_leave_out_packs_and_the_site_index(tmp_path: Path) -> None:
    for name in ("ansi/bbs/a.ans", "ansi/bbs/.descs", "ansi/bbs/p.zip", "ansi/b.txt"):
        write(tmp_path, name, b"x")
    found = loose_files([tmp_path / "ansi"])
    assert [p.relative_to(tmp_path).as_posix() for p in found] == ["ansi/b.txt", "ansi/bbs/a.ans"]


def test_loose_art_and_texts_are_works_released_at_their_url(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    write(tmp_path, "ansi/bbs/WELCOME.ANS", HORIZON)
    write(tmp_path, "ansi/information/history.txt", b"how ansi began\r\n")
    ingested = ingest_tree(db, stores, tmp_path, "ansi")
    assert [(i.path, i.format, i.work) for i in ingested] == [
        ("ansi/bbs/WELCOME.ANS", "ansi", True),
        ("ansi/information/history.txt", "text", True),
    ]
    found = rows(
        db,
        "select a.source_path, a.format, s.name, w.kind, w.rights -> 'scene_publication' ->> 'url'"
        " from artifact a join source s on s.id = a.source_id"
        " left join version v on v.id = a.version_id left join work w on w.id = v.work_id"
        " order by 1",
    )
    url = "http://artscene.textfiles.com/ansi/bbs/WELCOME.ANS"
    history = "http://artscene.textfiles.com/ansi/information/history.txt"
    assert found == [
        ("ansi/bbs/WELCOME.ANS", "ansi", "textfiles", "single", url),
        ("ansi/information/history.txt", "text", "textfiles", "single", history),
    ]


def test_text_files_take_the_kind_the_archive_declares(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    write(tmp_path, "rtty/COLLECTION/SNOOPY", b"   ___\r\n  (o o)\r\n")
    write(tmp_path, "rtty/COLLECTION/scan.gif", b"GIF89a\x01\x00\x01\x00")
    ingested = ingest_tree(db, stores, tmp_path, "rtty", declared="rtty")
    assert [(i.path, i.format) for i in ingested] == [
        ("rtty/COLLECTION/SNOOPY", "rtty"),
        ("rtty/COLLECTION/scan.gif", None),
    ]


def test_ingesting_again_changes_nothing_and_a_held_file_keeps_its_source(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    pack = tmp_path / "16colo" / "1995" / "a.zip"
    pack.parent.mkdir(parents=True)
    with zipfile.ZipFile(pack, "w") as archive:
        archive.writestr("HORIZON.ANS", HORIZON)
    ingest_pack(db, stores.originals, pack)
    site = tmp_path / "site"
    write(site, "ansi/artwork/horizon.ans", HORIZON)
    write(site, "ansi/artwork/other.ans", HORIZON + b" ")
    first = ingest_tree(db, stores, site, "ansi")
    again = ingest_tree(db, stores, site, "ansi")
    assert [i.new for i in first] == [False, True]
    assert [i.new for i in again] == [False, False]
    held = rows(db, f"select source_path from artifact where sha256 = '{sha256_hex(HORIZON)}'")
    assert held == [("1995/a.zip/HORIZON.ANS",)]


def test_loose_files_are_split_by_their_directory(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    for name in ("asciiart/A/one.txt", "asciiart/A/two.txt", "asciiart/B/three.txt"):
        write(tmp_path, name, f"{name}\r\n".encode())
    ingested = ingest_tree(db, stores, tmp_path, "asciiart", declared="ascii")
    found = dict(
        rows(db, "select sha256, split || ' ' || packs || ' ' || archives[1] from work_split")
    )
    assert {i.path: found[i.sha256] for i in ingested} == {
        "asciiart/A/one.txt": f"{expected_split('asciiart/A')} 0 textfiles",
        "asciiart/A/two.txt": f"{expected_split('asciiart/A')} 0 textfiles",
        "asciiart/B/three.txt": f"{expected_split('asciiart/B')} 0 textfiles",
    }


def test_a_pack_in_a_site_tree_keeps_its_path_on_the_site(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    pack = tmp_path / "ascii" / "123" / "1231.zip"
    pack.parent.mkdir(parents=True)
    with zipfile.ZipFile(pack, "w") as archive:
        archive.writestr("LOGO.ASC", b"  _ _\r\n | | |\r\n")
    ingest_pack(db, stores.originals, pack, TEXTFILES, site_root=tmp_path)
    found = rows(
        db,
        "select a.source_path, w.rights -> 'scene_publication' ->> 'url' from artifact a"
        " join version v on v.id = a.version_id join work w on w.id = v.work_id order by 1",
    )
    url = "http://artscene.textfiles.com/ascii/123/1231.zip"
    assert found == [("ascii/123/1231.zip", url), ("ascii/123/1231.zip/LOGO.ASC", url)]


def test_the_declared_kind_comes_before_the_guess_by_escape_sequences(
    db: Connection, stores: Stores, tmp_path: Path
) -> None:
    write(tmp_path, "vt100/bambi.vt", b"\x1b[2J\x1b[1;1HBambi\x1b#6")
    write(tmp_path, "vt100/zorro.ans", b"\x1b[1;31mZ")
    ingested = ingest_tree(db, stores, tmp_path, "vt100", declared="vt100")
    assert [(i.path, i.format) for i in ingested] == [
        ("vt100/bambi.vt", "vt100"),
        ("vt100/zorro.ans", "ansi"),  # the file's own extension still comes first
    ]
