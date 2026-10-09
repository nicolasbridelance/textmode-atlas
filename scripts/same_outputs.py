# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Prove that a change of code leaves every output the same (ADR 0012, amended by ADR 0026).

Decodes, measures, reads and renders a sample of the corpus, one JSON line per artifact: grid
digest, features, text lines, rendered pixels, write counts or the decoding error. Run it with the
old code first on PYTHONPATH (a worktree of the base commit) and with the new, then compare:

    git worktree add /tmp/base main
    PYTHONPATH=/tmp/base/renderers/src:/tmp/base/analysis/src \
        uv run python scripts/same_outputs.py run 3000 old.jsonl
    uv run python scripts/same_outputs.py run 3000 new.jsonl
    uv run python scripts/same_outputs.py compare old.jsonl new.jsonl
"""

import dataclasses
import json
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text
from tm.config import settings
from tm.storage import S3Store, get_original, s3_client
from tm_analysis.features import extract
from tm_analysis.text import text_lines
from tm_render.ansi import DecodeError, decode
from tm_render.conservation import BitmapFont, Settings, render


def run(n: int, out: Path) -> None:
    cfg = settings()
    store = S3Store(s3_client(), cfg.originals_bucket)
    font = BitmapFont.load(Path("corpus/fonts/ibm-vga-8x16.f16"))
    with create_engine(cfg.database_url).connect() as conn:
        shas = (
            conn.execute(
                text(
                    "select a.sha256 from artifact a where a.format in ('ansi', 'ascii')"
                    " order by md5(a.sha256) limit :n"
                ),
                {"n": n},
            )
            .scalars()
            .all()
        )
    with out.open("w") as f:
        for sha in shas:
            try:
                decoded = decode(get_original(store, sha))
            except DecodeError as err:
                f.write(json.dumps({"sha": sha, "error": err.kind}) + "\n")
                continue
            grid = decoded.grid
            rendering = render(grid, font, Settings.from_sauce(decoded.sauce))
            f.write(
                json.dumps(
                    {
                        "sha": sha,
                        "grid": grid.digest(),
                        "features": dataclasses.asdict(extract(grid)),
                        "text": [dataclasses.asdict(line) for line in text_lines(grid)],
                        "pixels": rendering.recipe["pixels_sha256"],
                        "stream": dataclasses.asdict(decoded.stream),
                    },
                    sort_keys=True,
                )
                + "\n"
            )
    print(len(shas), "done", out)


def compare(old_path: Path, new_path: Path) -> None:
    old = [json.loads(line) for line in old_path.open()]
    new = [json.loads(line) for line in new_path.open()]
    if [o["sha"] for o in old] != [n["sha"] for n in new]:
        sys.exit("the two runs did not read the same artifacts")
    keys = ("error", "grid", "features", "text", "pixels", "stream")
    differ: dict[str, Any] = {
        k: sum(o.get(k) != n.get(k) for o, n in zip(old, new, strict=True)) for k in keys
    }
    print(f"{len(old)} artifacts; differences: {differ}")
    if any(differ.values()):
        sys.exit(1)


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]), Path(sys.argv[3]))
    else:
        compare(Path(sys.argv[2]), Path(sys.argv[3]))
