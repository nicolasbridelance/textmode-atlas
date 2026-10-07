# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Rights and privacy: the single function that decides what may be shown.

`can_display()` is called by `tm export` and by the API, never by the frontend. It covers images
and sound alike. This module is held at 100% branch coverage.
"""

from __future__ import annotations

import datetime as dt
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict

Display = Literal["none", "metadata", "file"]


class Permission(BaseModel):
    """Display permission granted by the author or rights holder."""

    model_config = ConfigDict(extra="forbid")

    display: bool = False
    granted_by: str | None = None  # 'identity:<handle>', or 'human:<login>' for a deposit
    granted_at: dt.date | None = None
    evidence_note: str | None = None


class Rights(BaseModel):
    model_config = ConfigDict(extra="forbid")

    permission: Permission = Permission()
    # License declared by the author, if any (CC0 for the project's golden artifacts).
    license: str | None = None


class Privacy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    person_link: Literal["private", "public"] = "private"
    mask_real_names: bool = True
    sensitive_membership: Literal["period_source_only", "public"] = "period_source_only"
    withdrawn: bool = False


class Displayable(Protocol):
    """What `can_display()` needs to know about a work."""

    @property
    def rights(self) -> Rights: ...

    @property
    def privacy(self) -> Privacy: ...


class Policy(Protocol):
    """Written policy for display without explicit permission (orphan works, etc.)."""

    def allows(self, work: Displayable) -> bool: ...


class ClosedPolicy:
    """Default policy: nothing is shown without permission.

    It stays in place until a written rule has been approved by a lawyer.
    """

    def allows(self, work: Displayable) -> bool:
        return False


def can_display(work: Displayable, policy: Policy | None = None) -> Display:
    if work.privacy.withdrawn:
        return "none"  # record hidden
    if work.rights.permission.display:
        return "file"  # file and renderings
    if (policy or ClosedPolicy()).allows(work):
        return "file"
    return "metadata"  # record, relations, link to the source archive
