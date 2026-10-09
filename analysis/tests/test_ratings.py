# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from tm_analysis.ratings import Inference, infer


def test_whole_words_only() -> None:
    assert infer(["hello shell", "Hellraiser", "skillful"]) == []
    assert infer(["go to hell"]) == [Inference("fear", "12", ("hell",))]


def test_the_highest_level_wins_and_keeps_its_words() -> None:
    found = infer(["damn", "FUCKING lamers"])
    assert found == [Inference("language", "16", ("fucking",))]


def test_accents_and_endings_are_folded() -> None:
    assert infer(["Les démons", "whiskey"]) == [
        Inference("drugs", "12", ("whiskey",)),
        Inference("fear", "12", ("demons",)),
    ]


def test_phrases_match_across_a_space() -> None:
    assert infer(["credit cards accepted"]) == [Inference("crime", "16", ("credit cards",))]
