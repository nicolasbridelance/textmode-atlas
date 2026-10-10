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
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import Connection, text

from tm.acquisitions import Fetch, insert_acquisition
from tm.corpus import Acquisition, AcquisitionSource
from tm.packs import extension
from tm.records import (
    ArtifactRow,
    Dating,
    artifact_known,
    ensure_source,
    insert_artifact,
    insert_work,
)
from tm.rights import Rights, ScenePublication
from tm.storage import ObjectStore, put_original

USER_AGENT = "textmode-atlas/0.1 (https://github.com/nicolasbridelance/textmode-atlas)"
RECORDED_BY = "algo:tm.acquire@1"
TIMEOUT_SECONDS = 120
KEPT_HEADERS = ("Last-Modified", "ETag", "Content-Type")


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


def rights_of(entry: Acquisition) -> Rights:
    """The basis the manifest gives, as the rights the work carries."""
    if entry.basis == "scene":
        publication = {"archive": entry.source, "url": str(entry.url)}
        return Rights(scene_publication=ScenePublication.model_validate(publication))
    return Rights(license=entry.license or "public-domain")


def acquire(
    conn: Connection,
    store: ObjectStore,
    entry: Acquisition,
    source: AcquisitionSource,
    fetch: Downloader = download,
) -> Acquired:
    url = str(entry.url)
    held = conn.execute(
        text("select sha256 from acquisition where url = :url limit 1"), {"url": url}
    ).scalar()
    if held is not None:
        return Acquired(url, held.strip(), fetched=False, new_work=False)
    got = fetch(url)
    sha256, _ = put_original(store, got.data)
    source_id = ensure_source(conn, "archive", source.name, str(source.url), source.note)
    new_work = not artifact_known(conn, sha256)
    if new_work:
        path = urllib.parse.unquote(urllib.parse.urlsplit(url).path).lstrip("/")
        version_id = insert_work(conn, "single", entry.title, rights_of(entry), Dating())
        insert_artifact(
            conn,
            ArtifactRow(
                sha256=sha256,
                bytes=len(got.data),
                format=extension(path),
                charset=None,
                sauce=None,
                source_id=source_id,
                source_path=path,
                version_id=version_id,
            ),
        )
    when = got.retrieved_at.isoformat(timespec="seconds")
    fetch_row = Fetch(sha256, url, "http", when, "recorded", got.remote)
    insert_acquisition(conn, fetch_row, source_id, RECORDED_BY)
    return Acquired(url, sha256, fetched=True, new_work=new_work)
