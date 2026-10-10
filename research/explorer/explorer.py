# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The local museum: collection, scientific constellation and one shared work screen.

Reads train-only datasets and private derived storage. Display decisions remain on the
server. Serves the built Svelte museum on loopback; no private dataset is copied into it.

    uv run --group research python research/explorer/explorer.py   # or: just explore
"""

from __future__ import annotations

import io
import json
import logging
import re
import sys
import unicodedata
from functools import lru_cache
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import duckdb
import numpy as np
import pyarrow as pa
from graph import Graph  # next to this file
from museum import asset, english
from PIL import Image
from readings import readings
from sqlalchemy import create_engine
from thumbnails import MODES, thumbnail  # next to this file
from tm.access import Access, load_access
from tm.config import settings
from tm.eda.live import Live
from tm.storage import S3Store, grid_key, rendering_key, s3_client
from tm_analysis.neighbours import PROFILE, profile
from tm_render.compact import encode
from tm_render.conservation import BitmapFont, Settings, render
from tm_render.grid import from_parquet

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "datasets" / "build" / "works" / "6"
FONT = ROOT / "corpus" / "fonts" / "ibm-vga-8x16.f16"
SITE = ROOT / "apps" / "museum" / "build"
GRAPH_SCRIPT = Path(__file__).with_name("graph.js")
READINGS = ROOT / "datasets" / "build" / "interpretations" / "1"
GRAPH = ROOT / "datasets" / "build" / "graph" / "2"
HOST, PORT = "127.0.0.1", 8737
PAGE_SIZE = 120
NEIGHBOURS = 10  # as the graph build (k), so that the wall and the graph agree
SHA = re.compile(r"^[0-9a-f]{64}$")
SEED = re.compile(r"^[0-9A-Za-z_-]{1,32}$")
FIRST_EDA = 60.0  # seconds a first visitor waits for the first exploration
DEFAULT_SEED = "explorer"  # the shuffle every visitor sees first
ORDERS = {
    "random": "hash(sha256 || ?)",  # shuffled by the seed (`_seed`)
    "year": "year, pack, path",
    "colours": "n_colors desc nulls last",
    "entropy": "glyph_entropy desc nulls last",
    "shade": "class_shade desc nulls last",
    "half_block": "class_half_block desc nulls last",
    "letters": "class_alphanumeric desc nulls last",
    "drawn": "draw_order nulls last",
    "tall": "rows desc nulls last",
    "wide": "cols desc nulls last",
    "fill": "fill_ratio desc nulls last",
    "redrawn": "overwrites::double / greatest(writes, 1) desc nulls last",
    "clears": "clears desc nulls last",
}
log = logging.getLogger(__name__)


class Corpus:
    """The dataset, the stores, and what the explorer derives from them."""

    def __init__(self, build: Path) -> None:
        self.manifest = json.loads((build / "manifest.json").read_text())
        self.db = duckdb.connect()
        self.access = _access()
        visible = [sha for sha, rule in self.access.items() if rule.shown != "nothing"]
        self.db.register("visible_rows", pa.table({"sha256": visible}))
        self.db.execute("create table visible as select * from visible_rows")
        self.db.register(
            "visit_rows",
            pa.table(
                {
                    "sha256": list(self.access),
                    "shown": [r.shown for r in self.access.values()],
                    "level": [r.level for r in self.access.values()],
                }
            ),
        )
        self.db.execute("create table visit_rules as select * from visit_rows")
        self.db.execute(
            f"create view works as select w.* from '{build / 'works.parquet'}' w"
            " join visible using (sha256)"
        )
        self.db.execute(f"create view features as select * from '{build / 'features.parquet'}'")
        self.db.execute(
            "create table w as select * from works left join features using (sha256, cols, rows)"
        )
        self.db.execute(  # the words written in the works, folded once for search (leads I2)
            f"create table lines as select sha256, row, text, strip_accents(lower(text)) as folded"
            f" from '{build / 'text.parquet'}'"
        )
        cfg = settings()
        self.derived = S3Store(s3_client(), cfg.derived_bucket)
        self.font = BitmapFont.load(FONT)
        decoder, version = self.manifest["extractors"]["decoder"].split("@")
        self.decoder, self.decoder_version = decoder, version
        self._profiles()

    def _profiles(self) -> None:
        """Profiles of every measured work (`tm_analysis.neighbours`), for the wall's neighbours
        when no graph build exists."""
        names = ", ".join(PROFILE)
        rows = self.db.execute(
            f"select sha256, {names}, fg_hist from w where fill_ratio is not null order by sha256"
        ).fetchall()
        self.order = [row[0] for row in rows]
        self.index = {sha: i for i, sha in enumerate(self.order)}
        self.matrix = profile([row[1:-1] for row in rows], [row[-1] for row in rows])
        self.nearest: dict[str, list[str]] = {}

    def use_graph(self, graph: Graph) -> None:
        """Take the neighbours of the graph build, so that the wall shows the graph's ties."""
        self.nearest = graph.neighbours()

    def _nearest(self, sha: str) -> list[str]:
        if sha in self.nearest:
            return self.nearest[sha]
        if sha not in self.index:
            return []
        distances = np.linalg.norm(self.matrix - self.matrix[self.index[sha]], axis=1)
        distances[self.index[sha]] = np.inf
        closest = np.argpartition(distances, NEIGHBOURS)[:NEIGHBOURS]
        return [self.order[i] for i in closest[np.argsort(distances[closest], kind="stable")]]

    def rows(self, sql: str, params: list[Any]) -> list[dict[str, Any]]:
        cursor = self.db.cursor().execute(sql, params)  # one cursor per request thread
        names = [d[0] for d in cursor.description]
        return [dict(zip(names, row, strict=True)) for row in cursor.fetchall()]

    def facets(self) -> dict[str, Any]:
        return {
            "years": self.rows(
                "select year, count(*) as works from works where year is not null"
                " group by year order by year",
                [],
            ),
            "formats": self.rows(
                "select format, count(*) as works from works group by format order by works desc",
                [],
            ),
            "archives": self.rows(
                "select archive, count(*) as works from (select unnest(archives) as archive"
                " from works) group by archive order by works desc",
                [],
            ),
            "kinds": self.rows(
                "select content_kind as kind, count(*) as works from works"
                " where content_kind is not null group by 1 order by works desc",
                [],
            ),
            "orders": list(ORDERS),
            "dataset": {
                "version": self.manifest["version"],
                "extractors": self.manifest["extractors"],
                "works": self.manifest["tables"]["works"]["rows"],
                "measured": self.manifest["tables"]["features"]["rows"],
            },
        }

    def wall(self, query: dict[str, str]) -> dict[str, Any]:
        where, params = _conditions(query)
        words = _fold(query.get("words", ""))
        hit = (  # the first line that matches, shown on the card
            "(select text from lines l where l.sha256 = w.sha256 and folded like ?"
            " order by row limit 1)"
        )
        order, order_params = _order(query)
        offset = max(0, int(query.get("offset", "0")))
        total = self.db.cursor().execute(f"select count(*) from w where {where}", params)
        total = total.fetchone()
        works = self.rows(
            "select sha256, archive, pack, year, path, format, content_kind, sauce_title,"
            " sauce_author, sauce_group, cols, rows, decoding,"
            " rendering_sha256 is not null as rendered,"
            " (select shown from visit_rules v where v.sha256 = w.sha256) as display,"
            f" {hit if words else 'null'} as hit from w"
            f" where {where} order by {order}, sha256 limit {PAGE_SIZE} offset {offset}",
            ([f"%{words}%"] if words else []) + params + order_params,
        )
        return {"total": total[0] if total else 0, "offset": offset, "works": works}

    def surprise(self, query: dict[str, str]) -> dict[str, str] | None:
        """One work drawn by the seed among the filtered works whose files may be shown."""
        return surprise(self.db, query)

    def work(self, sha: str) -> dict[str, Any] | None:
        found = self.rows("select * from w where sha256 = ?", [sha])
        if not found:
            return None
        work = found[0]
        work["neighbours"] = self.neighbours(sha)
        return work

    def neighbours(self, sha: str) -> list[dict[str, Any]]:
        nearest = self._nearest(sha)
        if not nearest:
            return []
        placeholders = ", ".join("?" * len(nearest))
        found = self.rows(
            "select sha256, pack, year, path, sauce_author, sauce_group, decoding from w"
            f" where sha256 in ({placeholders})",
            nearest,
        )
        rank = {s: i for i, s in enumerate(nearest)}
        return sorted(found, key=lambda w: rank[w["sha256"]])

    def text(self, sha: str) -> list[dict[str, Any]] | None:
        """The text layer of the work's grid, as the dataset holds it: rows with words."""
        if not self.can_show(sha):
            return None
        return self.rows("select row, text from lines where sha256 = ? order by row", [sha])

    def image(self, sha: str, kind: str) -> bytes | None:
        """The stored rendering (`full`) or a card for the wall (`thumbnails.MODES`); works not
        rendered yet are drawn from their grid, without storing anything."""
        if not self.can_show(sha):
            return None
        row = (
            self.db.cursor()
            .execute(
                "select rendering_sha256, decoding, sauce_ice, sauce_problems from w"
                " where sha256 = ?",
                [sha],
            )
            .fetchone()
        )
        if row is None or row[1] != "ok":
            return None
        rendering, _, ice, problems = row
        if rendering:
            image = Image.open(io.BytesIO(self.derived.get(rendering_key(rendering))))
        else:
            image = self._preview(sha, bool(ice) and not problems)
        if kind in MODES:
            image = thumbnail(image, kind)
        out = io.BytesIO()
        image.save(out, "PNG")
        return out.getvalue()

    def _preview(self, sha: str, ice: bool) -> Image.Image:
        grid = from_parquet(self.derived.get(grid_key(sha, self.decoder, self.decoder_version)))
        drawn = render(grid, self.font, Settings(high_bg="ice" if ice else "blink"))
        return Image.open(io.BytesIO(drawn.png))

    def can_show(self, sha: str) -> bool:
        rule = self.access.get(sha)
        return rule is not None and rule.shown == "files"

    def compact(self, sha: str) -> bytes | None:
        work = self.work(sha)
        if not work or not self.can_show(sha) or work["decoding"] != "ok":
            return None
        grid = from_parquet(self.derived.get(grid_key(sha, self.decoder, self.decoder_version)))
        ice = bool(work["sauce_ice"]) and not work["sauce_problems"]
        return encode(grid, ice) if grid.fits_v1() else None

    def record(self, sha: str) -> dict[str, Any] | None:
        work = self.work(sha)
        if work is None:
            return None
        rule = self.access[sha]
        shown = rule.shown if work["decoding"] == "ok" else "record"
        return {
            "schema": 2,
            "sha256": sha,
            "title": work["sauce_title"],
            "file": work["path"].rsplit("/", 1)[-1],
            "format": work["format"],
            "year": work["year"],
            "shown": shown,
            "credit": {
                "author": work["sauce_author"],
                "group": work["sauce_group"],
                "pack": work["pack"],
                "archive": work["archive"],
                "url": rule.url,
            },
            "audience": {
                "level": rule.level,
                "reviewed": rule.reviewed,
                "descriptors": rule.descriptors,
                "notices": rule.notices,
            },
            "grid": {
                "cols": work["cols"] or 0,
                "rows": work["rows"] or 0,
                "ice": bool(work["sauce_ice"]) and not work["sauce_problems"],
            },
            "files": {},
            "provenance": [],
            "withdraw": settings().withdraw_url,
            "text": self.text(sha) or [],
            "lists": {kind: f"lists/{sha}/{kind}.json" for kind in ("pack", "author", "year")},
            "research": {
                "dataset": {
                    "version": self.manifest["version"],
                    "extractors": self.manifest["extractors"],
                },
                "decoding": work["decoding"],
                "features": self.features(work),
                "neighbours": work["neighbours"],
                "readings": readings(READINGS, sha) if shown == "files" else [],
            },
        }

    def features(self, work: dict[str, Any]) -> dict[str, Any]:
        if not self.can_show(work["sha256"]):
            return {}
        names = (*PROFILE, "writes", "overwrites", "clears", "content_kind", "system")
        return {name: work[name] for name in names if name in work and work[name] is not None}

    def visit(self, sha: str | None = None, kind: str = "days") -> dict[str, Any]:
        params: list[Any] = []
        where = "v.shown = 'files' and w.decoding = 'ok'"
        if sha:
            field = {"pack": "pack", "author": "sauce_author", "year": "year"}[kind]
            where += f" and w.{field} = (select {field} from w where sha256 = ?)"
            params.append(sha)
        limit = f" limit {PAGE_SIZE}" if kind == "days" else ""
        entries = self.rows(
            "select w.sha256, sauce_title as title, path as file, path, sauce_author as author,"
            ' sauce_group as "group", pack, year, cols, rows, v.level'
            f" from w join visit_rules v using (sha256) where {where} order by path, sha256{limit}",
            params,
        )
        return {"works": entries}


