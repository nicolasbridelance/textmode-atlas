# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import datetime as dt

import pytest
from pydantic import ValidationError
from sqlalchemy import Connection, text
from stores import Stores
from tm.acquire import Download, acquire, cut, page_charset, rights_of
from tm.corpus import Acquisition, Acquisitions, AcquisitionSource
from tm.storage import sha256_hex

WHEN = dt.datetime(2026, 10, 10, 9, 0, tzinfo=dt.UTC)
COMMONS = AcquisitionSource(
    name="wikimedia-commons", url="https://commons.wikimedia.org/", note="Free media."
)
SCENE_ORG = AcquisitionSource(name="scene.org", url="https://files.scene.org/", note="Scene.")


def entry(**changes: object) -> Acquisition:
    values: dict[str, object] = {
        "practice": "jacquard",
        "title": "Woven portrait",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e1/Jacquard.jpg",
        "source": "wikimedia-commons",
        "basis": "public-domain",
        "why": {"en": "A woven image.", "fr": "Une image tissée."},
    }
    return Acquisition.model_validate(values | changes)


def lines(*rows: str) -> bytes:
    return "".join(row + "\n" for row in rows).encode()


PAGE = lines("<html><body>", "<pre>  (^_^)  &lt;hi&gt;", "  /|\\</pre>", "</body></html>")
FACE = lines("  (^_^)  <hi>", "  /|\\")
EXCERPT = Acquisition(
    practice="kaomoji",
    title="A face",
    url="https://web.archive.org/web/1999/http://example.org/faces.html",
    source="wayback",
    basis="excerpt",
    lines="2-3",
    html=True,
    credit="unknown",
    why={"en": "A face.", "fr": "Un visage."},
)


class Downloads:
    """A stand-in for the network: serves fixed bytes and counts requests."""

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.requests: list[str] = []

    def __call__(self, url: str) -> Download:
        self.requests.append(url)
        return Download(self.data, WHEN, {"ETag": '"abc"'})


def test_a_licensed_file_must_name_its_licence() -> None:
    with pytest.raises(ValidationError, match="names its licence"):
        entry(basis="license")


def test_only_a_scene_archive_can_hold_on_the_scene_basis() -> None:
    with pytest.raises(ValidationError, match="not a scene archive"):
        entry(basis="scene")


def test_a_manifest_names_its_sources_and_each_url_once() -> None:
    with pytest.raises(ValidationError, match="unknown sources: wikimedia-commons"):
        Acquisitions(version=1, sources=[SCENE_ORG], entries=[entry()])
    with pytest.raises(ValidationError, match="each file is acquired once"):
        Acquisitions(version=1, sources=[COMMONS], entries=[entry(), entry(title="Again")])


def test_rights_follow_the_basis() -> None:
    scene = entry(source="scene.org", basis="scene", url="https://files.scene.org/get/a.zip")
    day = WHEN.date()
    assert rights_of(scene, day).scene_publication is not None
    assert rights_of(entry(), day).license == "public-domain"
    assert rights_of(entry(basis="license", license="CC0-1.0"), day).license == "CC0-1.0"
    excerpt = rights_of(EXCERPT, day).excerpt
    assert excerpt is not None
    assert (excerpt.cut, excerpt.credit) == ("lines 2-3 of the page, tags removed", "unknown")


def test_an_excerpt_names_its_lines_and_its_credit() -> None:
    with pytest.raises(ValidationError, match="names lines and credit"):
        entry(basis="excerpt")
    with pytest.raises(ValidationError, match="names lines and credit"):
        entry(lines="1-2", credit="x")


def test_the_cut_keeps_the_lines_and_drops_the_tags() -> None:
    assert cut(PAGE, EXCERPT, "utf-8") == FACE
    raw = EXCERPT.model_copy(update={"html": False})
    assert cut(PAGE, raw, "utf-8") == lines("<pre>  (^_^)  &lt;hi&gt;", "  /|\\</pre>")
    with pytest.raises(ValueError, match="outside the page"):
        cut(PAGE, EXCERPT.model_copy(update={"lines": "40-41"}), "utf-8")


def test_html_blocks_end_lines_and_hard_spaces_are_spaces() -> None:
    word = lines("<pre>19-Sep-82\xa0\xa0 Fahlman</pre><pre>:-)</pre>")
    one = EXCERPT.model_copy(update={"lines": "1-1"})
    assert cut(word.replace(b"\xc2", b""), one, "cp1252") == lines("19-Sep-82   Fahlman", ":-)")


def test_a_pattern_keeps_only_the_drawing() -> None:
    forth = lines('\ts"   ,  ,"   logo+', '\ts"  (o o)\\"  logo+')
    beastie = EXCERPT.model_copy(
        update={"html": False, "lines": "1-2", "pattern": r's"(.*)"\s+logo\+'}
    )
    assert cut(forth, beastie, "utf-8") == lines("   ,  ,", "  (o o)\\")
    with pytest.raises(ValueError, match="does not match"):
        cut(lines("no drawing here"), beastie.model_copy(update={"lines": "1-1"}), "utf-8")


