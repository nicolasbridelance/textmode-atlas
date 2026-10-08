# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Originals and derived buckets on disk, shared by the pipeline tests (fixture `stores`)."""

from __future__ import annotations

from pathlib import Path

from tm.storage import LocalStore


class Stores:
    def __init__(self, root: Path) -> None:
        self.originals = LocalStore(root / "originals")
        self.derived = LocalStore(root / "derived")
