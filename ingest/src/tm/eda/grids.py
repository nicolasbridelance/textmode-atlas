# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The chapters read from the grids: what the works hold, measured by features v1.

Train packs only (research programme, rule 3). One scan brings every measured work's row;
the chapters aggregate it here, so that the features table is read once per refresh.
"""

from __future__ import annotations

import math
from collections import defaultdict
from statistics import median
from typing import Any

from sqlalchemy import Connection
from tm_analysis.versions import FEATURES_VERSION

from tm.eda.base import SHOWN, Scope, rows_of
from tm.eda.stats import Kind, kitagawa

BRIGHT = 0.05  # share of ink on a bright background for a work to count as iCE
TALLER = 1.5  # how much taller the recent median work must be
ICE_FACTOR = 10
WIDE = 80
BEFORE, AFTER = "1994-95", "2000-04"  # the composition chapter compares these eras
RECENT = "2013-26"
NINETIES = ("1994-95", "1996-97", "1998-99", "2000-04")
HEIGHT_BINS = 13  # rows in powers of two: 1, 2, 4 … 4,096 and more
GREYS = (7, 8, 15)  # light grey, dark grey, white in the VGA palette
GREY_FLOOR = 1 / 3  # the share of ink the greys keep in every era, for the reading to hold
MIN_ERA = 100  # works an era needs to count in a check
CLASSES = ("block", "half_block", "shade", "alphanumeric", "punctuation")
ERA = """case when {y} < 1994 then '1990-93' when {y} < 1996 then '1994-95'
  when {y} < 1998 then '1996-97' when {y} < 2000 then '1998-99' when {y} < 2005 then '2000-04'
  when {y} < 2013 then '2005-12' else '2013-26' end"""
# What the grid holds, as `works.sql` says it (datasets/works): blocks or text, coloured or not.
KIND = """case when f.n_colors = 0 then 'empty'
  when f.class_block + f.class_half_block + f.class_shade >= 0.25
    then case when f.n_colors > 2 then 'coloured_blocks' else 'blocks' end
  else case when f.n_colors > 2 then 'coloured_text' else 'text' end end"""
TRAIN = f"""select {ERA.format(y="extract(year from v.date_min)")} as era,
    a.format = 'ansi' as ansi, {KIND} as kind, d.rows, f.cols, f.high_bg_ratio, f.fg_hist,
    f.class_block as block, f.class_half_block as half_block, f.class_shade as shade,
    f.class_alphanumeric as alphanumeric, f.class_punctuation as punctuation
  from work_split s
  join artifact a on a.sha256 = s.sha256 and s.split = 'train'
  join version v on v.id = a.version_id
  join work w on w.id = v.work_id and w.kind = 'single'
  join decoding d on d.sha256 = a.sha256 and d.decoder_version = :decoder and d.status = 'ok'
  join features f on f.sha256 = a.sha256 and f.extractor_version = :features
    and f.grid_sha256 = d.grid_sha256
  where v.date_min is not null and {SHOWN}"""


def grids(conn: Connection, scope: Scope) -> dict[str, Any]:
    works = rows_of(conn, TRAIN, scope.params(features=FEATURES_VERSION))
    by_era: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for work in works:
        by_era[work["era"]].append(work)
    eras = dict(sorted(by_era.items()))
    return {
        "composition": composition(eras),
        "revival": revival(eras),
        "palette": palette(eras),
    }


def _kinds(works: list[dict[str, Any]]) -> dict[str, Kind]:
    """Each content kind among the ANSI files: its share, and its mean shade share."""
    ansi = [w for w in works if w["ansi"]]
    groups: dict[str, list[float]] = defaultdict(list)
    for work in ansi:
        groups[work["kind"]].append(work["shade"])
    return {k: Kind(len(v) / len(ansi), sum(v) / len(v)) for k, v in groups.items()}


def composition(eras: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Did shading recede, or did the packs fill with text? Mean shade share of ANSI files,
    overall and by kind, and the change between two eras split in two."""
    series: list[dict[str, Any]] = []
    for era, works in eras.items():
        kinds = _kinds(works)
        series.append(
            {
                "era": era,
                "all": sum(k.share * k.mean for k in kinds.values()),
                "kinds": {name: {"share": k.share, "shade": k.mean} for name, k in kinds.items()},
            }
        )
    if BEFORE not in eras or AFTER not in eras:
        return {"eras": series, "before": BEFORE, "after": AFTER, "split": None, "checks": {}}
    split = kitagawa(_kinds(eras[BEFORE]), _kinds(eras[AFTER]))
    holds = abs(split["composition"]) > abs(split["within"])
    return {
        "eras": series,
        "before": BEFORE,
        "after": AFTER,
        "split": split,
        "checks": {"composition_dominates": {"holds": holds, **split}},
    }


def _height_bin(rows: int) -> int:
    return min(HEIGHT_BINS - 1, int(math.log2(max(1, rows))))


def _era_summary(era: str, works: list[dict[str, Any]]) -> dict[str, Any]:
    heights = [0] * HEIGHT_BINS
    for work in works:
        heights[_height_bin(work["rows"])] += 1
    return {
        "era": era,
        "works": len(works),
        "median_rows": median(w["rows"] for w in works),
        "wide": sum(w["cols"] > WIDE for w in works) / len(works),
        "ice": sum(w["high_bg_ratio"] > BRIGHT for w in works) / len(works),
        "heights": heights,
    }


def revival(eras: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """After the quiet years, did the works come back the same?"""
    summaries = [_era_summary(era, works) for era, works in eras.items()]
    by = {e["era"]: e for e in summaries}
    recent = by.get(RECENT)
    nineties = [by[e] for e in NINETIES if e in by]
    if not recent or not nineties:
        return {"eras": summaries, "checks": {}}
    rows = max(e["median_rows"] for e in nineties)
    ice = max(e["ice"] for e in nineties)
    return {
        "eras": summaries,
        "checks": {
            "taller": {
                "holds": recent["median_rows"] >= TALLER * rows,
                "recent": recent["median_rows"],
                "nineties": rows,
            },
            "ice_later": {
                "holds": recent["ice"] > ICE_FACTOR * ice,
                "recent": recent["ice"],
                "nineties": ice,
            },
        },
    }


def _ink(works: list[dict[str, Any]]) -> list[float]:
    """Share of the ink in each of the sixteen foreground colours."""
    totals: list[float] = [0.0] * len(works[0]["fg_hist"]) if works else []
    for work in works:
        for colour, cells in enumerate(work["fg_hist"]):
            totals[colour] += cells
    ink = sum(totals)
    return [t / ink for t in totals] if ink else totals


def palette(eras: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Which colours and which characters did coloured ANSI art draw with?"""
    series: list[dict[str, Any]] = []
    for era, works in eras.items():
        coloured = [w for w in works if w["ansi"] and w["kind"].startswith("coloured")]
        if not coloured:
            continue
        ink = _ink(coloured)
        glyphs = {c: sum(w[c] for w in coloured) / len(coloured) for c in CLASSES}
        series.append(
            {
                "era": era,
                "works": len(coloured),
                "ink": ink,
                "greys": sum(ink[c] for c in GREYS),
                "glyphs": {**glyphs, "other": max(0.0, 1 - sum(glyphs.values()))},
            }
        )
    counted = [e for e in series if e["works"] >= MIN_ERA]
    lowest = min((e["greys"] for e in counted), default=None)
    checks = (
        {"mostly_grey": {"holds": lowest >= GREY_FLOOR, "lowest": lowest}}
        if lowest is not None
        else {}
    )
    return {"eras": series, "checks": checks}
