# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""`tm lists`: the lists of a visit name only works whose files are shown (ADR 0023)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from packs_on_disk import HORIZON, ROOT, ingest
from sqlalchemy import Connection, text
from stores import Stores
from tm.decode import decode_pending
from tm.export import export_work, exportable
from tm.lists import DAYS, INDEX, Lists, collect, write_lists
from tm.render import render_pending
from tm.storage import LocalStore
from tm.text_layer import pending_text, read_artifact
from tm_render.conservation import BitmapFont

pytestmark = pytest.mark.db

FONT = BitmapFont.load(ROOT / "corpus" / "fonts" / "ibm-vga-8x16.f16")
SECOND = HORIZON.replace(b"Horizon", b"Horizn2", 1)  # another file, same pack
PACK = "lists/packs/16colo-demo95.json"


@pytest.fixture
def public(tmp_path: Path) -> LocalStore:
    return LocalStore(tmp_path / "public")


@pytest.fixture
def ready(db: Connection, stores: Stores, tmp_path: Path) -> None:
    members = {"B-HORIZON.ANS": HORIZON, "A-SECOND.ANS": SECOND}
    ingest(db, stores, tmp_path / "1995" / "demo95.zip", members)
    decode_pending(db, stores.originals, stores.derived)
    render_pending(db, stores.derived, FONT, scale=1)
    for row in pending_text(db):
        read_artifact(db, stores.derived, row)


def lists_of(db: Connection, public: LocalStore) -> dict[str, int]:
    return write_lists(collect(exportable(db)), public)


@pytest.mark.usefixtures("ready")
def test_a_pack_lists_its_shown_works_in_pack_order(db: Connection, public: LocalStore) -> None:
    lists_of(db, public)
    pack = json.loads(public.get(PACK))
    assert pack["url"] == "https://16colo.rs/pack/demo95/"
    assert [w["path"] for w in pack["works"]] == ["A-SECOND.ANS", "B-HORIZON.ANS"]
    assert json.loads(public.get(INDEX))[0].startswith("lists/")
    assert "works" in json.loads(public.get(DAYS))


@pytest.mark.usefixtures("ready")
def test_a_withdrawn_work_leaves_every_list(db: Connection, public: LocalStore) -> None:
    lists_of(db, public)
    db.execute(text("""update work set privacy = '{"withdrawn": true}' where kind = 'single'"""))
    counts = lists_of(db, public)
    assert not public.exists(PACK)
    assert counts["removed"] > 0
    assert json.loads(public.get(DAYS)) == {"works": []}


@pytest.mark.usefixtures("ready")
def test_an_unchanged_list_is_not_written_again(db: Connection, public: LocalStore) -> None:
    lists_of(db, public)
    assert lists_of(db, public)["written"] == 0


@pytest.mark.usefixtures("ready")
def test_a_refused_work_is_named_by_no_list(db: Connection, public: LocalStore) -> None:
    db.execute(
        text(
            """update work set rights = '{"permission": {"display": true}}' where kind = 'single'"""
        )
    )
    db.execute(text("update work set rights = '{}' where kind = 'set'"))  # no credit link
    assert lists_of(db, public)["lists"] == 1  # the days, empty
    assert not public.exists(PACK)


@pytest.mark.usefixtures("ready")
def test_a_shown_record_carries_its_words_and_its_lists(
    db: Connection, stores: Stores, public: LocalStore
) -> None:
    sha = hashlib.sha256(HORIZON).hexdigest()
    [row] = [r for r in exportable(db) if r.sha256 == sha]
    export_work(db, stores.derived, public, row, "https://example.org/withdraw")
    record = json.loads(public.get(f"works/{sha}/record.json"))
    assert record["schema"] == 2
    assert record["lists"]["pack"] == PACK
    assert any("orizon" in line["text"].lower() for line in record["text"])


def test_an_unsigned_undated_tall_work_is_only_in_its_pack() -> None:
    row = SimpleNamespace(
        sha256="0" * 64, source_path="x/TALL.ANS", pack_path="TALL.ANS", sauce=None, title=None,
        pack="demo95", archive="16colo", pack_url="https://16colo.rs/pack/demo95/", year=None,
        cols=80, rows=500,
    )  # fmt: skip
    lists = Lists()
    lists.add(row, "12")  # pyright: ignore[reportArgumentType]
    assert list(lists.entries) == [PACK]
    assert lists.days == []
