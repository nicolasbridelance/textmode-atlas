# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Single acquisitions from the manifest `corpus/acquisitions.yaml` (ADR 0031).

Bulk sources are mirrored, then ingested (`tm ingest pack`, `tm ingest files`). The first
representative of a practice is one file, chosen by hand, from a source of any kind: a scene
archive, a museum's open collection, a licensed repository. Each comes with the basis on which
the museum holds it, so its rights are the manifest's, file by file.

An acquired file is stored write-once and becomes a `single` work whose title and rights are the
manifest's; a file the museum already holds keeps its work and first source. Every fetch is
recorded (ADR 0021). A URL already acquired is not fetched again, so running twice changes
nothing.
"""

from __future__ import annotations

import datetime as dt
import html
import re
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import Connection, text

from tm.acquisitions import Fetch, insert_acquisition
from tm.corpus import Acquisition, AcquisitionSource
from tm.packs import CHARSET as CHARSET_CP437
from tm.packs import extension
from tm.records import (
    ArtifactRow,
    Dating,
    artifact_known,
    ensure_source,
    insert_artifact,
    insert_work,
)
from tm.rights import Excerpt, Rights, ScenePublication
from tm.storage import ObjectStore, put_original, sha256_hex

USER_AGENT = "textmode-atlas/0.1 (https://github.com/nicolasbridelance/textmode-atlas)"
RECORDED_BY = "algo:tm.acquire@1"
TIMEOUT_SECONDS = 120
KEPT_HEADERS = ("Last-Modified", "ETag", "Content-Type")
TAG = re.compile(r"<[^>]*>")
NEWLINE = b"\n"
HARD_SPACE = "\N{NO-BREAK SPACE}"
CHARSET_PARAM = re.compile(r"charset=([\w-]+)", re.IGNORECASE)
CHARSET_META = re.compile(rb"charset=[\"']?([\w-]+)", re.IGNORECASE)
BLOCK_END = re.compile(r"</pre>|</p>|<br\s*/?>", re.IGNORECASE)


@dataclass(frozen=True)
class Download:
    data: bytes
    retrieved_at: dt.datetime
    remote: dict[str, str]


Downloader = Callable[[str], Download]


@dataclass(frozen=True)
class Acquired:
    url: str
    sha256: str
    fetched: bool
    new_work: bool


def download(url: str) -> Download:
    """Fetch one file politely, keeping the headers that date it."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        remote = {k: response.headers[k] for k in KEPT_HEADERS if response.headers[k]}
        return Download(response.read(), dt.datetime.now(dt.UTC), remote)


def rights_of(entry: Acquisition, taken_at: dt.date) -> Rights:
    """The basis the manifest gives, as the rights the work carries."""
    if entry.basis == "scene":
        publication = {"archive": entry.source, "url": str(entry.url)}
        return Rights(scene_publication=ScenePublication.model_validate(publication))
    if entry.basis == "excerpt":
        excerpt = Excerpt(
            taken_from=entry.url, cut=_how(entry), taken_at=taken_at, credit=entry.credit or ""
        )
        return Rights(excerpt=excerpt)
    return Rights(license=entry.license or "public-domain")


def _how(entry: Acquisition) -> str:
    return f"lines {entry.lines}" + (" of the page, tags removed" if entry.html else "")


def cut(data: bytes, entry: Acquisition, charset: str) -> bytes:
    """The lines an excerpt names: byte for byte, or, from HTML, the text without its tags; and
    from each line, when the manifest gives a pattern, only what its group matches."""
    first, last = (int(n) for n in (entry.lines or "").split("-"))
    chosen = NEWLINE.join(data.split(NEWLINE)[first - 1 : last]).rstrip()
    if not chosen.strip():
        raise ValueError(f"{entry.url}: lines {entry.lines} are empty or outside the page")
    if entry.html:
        chosen = _text_of(chosen.decode(charset, errors="replace")).encode("utf-8")
    if entry.pattern:
        chosen = NEWLINE.join(_matched(entry, line) for line in chosen.splitlines())
    return chosen.rstrip() + NEWLINE


