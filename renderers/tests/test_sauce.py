# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
import struct

from tm_render.sauce import split


def record(comments: int = 0, flags: int = 0, width: int = 80, height: int = 25) -> bytes:
    return (
        b"SAUCE00"
        + b"Title".ljust(35)
        + b"Author".ljust(20)
        + b"Group".ljust(20)
        + b"19940601"
        + struct.pack("<IBBHHHHBB", 3, 1, 1, width, height, 0, 0, comments, flags)
        + b"IBM VGA".ljust(22, b"\0")
    )


def test_no_record_keeps_content() -> None:
    assert split(b"hello") == (b"hello", None)


def test_content_stops_at_dos_eof() -> None:
    assert split(b"art\x1agarbage")[0] == b"art"


def test_record_fields() -> None:
    content, sauce = split(b"art\x1a" + record(flags=0b0000_0101))
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


def test_letter_spacing_and_aspect_flags() -> None:
    _, sauce = split(b"x" + record(flags=0b0000_1010))
    assert sauce is not None
    assert sauce.letter_spacing == "8px"
    assert sauce.legacy_aspect
    assert not sauce.ice_colors


def test_comment_block() -> None:
    comment = b"COMNT" + b"first line".ljust(64) + b"second".ljust(64)
    content, sauce = split(b"art\x1a" + comment + record(comments=2))
    assert content == b"art"
    assert sauce is not None
    assert sauce.comments == ("first line", "second")


def test_announced_comments_that_are_missing_are_ignored() -> None:
    content, sauce = split(b"art\x1a" + record(comments=3))
    assert content == b"art"
    assert sauce is not None
    assert sauce.comments == ()
