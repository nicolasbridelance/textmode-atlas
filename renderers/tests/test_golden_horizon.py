# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Decoding Horizon gives back exactly what its composer drew."""

import importlib.util
import sys
from pathlib import Path

from tm_render.ansi import decode

GOLDEN = Path(__file__).resolve().parents[2] / "tests" / "golden" / "ansi"
spec = importlib.util.spec_from_file_location("horizon", GOLDEN / "horizon.py")
assert spec
assert spec.loader
horizon = importlib.util.module_from_spec(spec)
sys.modules["horizon"] = horizon  # dataclasses resolve their module through sys.modules
spec.loader.exec_module(horizon)

SPACE, BLACK = 0x20, 0


def test_horizon_round_trip() -> None:
    expected = horizon.compose()
    decoded = decode((GOLDEN / "horizon.ans").read_bytes())
    assert (decoded.grid.cols, decoded.grid.rows) == (80, 40)
    assert decoded.skipped_sequences == 0
    for row, line in enumerate(expected):
        for col, want in enumerate(line):
            got = decoded.grid.cell(row, col)
            if got is None:  # trailing blanks are not written, as editors save files
                assert (want.char, want.bg) == (SPACE, BLACK), (row, col)
                continue
            assert (got.codepoint, got.fg, got.bg) == (want.char, want.fg, want.bg), (row, col)


def test_horizon_sauce() -> None:
    sauce = decode((GOLDEN / "horizon.ans").read_bytes()).sauce
    assert sauce is not None
    assert (sauce.title, sauce.author, sauce.group) == ("Horizon", "claude", "textmode-atlas")
    assert sauce.letter_spacing == "9px"
    assert not sauce.ice_colors
