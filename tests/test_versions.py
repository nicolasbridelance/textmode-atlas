# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Guard for ADR 0012: the declared version of the decoder, renderer and feature extractor
matches their code.

When this fails after a change to the code in COVERS:
  1. raise the version in `tm_render/versions.py` (or `tm_analysis/versions.py`) by one;
  2. add the new digest (printed below) under that version in PINS;
  3. keep the old entries: they are the history of what each version was.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import pytest
import tm_analysis
import tm_render
from tm_analysis.versions import FEATURES_VERSION
from tm_render.versions import DECODER_VERSION, RENDERER_VERSION

RENDER = Path(tm_render.__file__).parent
ANALYSIS = Path(tm_analysis.__file__).parent
COVERS = {
    "decoder": (RENDER / "ansi.py", RENDER / "sauce.py", RENDER / "grid.py"),
    "renderer": (RENDER / "conservation.py",),
    "features": (ANALYSIS / "features.py",),
}
DECLARED = {"decoder": DECODER_VERSION, "renderer": RENDERER_VERSION, "features": FEATURES_VERSION}
PINS = {
    "decoder": {
        "1": "44389ece653d37c069bc8bf98d8e4bdea16f8506ee4a5411cf83acbfbe8205eb",
        "2": "2d265d8cbef4796364a6523b815a21156f2573ef354eae5a811038fc4b64b574",
        "3": "1f9b38b8579d77499978944519e3973949758b66fe274a1b2e045b0b53cde4e7",
    },
    "renderer": {"1": "acf2f900bd645c61dac80da37121cceab3abb36ae5bbbc627da178422e6d5c28"},
    "features": {"1": "6722aeabbaa4cbee87caa167ef6d32a9abb8adfea9aa36ecb889ffa357271079"},
}


def ast_digest(*sources: str) -> str:
    """SHA-256 of the syntax trees: comments, docstrings and formatting do not change it."""
    sha = hashlib.sha256()
    for source in sources:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            body = getattr(node, "body", None)
            if isinstance(body, list) and _starts_with_docstring(body):
                del body[0]
                body.extend([ast.Pass()] if not body else [])
        sha.update(ast.dump(tree).encode())
    return sha.hexdigest()


def _starts_with_docstring(body: list[ast.stmt]) -> bool:
    first = body[0] if body else None
    return (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
    )


def covered_digest(kind: str) -> str:
    return ast_digest(*(path.read_text("utf-8") for path in COVERS[kind]))


def test_digest_ignores_comments_docstrings_and_layout() -> None:
    base = ast_digest("def f(x):\n    return x + 1\n")
    noisy = ast_digest('def f(x):\n    """Doc."""\n    # a comment\n    return (x +\n  1)\n')
    assert base == noisy


def test_digest_sees_a_change_of_behavior() -> None:
    assert ast_digest("def f(x):\n    return x + 1\n") != ast_digest(
        "def f(x):\n    return x + 2\n"
    )


@pytest.mark.parametrize("kind", COVERS)
def test_declared_version_is_the_latest_pinned(kind: str) -> None:
    latest = str(max(int(version) for version in PINS[kind]))
    assert DECLARED[kind] == latest, f"{kind} declares {DECLARED[kind]}, latest pin is {latest}"


@pytest.mark.parametrize("kind", COVERS)
def test_code_matches_the_pin_of_its_version(kind: str) -> None:
    pinned = PINS[kind].get(DECLARED[kind])
    assert covered_digest(kind) == pinned, (
        f"the {kind} code changed without a new version (ADR 0012): "
        f'raise it and pin "{covered_digest(kind)}"'
    )
