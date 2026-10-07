# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("msg", ROOT / "scripts" / "check_commit_msg.py")
assert spec
assert spec.loader
msg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(msg)


@pytest.mark.parametrize(
    "message",
    [
        "feat(render): decode ANSI into a grid",
        "fix: keep column 9 for box-drawing glyphs\n\nWhy it matters.",
        "chore(hygiene): purge post-feat(render)",
        "feat(api)!: drop the v0 search endpoint",
        "Merge branch 'main' into scaffold",
        "fixup! feat(render): decode ANSI into a grid",
    ],
)
def test_valid_messages(message: str) -> None:
    assert msg.problems(message) == []


@pytest.mark.parametrize(
    ("message", "problem"),
    [
        ("Scaffold the monorepo", "subject must be"),
        ("feature: add things", "subject must be"),
        ("feat(Render): x", "subject must be"),
        ("feat: " + "x" * 80, "max 72"),
        ("feat: add the decoder.", "period"),
        ("feat: add the decoder\nno blank line", "second line"),
        ("# only a comment\n", "empty"),
    ],
)
def test_invalid_messages(message: str, problem: str) -> None:
    assert any(problem in p for p in msg.problems(message))
