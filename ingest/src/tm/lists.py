# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""`tm lists`: the lists a visit walks through (ADR 0023).

Packs, signatures, years and the work of the day, written to the public bucket under `lists/`
from the same decision as the works (`tm.export.decide`). A list names only works whose files
are shown; the site never filters. `lists/index.json` names every list written, so a run
removes the lists it no longer writes without listing the bucket.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import Row

from tm.export import ExportError, credit_of, decide, list_paths
from tm.storage import ObjectStore

INDEX = "lists/index.json"
DAYS = "lists/days.json"
DAYS_IN_YEAR = 366
YEAR_SAMPLE = 120
DAY_LEVELS = ("3", "7", "12")
DAY_COLS = 80
DAY_ROWS = range(20, 61)  # one or two screens: under a minute at 2,400 baud
SEED = "textmode-atlas lists 1"


@dataclass
class Lists:
    """Entries of every list, by path, before they are written."""

    entries: dict[str, list[dict[str, Any]]] = field(default_factory=lambda: defaultdict(list))
    heads: dict[str, dict[str, Any]] = field(default_factory=dict[str, dict[str, Any]])
    days: list[tuple[str, dict[str, Any]]] = field(default_factory=list[tuple[str, dict[str, Any]]])

    def add(self, row: Row[Any], level: str) -> None:
        entry = _entry(row, level)
        paths = list_paths(row)
        if paths["pack"]:
            self.heads[paths["pack"]] = {
                "pack": row.pack, "archive": row.archive, "url": row.pack_url, "year": row.year,
            }  # fmt: skip
        if paths["author"]:
            self.heads[paths["author"]] = {"author": entry["author"]}
        if paths["year"]:
            self.heads[paths["year"]] = {"year": row.year}
        for path in filter(None, paths.values()):
            self.entries[path].append(entry)
        if level in DAY_LEVELS and row.cols == DAY_COLS and row.rows in DAY_ROWS:
            self.days.append((_draw(row.sha256), entry))


def collect(rows: Iterable[Row[Any]]) -> Lists:
    """Every list, from the works whose files are shown."""
    lists = Lists()
    for row in rows:
        try:
            outcome, level = decide(row)
        except ExportError:
            continue  # refused by the export, so never named by a list
        if outcome == "files":
            lists.add(row, level)
    return lists


def write_lists(lists: Lists, public: ObjectStore) -> dict[str, int]:
    """Write every list that changed, and remove those the previous run wrote and this one
    does not."""
    files = {path: _list(path, lists) for path in lists.entries}
    files[DAYS] = {"works": [e for _, e in sorted(lists.days, key=_key)[:DAYS_IN_YEAR]]}
    previous: list[str] = json.loads(public.get(INDEX)) if public.exists(INDEX) else []
    removed = sorted(set(previous) - set(files))
    for path in removed:
        public.delete(path)
    written = sum(_put(public, path, value) for path, value in sorted(files.items()))
    _put(public, INDEX, sorted(files))
    return {"lists": len(files), "written": written, "removed": len(removed)}


def _list(path: str, lists: Lists) -> dict[str, Any]:
    entries = lists.entries[path]
    if path.startswith("lists/years/"):
        entries = sorted(entries, key=lambda e: _draw(e["sha256"]))[:YEAR_SAMPLE]
    elif path.startswith("lists/authors/"):
        entries = sorted(entries, key=lambda e: (e["year"] or 0, e["pack"] or "", e["path"]))
    else:
        entries = sorted(entries, key=lambda e: e["path"])
    return {**lists.heads[path], "works": entries}


def _entry(row: Row[Any], level: str) -> dict[str, Any]:
    credit = credit_of(row)
    return {
        "sha256": row.sha256,
        "title": credit["title"],
        "file": row.source_path.rsplit("/", 1)[-1],
        "path": row.pack_path or "",
        "author": credit["author"],
        "group": credit["group"],
        "pack": row.pack,
        "year": row.year,
        "cols": row.cols,
        "rows": row.rows,
        "level": level,
    }


def _draw(sha256: str) -> str:
    """A fixed, reproducible order: the hash of the work's hash and a seed."""
    return hashlib.sha256(f"{SEED} {sha256}".encode()).hexdigest()


def _key(item: tuple[str, dict[str, Any]]) -> str:
    return item[0]


def _put(public: ObjectStore, path: str, value: object) -> bool:
    data = (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode()
    if public.exists(path) and public.get(path) == data:
        return False
    public.put(path, data, "application/json")
    return True
