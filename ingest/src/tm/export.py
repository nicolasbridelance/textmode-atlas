# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""`tm export`: what may be shown goes to the public bucket, and nothing else (ADR 0022).

For each decoded art file, one decision, from `can_display()` (rights) and `audience()` (the
audience grid), both applied here and never by the site:

- nothing: withdrawn, or `withheld`. Whatever an earlier export published is deleted;
- the record alone: display allowed for metadata only, or level 18 while no age check exists;
- the record, the compact grid and the conservation PNG: everything else.

Every object lives under `works/<sha256>/`, so an export can delete what it may no longer show
without listing the bucket. A file is never shown without a credit that links to its archive
(ADR 0009), and only renderings of acquired artifacts are exported (invariant 9). The record and
the PNG carry the provenance of the file (ADR 0021); the PNG keeps its pixels.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import struct
import zlib
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

from sqlalchemy import Connection, Row, text
from tm_analysis.versions import TEXT_VERSION
from tm_render.compact import encode
from tm_render.versions import DECODER_VERSION, RENDERER_VERSION

from tm.audience import Rated, audience
from tm.decode import DECODER
from tm.grids import stored_grid
from tm.rights import Privacy, Rights, can_display
from tm.shards import EVERYTHING, Shard, condition
from tm.storage import ObjectStore, rendering_key

RECORD_SCHEMA = 2  # 2: the work's words and its lists (ADR 0023)
NOT_YET_SHOWN = ("18",)  # no age check yet (ADR 0019): record only
FILES = ("record.json", "grid.tmg", "conservation.png")
Outcome = Literal["files", "record", "nothing"]

WORKS = """
select a.sha256, a.source_path, a.format, a.sauce, w.title, w.rights, w.privacy,
  coalesce(w.rights -> 'scene_publication' ->> 'url', w.rights -> 'excerpt' ->> 'taken_from',
    case when w.rights ? 'license' then (select q.url from acquisition q
      where q.sha256 = a.sha256 order by q.retrieved_at nulls last limit 1) end) as own_url,
  w.rights ->> 'license' as license, w.rights -> 'excerpt' ->> 'credit' as excerpt_credit,
  d.grid_sha256, d.cols, d.rows, d.sauce_problems,
  wa.level, wa.descriptors, wa.notices, wa.reviewed,
  r.output_sha256 as rendering_sha256,
  p.archive, p.pack, p.pack_url, p.year, p.pack_path, t.line_rows, t.lines
from decoding d
join artifact a on a.sha256 = d.sha256
join version v on v.id = a.version_id
join work w on w.id = v.work_id and w.kind = 'single'
left join work_audience wa on wa.sha256 = a.sha256
left join lateral (
  select output_sha256 from representation r
  where r.sha256 = a.sha256 and r.level = 'conservation'
    and r.recipe ->> 'renderer_version' = :renderer_version
    and r.recipe ->> 'grid_sha256' = d.grid_sha256 and (r.recipe ->> 'scale')::int = 1
  order by r.created_at desc, r.output_sha256 limit 1
) r on true
left join lateral (
  select s.name as archive, sw.title as pack,
    sw.rights -> 'scene_publication' ->> 'url' as pack_url,
    extract(year from sv.date_min)::int as year, m.path as pack_path
  from set_member m
  join work sw on sw.id = m.set_work_id
  join version sv on sv.work_id = sw.id
  join artifact pa on pa.version_id = sv.id
  join source s on s.id = pa.source_id and s.kind = 'archive'
  where m.sha256 = a.sha256
  order by sv.date_min nulls last, s.name, m.path
  limit 1
) p on true
left join text_layer t on t.sha256 = a.sha256 and t.extractor_version = :text_version
  and t.grid_sha256 = d.grid_sha256
where d.status = 'ok' and d.decoder = :decoder and d.decoder_version = :decoder_version
"""
PROVENANCE = """
select source, url, method, retrieved_at, retrieved_basis, remote, via_archive, path_in_archive
from artifact_provenance where sha256 = :sha256
order by retrieved_at nulls last, source, url
"""


class ExportError(Exception):
    """A work the rules would show but that lacks what showing requires."""


@dataclass(frozen=True)
class Shown:
    rights: Rights
    privacy: Privacy


def decide(row: Row[Any]) -> tuple[Outcome, str]:
    """What may be published of a work, and its audience level."""
    display = can_display(
        Shown(Rights.model_validate(row.rights), Privacy.model_validate(row.privacy))
    )
    rated = None if row.level is None else Rated(row.level, bool(row.reviewed))
    level = audience(rated)
    if display == "none" or level == "withheld":
        return "nothing", level
    if display == "metadata" or level in NOT_YET_SHOWN:
        return "record", level
    if not credit_url(row):
        raise ExportError(f"{row.sha256}: no credit link to its source (ADR 0009, 0032)")
    if not row.rendering_sha256:
        raise ExportError(f"{row.sha256}: no conservation rendering of the acquired file")
    return "files", level


def exportable(conn: Connection, shard: Shard = EVERYTHING) -> Sequence[Row[Any]]:
    params = {
        "decoder": DECODER,
        "decoder_version": DECODER_VERSION,
        "renderer_version": RENDERER_VERSION,
        "text_version": TEXT_VERSION,
        **shard.params(),
    }
    sql = WORKS + condition("a.sha256") + " order by a.sha256"
    return conn.execute(text(sql), params).all()


