# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
import shutil
from pathlib import Path

from tm.cli import app
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[2] / "corpus"
runner = CliRunner()


def copy_corpus(tmp_path: Path) -> Path:
    root = tmp_path / "corpus"
    shutil.copytree(ROOT, root)
    return root


def test_corpus_check_passes_on_repository() -> None:
    result = runner.invoke(app, ["corpus", "check", "--root", str(ROOT)])
    assert result.exit_code == 0, result.output


def test_corpus_check_reports_invalid_file(tmp_path: Path) -> None:
    root = copy_corpus(tmp_path)
    (root / "collections" / "broken.yaml").write_text(
        "title: {en: x, fr: x}\nwhere: {colour: [red]}\n"
    )
    result = runner.invoke(app, ["corpus", "check", "--root", str(root)])
    assert result.exit_code == 1
    assert "broken.yaml" in result.output


def test_corpus_check_reports_stale_schema_then_schema_fixes_it(tmp_path: Path) -> None:
    root = copy_corpus(tmp_path)
    (root / "schema" / "radios.schema.json").write_text("{}")
    assert runner.invoke(app, ["corpus", "check", "--root", str(root)]).exit_code == 1
    assert runner.invoke(app, ["corpus", "schema", "--root", str(root)]).exit_code == 0
    assert runner.invoke(app, ["corpus", "check", "--root", str(root)]).exit_code == 0


def test_ingest_pack_refuses_an_unknown_source(tmp_path: Path) -> None:
    result = runner.invoke(app, ["ingest", "pack", str(tmp_path), "--source", "nowhere"])
    assert result.exit_code == 2
    assert "unknown source" in result.output
