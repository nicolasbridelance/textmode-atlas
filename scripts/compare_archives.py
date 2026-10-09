# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Compare the textfiles.com artpacks with 16colo by hash, for the archives note (Q21, Q26).

For every archive of the textfiles mirror: is there a 16colo pack of the same name, are the
archives the same bytes, and how many of its files 16colo holds, in the namesake or in any pack.
Only hashes are compared, no work is read, so all splits are used. 16colo's side comes from the
database (`tm ingest pack`), the textfiles side from the mirror (`mirror_textfiles.py`).

    uv run python scripts/compare_archives.py data/textfiles/artpacks out.tsv
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

from sqlalchemy import create_engine, text
from tm.archives import ArchiveError, expand
from tm.config import settings
from tm.packs import ARCHIVES
from tm.storage import sha256_hex

PACKS = """
select lower(w.title) as stem, a.sha256 as archive, m.sha256 as member
from pack_split p
join artifact a on a.sha256 = p.pack_sha256
join version v on v.id = a.version_id
join work w on w.id = v.work_id
left join set_member m on m.set_work_id = p.set_work_id
where p.archive = '16colo'
"""
FIELDS = [
    "year", "file", "description", "status", "namesake", "same_bytes", "members",
    "in_namesake", "in_16colo",
]  # fmt: skip


class SixteenColo:
    """16colo's packs as hashes: archive bytes, and member files by pack name and overall."""

    def __init__(self) -> None:
        self.archives: set[str] = set()
        self.by_name: dict[str, set[str]] = defaultdict(set)
        self.members: set[str] = set()
        with create_engine(settings().database_url).connect() as conn:
            for stem, archive, member in conn.execute(text(PACKS)):
                self.archives.add(archive)
                self.by_name[stem].update([member] if member else [])
                self.members.update([member] if member else [])


def compare(path: Path, colo: SixteenColo) -> dict[str, object]:
    stem = path.stem.lower()
    namesake = colo.by_name.get(stem)
    row: dict[str, object] = {
        "file": path.name,
        "namesake": namesake is not None,
        "same_bytes": sha256_hex(path.read_bytes()) in colo.archives,
    }
    try:
        expanded = expand(path, ARCHIVES[path.suffix.lower()])
    except ArchiveError as err:
        return row | {"status": err.kind}
    members = {sha256_hex(data) for _, data in expanded.members}
    return row | {
        "status": "partial" if expanded.unreadable else "ok",
        "members": len(members),
        "in_namesake": len(members & namesake) if namesake is not None else 0,
        "in_16colo": len(members & colo.members),
    }


def main() -> None:
    mirror, out = Path(sys.argv[1]), Path(sys.argv[2])
    colo = SixteenColo()
    with (mirror / "index.tsv").open(encoding="utf-8") as index:
        listed = list(csv.DictReader(index, delimiter="\t"))
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for entry in listed:
            path = mirror / entry["year"] / entry["file"]
            if path.suffix.lower() not in ARCHIVES or not path.exists():
                continue
            row = compare(path, colo)
            writer.writerow(row | {"year": entry["year"], "description": entry["description"]})
    print(f"{len(listed)} listed, written to {out}")


if __name__ == "__main__":
    main()
