# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from sqlalchemy import Connection, text
from stores import Stores
from tm import loose, packs
from tm.documents import promote_documents
from tm.loose import ingest_loose
from tm.packs import TEXTFILES, ingest_pack
from tm.storage import original_key, sha256_hex

pytestmark = pytest.mark.db

NFO = b"\xdc\xdc demo pack \xdc\xdc\r\n"
WORK = (
    "select a.source_path, w.kind, w.title, v.date_min::text, v.date_basis,"
    " w.rights -> 'scene_publication' ->> 'url' from artifact a"
    " join version v on v.id = a.version_id join work w on w.id = v.work_id"
    " where a.format in ('nfo', 'diz', 'text') order by 1"
)


def held_before_adr_0033(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ingest as before ADR 0033: texts are artifacts only."""
    monkeypatch.setattr(packs, "is_document", lambda _name, _data: False)
    monkeypatch.setattr(loose, "is_document", lambda _name, _data: False)


def rows(db: Connection, sql: str) -> list[tuple[object, ...]]:
    return [tuple(row) for row in db.execute(text(sql)).all()]


def test_texts_held_before_become_works_with_their_pack_rights(
    db: Connection, stores: Stores, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pack = tmp_path / "1995" / "demo95.zip"
    pack.parent.mkdir()
    with zipfile.ZipFile(pack, "w") as archive:
        archive.writestr("DEMO.NFO", NFO)
        archive.writestr("SETUP.TXT", b"MZ\x00\x00program")
    with monkeypatch.context() as patch:
        held_before_adr_0033(patch)
        ingest_pack(db, stores.originals, pack)
    assert rows(db, WORK) == []
    promoted = promote_documents(db, stores.originals)
    assert [(p.source_path, p.work) for p in promoted] == [
        ("1995/demo95.zip/DEMO.NFO", True),
        ("1995/demo95.zip/SETUP.TXT", False),
    ]
    url = "https://16colo.rs/pack/demo95/"
    assert rows(db, WORK) == [
        ("1995/demo95.zip/DEMO.NFO", "single", "DEMO.NFO", "1995-01-01", "pack", url)
    ]
    assert [p.work for p in promote_documents(db, stores.originals)] == [False]


def test_a_loose_text_held_before_is_released_at_its_url(
    db: Connection, stores: Stores, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "ansi" / "information" / "history.txt"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"how ansi began\r\n")
    with monkeypatch.context() as patch:
        held_before_adr_0033(patch)
        ingest_loose(db, stores.originals, path, site_root=tmp_path, source=TEXTFILES)
    promote_documents(db, stores.originals)
    url = "http://artscene.textfiles.com/ansi/information/history.txt"
    assert rows(db, WORK) == [
        ("ansi/information/history.txt", "single", "history.txt", None, None, url)
    ]


def test_a_text_whose_original_is_not_stored_waits(
    db: Connection, stores: Stores, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "ansi" / "info.nfo"
    path.parent.mkdir(parents=True)
    path.write_bytes(NFO)
    with monkeypatch.context() as patch:
        held_before_adr_0033(patch)
        ingest_loose(db, stores.originals, path, site_root=tmp_path, source=TEXTFILES)
    stores.originals.delete(original_key(sha256_hex(NFO)))
    assert [(p.work, p.held) for p in promote_documents(db, stores.originals)] == [(False, False)]
    assert rows(db, WORK) == []
