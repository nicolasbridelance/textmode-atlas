# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The breadth of the collection (ADR 0031, 0032): which practices of the character arts it
holds, from which sources, and on what basis it may show them.

Read from the database and from the registry of practices (`corpus/practices.yaml`): a practice
counts as held when the artifact the registry names is in the database, not because the
registry says so.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from sqlalchemy import Connection

from tm.corpus import Practices
from tm.eda.base import SHOWN, Scope, rows_of
from tm.eda.chapters import SINGLE

# The first basis that applies, in the order can_display() asks (ADR 0009, 0032).
BASIS = """case
  when (w.rights -> 'permission' ->> 'display')::boolean then 'permission'
  when jsonb_typeof(w.rights -> 'scene_publication') = 'object' then 'scene'
  when w.rights ->> 'license' is not null then 'license'
  when jsonb_typeof(w.rights -> 'excerpt') = 'object' then 'excerpt'
  else 'none' end"""


def breadth(conn: Connection, scope: Scope, registry: Practices) -> dict[str, Any]:
    """How wide the collection is: practices held by family, works by source and by basis."""
    named = {p.code: p.representative.sha256 for p in registry.practices if p.representative}
    found = {
        row["sha256"].strip()
        for row in rows_of(
            conn,
            "select sha256 from artifact where sha256 = any(:named)",
            {"named": sorted(named.values())},
        )
    }
    total = Counter(p.family for p in registry.practices)
    held_in = Counter(p.family for p in registry.practices if named.get(p.code) in found)
    families = [
        {
            "family": family.code,
            "label": family.label,
            "total": total[family.code],
            "held": held_in[family.code],
        }
        for family in registry.families
    ]
    sources = rows_of(
        conn,
        f"select s.name as source, count(*) as works from {SINGLE}"
        f" join source s on s.id = a.source_id where {SHOWN} group by 1 order by 2 desc",
        scope.params(),
    )
    bases = rows_of(
        conn,
        f"select {BASIS} as basis, count(*) as works from {SINGLE}"
        f" where {SHOWN} group by 1 order by 2 desc",
        scope.params(),
    )
    held = sum(held_in.values())
    missing = sorted(code for code, sha in named.items() if sha not in found)
    return {
        "families": families,
        "sources": sources,
        "bases": bases,
        "checks": {
            "representatives_held": {
                "holds": not missing,
                "missing": len(missing),
                "names": ", ".join(missing),
            },
            "practices_held": {
                "holds": held > 0,
                "held": held,
                "total": len(registry.practices),
                "empty_families": sum(held_in[f.code] == 0 for f in registry.families),
            },
        },
    }
