# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Inferred content ratings (ADR 0020): a first pass for the reviewers, never a judgement.

Two programs write `content_rating` rows with `nature = 'inferred'`:

- `algo:keywords@<version>` reads the words of each art file (text layer, file name, SAUCE
  title) and infers descriptors at the level its rules give (`tm_analysis.ratings`);
- `algo:stream@<version>` infers the `flashing` notice from the decoding: cells with the blink
  bit outside iCE, or a work that redraws a third of its cells or more (an animation).

A run adds only what is missing for its version, so it can be run again after new ingestion.
Rows of an earlier keyword version are superseded, never erased: by the new row for the same
descriptor, or by a row saying the new version no longer finds it (`present` false).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from sqlalchemy import Connection, text
from tm_analysis.ratings import infer
from tm_analysis.versions import FEATURES_VERSION, RATING_VERSION, TEXT_VERSION
from tm_render.versions import DECODER_VERSION

GRID_VERSION = 2  # corpus/ratings/grid.yaml
KEYWORDS = f"algo:keywords@{RATING_VERSION}"
STREAM = "algo:stream@1"  # its rule is the FLASHING query below
REDRAWN = 0.3  # share of writes on an already written cell: an animation (works note)

WORDS = """
select a.sha256, a.source_path, a.sauce ->> 'title' as title, t.lines
from artifact a
join version v on v.id = a.version_id
join work w on w.id = v.work_id and w.kind = 'single'
left join text_layer t on t.sha256 = a.sha256 and t.extractor_version = :text_version
where not exists (
  select 1 from content_rating r where r.sha256 = a.sha256 and r.asserted_by = :algo
)
"""
FLASHING = """
select d.sha256
from decoding d
join artifact a on a.sha256 = d.sha256
left join features f on f.sha256 = d.sha256 and f.extractor_version = :features_version
  and f.grid_sha256 = d.grid_sha256
where d.decoder_version = :decoder_version and d.status = 'ok'
  and (
    (f.high_bg_ratio > 0 and coalesce((a.sauce ->> 'flags')::int & 1, 0) = 0)
    or d.overwrites::double precision / greatest(d.writes, 1) >= :redrawn
  )
  and not exists (
    select 1 from content_rating r where r.sha256 = d.sha256 and r.asserted_by = :algo
  )
"""
INSERT = """
insert into content_rating (sha256, descriptor, kind, present, level, grid_version, nature,
  asserted_by, evidence_note)
values (:sha256, :descriptor, :kind, :present, :level, :grid_version, 'inferred', :algo, :note)
returning id
"""
EARLIER = """
select id, sha256, descriptor from content_rating
where asserted_by like 'algo:keywords@%' and asserted_by <> :algo and superseded_by is null
"""
SUPERSEDE = "update content_rating set superseded_by = :new where id = :old"


def rate_words(conn: Connection) -> Counter[tuple[str, str]]:
    """Infer descriptors from the words of every art file not yet read at this version."""
    found: Counter[tuple[str, str]] = Counter()
    earlier: dict[str, dict[str, str]] = {}
    for row in conn.execute(text(EARLIER), {"algo": KEYWORDS}):
        earlier.setdefault(row.sha256, {})[row.descriptor] = str(row.id)
    rows = conn.execute(text(WORDS), {"text_version": TEXT_VERSION, "algo": KEYWORDS}).all()
    for row in rows:
        name = row.source_path.rsplit("/", 1)[-1]
        inferences = infer(_texts(name, row.title, row.lines or []))
        replaced = earlier.get(row.sha256, {})
        for inference in inferences:
            new = _insert(conn, row.sha256, inference.descriptor, inference.level,
                          "words: " + ", ".join(inference.words))  # fmt: skip
            found[(inference.descriptor, inference.level)] += 1
            if inference.descriptor in replaced:
                _supersede(conn, replaced.pop(inference.descriptor), new)
        for descriptor, old in replaced.items():  # no longer found by this version
            new = _insert(conn, row.sha256, descriptor, None, f"not found by {KEYWORDS}")
            _supersede(conn, old, new)
    return found


def _insert(conn: Connection, sha256: str, descriptor: str, level: str | None, note: str) -> str:
    values = {
        "sha256": sha256,
        "descriptor": descriptor,
        "kind": "descriptor",
        "present": level is not None,
        "level": level,
        "grid_version": GRID_VERSION,
        "algo": KEYWORDS,
        "note": note,
    }
    return str(conn.execute(text(INSERT), values).scalar_one())


def _supersede(conn: Connection, old: str, new: str) -> None:
    conn.execute(text(SUPERSEDE), {"old": old, "new": new})


def rate_flashing(conn: Connection) -> int:
    """Infer the flashing notice from the decoded stream."""
    params = {
        "features_version": FEATURES_VERSION,
        "decoder_version": DECODER_VERSION,
        "redrawn": REDRAWN,
        "algo": STREAM,
    }
    shas = conn.execute(text(FLASHING), params).scalars().all()
    for sha in shas:
        conn.execute(
            text(INSERT),
            {
                "sha256": sha,
                "descriptor": "flashing",
                "kind": "notice",
                "present": True,
                "level": None,
                "grid_version": GRID_VERSION,
                "algo": STREAM,
                "note": "blinking cells outside iCE, or a third of the cells redrawn",
            },
        )
    return len(shas)


def _texts(name: str, title: str | None, lines: Iterable[str]) -> list[str]:
    return [name, title or "", *lines]


@dataclass(frozen=True)
class Rated:
    """A file's row in `work_audience`."""

    level: str
    reviewed: bool


LEVELS = ("3", "7", "12", "16", "18", "withheld")
UNREVIEWED_FLOOR = "12"  # grid rule 4 (v2, a trial): never lower until a person reviews


def audience(rated: Rated | None) -> str:
    """The level a file is shown at. Applied by `tm export` and the API, never by the frontend.

    A file no person has reviewed is shown at its inferred level, and at 12 at the least, even
    when no program found anything in it (no row at all).
    """
    if rated is None:
        return UNREVIEWED_FLOOR
    if rated.reviewed:
        return rated.level
    return max(rated.level, UNREVIEWED_FLOOR, key=LEVELS.index)
