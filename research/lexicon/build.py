# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Build a private exploratory lexical lab from a verified train-only snapshot.

Run with the project's Python; one DuckDB thread, no database or service writes.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import logging
import re
import shutil
import unicodedata
from pathlib import Path

log = logging.getLogger(__name__)

FIRST_YEAR, LAST_YEAR = 1990, 2026
MIN_TOKEN = 3
DISPLAY_TERMS, CONTEXT_TERMS, CONTEXT_PACKS = 2000, 250, 3
DISPLAY_CREDITS = 300
VERSION = "1"
TOKEN = re.compile(r"[^\W_]+", re.UNICODE)
ERAS = ("1990–1993", "1994–1996", "1997–1999", "2000–2004", "2005–2012", "2013–2026", "Unknown")
STOP = set(
    [
        "the",
        "and",
        "for",
        "this",
        "you",
        "all",
        "that",
        "with",
        "like",
        "here",
        "but",
        "one",
        "from",
        "your",
        "not",
        "are",
        "out",
        "was",
        "have",
        "just",
        "can",
        "some",
        "new",
        "time",
        "what",
        "now",
        "com",
        "www",
        "org",
        "net",
        "http",
        "https",
        "it",
        "its",
        "to",
        "of",
        "in",
        "is",
        "on",
        "as",
        "at",
        "be",
        "by",
        "we",
        "our",
        "an",
        "a",
        "or",
        "do",
        "no",
        "if",
        "me",
        "my",
        "so",
        "us",
        "they",
        "them",
        "their",
        "will",
        "would",
        "has",
        "had",
        "his",
        "her",
        "than",
        "then",
        "also",
        "more",
        "get",
        "see",
        "about",
        "into",
        "these",
        "those",
        "there",
        "when",
        "who",
        "how",
        "too",
        "only",
        "any",
        "very",
        "should",
        "must",
        "don't",
        "doesn't",
        "it's",
        "i'm",
        "i'll",
        "you've",
        "you're",
        "we're",
        "been",
        "being",
        "were",
        "did",
        "does",
        "let's",
        "may",
        "please",
    ]
)
MARKERS = {
    "bbs": {"sysop", "node", "baud", "running", "bbs", "call"},
    "greets": {"greets", "greetings", "hellos"},
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def era(year: int | None) -> str:
    if year is None or not FIRST_YEAR <= year <= LAST_YEAR:
        return "Unknown"
    for limit, name in zip((1993, 1996, 1999, 2004, 2012, 2026), ERAS, strict=False):
        if year <= limit:
            return name
    return "Unknown"


def tokens(text: str) -> list[str]:
    return [
        t
        for t in TOKEN.findall(unicodedata.normalize("NFC", text).casefold())
        if len(t) >= MIN_TOKEN and not t.isdigit()
    ]


def write_csv(path: Path, columns: list[str], rows) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)


def source_lines(db):
    cursor = db.execute("select sha256, row, text from lines order by sha256, row")
    while batch := cursor.fetchmany(2000):
        yield from batch


def documents(db):
    current, parts = None, []
    for sha, _, text in source_lines(db):
        if current is not None and sha != current:
            yield current, " ".join(parts)
            parts = []
        current = sha
        parts.append(text)
    if current is not None:
        yield current, " ".join(parts)


def snapshot(source: Path, target: Path) -> dict:
    manifest = json.loads((source / "manifest.json").read_text())
    target.mkdir(parents=True, exist_ok=True)
    for name in ("works", "text"):
        info = manifest["tables"][name]
        src, dst = source / info["file"], target / info["file"]
        expected = info["sha256"]
        if digest(src) != expected:
            raise ValueError(f"Source digest mismatch: {src}")
        if not dst.exists() or digest(dst) != expected:
            shutil.copyfile(src, dst)
        if digest(dst) != expected:
            raise ValueError(f"Snapshot digest mismatch: {dst}")
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def registry(meta: list[dict], field: str) -> list[dict]:
    found = {}
    for w in meta:
        raw = w[field] or ""
        key = unicodedata.normalize("NFC", raw).casefold().strip()
        if not key:
            continue
        r = found.setdefault(
            key,
            {
                "key": key,
                "variants": set(),
                "works": 0,
                "packs": set(),
                "years": [],
                "example_sha256": w["sha256"],
            },
        )
        r["variants"].add(raw)
        r["works"] += 1
        r["packs"].add(w["pack_sha256"])
        if w["year"] is not None:
            r["years"].append(w["year"])
    result = []
    for r in found.values():
        r["variants"] = sorted(r["variants"])
        r["packs"] = len(r["packs"])
        years = r.pop("years")
        r["first_filing_year"] = min(years) if years else None
        r["last_filing_year"] = max(years) if years else None
        r["status"] = "sauce_string_unresolved"
        r["review_flag"] = (
            "possible_placeholder"
            if re.search(r"read.*(ini|nfo|info)|unknown|anonymous|^none$|^n/?a$", r["key"])
            else ""
        )
        result.append(r)
    return sorted(result, key=lambda r: (-r["works"], r["key"]))


