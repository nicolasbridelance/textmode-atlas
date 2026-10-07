# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass, field

import pytest
from tm.rights import (
    Displayable,
    Permission,
    Privacy,
    Rights,
    ScenePublication,
    ScenePublishedPolicy,
    can_display,
)


@dataclass
class Work:
    rights: Rights = field(default_factory=Rights)
    privacy: Privacy = field(default_factory=Privacy)


class NeverPolicy:
    def allows(self, work: Displayable) -> bool:
        return False


GRANTED = Rights(permission=Permission(display=True, granted_by="identity:example"))
SCENE = Rights(
    scene_publication=ScenePublication(archive="16colo", url="https://16colo.rs/pack/x/")
)


def test_unknown_provenance_is_metadata_only() -> None:
    assert can_display(Work()) == "metadata"


def test_permission_shows_file() -> None:
    assert can_display(Work(rights=GRANTED)) == "file"


def test_scene_published_work_is_shown_by_default() -> None:
    assert can_display(Work(rights=SCENE)) == "file"


def test_withdrawal_wins_over_permission() -> None:
    assert can_display(Work(rights=GRANTED, privacy=Privacy(withdrawn=True))) == "none"


def test_withdrawal_wins_over_scene_publication() -> None:
    assert can_display(Work(rights=SCENE, privacy=Privacy(withdrawn=True))) == "none"


def test_policy_is_injected() -> None:
    assert can_display(Work(rights=SCENE), NeverPolicy()) == "metadata"
    assert can_display(Work(rights=GRANTED), NeverPolicy()) == "file"


def test_scene_policy_needs_a_scene_archive() -> None:
    assert ScenePublishedPolicy().allows(Work(rights=SCENE))
    assert not ScenePublishedPolicy().allows(Work(rights=GRANTED))


def test_only_scene_archives_count() -> None:
    with pytest.raises(ValueError, match="archive"):
        ScenePublication.model_validate({"archive": "random-blog", "url": "https://x.example/"})


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValueError, match="extra"):
        Rights.model_validate({"permission": {"display": True, "displya": True}})
