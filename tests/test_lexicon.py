# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""File-frequency, coverage, provenance and concordance checks on synthetic text."""

import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research/lexicon/build.py"
spec = importlib.util.spec_from_file_location("lexicon_build", SCRIPT)
assert spec
assert spec.loader
lexicon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lexicon)


@pytest.fixture
def source(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    source.mkdir()
    works = []
    for sha, year, author, group, pack, format_, status in (
        ("a", 1992, "Ada", "Crew", "p1", "ansi", "ok"),
        ("b", 1992, "ADA", "crew", "p1", "ansi", "ok"),
        ("c", 1997, "A.D.A.", "READ THE INI FILE", "p2", "ascii", "ok"),
        ("d", 1995, None, None, "p3", "rip", "error"),
        ("e", None, None, None, "p4", "ansi", "ok"),
    ):
        works.append(
            {
                "sha256": sha * 64,
                "year": year,
                "sauce_author": author,
                "sauce_group": group,
                "pack_sha256": pack,
                "pack": pack,
                "path": f"{sha}.txt",
                "sauce_title": None,
                "archive": "synthetic",
                "pack_url": "https://example.invalid/",
                "format": format_,
                "decoding": status,
                "decoding_error": "unsupported_format" if status == "error" else None,
                "grid_sha256": None,
                "content_kind": "text" if status == "ok" else None,
            }
        )
    texts = [
        {"sha256": "a" * 64, "row": 1, "text": "Sysop sysop naïve Straße café"},
        {"sha256": "a" * 64, "row": 2, "text": "call_sysop cafe\u0301"},
        {"sha256": "b" * 64, "row": 1, "text": "SYSOP"},
        {"sha256": "c" * 64, "row": 3, "text": "greets cosysop rs 123 </script>"},
    ]
    for name, rows in (("works", works), ("text", texts)):
        pq.write_table(pa.Table.from_pylist(rows), source / f"{name}.parquet")
    manifest = {
        "name": "works",
        "version": "5",
        "extractors": {"text": "2"},
        "tables": {
            name: {"file": f"{name}.parquet", "sha256": lexicon.digest(source / f"{name}.parquet")}
            for name in ("works", "text")
        },
    }
    (source / "manifest.json").write_text(json.dumps(manifest))
    return source


@pytest.fixture
def built(source: Path, tmp_path: Path) -> tuple[Path, dict]:
    root = tmp_path / "built"
    return root, lexicon.build(source, root)


def test_frequency_counts_files_instead_of_repeated_words(built: tuple[Path, dict]) -> None:
    root, data = built
    words = {word["term"]: word for word in data["lexical"]}
    assert words["sysop"]["works"] == 2
    assert words["sysop"]["occurrences"] == 4
    assert words["sysop"]["packs"] == 1
    assert len(words["sysop"]["examples"]) == 1
    assert words["café"]["occurrences"] == 2
    assert "strasse" in words
    assert "rs" not in words
    assert "123" not in words
    with (root / "output/lexicon.csv").open() as file:
        rows = list(csv.DictReader(file))
    assert sum(int(row["occurrences"]) for row in rows) == data["summary"]["tokens"]


def test_coverage_includes_textless_ansi_and_separates_unsupported(
    built: tuple[Path, dict],
) -> None:
    _, data = built
    assert data["summary"]["works"] == 5
    assert data["summary"]["text_works"] == 3
    assert data["summary"]["decoded"] == 4
    assert data["summary"]["unsupported"] == 1
    assert data["totals"]["1990–1993"]["bbs"] == 2
    assert data["totals"]["Unknown"]["ansi_decoded"] == 1
    assert data["totals"]["Unknown"]["text"] == 0
    assert data["totals"]["1997–1999"]["greets"] == 0  # ASCII is outside ANSI denominator.


def test_credits_preserve_variants_without_resolving_aliases(built: tuple[Path, dict]) -> None:
    _, data = built
    authors = {r["key"]: r for r in data["authors"]}
    assert authors["ada"]["variants"] == ["ADA", "Ada"]
    assert authors["ada"]["works"] == 2
    assert authors["a.d.a."]["status"] == "sauce_string_unresolved"
    assert data["summary"]["authors"] == 2
    groups = {r["key"]: r for r in data["groups"]}
    assert groups["read the ini file"]["review_flag"] == "possible_placeholder"


def test_report_escapes_source_text_and_records_algorithm(built: tuple[Path, dict]) -> None:
    root, data = built
    html = (root / "output/report.html").read_text()
    embedded = html.split('<script type="application/json" id="data">', 1)[1].split("</script>", 1)[
        0
    ]
    assert json.loads(embedded) == data
    assert "</script>" not in embedded
    assert data["analysis"]["asserted_by"] == "algo:lexicon@1"
    assert data["analysis"]["code_sha256"]["build.py"] == lexicon.digest(SCRIPT)


def test_rebuild_is_identical_and_source_is_unchanged(source: Path, tmp_path: Path) -> None:
    before = {p.name: lexicon.digest(p) for p in source.iterdir()}
    root = tmp_path / "built"
    lexicon.build(source, root)
    first = {p.name: lexicon.digest(p) for p in (root / "output").iterdir()}
    lexicon.build(root / "snapshot", root)
    assert first == {p.name: lexicon.digest(p) for p in (root / "output").iterdir()}
    assert before == {p.name: lexicon.digest(p) for p in source.iterdir()}


def test_tampered_source_is_rejected(source: Path, tmp_path: Path) -> None:
    with (source / "text.parquet").open("ab") as file:
        file.write(b"changed")
    with pytest.raises(ValueError, match="digest mismatch"):
        lexicon.build(source, tmp_path / "built")


@pytest.mark.parametrize(
    ("filters", "expected"),
    [
        ([], 3),
        (["--year-max", "1991"], 0),
        (["--author", "ada"], 3),
        (["--group", "other"], 0),
        (["--limit", "1"], 1),
    ],
)
def test_concordance_matches_whole_tokens_and_filters(
    built: tuple[Path, dict],
    filters: list[str],
    expected: int,
) -> None:
    root, _ = built
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "research/lexicon/concordance.py"),
            "sysop",
            "--snapshot",
            str(root / "snapshot"),
            *filters,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    rows = [json.loads(line) for line in result.stdout.splitlines()]
    assert len(rows) == expected
    assert all(row["sha256"] != "c" * 64 for row in rows)  # cosysop does not match.


@pytest.mark.parametrize("term", ["CAFÉ", "cafe\u0301"])
def test_concordance_normalizes_unicode_input(built: tuple[Path, dict], term: str) -> None:
    root, _ = built
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "research/lexicon/concordance.py"),
            term,
            "--snapshot",
            str(root / "snapshot"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert len(result.stdout.splitlines()) == 2
