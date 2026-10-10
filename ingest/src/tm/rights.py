# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Rights and privacy: the single function that decides what may be shown.

`can_display()` is called by `tm export` and by the API, never by the frontend. It covers images
and sound alike. This module is held at 100% branch coverage.

Display rule (ADR 0009, 0032): a work is shown with the permission of its author, or, failing
that, when the scene itself released it freely and a scene archive still holds it, when a licence
or the public domain covers it, or when the museum cut it out itself from where it was found,
credited. Every case is withdrawn on request.
"""

from __future__ import annotations

import datetime as dt
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

Display = Literal["none", "metadata", "file"]

# Archives kept by the scene itself, where works were released for free distribution.
SceneArchive = Literal["16colo", "demozoo", "scene.org", "textfiles"]


class Permission(BaseModel):
    """Display permission granted by the author or rights holder."""

    model_config = ConfigDict(extra="forbid")

    display: bool = False
    granted_by: str | None = None  # 'identity:<handle>', or 'human:<login>' for a deposit
    granted_at: dt.date | None = None
    evidence_note: str | None = None


class ScenePublication(BaseModel):
    """Where the scene released a work for free distribution, as found today."""

    model_config = ConfigDict(extra="forbid")

    archive: SceneArchive
    url: HttpUrl


class Excerpt(BaseModel):
    """A textual artwork the museum cut out itself from something larger (ADR 0032): where from,
    how, when, and who made it as signed (or "unknown")."""

    model_config = ConfigDict(extra="forbid")

    taken_from: HttpUrl
    cut: str = Field(min_length=1)
    taken_at: dt.date
    credit: str = Field(min_length=1)


class Rights(BaseModel):
    model_config = ConfigDict(extra="forbid")

    permission: Permission = Permission()
    scene_publication: ScenePublication | None = None
    # License declared by the author, or "public-domain" (CC0 for the project's golden artifacts).
    license: str | None = None
    excerpt: Excerpt | None = None


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
    """Rule for display without explicit permission."""

    def allows(self, work: Displayable) -> bool: ...


class MuseumPolicy:
    """ADR 0009 and 0032: show what the scene released freely and still distributes, what a
    licence or the public domain covers, and what the museum cut out itself, credited."""

    def allows(self, work: Displayable) -> bool:
        rights = work.rights
        return any((rights.scene_publication, rights.license, rights.excerpt))


MUSEUM = MuseumPolicy()


def can_display(work: Displayable, policy: Policy = MUSEUM) -> Display:
    if work.privacy.withdrawn:
        return "none"  # record hidden
    if work.rights.permission.display:
        return "file"  # file and renderings
    if policy.allows(work):
        return "file"
    return "metadata"  # record, relations, link to the source archive
