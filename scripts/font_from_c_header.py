# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Extract a bitmap font from a libansilove C header (`const uint8_t name[N] = {…};`).

Usage: python scripts/font_from_c_header.py <header.h> <output.f16>

The output is the raw array: 256 glyphs, one 8-pixel row per byte, most significant bit on the
left. The output's hash is written into the rendering profiles that use it.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path


def extract(source: str) -> bytes:
    match = re.search(r"\[(\d+)\]\s*=\s*\{(.*?)\};", source, re.S)
    if match is None:
        raise ValueError("no array found")
    size, body = int(match.group(1)), match.group(2)
    data = bytes(int(v, 16) for v in re.findall(r"0x([0-9a-fA-F]{2})", body))
    if len(data) != size:
        raise ValueError(f"read {len(data)} bytes, {size} declared")
    return data


def main() -> None:
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    data = extract(src.read_text(encoding="utf-8"))
    dst.write_bytes(data)
    print(f"{dst}: {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
