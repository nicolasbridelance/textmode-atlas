# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from typing import Any

import pytest
from conftest import SauceRecord
from tm_render.sauce import split


def test_no_record_keeps_content() -> None:
    assert split(b"hello") == (b"hello", None)


def test_content_stops_at_dos_eof() -> None:
    assert split(b"art\x1agarbage")[0] == b"art"


def test_record_fields(sauce_record: SauceRecord) -> None:
    content, sauce = split(b"art\x1a" + sauce_record(flags=0b0000_0101))
    assert content == b"art"
    assert sauce is not None
    assert (sauce.title, sauce.author, sauce.group, sauce.date) == (
        "Title",
        "Author",
        "Group",
        "19940601",
    )
    assert (sauce.width, sauce.height, sauce.font) == (80, 25, "IBM VGA")
    assert sauce.ice_colors
    assert sauce.letter_spacing == "9px"
    assert not sauce.legacy_aspect


def test_letter_spacing_and_aspect_flags(sauce_record: SauceRecord) -> None:
    _, sauce = split(b"x" + sauce_record(flags=0b0000_1010))
    assert sauce is not None
    assert sauce.letter_spacing == "8px"
    assert sauce.legacy_aspect
    assert not sauce.ice_colors


def test_comment_block(sauce_record: SauceRecord) -> None:
    comment = b"COMNT" + b"first line".ljust(64) + b"second".ljust(64)
    content, sauce = split(b"art\x1a" + comment + sauce_record(comments=2))
    assert content == b"art"
    assert sauce is not None
    assert sauce.comments == ("first line", "second")


def test_announced_comments_that_are_missing_are_ignored(sauce_record: SauceRecord) -> None:
    content, sauce = split(b"art\x1a" + sauce_record(comments=3))
    assert content == b"art"
    assert sauce is not None
    assert sauce.comments == ()


def test_a_well_formed_record_has_no_problems(sauce_record: SauceRecord) -> None:
    data = b"art\x1a" + sauce_record()
    sauce = split(data)[1]
    assert sauce is not None
    assert sauce.problems(len(data)) == ()


def test_binary_text_puts_any_value_in_the_file_type(sauce_record: SauceRecord) -> None:
    data = b"art" + sauce_record(types=(5, 80))
    sauce = split(data)[1]
    assert sauce is not None
    assert sauce.problems(len(data)) == ()


@pytest.mark.parametrize(
    ("fields", "expected"),
    [
        # Polyester, 1996–97: the group text overflows into the binary fields ("by").
        ({"types": (98, 121)}, ("type_out_of_spec",)),
        # Spaces as padding: 0x2020xxxx bytes declared for a file of a few hundred.
        ({"file_size": 0x2020_02D0}, ("size_exceeds_file",)),
        # RiSE, 1995: a field one byte too long shifts the rest of the record.
        ({"file_size": 1 << 24, "types": (1, 80)}, ("type_out_of_spec", "size_exceeds_file")),
    ],
)
def test_corrupt_binary_fields_are_named(
    sauce_record: SauceRecord, fields: dict[str, Any], expected: tuple[str, ...]
) -> None:
    data = b"art\x1a" + sauce_record(**fields)
    sauce = split(data)[1]
    assert sauce is not None
    assert sauce.problems(len(data)) == expected
