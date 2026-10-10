# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""A live exploration of the database (ADR 0028): figures and checks, recomputed on demand.

Reads PostgreSQL directly, unlike research, which reads frozen datasets. Exploratory: what it
suggests is tested later on the `test` packs, which it never reads for grid measures.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Connection, text

from tm.access import load_access
from tm.eda.chapters import Scope, contents, material, peak, sauce

SCHEMA = 1
# Any write anywhere changes it: inserts, updates and deletes counted by PostgreSQL itself.
FINGERPRINT = """select coalesce(sum(n_tup_ins + n_tup_upd + n_tup_del), 0)::bigint
from pg_stat_user_tables"""


def fingerprint(conn: Connection) -> int:
    """A number that changes when the database does; cheap enough to ask every few seconds."""
    return int(conn.execute(text(FINGERPRINT)).scalar_one())


def snapshot(conn: Connection) -> dict[str, Any]:
    """Every chapter, computed now, with when and in how long."""
    started = time.perf_counter()
    mark = fingerprint(conn)
    access = load_access(conn)
    scope = Scope(sorted(sha for sha, rule in access.items() if rule.shown == "nothing"))
    grids = material(conn, scope)
    return {
        "schema": SCHEMA,
        "computed_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "fingerprint": mark,
        "hidden": len(scope.hidden),
        "chapters": {
            "contents": contents(conn, scope),
            "peak": peak(conn, scope),
            "sauce": sauce(conn, scope),
            "composition": grids["composition"],
            "revival": grids["revival"],
        },
        "seconds": round(time.perf_counter() - started, 2),
    }
