# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
import datetime as dt
from dataclasses import dataclass, field

import pytest
from tm.rights import (
    Displayable,
    Excerpt,
    MuseumPolicy,
    Permission,
    Privacy,
    Rights,
    ScenePublication,
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


EXCERPT = Excerpt(
    taken_from="https://web.archive.org/web/1999/http://example.org/sig.html",
    cut="lines 12-18",
    taken_at=dt.date(2026, 10, 10),
    credit="unknown",
)


@pytest.mark.parametrize(
    "rights",
    [SCENE, Rights(license="CC0-1.0"), Rights(license="public-domain"), Rights(excerpt=EXCERPT)],
)
def test_the_museum_policy_shows_scene_licensed_and_excerpted_works(rights: Rights) -> None:
    assert MuseumPolicy().allows(Work(rights=rights))
    assert can_display(Work(rights=rights)) == "file"


def test_the_museum_policy_needs_a_basis() -> None:
    assert not MuseumPolicy().allows(Work(rights=GRANTED))
    assert not MuseumPolicy().allows(Work())


def test_withdrawal_wins_over_an_excerpt() -> None:
    work = Work(rights=Rights(excerpt=EXCERPT), privacy=Privacy(withdrawn=True))
    assert can_display(work) == "none"


def test_an_excerpt_names_its_credit() -> None:
    with pytest.raises(ValueError, match="credit"):
        Excerpt.model_validate(EXCERPT.model_dump() | {"credit": ""})


def test_only_scene_archives_count() -> None:
    with pytest.raises(ValueError, match="archive"):
        ScenePublication.model_validate({"archive": "random-blog", "url": "https://x.example/"})


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValueError, match="extra"):
        Rights.model_validate({"permission": {"display": True, "displya": True}})
