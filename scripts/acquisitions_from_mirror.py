# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Write `acquisitions.tsv` for a mirror made before fetching recorded itself (ADR 0021).

Each file's URL is the base URL plus its path in the mirror. Its time is either:

- `--retrieved-at` with basis `mirror_run`: the end of the mirroring run (rsync kept the remote
  file dates, which go to `remote.mtime`);
- or each file's own date, with basis `file_mtime`, when the mirror wrote files as it fetched.

    uv run python scripts/acquisitions_from_mirror.py data/16colo/archive-pack \\
        rsync://16colo.rs/archive-pack/ --method rsync --retrieved-at 2026-10-08T11:48:20Z
    uv run python scripts/acquisitions_from_mirror.py data/textfiles/artpacks \\
        http://artscene.textfiles.com/artpacks/ --method http
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import urllib.parse
from pathlib import Path

COLUMNS = ("path", "url", "method", "retrieved_at", "retrieved_basis", "remote", "sha256")
SKIP = {"acquisitions.tsv", "index.tsv"}


def iso(timestamp: float) -> str:
    return dt.datetime.fromtimestamp(timestamp, dt.UTC).isoformat(timespec="seconds")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mirror", type=Path)
    parser.add_argument("base")
    parser.add_argument("--method", choices=["rsync", "http"], required=True)
    parser.add_argument("--retrieved-at", help="end of the run, if files kept remote dates")
    args = parser.parse_args()
    files = sorted(p for p in args.mirror.rglob("*") if p.is_file() and p.name not in SKIP)
    out = args.mirror / "acquisitions.tsv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(COLUMNS)
        for path in files:
            relative = path.relative_to(args.mirror).as_posix()
            mtime = iso(path.stat().st_mtime)
            run = args.retrieved_at is not None
            writer.writerow([
                relative,
                args.base + urllib.parse.quote(relative),
                args.method,
                args.retrieved_at if run else mtime,
                "mirror_run" if run else "file_mtime",
                json.dumps({"mtime": mtime} if run else {}),
                hashlib.sha256(path.read_bytes()).hexdigest(),
            ])  # fmt: skip
    print(f"{len(files)} files, written to {out}")


if __name__ == "__main__":
    main()
