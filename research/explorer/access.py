# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Live museum display decisions; private storage is never a display permission."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import create_engine, text
from tm.audience import Rated, audience
from tm.config import settings
from tm.export import NOT_YET_SHOWN, Shown
from tm.rights import Privacy, Rights, can_display

POLICIES = """
select a.sha256, w.rights, w.privacy, wa.level, wa.reviewed,
       wa.descriptors, wa.notices
from artifact a join version v on v.id = a.version_id
join work w on w.id = v.work_id and w.kind = 'single'
left join work_audience wa on wa.sha256 = a.sha256
"""


@dataclass(frozen=True)
class Access:
    shown: str
    level: str
    reviewed: bool
    descriptors: list[str]
    notices: list[str]
    url: str | None


def classify(row: Any) -> Access:
    rights = Rights.model_validate(row.rights)
    display = can_display(Shown(rights, Privacy.model_validate(row.privacy)))
    rating = Rated(row.level, bool(row.reviewed)) if row.level is not None else None
    level = audience(rating)
    shown = "files" if display == "file" and level not in NOT_YET_SHOWN else "record"
    if display == "none" or level == "withheld":
        shown = "nothing"
    url = str(rights.scene_publication.url) if rights.scene_publication else None
    return Access(shown, level, bool(row.reviewed), row.descriptors or [], row.notices or [], url)


def load_access() -> dict[str, Access]:
    engine = create_engine(settings().database_url)
    try:
        with engine.connect() as conn:
            return {row.sha256: classify(row) for row in conn.execute(text(POLICIES))}
    finally:
        engine.dispose()
