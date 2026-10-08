# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
import struct
from collections.abc import Callable

import pytest

SauceRecord = Callable[..., bytes]


def _record(
    *,
    comments: int = 0,
    flags: int = 0,
    width: int = 80,
    height: int = 25,
    file_size: int = 3,
    types: tuple[int, int] = (1, 1),
) -> bytes:
    return (
        b"SAUCE00"
        + b"Title".ljust(35)
        + b"Author".ljust(20)
        + b"Group".ljust(20)
        + b"19940601"
        + struct.pack("<IBBHHHHBB", file_size, *types, width, height, 0, 0, comments, flags)
        + b"IBM VGA".ljust(22, b"\0")
    )


@pytest.fixture
def sauce_record() -> SauceRecord:
    """Build a 128-byte SAUCE record; keyword arguments set its binary fields."""
    return _record
