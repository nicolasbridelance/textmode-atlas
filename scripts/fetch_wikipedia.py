# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Fetch the Wikipedia articles of the field, in every language, and their Wikidata items.

Politely, as the source note asks (docs/sources/wikipedia.md): one request at a time, a pause,
`maxlag`, a named User-Agent, titles batched by 50, `Retry-After` honoured. Seeds are the topics
of the source note and the members of a few English categories (one level of subcategories);
language links then give every language that has an article.

Writes into `data/wikipedia/<date>/` (local; Wikipedia text is CC BY-SA and is never
republished by the museum, Wikidata is CC0):

- `pages.jsonl`: one article per line (lang, title, pageid, revid, timestamp, qid, wikitext);
- `wikidata.jsonl`: one Wikidata entity per line, as the API returns it;
- `fetches.tsv`: every request (time, URL, status, SHA-256 of the body);
- `manifest.json`: seeds, counts, User-Agent.

Resumable: a language whose titles are all in `pages.jsonl` is not fetched again.

    uv run python scripts/fetch_wikipedia.py [data/wikipedia]
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path
from typing import Any

USER_AGENT = "textmode-atlas/0.1 (https://github.com/nicolasbridelance/textmode-atlas; research)"
PAUSE_SECONDS = 1.0
BATCH = 50
MAX_TRIES = 5
TOO_MANY = 429
CATEGORY_NS = 14
SEED_TITLES = [
    "Teletext", "ASCII art", "Bulletin board system", "Minitel", "Concrete poetry", "Demoscene",
    ".nfo", "Videotex", "Kaomoji", "Code page 437", "Text mode", "ACiD Productions", "ANSI art",
    "Box-drawing characters", "FIGlet", "Block Elements", "Semigraphics", "Warez scene",
    "Crack intro", "PETSCII", "Jason Scott", "Textfiles.com", "Artpack", "Scene.org",
    "Shift JIS art", "TheDraw", "Computer art scene", "ATASCII", "ICE Advertisements",
    "ANSI escape code", "Tracker (music software)", "Module file", "FILE ID.DIZ",
    "SAUCE (file format)",
]  # fmt: skip
SEED_CATEGORIES = [
    "Category:Artscene", "Category:Artscene groups", "Category:ASCII art", "Category:Demoscene",
    "Category:Demogroups", "Category:Bulletin board systems",
]  # fmt: skip


class Client:
    """One MediaWiki API caller: sequential, paused, every request logged."""

    def __init__(self, log: Path) -> None:
        self.log = log

    def get(self, host: str, params: dict[str, str]) -> dict[str, Any]:
        query = urllib.parse.urlencode({**params, "format": "json", "maxlag": "5"})
        url = f"https://{host}/w/api.php?{query}"
        for attempt in range(MAX_TRIES):
            time.sleep(PAUSE_SECONDS * (2**attempt))
            try:
                body = self._fetch(url)
            except urllib.error.HTTPError as err:
                self._record(url, err.code, b"")
                if err.code != TOO_MANY:
                    raise
                time.sleep(float(err.headers.get("Retry-After", "10")))
                continue
            data = json.loads(body)
            if data.get("error", {}).get("code") != "maxlag":
                return data
        raise RuntimeError(f"gave up after {MAX_TRIES} tries: {url}")

    def _fetch(self, url: str) -> bytes:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=120) as response:
            body = response.read()
        self._record(url, response.status, body)
        return body

    def _record(self, url: str, status: int, body: bytes) -> None:
        with self.log.open("a", newline="", encoding="utf-8") as out:
            now = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
            sha = hashlib.sha256(body).hexdigest()
            csv.writer(out, delimiter="\t", lineterminator="\n").writerow([now, url, status, sha])

    def query(self, host: str, params: dict[str, str]) -> Iterator[dict[str, Any]]:
        """Every page of a query, following `continue`."""
        extra: dict[str, str] = {}
        while True:
            data = self.get(host, {"action": "query", **params, **extra})
            yield data.get("query", {})
            if "continue" not in data:
                return
            extra = data["continue"]


def wiki(lang: str) -> str:
    return f"{lang}.wikipedia.org"


def category_members(client: Client, category: str, depth: int = 1) -> set[str]:
    """Articles of an English category and of its subcategories down to `depth`."""
    params = {"list": "categorymembers", "cmtitle": category, "cmlimit": "500"}
    titles: set[str] = set()
    for part in client.query(wiki("en"), params):
        for member in part.get("categorymembers", []):
            if member["ns"] == 0:
                titles.add(member["title"])
            elif member["ns"] == CATEGORY_NS and depth > 0:
                titles |= category_members(client, member["title"], depth - 1)
    return titles


