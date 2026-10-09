# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The budget of paid model calls: nothing is spent without the owner's grant.

The ledger is an append-only JSON Lines file, one entry per grant, reservation or spend,
outside the repository (`TM_MODEL_LEDGER`, machine-local). A call needs a grant for its
scope with room for its estimate *before* it is made, and records what it actually cost
after. No entry ever holds a key: the ledger knows amounts, models and scopes only.
"""

from __future__ import annotations

import json
import re
import uuid
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

Kind = Literal["grant", "reserve", "spend", "release"]
CREDENTIAL = re.compile(r"sk-[\w-]{8,}|[A-Za-z0-9_\-]{32,}")  # an API key, a long token
Record = Callable[..., None]


class BudgetError(Exception):
    """A call the budget does not allow, with what is left."""


@dataclass(frozen=True)
class Balance:
    scope: str
    granted: float
    spent: float
    reserved: float

    @property
    def left(self) -> float:
        return self.granted - self.spent - self.reserved


def _clean(note: str) -> str:
    if CREDENTIAL.search(note):
        raise BudgetError("a ledger note must not look like a credential")
    return note


class Ledger:
    """Append-only: entries are added, never changed or removed."""

    def __init__(self, path: Path, clock: Callable[[], datetime] = lambda: datetime.now(UTC)):
        self.path = path
        self.clock = clock

    def entries(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as lines:
            return [json.loads(line) for line in lines if line.strip()]

    def _append(self, kind: Kind, scope: str, usd: float, **fields: Any) -> dict[str, Any]:
        if usd < 0:
            raise BudgetError("amounts are never negative")
        entry = {"at": self.clock().isoformat(), "kind": kind, "scope": scope, "usd": usd}
        entry |= fields
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as out:
            out.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry

    def grant(self, scope: str, usd: float, by: str, note: str) -> None:
        """Record the owner's authorization: up to `usd` dollars for `scope`."""
        self._append("grant", scope, usd, by=_clean(by), note=_clean(note))

    def balance(self, scope: str) -> Balance:
        sums = {"grant": 0.0, "spend": 0.0, "reserve": 0.0, "release": 0.0}
        for entry in self.entries():
            if entry["scope"] == scope:
                sums[entry["kind"]] += entry["usd"]
        reserved = sums["reserve"] - sums["release"]
        return Balance(scope, sums["grant"], sums["spend"], reserved)

    def scopes(self) -> list[str]:
        return sorted({entry["scope"] for entry in self.entries()})

    @contextmanager
    def call(self, scope: str, estimate_usd: float, model: str) -> Generator[Record]:
        """Reserve the estimate, yield a `record(cost)` function, release the reservation.

        Raises before any call when the grant has no room. A call that fails still records
        what it cost if `record` was called; an unrecorded call is charged its estimate.
        """
        balance = self.balance(scope)
        if estimate_usd > balance.left:
            raise BudgetError(
                f"{scope}: estimate ${estimate_usd:.4f} exceeds what is left"
                f" (${balance.left:.4f} of ${balance.granted:.2f} granted)"
            )
        call_id = uuid.uuid4().hex
        self._append("reserve", scope, estimate_usd, call=call_id, model=model)
        spent: list[float] = []

        def record(cost_usd: float, **usage: Any) -> None:
            spent.append(cost_usd)
            self._append("spend", scope, cost_usd, call=call_id, model=model, **usage)

        try:
            yield record
        finally:
            if not spent:
                self._append(
                    "spend", scope, estimate_usd, call=call_id, model=model, unrecorded=True
                )
            self._append("release", scope, estimate_usd, call=call_id)
