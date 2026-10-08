# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Guard for ADR 0012: the declared version of the decoder and renderer matches their code.

When this fails after a change to the code in COVERS:
  1. raise the version in `tm_render/versions.py` by one;
  2. add the new digest (printed below) under that version in PINS;
  3. keep the old entries: they are the history of what each version was.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import pytest
import tm_render
from tm_render.versions import DECODER_VERSION, RENDERER_VERSION

PACKAGE = Path(tm_render.__file__).parent
COVERS = {
    "decoder": ("ansi.py", "sauce.py", "grid.py"),
    "renderer": ("conservation.py",),
}
DECLARED = {"decoder": DECODER_VERSION, "renderer": RENDERER_VERSION}
PINS = {
    "decoder": {
        "1": "44389ece653d37c069bc8bf98d8e4bdea16f8506ee4a5411cf83acbfbe8205eb",
        "2": "e9bbf4a74b73604fd9bf391024ee92c5fc128dd8b716236813958e5fd9795dec",
    },
    "renderer": {"1": "acf2f900bd645c61dac80da37121cceab3abb36ae5bbbc627da178422e6d5c28"},
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
    return ast_digest(*(PACKAGE.joinpath(name).read_text("utf-8") for name in COVERS[kind]))


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
