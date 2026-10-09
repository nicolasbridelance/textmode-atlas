# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Mirror textfiles.com's art collections beyond the yearly artpacks into data/textfiles.

The artpacks have their own script (`mirror_textfiles.py`). The other sections of
artscene.textfiles.com are trees of directories, each listed by a hand-made or Apache page:
ANSI and ASCII from BBSes, ASCII artpacks by group, the ACiD and iCE collections, RTTY and VT100
art. This walks the trees named on the command line and keeps every file under
`data/textfiles/<its path on the site>`, with the `.descs` files that describe a directory.

Politely, as the source note asks: one request at a time, a pause between requests, a named
User-Agent. A name without a dot is tried as a directory first (the server redirects `name` to
`name/`), and fetched as a file when it is not one. Previews the site draws (`.png/`), links
outside the tree and links to other sites are not followed. Resumable: a file already present
is not fetched again. Each fetch is recorded in `acquisitions.tsv` (ADR 0021), its path relative
to the root, for `tm ingest acquisitions --source textfiles`.

    uv run python scripts/mirror_textfiles_collections.py data/textfiles ansi ascii asciiart \
        acid/ARTPACKS acid/BBSMODS ice/icepacks ice/specials rtty vt100
"""

from __future__ import annotations

import re
import sys
import time
import urllib.error
import urllib.parse
from pathlib import Path

from mirror_textfiles import PAUSE_SECONDS, fetch_with_headers, record

SITE = "http://artscene.textfiles.com/"
HREF = re.compile(r'href="(?P<link>[^"#?]+)"', re.IGNORECASE)
NOT_FOUND = 404


def links(page: bytes, base: str) -> list[str]:
    """Absolute URLs of the entries a listing shows, inside its own directory, in page order."""
    found: list[str] = []
    for match in HREF.finditer(page.decode("latin-1")):
        # The pages are Latin-1, and so are the names on the server: `·` must travel as `%B7`.
        link = urllib.parse.quote(match["link"], safe="/%~:", encoding="latin-1")
        url = urllib.parse.urljoin(base, link)
        rest = url.removeprefix(base)
        if url == rest or not rest or rest.startswith(".png/") or "/" in rest.rstrip("/"):
            continue  # another site, the directory itself, a preview, or deeper than one step
        if url not in found:
            found.append(url)
    return found


def walk(root: Path, url: str) -> tuple[int, int]:
    """Mirror one directory and those under it; return files fetched and files already held."""
    page, _ = fetch_with_headers(url)
    time.sleep(PAUSE_SECONDS)
    fetched = held = 0
    for entry in links(page, url):
        name = entry.removeprefix(url).rstrip("/")
        if entry.endswith("/") or "." not in name.lstrip("."):
            try:
                below = walk(root, entry.rstrip("/") + "/")
            except urllib.error.HTTPError as err:
                if err.code != NOT_FOUND:
                    print(f"failed {entry}: {err}")
                    continue
            else:
                fetched, held = fetched + below[0], held + below[1]
                continue
        if fetch_file(root, entry):
            fetched += 1
        else:
            held += 1
    return fetched, held


def fetch_file(root: Path, url: str) -> bool:
    """Keep one file under its site path; False when it is already held or cannot be had."""
    path = urllib.parse.unquote(url.removeprefix(SITE), encoding="latin-1")
    target = root / path
    if target.exists():
        return False
    try:
        data, remote = fetch_with_headers(url)
    except OSError as err:
        print(f"failed {path}: {err}")
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    record(root, path, url, data, remote)
    time.sleep(PAUSE_SECONDS)
    return True


def main() -> None:
    root = Path(sys.argv[1])
    for tree in sys.argv[2:]:
        fetched, held = walk(root, f"{SITE}{tree.strip('/')}/")
        print(f"{tree}: {fetched} fetched, {held} already held or failed")


if __name__ == "__main__":
    main()