def _access() -> dict[str, Access]:
    engine = create_engine(settings().database_url)
    try:
        with engine.connect() as conn:
            return load_access(conn)
    finally:
        engine.dispose()


def _seed(query: dict[str, str]) -> str:
    seed = query.get("seed") or DEFAULT_SEED
    if not SEED.match(seed):
        raise ValueError("seed: 1 to 32 letters, digits, - or _")
    return seed


def _order(query: dict[str, str]) -> tuple[str, list[Any]]:
    """The wall's order and its parameters: `random` is a shuffle a seed makes reproducible."""
    name = query.get("order") or "random"
    order = ORDERS.get(name, ORDERS["random"])
    return order, [_seed(query)] if order == ORDERS["random"] else []


def surprise(db: duckdb.DuckDBPyConnection, query: dict[str, str]) -> dict[str, str] | None:
    """The first work of the seeded shuffle that is decoded and may be shown with its files."""
    where, params = _conditions(query)
    seed = _seed(query)
    found = db.execute(
        "select sha256 from w join visit_rules v using (sha256)"
        f" where {where} and v.shown = 'files' and w.decoding = 'ok'"
        " order by hash(sha256 || ?), sha256 limit 1",
        [*params, seed],
    ).fetchone()
    return {"sha256": found[0], "seed": seed} if found else None


