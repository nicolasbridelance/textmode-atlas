# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The existing corpus service hosts the one museum, without publishing private storage."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from urllib.parse import unquote


def asset(root: Path, path: str) -> tuple[str, bytes] | None:
    relative = unquote(path).lstrip("/") or "index.html"
    wanted = (root / relative).resolve()
    if not wanted.is_relative_to(root.resolve()):
        return None
    candidates = [wanted, wanted.with_suffix(".html"), wanted / "index.html"]
    for candidate in candidates:
        if candidate.resolve().is_relative_to(root.resolve()) and candidate.is_file():
            kind = mimetypes.guess_type(candidate)[0] or "application/octet-stream"
            return kind, candidate.read_bytes()
    return None
