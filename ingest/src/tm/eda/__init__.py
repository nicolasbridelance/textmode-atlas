# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""A live exploration of the database (ADR 0028): figures and checks, recomputed on demand.

Reads PostgreSQL directly, unlike research, which reads frozen datasets. Exploratory: what it
suggests is tested later on the `test` packs, which it never reads for grid measures.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import Connection, text

from tm.access import load_access
from tm.corpus import load_practices
from tm.eda.base import Scope
from tm.eda.breadth import breadth
from tm.eda.chapters import contents, makers, peak, sauce
from tm.eda.grids import grids
from tm.storage import ObjectStore

SCHEMA = 3  # 3: the breadth of the collection (ADR 0031)
PUBLIC_KEY = "eda/snapshot.json"  # where the static site finds the last published snapshot
SERIAL = "set local max_parallel_workers_per_gather = 0"  # for this snapshot's transaction
# Any write anywhere changes it: inserts, updates and deletes counted by PostgreSQL itself.
FINGERPRINT = """select coalesce(sum(n_tup_ins + n_tup_upd + n_tup_del), 0)::bigint
from pg_stat_user_tables"""


def fingerprint(conn: Connection) -> int:
    """A number that changes when the database does; cheap enough to ask every few seconds."""
    return int(conn.execute(text(FINGERPRINT)).scalar_one())


def snapshot(conn: Connection, corpus: Path = Path("corpus")) -> dict[str, Any]:
    """Every chapter, computed now, with when and in how long; `corpus` holds the registry of
    practices the breadth chapter reads."""
    started = time.perf_counter()
    # Parallel scans share memory through /dev/shm, which Docker caps at 64 MB: the grid scan
    # filled it ("could not resize shared memory segment"). Serial, it costs a few seconds.
    conn.execute(text(SERIAL))
    mark = fingerprint(conn)
    access = load_access(conn)
    scope = Scope(sorted(sha for sha, rule in access.items() if rule.shown == "nothing"))
    measured = grids(conn, scope)
    return {
        "schema": SCHEMA,
        "computed_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "fingerprint": mark,
        "hidden": len(scope.hidden),
        "chapters": {
            "contents": contents(conn, scope),
            "peak": peak(conn, scope),
            "makers": makers(conn, scope),
            "sauce": sauce(conn, scope),
            "composition": measured["composition"],
            "palette": measured["palette"],
            "revival": measured["revival"],
            "breadth": breadth(conn, scope, load_practices(corpus / "practices.yaml")),
        },
        "seconds": round(time.perf_counter() - started, 2),
    }


def publish(found: dict[str, Any], public: ObjectStore) -> str:
    """Write a snapshot where the static site reads it: aggregates only, hidden works already
    left out of every count (ADR 0028, amendment 1). Returns the key written."""
    data = json.dumps(found, default=str, separators=(",", ":")).encode()
    public.put(PUBLIC_KEY, data, "application/json")
    return PUBLIC_KEY