def _fold(text: str) -> str:
    """Lower case without accents, as `lines.folded`: `nao` finds `não`."""
    decomposed = unicodedata.normalize("NFKD", text.strip().lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _conditions(query: dict[str, str]) -> tuple[str, list[Any]]:
    """The wall's filters as SQL conditions on `w`, with their parameters."""
    where, params = ["true"], []
    if query.get("year"):
        where.append("year = ?")
        params.append(int(query["year"]))
    for field, column in (("format", "format"), ("kind", "content_kind")):
        if query.get(field):
            where.append(f"{column} = ?")
            params.append(query[field])
    if query.get("archive"):  # held by that archive, in any of its packs
        where.append("list_contains(archives, ?)")
        params.append(query["archive"])
    if text := query.get("q", "").strip().lower():
        where.append(
            "(lower(coalesce(sauce_group, '')) like ? or lower(coalesce(sauce_author, ''))"
            " like ? or lower(pack) like ? or lower(path) like ?)"
        )
        params.extend([f"%{text}%"] * 4)
    if words := _fold(query.get("words", "")):
        where.append("sha256 in (select sha256 from lines where folded like ?)")
        params.append(f"%{words}%")
    return " and ".join(where), params


class Handler(BaseHTTPRequestHandler):
    """Routes: the page, the JSON endpoints, and images (cards for the wall, or the work)."""

    corpus: Corpus
    graph: Graph | None = None
    live: Live | None = None

    def do_GET(self) -> None:
        url = urlparse(self.path)
        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            self.route(url.path.strip("/").split("/"), query)
        except (ValueError, KeyError) as err:
            self.send(HTTPStatus.BAD_REQUEST, "text/plain", str(err).encode())

    def route(self, parts: list[str], query: dict[str, str]) -> None:
        if parts[0] == "files":
            self.route_files(parts[1:])
            return
        match parts:
            case ["api", *_]:
                self.route_api(parts, query)
            case ["image", kind, sha] if SHA.match(sha) and kind in (*MODES, "full"):
                self.png(_image(self.corpus, sha, kind))
            case _:
                self.route_page(parts)

    def route_api(self, parts: list[str], query: dict[str, str]) -> None:
        match parts:
            case ["api", "graph", _]:
                self.route_graph(parts)
            case ["api", "facets"]:
                self.json(self.corpus.facets())
            case ["api", "works"]:
                self.json(self.corpus.wall(query))
            case ["api", "eda"]:
                self.route_eda()
            case ["api", "surprise"]:
                self.json(self.corpus.surprise(query))
            case ["api", "work", sha] if SHA.match(sha):
                self.json(self.corpus.work(sha))
            case ["api", "text", sha] if SHA.match(sha):
                self.json(self.corpus.text(sha))
            case _:
                self.route_page(parts)

    def route_eda(self) -> None:
        """The live exploration (ADR 0028); the first one is computed while the visitor waits."""
        found = self.live.current(wait=FIRST_EDA) if self.live else None
        if found is None:
            self.send(HTTPStatus.SERVICE_UNAVAILABLE, "text/plain", b"exploration not ready")
            return
        self.send(HTTPStatus.OK, "application/json", json.dumps(found, default=str).encode())

    def route_page(self, parts: list[str]) -> None:
        if (unprefixed := english(parts)) is not None:
            self.redirect(unprefixed)
            return
        if parts == ["atlas-graph.js"]:
            self.send(HTTPStatus.OK, "text/javascript", GRAPH_SCRIPT.read_bytes())
            return
        page = "constellation" if parts == ["graph"] else "/".join(parts)
        found = asset(SITE, page)
        if found is None:
            self.send(HTTPStatus.NOT_FOUND, "text/plain", b"not found: build the museum first")
            return
        kind, body = found
        self.send(HTTPStatus.OK, kind, body)

    def route_files(self, parts: list[str]) -> None:
        match parts:
            case ["lists", "days.json"]:
                self.json(self.corpus.visit())
            case ["lists", sha, kind] if SHA.match(sha):
                name = kind.removesuffix(".json")
                if name in ("pack", "author", "year"):
                    self.json(self.corpus.visit(sha, name))
                else:
                    self.send(HTTPStatus.NOT_FOUND, "text/plain", b"unknown list")
            case ["works", sha, "record.json"] if SHA.match(sha):
                self.json(self.corpus.record(sha))
            case ["works", sha, "grid.tmg"] if SHA.match(sha):
                self.binary(self.corpus.compact(sha))
            case ["works", sha, "conservation.png"] if SHA.match(sha):
                self.png(_image(self.corpus, sha, "full"))
            case _:
                self.send(HTTPStatus.NOT_FOUND, "text/plain", b"not found")

    def redirect(self, path: str) -> None:
        query = urlparse(self.path).query
        self.send_response(HTTPStatus.PERMANENT_REDIRECT)
        self.send_header("Location", f"{path}?{query}" if query else path)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def binary(self, data: bytes | None) -> None:
        if data is None:
            self.send(HTTPStatus.NOT_FOUND, "text/plain", b"no grid")
            return
        self.send(HTTPStatus.OK, "application/octet-stream", data)

    def route_graph(self, parts: list[str]) -> None:
        """The graph page and its three payloads (nodes, edges, communities)."""
        if self.graph and parts[-1] in ("nodes", "edges", "communities"):
            kind = "application/octet-stream" if parts[-1] == "edges" else "application/json"
            self.send(HTTPStatus.OK, kind, getattr(self.graph, parts[-1]), cache=True)
        else:
            self.send(HTTPStatus.NOT_FOUND, "text/plain", b"no graph: run `just graph`")

    def json(self, value: object) -> None:
        if value is None:
            self.send(HTTPStatus.NOT_FOUND, "text/plain", b"not found")
            return
        self.send(HTTPStatus.OK, "application/json", json.dumps(value, default=str).encode())

    def png(self, data: bytes | None) -> None:
        if data is None:
            self.send(HTTPStatus.NOT_FOUND, "text/plain", b"no image")
            return
        self.send(HTTPStatus.OK, "image/png", data, cache=True)

    def send(self, status: HTTPStatus, kind: str, body: bytes, cache: bool = False) -> None:
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        if cache:
            self.send_header("Cache-Control", "private, max-age=86400")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        log.debug(format, *args)


@lru_cache(maxsize=4096)
def _image(corpus: Corpus, sha: str, kind: str) -> bytes | None:
    return corpus.image(sha, kind)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if not (BUILD / "manifest.json").exists():
        sys.exit("No works dataset: run `uv run tm dataset build works` first.")
    if not (SITE / "index.html").exists():
        sys.exit("Build the museum first: pnpm --filter museum build")
    corpus = Corpus(BUILD)
    Handler.corpus = corpus
    if Graph.exists(GRAPH):
        allowed = {sha for sha in corpus.access if corpus.can_show(sha)}
        Handler.graph = Graph(GRAPH, BUILD, allowed)
        Handler.graph.check(corpus.manifest)
        corpus.use_graph(Handler.graph)
    Handler.live = Live(
        create_engine(settings().database_url, execution_options={"postgresql_readonly": True})
    )
    Handler.live.start()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    log.info("Museum on http://%s:%d (%s measured works)", HOST, PORT, len(corpus.order))
    server.serve_forever()


if __name__ == "__main__":
    main()