def _text_of(page: str) -> str:
    """HTML as the reader saw it: blocks end lines, tags go, entities and hard spaces are read."""
    text = html.unescape(TAG.sub("", BLOCK_END.sub("\n", page))).replace(HARD_SPACE, " ")
    return "\n".join(line.rstrip() for line in text.splitlines())


def _matched(entry: Acquisition, line: bytes) -> bytes:
    found = re.search(entry.pattern or "", line.decode("latin-1"))
    if not found:
        raise ValueError(f"{entry.url}: a line of the cut does not match the pattern: {line!r}")
    kept = found.group(1)
    if entry.escapes:
        kept = kept.encode("latin-1").decode("unicode_escape")
    return kept.encode("latin-1")


def page_charset(remote: dict[str, str], data: bytes) -> str:
    """The page's encoding: from the HTTP header, else from the page's own meta tag."""
    found = CHARSET_PARAM.search(remote.get("Content-Type", "")) or CHARSET_META.search(data)
    if found is None:
        return "utf-8"
    name = found.group(1)
    return name if isinstance(name, str) else name.decode("ascii")


def _path(entry: Acquisition) -> str:
    """Where the file sits at its source: the URL's path and query, and the lines of an excerpt."""
    parts = urllib.parse.urlsplit(str(entry.url))
    path = urllib.parse.unquote(parts.path).lstrip("/") + (f"?{parts.query}" if parts.query else "")
    return path + (f"#lines={entry.lines}" if entry.lines else "")


def _charset_of(declared: str | None) -> str | None:
    return CHARSET_CP437 if declared in ("ansi", "ascii") else None


def _declare(conn: Connection, sha256: str, entry: Acquisition) -> None:
    """The manifest's word on the art kind of a file it acquired, when it declares one."""
    if entry.format:
        conn.execute(
            text(
                "update artifact set format = :format, charset = :charset"
                " where sha256 = :sha256 and format is distinct from :format"
            ),
            {"sha256": sha256, "format": entry.format, "charset": _charset_of(entry.format)},
        )


def acquire(
    conn: Connection,
    store: ObjectStore,
    entry: Acquisition,
    source: AcquisitionSource,
    fetch: Downloader = download,
) -> Acquired:
    url = str(entry.url)
    how = _how(entry) if entry.basis == "excerpt" else ""
    held = conn.execute(
        text(
            "select sha256 from acquisition where url = :url"
            " and coalesce(remote ->> 'cut', '') = :how limit 1"
        ),
        {"url": url, "how": how},
    ).scalar()
    if held is not None:
        _declare(conn, held.strip(), entry)
        return Acquired(url, held.strip(), fetched=False, new_work=False)
    got = fetch(url)
    remote = dict(got.remote)
    data = got.data
    if entry.basis == "excerpt":
        remote |= {"cut": how, "page_sha256": sha256_hex(got.data)}
        data = cut(got.data, entry, page_charset(got.remote, got.data))
    sha256, _ = put_original(store, data)
    source_id = ensure_source(conn, "archive", source.name, str(source.url), source.note)
    new_work = not artifact_known(conn, sha256)
    if new_work:
        path = _path(entry)
        rights = rights_of(entry, got.retrieved_at.date())
        version_id = insert_work(conn, "single", entry.title, rights, Dating())
        insert_artifact(
            conn,
            ArtifactRow(
                sha256=sha256,
                bytes=len(data),
                format=entry.format or extension(urllib.parse.urlsplit(url).path),
                charset=_charset_of(entry.format),
                sauce=None,
                source_id=source_id,
                source_path=path,
                version_id=version_id,
            ),
        )
    when = got.retrieved_at.isoformat(timespec="seconds")
    fetch_row = Fetch(sha256, url, "http", when, "recorded", remote)
    insert_acquisition(conn, fetch_row, source_id, RECORDED_BY)
    return Acquired(url, sha256, fetched=True, new_work=new_work)
