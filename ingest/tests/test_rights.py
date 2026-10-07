# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass, field

import pytest
from tm.rights import ClosedPolicy, Displayable, Permission, Privacy, Rights, can_display


@dataclass
class Work:
    rights: Rights = field(default_factory=Rights)
    privacy: Privacy = field(default_factory=Privacy)


class OpenPolicy:
    def allows(self, work: Displayable) -> bool:
        return True


GRANTED = Rights(permission=Permission(display=True, granted_by="identity:example"))


def test_default_is_metadata_only() -> None:
    assert can_display(Work()) == "metadata"


def test_permission_shows_file() -> None:
    assert can_display(Work(rights=GRANTED)) == "file"


def test_withdrawal_wins_over_permission() -> None:
    assert can_display(Work(rights=GRANTED, privacy=Privacy(withdrawn=True))) == "none"


def test_withdrawal_wins_over_policy() -> None:
    assert can_display(Work(privacy=Privacy(withdrawn=True)), OpenPolicy()) == "none"


def test_policy_can_allow() -> None:
    assert can_display(Work(), OpenPolicy()) == "file"


def test_closed_policy_never_allows() -> None:
    assert ClosedPolicy().allows(Work(rights=GRANTED)) is False
    assert can_display(Work(), ClosedPolicy()) == "metadata"


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValueError, match="extra"):
        Rights.model_validate({"permission": {"display": True, "displya": True}})
