# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""File signatures of the binary formats found in artpacks, to tell them from text art.

Some tools stamped every file of a pack with a SAUCE record of type Character/ANSI, pictures and
programs included (16colo: about 1,600 files). A file that starts with the signature of a known
binary format is that format, whatever its SAUCE says. NUL bytes alone do not tell: some editors
wrote them as blanks in real ANSI.
"""

from __future__ import annotations

# (offset, bytes) → format; the first match wins.
SIGNATURES: tuple[tuple[int, bytes, str], ...] = (
    (0, b"\xff\xd8\xff", "jpeg"),
    (0, b"GIF87a", "gif"),
    (0, b"GIF89a", "gif"),
    (0, b"\x89PNG\r\n\x1a\n", "png"),
    (0, b"PK\x03\x04", "zip"),
    (0, b"Rar!\x1a\x07", "rar"),
    (0, b"\x60\xea", "arj"),
    (2, b"-lh", "lha"),
    (0, b"MZ", "exe"),
    (0, b"MThd", "midi"),
    (0, b"IMPM", "it"),
    (0, b"Extended Module:", "xm"),
    (44, b"SCRM", "s3m"),
    (1080, b"M.K.", "mod"),
    (1080, b"M!K!", "mod"),
    (1080, b"4CHN", "mod"),
    (1080, b"6CHN", "mod"),
    (1080, b"8CHN", "mod"),
    (1080, b"FLT4", "mod"),
)
BMP_HEADER = 18
BMP_DIB_SIZES = frozenset({12, 40, 56, 64, 108, 124})  # the known bitmap header versions
IFF_TYPES = frozenset({b"ILBM", b"PBM ", b"8SVX", b"ANIM"})
PCX_MANUFACTURER = 0x0A
PCX_ENCODING_RLE = 1
PCX_HEADER = 4
PCX_BITS = frozenset({1, 2, 4, 8})
PCX_VERSIONS = frozenset({0, 2, 3, 4, 5})


def binary_format(data: bytes) -> str | None:
    """The binary format `data` starts with, or None when it may be text."""
    for offset, magic, name in SIGNATURES:
        if data[offset : offset + len(magic)] == magic:
            return name
    if data[:4] == b"FORM" and data[8:12] in IFF_TYPES:
        return "iff"
    if _bmp(data):
        return "bmp"
    if _pcx(data):
        return "pcx"
    return None


def _bmp(data: bytes) -> bool:
    """`BM`, reserved zeros, a known header size: two letters alone could start a text."""
    if len(data) < BMP_HEADER or data[:2] != b"BM" or data[6:10] != b"\0\0\0\0":
        return False
    return int.from_bytes(data[14:18], "little") in BMP_DIB_SIZES


def _pcx(data: bytes) -> bool:
    """Manufacturer 0x0A (a line feed in text), a known version, RLE encoding, 1–8 bits."""
    return (
        len(data) >= PCX_HEADER
        and data[0] == PCX_MANUFACTURER
        and data[1] in PCX_VERSIONS
        and data[2] == PCX_ENCODING_RLE
        and data[3] in PCX_BITS
    )
