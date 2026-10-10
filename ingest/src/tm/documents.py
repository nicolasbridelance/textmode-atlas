# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The texts of a pack become works (ADR 0033): NFO, FILE_ID.DIZ and text files held before
ingestion made works of them.

Each such artifact with no work gets a `single` work, with the rights and dating of the pack it
was first met in (the one its source path names), or, loose, of its archive at its URL and its
SAUCE date: what `tm ingest pack` and `tm ingest files` give the art beside it. A file whose bytes
are binary stays an artifact. The original is read, never written. Run twice, the second run
changes nothing.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from sqlalchemy import Connection, Row, text

from tm.packs import DOCUMENTS, is_document
from tm.records import Dating, insert_work, parse_sauce_date
from tm.rights import Rights, ScenePublication
from tm.storage import ObjectStore, get_original

FORMATS = sorted(set(DOCUMENTS.values()))

# The pack named by the artifact's source path (`<pack path>/<member>`) comes first.
PENDING = """
select a.sha256, a.source_path, a.sauce ->> 'title' as sauce_title,
  a.sauce ->> 'date' as sauce_date, s.name as archive, s.url as archive_url,
  p.rights as pack_rights, p.date_min, p.date_max, p.date_basis
from artifact a
join source s on s.id = a.source_id
left join lateral (
  select w.rights, v.date_min, v.date_max, v.date_basis
  from set_member m
  join work w on w.id = m.set_work_id
  join version v on v.work_id = w.id
  join artifact pa on pa.version_id = v.id
  where m.sha256 = a.sha256
  order by starts_with(a.source_path, pa.source_path || '/') desc, pa.source_path
  limit 1
) p on true
where a.version_id is null and a.format = any(:formats)
order by a.source_path, a.sha256
"""


@dataclass(frozen=True)
class Promoted:
    sha256: str
    source_path: str
    work: bool


def promote_documents(conn: Connection, originals: ObjectStore) -> list[Promoted]:
    """Give every text artifact with no work its work; return what was examined."""
    rows = conn.execute(text(PENDING), {"formats": FORMATS}).all()
    return [_promote(conn, originals, row) for row in rows]


def _promote(conn: Connection, originals: ObjectStore, row: Row[Any]) -> Promoted:
    name = PurePosixPath(row.source_path).name
    if not is_document(name, get_original(originals, row.sha256)):
        return Promoted(row.sha256, row.source_path, work=False)
    version_id = insert_work(
        conn,
        "single",
        row.sauce_title or name,
        *_rights_and_dating(row),
    )
    conn.execute(
        text("update artifact set version_id = :version where sha256 = :sha256"),
        {"version": version_id, "sha256": row.sha256},
    )
    return Promoted(row.sha256, row.source_path, work=True)


def _rights_and_dating(row: Row[Any]) -> tuple[Rights, Dating]:
    if row.pack_rights is not None:
        dating = Dating(row.date_min, row.date_max, row.date_basis)
        return Rights.model_validate(row.pack_rights), dating
    publication = {"archive": row.archive, "url": row.archive_url + row.source_path}
    date = parse_sauce_date(row.sauce_date)
    return (
        Rights(scene_publication=ScenePublication.model_validate(publication)),
        Dating(date, date, "sauce" if date else None),
    )
