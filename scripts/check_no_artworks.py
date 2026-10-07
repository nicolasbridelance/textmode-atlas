# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Refuse any artwork file tracked by Git, outside the golden artifacts (tests/golden/).

Checks: extensions of artwork and archive formats, and a maximum size per file.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ARTWORK_EXTENSIONS = {
    # text mode
    ".ans",
    ".asc",
    ".nfo",
    ".diz",
    ".xb",
    ".bin",
    ".adf",
    ".idf",
    ".pcb",
    ".avt",
    ".tnd",
    ".ice",
    ".rip",
    ".seq",
    ".prg",
    ".d64",
    ".atr",
    ".tti",
    ".t42",
    ".vdt",
    ".lbm",
    # music
    ".mod",
    ".xm",
    ".s3m",
    ".it",
    ".sid",
    ".mid",
    # archives and images
    ".zip",
    ".lha",
    ".lzh",
    ".arj",
    ".rar",
    ".7z",
    ".gif",
    ".png",
    ".jpg",
    ".jpeg",
}
# Golden artifacts and their renderings are made for the project (CC0, see REUSE.toml).
ALLOWED_PREFIXES = ("tests/golden/", "docs/assets/", "apps/museum/static/favicon")
MAX_BYTES = 512 * 1024


def violations(paths: list[str], root: Path) -> list[str]:
    found: list[str] = []
    for path in paths:
        if path.startswith(ALLOWED_PREFIXES):
            continue
        if Path(path).suffix.lower() in ARTWORK_EXTENSIONS:
            found.append(f"{path}: artwork file extension")
        elif (root / path).is_file() and (root / path).stat().st_size > MAX_BYTES:
            found.append(f"{path}: larger than {MAX_BYTES // 1024} KiB")
    return found


def tracked_files(root: Path) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in out.stdout.splitlines() if line]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    found = violations(tracked_files(root), root)
    for line in found:
        print(f"✗ {line}", file=sys.stderr)
    if not found:
        print("✓ no artwork file in the repository")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
