# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import pytest
from pydantic import ValidationError
from tm import corpus

ROOT = Path(__file__).resolve().parents[2] / "corpus"


def test_repository_corpus_is_valid() -> None:
    files = corpus.corpus_files(ROOT)
    assert files, "the corpus must not be empty"
    for path in files:
        corpus.load(path)


def test_schemas_are_up_to_date() -> None:
    for name, content in corpus.json_schemas().items():
        assert (ROOT / "schema" / name).read_text(encoding="utf-8") == content, name


def test_radio_stream_must_be_https() -> None:
    with pytest.raises(ValidationError, match="HTTPS"):
        corpus.Radio(id="x", name="X", homepage="https://x.example/", stream="http://x.example/s")


def test_radio_is_playable_only_with_agreement() -> None:
    radio = corpus.Radio(
        id="x", name="X", homepage="https://x.example/", stream="https://x.example/s"
    )
    assert not radio.playable
    assert radio.model_copy(update={"agreement": "granted"}).playable


def test_profile_rejects_unknown_system() -> None:
    with pytest.raises(ValidationError):
        corpus.Profile.model_validate(
            {
                "title": {"en": "x", "fr": "x"},
                "system": "unknown",
                "grid": "80x25",
                "cell": "9x16",
                "font": {"file": "f", "sha256": "0" * 64},
                "sources": ["s"],
            }
        )


def test_visitor_facing_titles_need_every_required_locale() -> None:
    with pytest.raises(ValidationError, match="missing translation"):
        corpus.Collection.model_validate({"title": {"en": "ANSI"}, "where": {"system": ["ansi"]}})
    with pytest.raises(ValidationError, match="missing translation"):
        corpus.Collection.model_validate(
            {"title": {"en": "ANSI", "fr": "  "}, "where": {"system": ["ansi"]}}
        )


def test_extra_locales_are_welcome() -> None:
    title = {"en": "ANSI", "fr": "ANSI", "ja": "ANSIアート", "sr-Latn": "ANSI"}
    collection = corpus.Collection.model_validate({"title": title, "where": {"system": ["a"]}})
    assert collection.title["ja"] == "ANSIアート"


def test_malformed_locale_tag_is_refused() -> None:
    with pytest.raises(ValidationError):
        corpus.Collection.model_validate(
            {"title": {"en": "x", "fr": "x", "French": "x"}, "where": {"system": ["a"]}}
        )


def _practices(**changes: object) -> dict[str, object]:
    practice = {
        "code": "ansi-art",
        "label": {"en": "ANSI art", "fr": "Art ANSI"},
        "family": "scene",
        "holding": ["file"],
    }
    registry = {
        "version": 1,
        "families": [{"code": "scene", "label": {"en": "Scenes", "fr": "Scènes"}}],
        "practices": [practice],
    }
    return registry | changes


def test_practices_registry_names_a_representative_for_some() -> None:
    registry = corpus.load_practices(ROOT / "practices.yaml")
    assert 0 < len(registry.held()) < len(registry.practices)


def test_practice_codes_are_unique() -> None:
    registry = _practices()
    twice = registry["practices"] * 2  # type: ignore[operator]
    with pytest.raises(ValidationError, match="practice codes must be unique: ansi-art"):
        corpus.Practices.model_validate(registry | {"practices": twice})


def test_practice_family_must_be_declared() -> None:
    with pytest.raises(ValidationError, match="unknown families: scene"):
        corpus.Practices.model_validate(
            _practices(families=[{"code": "other", "label": {"en": "O", "fr": "A"}}])
        )


def test_representative_names_its_source() -> None:
    with pytest.raises(ValidationError):
        corpus.Representative(sha256="0" * 64, path="1996/acid-50a.zip/ANS-50A.ANS")
    assert corpus.Representative(sha256="0" * 64, path="16colo:1996/acid-50a.zip/ANS-50A.ANS")
