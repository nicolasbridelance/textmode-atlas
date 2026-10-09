# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""`tm export`: only what may be shown reaches the public bucket (ADR 0022)."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

import pytest
from packs_on_disk import HORIZON, ROOT, ingest
from PIL import Image
from sqlalchemy import Connection, text
from stores import Stores
from tm.decode import decode_pending
from tm.export import ExportError, export_work, exportable
from tm.render import render_pending
from tm.storage import LocalStore, rendering_key
from tm_render.compact import decode
from tm_render.conservation import BitmapFont

pytestmark = pytest.mark.db

FONT = BitmapFont.load(ROOT / "corpus" / "fonts" / "ibm-vga-8x16.f16")
WITHDRAW = "https://example.org/withdraw"
SHA = hashlib.sha256(HORIZON).hexdigest()
PREFIX = f"works/{SHA}/"


@pytest.fixture
def public(tmp_path: Path) -> LocalStore:
    return LocalStore(tmp_path / "public")


@pytest.fixture
def ready(db: Connection, stores: Stores, tmp_path: Path) -> None:
    ingest(db, stores, tmp_path / "1995" / "demo95.zip", {"HORIZON.ANS": HORIZON})
    decode_pending(db, stores.originals, stores.derived)
    render_pending(db, stores.derived, FONT, scale=1)


def export(db: Connection, stores: Stores, public: LocalStore) -> str:
    [row] = exportable(db)
    return export_work(db, stores.derived, public, row, WITHDRAW)


def rate(db: Connection, descriptor: str, level: str) -> None:
    db.execute(
        text(
            "insert into content_rating (sha256, descriptor, kind, level, grid_version, nature,"
            " asserted_by) values (:s, :d, 'descriptor', :l, 2, 'reviewed', 'human:reviewer')"
        ),
        {"s": SHA, "d": descriptor, "l": level},
    )


@pytest.mark.usefixtures("ready")
def test_a_shown_work_carries_its_credit_and_provenance(
    db: Connection, stores: Stores, public: LocalStore
) -> None:
    db.execute(
        text(
            "insert into acquisition (sha256, source_id, url, method, retrieved_at,"
            " retrieved_basis, recorded_by) select a.sha256, a.source_id,"
            " 'rsync://16colo.rs/archive-pack/1995/demo95.zip', 'rsync',"
            " '2026-10-08T11:48:20Z', 'mirror_run', 'algo:test' from artifact a"
            " where a.source_path = '1995/demo95.zip'"
        )
    )
    assert export(db, stores, public) == "files"
    record = json.loads(public.get(PREFIX + "record.json"))
    assert record["credit"]["url"] == "https://16colo.rs/pack/demo95/"
    assert record["audience"] == {
        "level": "12", "descriptors": [], "notices": [], "reviewed": False,
    }  # fmt: skip
    assert record["withdraw"] == WITHDRAW
    [fetched] = record["provenance"]
    assert (fetched["path_in_archive"], fetched["retrieved_at"]) == (
        "HORIZON.ANS",
        "2026-10-08T11:48:20+00:00",
    )
    grid, _ = decode(public.get(PREFIX + "grid.tmg"))
    assert grid.digest() == db.execute(text("select grid_sha256 from decoding")).scalar()
    shown = public.get(PREFIX + "conservation.png")
    stored = stores.derived.get(rendering_key(exportable(db)[0].rendering_sha256))
    assert Image.open(io.BytesIO(shown)).tobytes() == Image.open(io.BytesIO(stored)).tobytes()
    text_chunks = Image.open(io.BytesIO(shown)).text  # pyright: ignore[reportAttributeAccessIssue]
    assert text_chunks["Source"] == "https://16colo.rs/pack/demo95/"
    assert WITHDRAW in text_chunks["Copyright"]
    assert (
        record["files"]["grid.tmg"] == hashlib.sha256(public.get(PREFIX + "grid.tmg")).hexdigest()
    )


@pytest.mark.usefixtures("ready")
def test_a_withdrawn_work_never_reaches_the_public_bucket(
    db: Connection, stores: Stores, public: LocalStore
) -> None:
    export(db, stores, public)
    db.execute(text("""update work set privacy = '{"withdrawn": true}' where kind = 'single'"""))
    assert export(db, stores, public) == "nothing"
    for name in ("record.json", "grid.tmg", "conservation.png"):
        assert not public.exists(PREFIX + name)


@pytest.mark.usefixtures("ready")
def test_adults_only_is_a_record_and_withheld_is_nothing(
    db: Connection, stores: Stores, public: LocalStore
) -> None:
    export(db, stores, public)
    rate(db, "violence", "18")
    assert export(db, stores, public) == "record"
    assert public.exists(PREFIX + "record.json")
    assert not public.exists(PREFIX + "conservation.png")
    rate(db, "sexual", "withheld")
    assert export(db, stores, public) == "nothing"
    assert not public.exists(PREFIX + "record.json")


@pytest.mark.usefixtures("ready")
def test_no_file_is_shown_without_a_credit_link(
    db: Connection, stores: Stores, public: LocalStore
) -> None:
    db.execute(
        text(
            """update work set rights = '{"permission": {"display": true}}'"""
            " where kind = 'single'"
        )
    )
    db.execute(text("update work set rights = '{}' where kind = 'set'"))
    with pytest.raises(ExportError, match="credit"):
        export(db, stores, public)


@pytest.mark.usefixtures("ready")
def test_an_unchanged_work_is_not_written_again(
    db: Connection, stores: Stores, public: LocalStore
) -> None:
    export(db, stores, public)
    png = Path(public._path(PREFIX + "conservation.png"))  # pyright: ignore[reportPrivateUsage]
    before = png.stat().st_mtime_ns
    export(db, stores, public)
    assert png.stat().st_mtime_ns == before


def test_no_file_is_shown_without_a_rendering_of_the_acquired_file(
    db: Connection, stores: Stores, public: LocalStore, tmp_path: Path
) -> None:
    ingest(db, stores, tmp_path / "1995" / "demo95.zip", {"HORIZON.ANS": HORIZON})
    decode_pending(db, stores.originals, stores.derived)
    with pytest.raises(ExportError, match="rendering"):
        export(db, stores, public)
