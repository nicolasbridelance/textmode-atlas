# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""What every chapter of the exploration shares: its scope and how it reads rows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Connection, text
from tm_render.versions import DECODER_VERSION

SHOWN = "a.sha256 <> all(cast(:hidden as text[]))"


@dataclass(frozen=True)
class Scope:
    """What every chapter leaves out: works the policy shows nothing of (`tm.access`)."""

    hidden: list[str]

    def params(self, **more: Any) -> dict[str, Any]:
        return {"hidden": self.hidden, "decoder": DECODER_VERSION, **more}


def rows_of(conn: Connection, sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute(text(sql), params).mappings()]
