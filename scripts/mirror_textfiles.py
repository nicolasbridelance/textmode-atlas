# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Mirror textfiles.com's artpacks (artscene.textfiles.com/artpacks/<year>/) into data/textfiles.

Politely, as the source note asks: one request at a time, a pause between downloads, a named
User-Agent. Resumable: a file already present with the listed size is not fetched again. The
listing's rows (year, file, size, description) are kept in `index.tsv`, since the descriptions
name the group and often the month of release. Each fetch is recorded in `acquisitions.tsv`
(ADR 0021) with its time and the server's `Last-Modified` and `ETag`, for
`tm ingest acquisitions --source textfiles`.

    uv run python scripts/mirror_textfiles.py [data/textfiles]
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "http://artscene.textfiles.com/artpacks/"
YEARS = range(1992, 2009)
USER_AGENT = "textmode-atlas/0.1 (https://github.com/nicolasbridelance/textmode-atlas)"
PAUSE_SECONDS = 0.5
ACQUISITION_COLUMNS = (
    "path",
    "url",
    "method",
    "retrieved_at",
    "retrieved_basis",
    "remote",
    "sha256",
)
ROW = re.compile(
    r'<A HREF="(?P<file>[^"/]+)">[^<]*</A>.*?'
    r"<TD>\s*(?P<size>\d+)<BR><TD>\s*(?P<description>[^<\n]*)",
    re.IGNORECASE,
)


def fetch(url: str) -> bytes:
    return fetch_with_headers(url)[0]


def fetch_with_headers(url: str) -> tuple[bytes, dict[str, str]]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        kept = {k: response.headers[k] for k in ("Last-Modified", "ETag") if response.headers[k]}
        return response.read(), kept


def record(root: Path, path: str, url: str, data: bytes, remote: dict[str, str]) -> None:
    """Append one acquisition, in the columns `tm ingest acquisitions` reads."""
    record_file = root / "acquisitions.tsv"
    new = not record_file.exists()
    with record_file.open("a", newline="", encoding="utf-8") as out:
        writer = csv.writer(out, delimiter="\t", lineterminator="\n")
        if new:
            writer.writerow(ACQUISITION_COLUMNS)
        now = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
        sha = hashlib.sha256(data).hexdigest()
        writer.writerow([path, url, "http", now, "recorded", json.dumps(remote), sha])


def listing(year: int) -> list[tuple[str, int, str]]:
    page = fetch(f"{BASE}{year}/").decode("latin-1")
    return [
        (m["file"], int(m["size"]), html.unescape(m["description"]).strip())
        for m in ROW.finditer(page)
    ]


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "data/textfiles") / "artpacks"
    root.mkdir(parents=True, exist_ok=True)
    rows = [(year, *row) for year in YEARS for row in listing(year)]
    with (root / "index.tsv").open("w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out, delimiter="\t", lineterminator="\n")
        writer.writerow(["year", "file", "size", "description"])
        writer.writerows(rows)
    fetched = 0
    for year, name, size, _ in rows:
        target = root / str(year) / name
        if target.exists() and target.stat().st_size == size:
            continue
        target.parent.mkdir(exist_ok=True)
        url = f"{BASE}{year}/{urllib.parse.quote(name)}"  # `#` in names
        try:
            data, remote = fetch_with_headers(url)
        except OSError as err:
            print(f"failed {year}/{name}: {err}")
            continue
        target.write_bytes(data)
        record(root, f"{year}/{name}", url, data, remote)
        fetched += 1
        if len(data) != size:
            print(f"size {year}/{name}: listed {size}, got {len(data)}")
        time.sleep(PAUSE_SECONDS)
    print(f"{len(rows)} listed, {fetched} fetched")


if __name__ == "__main__":
    main()