def open_database(root):
    import duckdb

    db = duckdb.connect(
        config={
            "threads": 1,
            "memory_limit": "512MB",
            "temp_directory": str(root / "temp"),
            "preserve_insertion_order": False,
        }
    )
    for table, file in (("works", "works"), ("lines", "text")):
        path = (root / "snapshot" / f"{file}.parquet").as_posix().replace("'", "''")
        db.execute(f"create view {table} as select * from '{path}'")
    return db


def metadata(db):
    cur = db.execute("select * from works order by sha256")
    columns = [c[0] for c in cur.description]
    meta = [dict(zip(columns, row, strict=True)) for row in cur.fetchall()]
    by_sha = {w["sha256"]: w for w in meta}
    for w in meta:
        w["era"] = era(w["year"])
    return meta, by_sha


def measure(db, meta, by_sha):
    counts = collections.Counter()
    frequency = collections.Counter()
    by_era = {e: collections.Counter() for e in ERAS}
    totals = {
        e: {"all": 0, "decoded": 0, "text": 0, "ansi_decoded": 0, "bbs": 0, "greets": 0}
        for e in ERAS
    }
    text_shas = set()
    for w in meta:
        t = totals[w["era"]]
        t["all"] += 1
        t["decoded"] += w["decoding"] == "ok"
        t["ansi_decoded"] += w["decoding"] == "ok" and w["format"] == "ansi"
    for sha, text in documents(db):
        if sha not in by_sha:
            raise ValueError(f"Text references absent work: {sha}")
        ts = tokens(text)
        unique = set(ts)
        counts.update(unique)
        frequency.update(ts)
        w = by_sha[sha]
        e = w["era"]
        by_era[e].update(unique)
        totals[e]["text"] += 1
        text_shas.add(sha)
        if w["format"] == "ansi" and w["decoding"] == "ok":
            for name, markers in MARKERS.items():
                totals[e][name] += bool(unique & markers)
    ranked = sorted(counts, key=lambda t: (-counts[t], t))
    return counts, frequency, by_era, totals, text_shas, ranked


def lexical_preview(db, by_sha, ranked, counts, frequency, by_era):
    shown = ranked[:DISPLAY_TERMS]
    examples = {t: [] for t in ranked[:CONTEXT_TERMS]}
    example_seen = {t: set() for t in examples}
    pack_seen = {t: set() for t in shown}
    shown_set = set(shown)
    for sha, text in documents(db):
        pack = by_sha[sha]["pack_sha256"]
        for term in set(tokens(text)) & shown_set:
            pack_seen[term].add(pack)
    for sha, row, text in source_lines(db):
        for term in set(tokens(text)) & examples.keys():
            w = by_sha[sha]
            # Up to three distinct representative packs, with original line and cell row.
            if len(examples[term]) < CONTEXT_PACKS and w["pack_sha256"] not in example_seen[term]:
                examples[term].append(
                    {
                        "sha256": sha,
                        "row": row,
                        "text": text,
                        "pack": w["pack"],
                        "year": w["year"],
                        "path": w["path"],
                    }
                )
                example_seen[term].add(w["pack_sha256"])
    lexical = [
        {
            "term": term,
            "works": counts[term],
            "occurrences": frequency[term],
            "packs": len(pack_seen[term]),
            "common": term in STOP,
            "eras": [by_era[e][term] for e in ERAS],
            "examples": examples.get(term, []),
        }
        for term in shown
    ]
    return lexical


