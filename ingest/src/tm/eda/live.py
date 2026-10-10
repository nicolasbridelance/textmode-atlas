# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Keep a snapshot current: recompute it when the database's fingerprint changes (ADR 0028)."""

from __future__ import annotations

import logging
import threading
from typing import Any

from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError

from tm.eda import fingerprint, snapshot

EVERY = 30.0  # seconds between two looks at the fingerprint
log = logging.getLogger(__name__)


class Live:
    """The last snapshot, and a background thread that replaces it when the database moved.

    A visitor never waits for a computation, except for the very first one."""

    def __init__(self, engine: Engine, every: float = EVERY) -> None:
        self.engine = engine
        self.every = every
        self._snapshot: dict[str, Any] | None = None
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._first = threading.Event()

    def start(self) -> None:
        threading.Thread(target=self._run, name="eda", daemon=True).start()

    def stop(self) -> None:
        self._stop.set()

    def current(self, wait: float = 0.0) -> dict[str, Any] | None:
        """The last snapshot; `wait` seconds at most for the first one."""
        self._first.wait(wait)
        with self._lock:
            return self._snapshot

    def refresh(self) -> bool:
        """Recompute if the database changed since the last snapshot; True if it did."""
        with self.engine.connect() as conn:
            mark = fingerprint(conn)
            if self._snapshot is not None and self._snapshot["fingerprint"] == mark:
                return False
            fresh = snapshot(conn)
        with self._lock:
            self._snapshot = fresh
        self._first.set()
        log.info("exploration recomputed in %ss", fresh["seconds"])
        return True

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self.refresh()
            except SQLAlchemyError:
                log.exception("exploration not refreshed")  # the last snapshot stays
            self._stop.wait(self.every)
