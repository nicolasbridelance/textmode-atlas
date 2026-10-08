# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Small art files built for the tests (CC0, project-made)."""

from __future__ import annotations

import struct

ICE_AND_9PX = 0b0000_0101

# A SAUCE record whose binary fields hold spaces where zeros belong, as some tools wrote them:
# width 0x2050 instead of 80, and an original size larger than the file. Its flags ask for iCE
# colours and 9-pixel letters, which a record set aside must not impose either.
CORRUPT_SAUCE_ART = (
    b"x" * 100
    + b"\x1aSAUCE00"
    + b"Title".ljust(35)
    + b"Author".ljust(20)
    + b"Group".ljust(20)
    + b"19960302"
    + struct.pack("<IBBHHHHBB", 0x2020_0064, 1, 1, 0x2050, 0x2014, 0, 0, 0, ICE_AND_9PX)
    + b"IBM VGA".ljust(22, b"\0")
)
