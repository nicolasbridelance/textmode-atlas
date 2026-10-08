# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Corpus explorer: a local wall of works to look at 16colo together (roadmap step 5).

A research tool, not the museum: it reads the `works` dataset (train packs only, so the test
packs stay unexamined) and the private derived bucket, and listens on 127.0.0.1 only. Works not
rendered yet are previewed from their grid, without storing anything.

    uv run --group research python research/explorer/explorer.py   # or: just explore
"""

from __future__ import annotations

import io
import json
import logging
import re
import sys
from functools import lru_cache
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import duckdb
import numpy as np
from PIL import Image
from tm.config import settings
from tm.storage import S3Store, grid_key, rendering_key, s3_client
from tm_analysis.text import text_lines
from tm_render.conservation import BitmapFont, Settings, render
from tm_render.grid import Grid, from_parquet

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "datasets" / "build" / "works" / "2"
FONT = ROOT / "corpus" / "fonts" / "ibm-vga-8x16.f16"
PAGE = Path(__file__).with_name("index.html")
HOST, PORT = "127.0.0.1", 8737
SCREEN_ROWS = 25  # a thumbnail is the first screen
PAGE_SIZE = 120
NEIGHBOURS = 12
SHA = re.compile(r"^[0-9a-f]{64}$")
ORDERS = {
    "random": "hash(sha256 || 'explorer')",
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
}
# Measures that place a work among the others (neighbours); colours enter as shares.
PROFILE = [
    "fill_ratio", "glyph_entropy", "class_block", "class_half_block", "class_shade", "class_box",
    "class_alphanumeric", "class_punctuation", "class_other", "high_bg_ratio", "symmetry_h",
    "symmetry_v", "draw_order", "center_row", "center_col",
]  # fmt: skip

log = logging.getLogger(__name__)


class Corpus:
    """The dataset, the stores, and what the explorer derives from them."""

    def __init__(self, build: Path) -> None:
        self.manifest = json.loads((build / "manifest.json").read_text())
        self.db = duckdb.connect()
        self.db.execute(f"create view works as select * from '{build / 'works.parquet'}'")
        self.db.execute(f"create view features as select * from '{build / 'features.parquet'}'")
        self.db.execute(
            "create table w as select * from works left join features using (sha256, cols, rows)"
        )
        cfg = settings()
        self.derived = S3Store(s3_client(), cfg.derived_bucket)
        self.font = BitmapFont.load(FONT)
        decoder, version = self.manifest["extractors"]["decoder"].split("@")
        self.decoder, self.decoder_version = decoder, version
        self._profiles()

    def _profiles(self) -> None:
        """Standardized feature vectors of every measured work, for nearest neighbours."""
        names = ", ".join(PROFILE)
        rows = self.db.execute(
            f"select sha256, {names}, fg_hist from w where fill_ratio is not null order by sha256"
        ).fetchall()
        self.order = [row[0] for row in rows]
        self.index = {sha: i for i, sha in enumerate(self.order)}
        measures = np.array([row[1 : len(PROFILE) + 1] for row in rows], dtype=float)
        colours = np.array([row[-1] for row in rows], dtype=float)
        colours /= np.maximum(colours.sum(axis=1, keepdims=True), 1)
        matrix = np.hstack([measures, colours])
        self.matrix = (matrix - matrix.mean(axis=0)) / (matrix.std(axis=0) + 1e-9)

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
        where, params = ["true"], []
        if query.get("year"):
            where.append("year = ?")
            params.append(int(query["year"]))
        for field, column in (("format", "format"), ("kind", "content_kind")):
            if query.get(field):
                where.append(f"{column} = ?")
                params.append(query[field])
        if text := query.get("q", "").strip().lower():
            where.append(
                "(lower(coalesce(sauce_group, '')) like ? or lower(coalesce(sauce_author, ''))"
                " like ? or lower(pack) like ? or lower(path) like ?)"
            )
            params.extend([f"%{text}%"] * 4)
        order = ORDERS.get(query.get("order", "random"), ORDERS["random"])
        offset = max(0, int(query.get("offset", "0")))
        condition = " and ".join(where)
        total = self.db.cursor().execute(f"select count(*) from w where {condition}", params)
        total = total.fetchone()
        works = self.rows(
            "select sha256, pack, year, path, format, content_kind, sauce_title, sauce_author,"
            " sauce_group, cols, rows, decoding, rendering_sha256 is not null as rendered from w"
            f" where {condition} order by {order}, sha256 limit {PAGE_SIZE} offset {offset}",
            params,
        )
        return {"total": total[0] if total else 0, "offset": offset, "works": works}

    def work(self, sha: str) -> dict[str, Any] | None:
        found = self.rows("select * from w where sha256 = ?", [sha])
        if not found:
            return None
        work = found[0]
        work["neighbours"] = self.neighbours(sha)
        return work

    def neighbours(self, sha: str) -> list[dict[str, Any]]:
        if sha not in self.index:
            return []
        distances = np.linalg.norm(self.matrix - self.matrix[self.index[sha]], axis=1)
        nearest = [self.order[i] for i in np.argsort(distances)[1 : NEIGHBOURS + 1]]
        placeholders = ", ".join("?" * len(nearest))
        found = self.rows(
            "select sha256, pack, year, path, sauce_author, sauce_group, decoding from w"
            f" where sha256 in ({placeholders})",
            nearest,
        )
        rank = {s: i for i, s in enumerate(nearest)}
        return sorted(found, key=lambda w: rank[w["sha256"]])

    def text(self, sha: str) -> list[dict[str, Any]] | None:
        """The text layer of the work's grid: rows that hold words (leads I2)."""
        if not self.rows("select 1 from w where sha256 = ? and decoding = 'ok'", [sha]):
            return None
        grid = from_parquet(self.derived.get(grid_key(sha, self.decoder, self.decoder_version)))
        return [{"row": line.row, "text": line.text} for line in text_lines(grid)]

    def image(self, sha: str, screen: bool) -> bytes | None:
        """The stored rendering, or a preview drawn from the grid; `screen` keeps the first
        screen at half size."""
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
            image = self._preview(sha, bool(ice) and not problems, screen)
        if screen:
            image = image.crop((0, 0, image.width, min(image.height, 16 * SCREEN_ROWS)))
            image = image.resize((image.width // 2, image.height // 2), Image.Resampling.BOX)
        out = io.BytesIO()
        image.save(out, "PNG")
        return out.getvalue()

    def _preview(self, sha: str, ice: bool, screen: bool) -> Image.Image:
        grid = from_parquet(self.derived.get(grid_key(sha, self.decoder, self.decoder_version)))
        if screen:
            cells = {pos: cell for pos, cell in grid.cells.items() if pos[0] < SCREEN_ROWS}
            grid = Grid(grid.cols, min(grid.rows, SCREEN_ROWS), cells)
        drawn = render(grid, self.font, Settings(high_bg="ice" if ice else "blink"))
        return Image.open(io.BytesIO(drawn.png))


class Handler(BaseHTTPRequestHandler):
    """Routes: the page, three JSON endpoints, and images (first screen or whole work)."""

    corpus: Corpus

    def do_GET(self) -> None:
        url = urlparse(self.path)
        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            self.route(url.path.strip("/").split("/"), query)
        except (ValueError, KeyError) as err:
            self.send(HTTPStatus.BAD_REQUEST, "text/plain", str(err).encode())

    def route(self, parts: list[str], query: dict[str, str]) -> None:
        match parts:
            case [""]:
                self.send(HTTPStatus.OK, "text/html; charset=utf-8", PAGE.read_bytes())
            case ["api", "facets"]:
                self.json(self.corpus.facets())
            case ["api", "works"]:
                self.json(self.corpus.wall(query))
            case ["api", "work", sha] if SHA.match(sha):
                self.json(self.corpus.work(sha))
            case ["api", "text", sha] if SHA.match(sha):
                self.json(self.corpus.text(sha))
            case ["image", kind, sha] if SHA.match(sha) and kind in ("screen", "full"):
                self.png(_image(self.corpus, sha, kind == "screen"))
            case _:
                self.send(HTTPStatus.NOT_FOUND, "text/plain", b"not found")

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
def _image(corpus: Corpus, sha: str, screen: bool) -> bytes | None:
    return corpus.image(sha, screen)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if not (BUILD / "manifest.json").exists():
        sys.exit("No works dataset: run `uv run tm dataset build works` first.")
    corpus = Corpus(BUILD)
    Handler.corpus = corpus
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    log.info("Corpus explorer on http://%s:%d (%s works)", HOST, PORT, len(corpus.order))
    server.serve_forever()


if __name__ == "__main__":
    main()
