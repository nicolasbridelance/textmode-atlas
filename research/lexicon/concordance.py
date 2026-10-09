# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Whole-token search with source rows, years and raw SAUCE credit filters."""

import argparse
import json
import unicodedata
from pathlib import Path

import duckdb
import typer
from build import TOKEN, tokens

FIELDS = ("sha256", "row", "text", "pack", "year", "path", "author", "group")
BATCH_SIZE = 1000


def conditions(args):
    where, params = ["true"], []
    for op, value in ((">=", args.year_min), ("<=", args.year_max)):
        if value is not None:
            where.append(f"w.year {op} ?")
            params.append(value)
    for field, value in (("sauce_author", args.author), ("sauce_group", args.group)):
        if value is not None:
            where.append(f"lower(trim(w.{field})) = lower(trim(?))")
            params.append(value)
    return " and ".join(where), params


def search(args, term):
    snapshot = args.snapshot.resolve()
    with duckdb.connect(
        config={
            "threads": 1,
            "memory_limit": "256MB",
            "temp_directory": str(snapshot.parent / "temp"),
        }
    ) as db:
        for table, name in (("works", "works"), ("lines", "text")):
            path = (snapshot / f"{name}.parquet").as_posix().replace("'", "''")
            db.execute(f"create view {table} as select * from '{path}'")
        where, params = conditions(args)
        cursor = db.execute(
            "select l.sha256,l.row,l.text,w.pack,w.year,w.path,w.sauce_author,w.sauce_group"
            " from lines l join works w using(sha256) where " + where + " order by l.sha256,l.row",
            params,
        )
        yield from matches(cursor, term, args.limit)


def matches(cursor, term, limit):
    found = 0
    while rows := cursor.fetchmany(BATCH_SIZE):
        for row in rows:
            if term in tokens(row[2]):
                yield dict(zip(FIELDS, row, strict=True))
                found += 1
                if found == limit:
                    return


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("term")
    repository = Path(__file__).resolve().parents[2]
    parser.add_argument(
        "--snapshot", type=Path, default=repository / "datasets/build/lexicon/1/snapshot"
    )
    parser.add_argument("--year-min", type=int)
    parser.add_argument("--year-max", type=int)
    parser.add_argument("--author", help="Exact raw SAUCE credit, case-insensitive")
    parser.add_argument("--group", help="Exact raw SAUCE group credit, case-insensitive")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    normalized = unicodedata.normalize("NFC", args.term).casefold()
    terms = tokens(normalized)
    if len(terms) != 1 or not TOKEN.fullmatch(normalized):
        parser.error("Pass one lexical token of at least three characters, not a phrase or number.")
    if args.limit < 1 or (
        args.year_min is not None and args.year_max is not None and args.year_min > args.year_max
    ):
        parser.error("Use a positive limit and a valid year interval.")
    return args, terms[0]


def main():
    args, term = arguments()
    for match in search(args, term):
        typer.echo(json.dumps(match, ensure_ascii=False))


if __name__ == "__main__":
    main()
