# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""SAUCE: the 128-byte metadata record appended to textmode files (spec v00.5, ACiD 1994).

Layout: optional EOF byte (0x1A), optional comment block (`COMNT` + 64-byte lines), then the
record starting with `SAUCE00`. Absent or malformed records give `None`: they are common, and
the content stays readable without them.

Some tools wrote records that start with `SAUCE00` but whose binary fields are wrong: text that
overflows into them, a field one byte too long that shifts the rest, spaces as padding instead of
zeros. `Sauce.problems` names the evidence; a record with problems is kept as it was written, but
its numbers (width, height, flags) are not to be trusted.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Literal

RECORD_SIZE = 128
COMMENT_LINE_SIZE = 64
COMMENT_HEADER = b"COMNT"
EOF_BYTE = 0x1A
_FIELDS = struct.Struct("<5s2s35s20s20s8sIBBHHHHBB22s")

LetterSpacing = Literal["legacy", "8px", "9px"]
_SPACING: dict[int, LetterSpacing] = {0: "legacy", 1: "8px", 2: "9px"}
# Highest file type defined for each data type (spec v00.5). Binary text (5) puts the width in
# the file type, so any value is valid.
_LAST_FILE_TYPE = {0: 0, 1: 8, 2: 13, 3: 3, 4: 24, 5: 255, 6: 0, 7: 9, 8: 0}


@dataclass(frozen=True)
class Sauce:
    title: str
    author: str
    group: str
    date: str
    file_size: int
    data_type: int
    file_type: int
    width: int
    height: int
    flags: int
    font: str
    comments: tuple[str, ...]

    @property
    def ice_colors(self) -> bool:
        """Bit 0: the attribute's high bit selects bright backgrounds instead of blinking."""
        return bool(self.flags & 1)

    @property
    def letter_spacing(self) -> LetterSpacing:
        return _SPACING.get((self.flags >> 1) & 0b11, "legacy")

    @property
    def legacy_aspect(self) -> bool:
        """Bits 3–4 = 01: stretch to the aspect ratio of a 4:3 CRT."""
        return (self.flags >> 3) & 0b11 == 1

    def problems(self, file_bytes: int) -> tuple[str, ...]:
        """Evidence that the binary fields are corrupt, for a file of `file_bytes` bytes.

        Both are impossible in a well-formed record: a type pair the spec does not define, and an
        original size larger than the whole file the record ends.
        """
        last = _LAST_FILE_TYPE.get(self.data_type, -1)
        found = {
            "type_out_of_spec": self.file_type > last,
            "size_exceeds_file": self.file_size > file_bytes,
        }
        return tuple(name for name, present in found.items() if present)


def _text(raw: bytes) -> str:
    return raw.split(b"\0", 1)[0].decode("cp437").rstrip()


def split(data: bytes) -> tuple[bytes, Sauce | None]:
    """Separate the content from its SAUCE record (and comments), if there is one."""
    if len(data) < RECORD_SIZE or data[-RECORD_SIZE:][:7] != b"SAUCE00":
        return _strip_eof(data), None
    fields = _FIELDS.unpack(data[-RECORD_SIZE:])
    comment_count = fields[13]
    end = len(data) - RECORD_SIZE
    comments, end = _comments(data, end, comment_count)
    sauce = Sauce(
        title=_text(fields[2]),
        author=_text(fields[3]),
        group=_text(fields[4]),
        date=_text(fields[5]),
        file_size=fields[6],
        data_type=fields[7],
        file_type=fields[8],
        width=fields[9],
        height=fields[10],
        flags=fields[14],
        font=_text(fields[15]),
        comments=comments,
    )
    return _strip_eof(data[:end]), sauce


def _comments(data: bytes, end: int, count: int) -> tuple[tuple[str, ...], int]:
    start = end - len(COMMENT_HEADER) - count * COMMENT_LINE_SIZE
    if count == 0 or start < 0 or data[start : start + len(COMMENT_HEADER)] != COMMENT_HEADER:
        return (), end
    body = data[start + len(COMMENT_HEADER) : end]
    lines = [body[i : i + COMMENT_LINE_SIZE] for i in range(0, len(body), COMMENT_LINE_SIZE)]
    return tuple(_text(line) for line in lines), start


def _strip_eof(content: bytes) -> bytes:
    """Content ends at the first EOF byte, as DOS viewers read it."""
    cut = content.find(bytes([EOF_BYTE]))
    return content if cut < 0 else content[:cut]
