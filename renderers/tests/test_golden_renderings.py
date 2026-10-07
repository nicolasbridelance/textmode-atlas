# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Determinism: every golden artifact renders to the recorded pixels, the same file every time.

The recorded pixels are also ansilove's (checked by `scripts/check_ansilove_parity.py`).
"""

import json
from pathlib import Path
from typing import Any

import pytest
from tm_render.ansi import decode
from tm_render.conservation import BitmapFont, Settings, render

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "tests" / "golden"
EXPECTED: dict[str, dict[str, Any]] = json.loads((GOLDEN / "renderings.json").read_text())
FONT = BitmapFont.load(ROOT / "corpus/fonts/ibm-vga-8x16.f16")


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_golden_rendering_is_reproducible(name: str) -> None:
    decoded = decode((GOLDEN / name).read_bytes())
    settings = Settings.from_sauce(decoded.sauce)
    first, second = (render(decoded.grid, FONT, settings) for _ in range(2))
    assert first.recipe["pixels_sha256"] == EXPECTED[name]["pixels_sha256"]
    assert first.png == second.png
    assert first.recipe == second.recipe
