# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Ask Discmaster where else each pack archive existed, and since when (lead I33, Q21).

Discmaster (discmaster.textfiles.com) indexes the files of the CD-ROMs, disks and FTP captures on
the Internet Archive, each with the date it carried there. A byte-identical copy of a pack found
on a shareware CD or an FTP site is a dated witness that does not descend from 16colo.

For every pack archive the museum holds (any scene archive), the archive is read from the
originals store, its BLAKE3 computed, and Discmaster searched by it. One request at a time, a
pause between them, our User-Agent; resumable: an archive already in the output is not asked
again. One JSON line per archive in `data/discmaster/witnesses.jsonl` (local, never in Git):

    {"sha256", "blake3", "archive", "path", "asked_at", "hits": [{"item", "file", "date", "size"}]}

    uv run python scripts/discmaster_witness.py [data/discmaster/witnesses.jsonl]
"""

from __future__ import annotations

import datetime as dt
import json
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import blake3
from sqlalchemy import create_engine, text
from tm.config import settings
from tm.storage import S3Store, get_original, s3_client

SEARCH = "https://discmaster.textfiles.com/search?b3sum={}&outputAs=json"
USER_AGENT = "textmode-atlas/0.1 (https://github.com/nicolasbridelance/textmode-atlas)"
PAUSE_SECONDS = 1.0
RETRY_SECONDS = (30, 120, 600)
PACKS = """
select p.pack_sha256, p.archive, a.source_path
from pack_split p join artifact a on a.sha256 = p.pack_sha256
order by p.archive, a.source_path
"""


def hits(found: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """What a witness needs from Discmaster's answer: where the copy sits and its date there."""
    return [
        {"item": hit["itemid"], "file": hit["fileid"], "date": hit.get("ts"), "size": hit["size"]}
        for hit in found
    ]


def asked(output: Path) -> set[str]:
    if not output.exists():
        return set()
    return {json.loads(line)["sha256"] for line in output.open(encoding="utf-8")}


def search(b3sum: str) -> list[dict[str, Any]]:
    """Discmaster's hits for a BLAKE3, waiting out refusals and server errors."""
    request = urllib.request.Request(SEARCH.format(b3sum), headers={"User-Agent": USER_AGENT})
    for wait in (*RETRY_SECONDS, None):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read())
        except (urllib.error.URLError, TimeoutError) as err:
            if wait is None:
                raise
            print(f"waiting {wait}s after {err}", flush=True)
            time.sleep(wait)
    raise AssertionError("unreachable")


def packs() -> Iterator[tuple[str, str, str]]:
    with create_engine(settings().database_url).connect() as conn:
        yield from conn.execute(text(PACKS)).tuples()


def main() -> None:
    output = Path(sys.argv[1] if len(sys.argv) > 1 else "data/discmaster/witnesses.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    done = asked(output)
    store = S3Store(s3_client(), settings().originals_bucket)
    todo = [pack for pack in packs() if pack[0] not in done]
    print(f"{len(done)} already asked, {len(todo)} to ask", flush=True)
    with output.open("a", encoding="utf-8") as out:
        for count, (sha256, archive, path) in enumerate(todo, start=1):
            b3sum = blake3.blake3(get_original(store, sha256)).hexdigest()
            found = hits(search(b3sum))
            now = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
            line = {"sha256": sha256, "blake3": b3sum, "archive": archive, "path": path}
            out.write(json.dumps({**line, "asked_at": now, "hits": found}) + "\n")
            out.flush()
            if found:
                print(f"{count}/{len(todo)} {path}: {len(found)} copies", flush=True)
            time.sleep(PAUSE_SECONDS)


if __name__ == "__main__":
    main()
