# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import pytest
from tm_render.ansi import DecodeError, decode
from tm_render.signatures import binary_format


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"\xff\xd8\xff\xe0\x00\x10JFIF", "jpeg"),
        (b"GIF89a\x40\x01", "gif"),
        (b"PK\x03\x04\x14\x00", "zip"),
        (b"MZ\x90\x00\x03", "exe"),
        (b"FORM\x00\x00\x10\x00ILBMBMHD", "iff"),
        (b"\x00" * 44 + b"SCRM" + b"\x00" * 10, "s3m"),
        (b"\x00" * 1080 + b"M.K." + b"\x00" * 10, "mod"),
        (b"BM" + (30).to_bytes(4, "little") + b"\x00" * 8 + (40).to_bytes(4, "little"), "bmp"),
        (b"\x0a\x05\x01\x08" + b"\x00" * 60, "pcx"),
    ],
)
def test_binary_formats_are_recognised(data: bytes, expected: str) -> None:
    assert binary_format(data) == expected


@pytest.mark.parametrize(
    "data",
    [
        b"\x1b[0;1;34m\xdb\xdb\xdb\r\n",
        b"FORMS by mOp\r\n",  # a word, not an IFF chunk
        b"BMX logo\r\n",
        b"\x0a\x0aline art\r\n",  # line feeds, not a PCX header
        b"\xdb\x00\xdb\x00 NUL used as blank\r\n",
    ],
)
def test_text_art_is_not_taken_for_binary(data: bytes) -> None:
    assert binary_format(data) is None


def test_the_decoder_classifies_a_picture_stamped_as_ansi() -> None:
    with pytest.raises(DecodeError) as raised:
        decode(b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 100)
    assert raised.value.kind == "binary_content"
