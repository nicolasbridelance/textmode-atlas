# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check", ROOT / "scripts" / "check_no_artworks.py")
assert spec
assert spec.loader
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def test_artwork_extensions_are_refused(tmp_path: Path) -> None:
    found = check.violations(["corpus/acid-0896.ZIP", "notes/logo.ans", "ok.py"], tmp_path)
    assert len(found) == 2


def test_golden_artifacts_are_allowed(tmp_path: Path) -> None:
    assert check.violations(["tests/golden/ansi/horizon.ans"], tmp_path) == []


def test_large_files_are_refused(tmp_path: Path) -> None:
    (tmp_path / "big.txt").write_bytes(b"x" * (check.MAX_BYTES + 1))
    assert check.violations(["big.txt"], tmp_path) == ["big.txt: larger than 512 KiB"]


def test_repository_is_clean() -> None:
    assert check.violations(check.tracked_files(ROOT), ROOT) == []