def test_a_pattern_keeps_one_group() -> None:
    with pytest.raises(ValidationError, match="one group"):
        EXCERPT.model_validate(EXCERPT.model_dump() | {"pattern": "(a)(b)"})


def test_the_page_names_its_encoding_when_the_server_does_not() -> None:
    page = b'<meta http-equiv=Content-Type content="text/html; charset=windows-1252">'
    assert page_charset({}, page) == "windows-1252"
    assert page_charset({"Content-Type": "text/html; charset=ISO-8859-1"}, page) == "ISO-8859-1"
    assert page_charset({}, b"<html>") == "utf-8"


@pytest.mark.db
def test_an_acquisition_is_a_work_with_its_provenance(db: Connection, stores: Stores) -> None:
    downloads = Downloads(b"woven")
    got = acquire(db, stores.originals, entry(), COMMONS, downloads)
    assert (got.sha256, got.fetched, got.new_work) == (sha256_hex(b"woven"), True, True)
    row = db.execute(
        text(
            "select w.title, w.rights->>'license', a.source_path, a.format, q.retrieved_basis,"
            " q.remote->>'ETag', q.recorded_by from artifact a"
            " join version v on v.id = a.version_id join work w on w.id = v.work_id"
            " join acquisition q on q.sha256 = a.sha256"
            " where a.sha256 = :s"
        ),
        {"s": got.sha256},
    ).one()
    assert tuple(row) == (
        "Woven portrait",
        "public-domain",
        "wikipedia/commons/e/e1/Jacquard.jpg",
        "jpg",
        "recorded",
        '"abc"',
        "algo:tm.acquire@1",
    )


@pytest.mark.db
def test_acquiring_twice_fetches_once(db: Connection, stores: Stores) -> None:
    downloads = Downloads(b"woven")
    acquire(db, stores.originals, entry(), COMMONS, downloads)
    again = acquire(db, stores.originals, entry(), COMMONS, downloads)
    assert (again.fetched, again.new_work, len(downloads.requests)) == (False, False, 1)


@pytest.mark.db
def test_a_file_already_held_keeps_its_work(db: Connection, stores: Stores) -> None:
    acquire(db, stores.originals, entry(), COMMONS, Downloads(b"same bytes"))
    other = entry(url="https://upload.wikimedia.org/wikipedia/commons/x/copy.jpg")
    got = acquire(db, stores.originals, other, COMMONS, Downloads(b"same bytes"))
    assert (got.fetched, got.new_work) == (True, False)
    works = db.execute(text("select count(*) from work where title = 'Woven portrait'")).scalar()
    fetches = db.execute(
        text("select count(*) from acquisition where sha256 = :s"), {"s": got.sha256}
    ).scalar()
    assert (works, fetches) == (1, 2)


WAYBACK = AcquisitionSource(name="wayback", url="https://web.archive.org/", note="Captures.")


@pytest.mark.db
def test_an_excerpt_stores_only_the_cut_and_says_where_from(db: Connection, stores: Stores) -> None:
    got = acquire(db, stores.originals, EXCERPT, WAYBACK, Downloads(PAGE))
    assert got.sha256 == sha256_hex(FACE)
    row = db.execute(
        text(
            "select a.source_path, w.rights -> 'excerpt' ->> 'credit', q.remote ->> 'page_sha256'"
            " from artifact a join version v on v.id = a.version_id"
            " join work w on w.id = v.work_id join acquisition q on q.sha256 = a.sha256"
            " where a.sha256 = :s"
        ),
        {"s": got.sha256},
    ).one()
    path = "web/1999/http://example.org/faces.html#lines=2-3"
    assert tuple(row) == (path, "unknown", sha256_hex(PAGE))
    other = EXCERPT.model_copy(update={"lines": "3-3"})
    second = acquire(db, stores.originals, other, WAYBACK, Downloads(PAGE))
    assert second.fetched


@pytest.mark.db
def test_the_manifest_declares_the_art_kind_of_a_file_it_acquired(
    db: Connection, stores: Stores
) -> None:
    poster = entry(url="https://www.textfiles.com/art/DECUS/bach.txt", title="Bach")
    got = acquire(db, stores.originals, poster, COMMONS, Downloads(b"  ##  \n"))
    declared = poster.model_copy(update={"format": "ascii"})
    acquire(db, stores.originals, declared, COMMONS, Downloads(b"never fetched"))
    row = db.execute(
        text("select format, charset from artifact where sha256 = :s"), {"s": got.sha256}
    ).one()
    assert tuple(row) == ("ascii", "cp437")