def language_links(client: Client, titles: list[str]) -> tuple[dict[str, set[str]], dict[str, str]]:
    """Every language's title for the English articles (English included), and each language's
    host, which is not always `<code>.wikipedia.org` (`gsw` is `als`, `nan` is `zh-min-nan`)."""
    by_lang: dict[str, set[str]] = defaultdict(set)
    hosts = {"en": wiki("en")}
    for start in range(0, len(titles), BATCH):
        batch = titles[start : start + BATCH]
        params = {"prop": "langlinks", "titles": "|".join(batch), "lllimit": "max", "llprop": "url"}
        params["redirects"] = "1"
        for part in client.query(wiki("en"), params):
            for page in part.get("pages", {}).values():
                if "missing" in page:
                    continue
                by_lang["en"].add(page["title"])
                for link in page.get("langlinks", []):
                    by_lang[link["lang"]].add(link["*"])
                    hosts[link["lang"]] = urllib.parse.urlparse(link["url"]).netloc
    return by_lang, hosts


def articles(client: Client, lang: str, host: str, titles: list[str]) -> Iterator[dict[str, Any]]:
    """The current wikitext of each title, with its revision and Wikidata item."""
    for start in range(0, len(titles), BATCH):
        params = {
            "prop": "revisions|pageprops",
            "titles": "|".join(titles[start : start + BATCH]),
            "rvprop": "ids|timestamp|content",
            "rvslots": "main",
            "ppprop": "wikibase_item",
            "redirects": "1",
        }
        for part in client.query(host, params):
            for page in part.get("pages", {}).values():
                if "missing" in page or not page.get("revisions"):
                    continue
                revision = page["revisions"][0]
                yield {
                    "lang": lang,
                    "title": page["title"],
                    "pageid": page["pageid"],
                    "revid": revision["revid"],
                    "timestamp": revision["timestamp"],
                    "qid": page.get("pageprops", {}).get("wikibase_item"),
                    "wikitext": revision["slots"]["main"].get("*", ""),
                }


def entities(client: Client, qids: list[str]) -> Iterator[dict[str, Any]]:
    for start in range(0, len(qids), BATCH):
        params = {"action": "wbgetentities", "ids": "|".join(qids[start : start + BATCH])}
        yield from client.get("www.wikidata.org", params).get("entities", {}).values()


def done_titles(path: Path) -> dict[str, set[str]]:
    done: dict[str, set[str]] = defaultdict(set)
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            page = json.loads(line)
            done[page["lang"]].add(page["title"])
    return done


def append(path: Path, rows: Iterator[dict[str, Any]]) -> int:
    count = 0
    with path.open("a", encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> None:
    base = Path(sys.argv[1] if len(sys.argv) > 1 else "data/wikipedia")
    root = base / dt.date.today().isoformat()
    root.mkdir(parents=True, exist_ok=True)
    client = Client(root / "fetches.tsv")
    seeds = set(SEED_TITLES)
    for category in SEED_CATEGORIES:
        seeds |= category_members(client, category)
    by_lang, hosts = language_links(client, sorted(seeds))
    print(f"{len(seeds)} seed articles, {len(by_lang)} languages")
    pages = root / "pages.jsonl"
    done = done_titles(pages)
    for lang in sorted(by_lang):
        todo = sorted(by_lang[lang] - done[lang])
        if not todo:
            continue
        try:
            print(
                f"{lang}: {append(pages, articles(client, lang, hosts[lang], todo))} of {len(todo)}"
            )
        except (OSError, ValueError, RuntimeError) as err:  # one language fails, not the rest
            print(f"{lang}: failed, {err}")
    qids = sorted({json.loads(line)["qid"] for line in pages.open(encoding="utf-8")} - {None})
    (root / "wikidata.jsonl").unlink(missing_ok=True)  # rewritten whole: items change
    count = append(root / "wikidata.jsonl", entities(client, qids))
    manifest = {
        "user_agent": USER_AGENT,
        "seed_titles": SEED_TITLES,
        "seed_categories": SEED_CATEGORIES,
        "seed_articles": len(seeds),
        "languages": len(by_lang),
        "articles": sum(len(t) for t in by_lang.values()),
        "wikidata_entities": count,
    }
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