def export_work(
    conn: Connection,
    derived: ObjectStore,
    public: ObjectStore,
    row: Row[Any],
    withdraw_url: str,
) -> Outcome:
    outcome, level = decide(row)
    prefix = f"works/{row.sha256}/"
    if outcome == "nothing":
        for name in FILES:
            public.delete(prefix + name)
        return outcome
    found = conn.execute(text(PROVENANCE), {"sha256": row.sha256}).mappings()
    provenance = [dict(p) for p in found]
    files: dict[str, bytes] = {}
    if outcome == "files":
        grid = stored_grid(derived, row.sha256, row.grid_sha256)
        files["grid.tmg"] = encode(grid, ice=_ice(row))
        png = derived.get(rendering_key(row.rendering_sha256))
        files["conservation.png"] = with_text(png, _png_text(row, provenance, withdraw_url))
    else:
        for name in FILES[1:]:
            public.delete(prefix + name)
    record = _record(
        row,
        level=level,
        outcome=outcome,
        provenance=provenance,
        files=files,
        withdraw_url=withdraw_url,
    )
    files["record.json"] = _json(record)
    current = prefix + "record.json"
    if public.exists(current) and public.get(current) == files["record.json"]:
        return outcome  # the record names the hash of every file: nothing changed
    for name, data in files.items():
        public.put(prefix + name, data, CONTENT_TYPES[name])
    return outcome


def _json(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, default=_iso) + "\n").encode()


def _iso(value: object) -> str:
    """Times in ISO 8601 (`2026-10-08T11:48:20+00:00`), anything else as text."""
    return value.isoformat() if isinstance(value, dt.datetime) else str(value)


CONTENT_TYPES = {
    "record.json": "application/json",
    "grid.tmg": "application/octet-stream",
    "conservation.png": "image/png",
}


def _sauce(row: Row[Any]) -> dict[str, Any]:
    sauce: dict[str, Any] = row.sauce or {}
    return sauce


def _ice(row: Row[Any]) -> bool:
    flags = int(_sauce(row).get("flags") or 0)
    return bool(flags & 1) and not row.sauce_problems


def credit_of(row: Row[Any]) -> dict[str, Any]:
    """Title and signature as the file carries them: a handle, never a civil name."""
    sauce = _sauce(row)
    return {
        "title": sauce.get("title") or row.title,
        "author": sauce.get("author") or None,
        "group": sauce.get("group") or None,
    }


def credit_url(row: Row[Any]) -> str | None:
    """The link a shown file credits: its pack at the archive, else its own place at its source:
    where the scene released it, the page the museum cut it from, or where its licence was."""
    return row.pack_url or row.own_url


def _credit(row: Row[Any]) -> dict[str, Any]:
    signed = credit_of(row)
    return {
        "author": signed["author"] or row.excerpt_credit,
        "group": signed["group"],
        "pack": row.pack,
        "archive": row.archive,
        "url": credit_url(row),
        "license": row.license,
    }


def _record(
    row: Row[Any],
    *,
    level: str,
    outcome: Outcome,
    provenance: list[dict[str, Any]],
    files: dict[str, bytes],
    withdraw_url: str,
) -> dict[str, Any]:
    return {
        "schema": RECORD_SCHEMA,
        "sha256": row.sha256,
        "title": credit_of(row)["title"],
        "file": row.source_path.rsplit("/", 1)[-1],
        "year": row.year,
        "format": row.format,
        "credit": _credit(row),
        "audience": {
            "level": level,
            "descriptors": row.descriptors or [],
            "notices": row.notices or [],
            "reviewed": bool(row.reviewed),
        },
        "shown": outcome,
        "grid": {"cols": row.cols, "rows": row.rows, "ice": _ice(row)},
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())},
        "provenance": provenance,
        "withdraw": withdraw_url,
        "text": _text(row) if outcome == "files" else [],
        "lists": list_paths(row) if outcome == "files" else None,
    }


def _text(row: Row[Any]) -> list[dict[str, Any]]:
    """The words of the work, as the text layer read them (ADR 0023)."""
    return [
        {"row": r, "text": line}
        for r, line in zip(row.line_rows or [], row.lines or [], strict=True)
    ]


def slug(value: str) -> str:
    """A list key: lower case letters and digits, other runs as one hyphen."""
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def list_paths(row: Row[Any]) -> dict[str, str | None]:
    """Where the lists of a shown work live in the public bucket (ADR 0023)."""
    author = slug(_credit(row)["author"] or "")
    return {
        "pack": f"lists/packs/{slug(row.archive)}-{slug(row.pack)}.json" if row.pack else None,
        "author": f"lists/authors/{author}.json" if author else None,
        "year": f"lists/years/{row.year}.json" if row.year else None,
    }


def _png_text(row: Row[Any], provenance: list[dict[str, Any]], withdraw_url: str) -> dict[str, str]:
    credit = _credit(row)
    signed = " / ".join(x for x in (credit["author"], credit["group"]) if x) or "unsigned"
    return {
        "Title": credit_of(row)["title"] or "",
        "Author": signed,
        "Source": credit["url"],
        "Copyright": "The artist's. Shown as released by the scene (ADR 0009); withdraw: "
        + withdraw_url,
        "Comment": json.dumps({"sha256": row.sha256, "provenance": provenance}, default=_iso),
    }


def with_text(png: bytes, entries: dict[str, str]) -> bytes:
    """The PNG with international text chunks added before IEND: its pixels do not change."""
    end = png.rindex(b"IEND") - 4  # the IEND chunk starts with its length
    chunks = b"".join(_itxt(key, value) for key, value in entries.items())
    return png[:end] + chunks + png[end:]


def _itxt(key: str, value: str) -> bytes:
    body = key.encode("latin-1") + b"\x00\x00\x00\x00\x00" + value.encode("utf-8")
    kind = b"iTXt"
    crc = zlib.crc32(kind + body) & 0xFFFFFFFF
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", crc)
