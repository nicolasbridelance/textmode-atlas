# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Packs written and ingested by the dataset and pilot tests, and copies of the definitions."""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path

from sqlalchemy import Connection
from stores import Stores
from tm.packs import SIXTEEN_COLO, PackSource, ingest_pack

ROOT = Path(__file__).resolve().parents[2]
HORIZON = (ROOT / "tests/golden/ansi/horizon.ans").read_bytes()
TEST_BELOW = 52


def ingest(
    db: Connection,
    stores: Stores,
    path: Path,
    members: dict[str, bytes],
    split: str = "",
    *,
    source: PackSource = SIXTEEN_COLO,
) -> None:
    """Write and ingest a pack; with `split`, vary the archive comment until its hash falls in
    that split (first byte below 52: test)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1000):
        with zipfile.ZipFile(path, "w") as archive:
            archive.comment = str(attempt).encode()
            for name, data in members.items():
                archive.writestr(name, data)
        is_test = hashlib.sha256(path.read_bytes()).digest()[0] < TEST_BELOW
        if not split or split == ("test" if is_test else "train"):
            break
    ingest_pack(db, stores.originals, path, source)


def definition(tmp_path: Path, name: str = "catalogue") -> Path:
    copy = tmp_path / "definitions" / name
    shutil.copytree(ROOT / "datasets" / name, copy)
    return copy