def export_tables(
    out, db, meta, authors, groups, text_shas, counts, frequency, by_era, ranked, totals
):
    reg_columns = [
        "key",
        "variants",
        "works",
        "packs",
        "first_filing_year",
        "last_filing_year",
        "example_sha256",
        "status",
        "review_flag",
    ]
    for name, records in (("authors", authors), ("groups", groups)):
        write_csv(
            out / f"{name}.csv",
            reg_columns,
            [
                [
                    json.dumps(r[c], ensure_ascii=False) if c == "variants" else r[c]
                    for c in reg_columns
                ]
                for r in records
            ],
        )
    work_cols = [
        "sha256",
        "path",
        "sauce_title",
        "sauce_author",
        "sauce_group",
        "pack",
        "pack_sha256",
        "year",
        "archive",
        "pack_url",
        "format",
        "decoding",
        "decoding_error",
        "grid_sha256",
        "content_kind",
    ]
    write_csv(
        out / "works.csv",
        [*work_cols, "has_text", "credit_status"],
        [
            [w[c] for c in work_cols] + [w["sha256"] in text_shas, "sauce_credit_unresolved"]
            for w in meta
        ],
    )
    write_csv(
        out / "lexicon.csv",
        ["term", "works", "occurrences", "works_with_text_denominator", *ERAS],
        [
            [t, counts[t], frequency[t], len(text_shas), *(by_era[e][t] for e in ERAS)]
            for t in ranked
        ],
    )
    write_csv(
        out / "eras.csv",
        ["era", *next(iter(totals.values())).keys()],
        [[e, *totals[e].values()] for e in ERAS],
    )
    errors = db.execute(
        "select format, decoding, decoding_error, count(*) n from works "
        "where decoding is distinct from 'ok' group by all order by n desc, format"
    ).fetchall()
    write_csv(out / "decoding.csv", ["format", "status", "reason", "works"], errors)
    return errors


def summary(meta, text_shas, counts, frequency, authors, groups, db, errors):
    summary = {
        "works": len(meta),
        "decoded": sum(w["decoding"] == "ok" for w in meta),
        "text_works": len(text_shas),
        "lines": db.execute("select count(*) from lines").fetchone()[0],
        "tokens": sum(frequency.values()),
        "forms": len(counts),
        "authors": len(authors),
        "groups": len(groups),
        "author_credited": sum(bool((w["sauce_author"] or "").strip()) for w in meta),
        "group_credited": sum(bool((w["sauce_group"] or "").strip()) for w in meta),
        "unsupported": sum(n for _, _, reason, n in errors if reason == "unsupported_format"),
    }
    return summary


def write_report(out, data):
    (out / "analysis.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    embedded = (
        json.dumps(data, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    template = Path(__file__).with_name("report.html").read_text()
    (out / "report.html").write_text(template.replace("__DATA__", embedded))
    shutil.copyfile(Path(__file__).with_name("README.md"), out / "METHODS.md")


def build(source, root):
    manifest = snapshot(source, root / "snapshot")
    out = root / "output"
    out.mkdir(exist_ok=True)
    with open_database(root) as db:
        meta, by_sha = metadata(db)
        counts, frequency, by_era, totals, text_shas, ranked = measure(db, meta, by_sha)
        lexical = lexical_preview(db, by_sha, ranked, counts, frequency, by_era)
        authors, groups = registry(meta, "sauce_author"), registry(meta, "sauce_group")
        errors = export_tables(
            out, db, meta, authors, groups, text_shas, counts, frequency, by_era, ranked, totals
        )
        found = summary(meta, text_shas, counts, frequency, authors, groups, db, errors)
    data = {
        "analysis": {
            "name": "lexicon",
            "version": VERSION,
            "nature": "inferred",
            "asserted_by": f"algo:lexicon@{VERSION}",
            "recipe": {
                "normalization": "NFC+casefold",
                "min_token": MIN_TOKEN,
                "era_bounds": [1993, 1996, 1999, 2004, 2012, LAST_YEAR],
                "markers": {name: sorted(words) for name, words in MARKERS.items()},
                "display_terms": DISPLAY_TERMS,
                "display_credits": DISPLAY_CREDITS,
                "context_terms": CONTEXT_TERMS,
                "context_packs": CONTEXT_PACKS,
            },
            "code_sha256": {
                name: digest(Path(__file__).with_name(name))
                for name in ("build.py", "report.html", "README.md")
            },
        },
        "summary": found,
        "eras": list(ERAS),
        "totals": totals,
        "lexical": lexical,
        "authors": authors[:DISPLAY_CREDITS],
        "groups": groups[:DISPLAY_CREDITS],
        "errors": [list(row) for row in errors],
        "manifest": manifest,
        "method": "NFC + Unicode casefold; Unicode letter/digit tokens >=3 characters; "
        "numeric-only tokens excluded; document frequency counts once per SHA-256.",
    }
    write_report(out, data)
    return data


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    repository = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=repository / "datasets/build/works/5")
    parser.add_argument("--output", type=Path, default=repository / "datasets/build/lexicon/1")
    args = parser.parse_args()
    root = args.output.resolve()
    data = build(args.source.resolve(), root)
    log.info("%s", json.dumps(data["summary"], ensure_ascii=False))
    log.info("Report: %s", root / "output/report.html")


if __name__ == "__main__":
    main()
