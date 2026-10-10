# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The chapters of the live exploration (ADR 0028): each returns its figures and its checks.

A check is what a written reading rests on. It is recomputed with the figures, so that the
page can say when a reading no longer matches the data. Catalogue metadata is read over every
pack; grid measures over the `train` packs only (research programme, rule 3).
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Connection, text
from tm_analysis.versions import FEATURES_VERSION
from tm_render.versions import DECODER_VERSION

from tm.eda.stats import Kind, group_agreement_test, histogram, kitagawa

ADOPTION_YEAR = 1994  # the year SAUCE appears in the archive (catalogue note)
MIN_PACK = 5  # ANSI files a pack needs for its SAUCE share to mean something
MIN_GROUP = 3  # packs a name prefix needs to count as a group
SHARE_BINS = 5
MAJORITY = 0.5  # a pack "has SAUCE" when most of its ANSI files do
PACKAGER_ONE_DATE = 0.25  # above this share of single-date packs, a packager stamped SAUCE
LATE_YEAR = 2000  # the decline is read from the peak to this year
MIN_PACKS = 50  # a year with fewer packs says little about their size
TALLER = 1.5  # how much taller the recent median work must be
ICE_FACTOR = 10
BRIGHT = 0.05  # share of ink on a bright background for a work to count as iCE
BEFORE, AFTER = "1994-95", "2000-04"  # the composition chapter compares these eras
RECENT = "2013-26"
NINETIES = ("1994-95", "1996-97", "1998-99", "2000-04")
ERA = """case when {y} < 1994 then '1990-93' when {y} < 1996 then '1994-95'
  when {y} < 1998 then '1996-97' when {y} < 2000 then '1998-99' when {y} < 2005 then '2000-04'
  when {y} < 2013 then '2005-12' else '2013-26' end"""
# What the grid holds, as `works.sql` says it (datasets/works): blocks or text, coloured or not.
KIND = """case when f.n_colors = 0 then 'empty'
  when f.class_block + f.class_half_block + f.class_shade >= 0.25
    then case when f.n_colors > 2 then 'coloured_blocks' else 'blocks' end
  else case when f.n_colors > 2 then 'coloured_text' else 'text' end end"""
ART = "('ansi', 'ascii', 'rip', 'xbin', 'bin', 'adf', 'tundra', 'pcboard', 'idf')"
SINGLE = """artifact a join version v on v.id = a.version_id
  join work w on w.id = v.work_id and w.kind = 'single'"""
SHOWN = "a.sha256 <> all(cast(:hidden as text[]))"
PREFIX = re.compile(r"[a-z]{2,}")


@dataclass(frozen=True)
class Scope:
    """What every chapter leaves out: works the policy shows nothing of (`tm.access`)."""

    hidden: list[str]

    def params(self, **more: Any) -> dict[str, Any]:
        return {"hidden": self.hidden, "decoder": DECODER_VERSION, **more}


def _rows(conn: Connection, sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute(text(sql), params).mappings()]


def contents(conn: Connection, scope: Scope) -> dict[str, Any]:
    """Before counting: what the database holds, and what it cannot read yet."""
    sources = _rows(
        conn,
        "select s.name as source, count(*) as files from artifact a"
        f" join source s on s.id = a.source_id where {SHOWN} group by 1 order by 2 desc",
        scope.params(),
    )
    [funnel] = _rows(
        conn,
        "select count(*) as art,"
        " count(d.sha256) as decoding, count(*) filter (where d.status = 'ok') as grids,"
        " count(r.sha256) as rendered, count(f.sha256) as measured,"
        " (select count(*) from work where kind = 'set') as packs"
        f" from {SINGLE}"
        " left join decoding d on d.sha256 = a.sha256 and d.decoder_version = :decoder"
        " left join lateral (select r.sha256 from representation r where r.sha256 = a.sha256"
        "   and r.level = 'conservation' limit 1) r on true"
        " left join features f on f.sha256 = a.sha256 and f.extractor_version = :features"
        "   and f.grid_sha256 = d.grid_sha256"
        f" where {SHOWN}",
        scope.params(features=FEATURES_VERSION),
    )
    unread = _rows(
        conn,
        "select a.format, d.error_class, count(*) as works from "
        f"{SINGLE} join decoding d on d.sha256 = a.sha256 and d.decoder_version = :decoder"
        f" where d.status = 'error' and {SHOWN} group by 1, 2 order by 3 desc",
        scope.params(),
    )
    missing = funnel["art"] - funnel["decoding"]
    return {
        "sources": sources,
        "funnel": funnel,
        "unread": unread,
        "checks": {"every_work_decoded": {"holds": missing == 0, "missing": missing}},
    }


def peak(conn: Connection, scope: Scope) -> dict[str, Any]:
    """Is the peak of the archive more packs, or bigger packs?"""
    years = _rows(
        conn,
        "with p as (select w.id, extract(year from v.date_min)::int as year,"
        "   count(distinct m.sha256) filter (where a.format in " + ART + f" and {SHOWN}) as art"
        "  from work w join version v on v.work_id = w.id"
        "  left join set_member m on m.set_work_id = w.id"
        "  left join artifact a on a.sha256 = m.sha256"
        "  where w.kind = 'set' group by 1, 2),"
        " s as (select extract(year from v.date_min)::int as year, count(*) as works"
        f"  from {SINGLE} where a.format in {ART} and {SHOWN} group by 1)"
        " select p.year, count(*) as packs, s.works,"
        "  percentile_cont(0.5) within group (order by p.art) as median_art"
        " from p join s using (year) where p.year is not null group by p.year, s.works"
        " order by p.year",
        scope.params(),
    )
    return {"years": years, "checks": _peak_checks(years)}


def _peak_checks(years: list[dict[str, Any]]) -> dict[str, Any]:
    """A check the data cannot support yet is left out: the page says it cannot tell."""
    sized = [y for y in years if y["packs"] >= MIN_PACKS]
    late = next((y for y in sized if y["year"] == LATE_YEAR), None)
    if not sized or late is None:
        return {}
    by_works = max(years, key=lambda y: y["works"])
    by_packs = max(years, key=lambda y: y["packs"])
    by_size = max(sized, key=lambda y: y["median_art"])
    return {
        "peaks_differ": {
            "holds": by_works["year"] != by_packs["year"],
            "works_year": by_works["year"],
            "works": by_works["works"],
            "packs_year": by_packs["year"],
            "packs": by_packs["packs"],
            "size_year": by_size["year"],
            "size": by_size["median_art"],
        },
        "fewer_and_smaller": {
            "holds": late["packs"] < by_packs["packs"]
            and late["median_art"] < by_size["median_art"],
            "year": LATE_YEAR,
            "packs": late["packs"],
            "size": late["median_art"],
        },
    }


def sauce(conn: Connection, scope: Scope) -> dict[str, Any]:
    """Who wrote the SAUCE records: the artists' tools, the packagers, or the groups?"""
    by_year = _rows(
        conn,
        "select extract(year from v.date_min)::int as year, a.format, count(*) as works,"
        " avg((a.sauce is not null)::int)::float as share"
        f" from {SINGLE} where a.format in ('ansi', 'ascii') and v.date_min is not null"
        f" and {SHOWN} group by 1, 2 having count(*) >= 100 order by 1, 2",
        scope.params(),
    )
    packs = _rows(
        conn,
        "select w.title as pack, avg((a.sauce is not null)::int)::float as share,"
        " count(*) as files, count(distinct a.sauce ->> 'date') as dates"
        " from set_member m join artifact a on a.sha256 = m.sha256 and a.format = 'ansi'"
        " join work w on w.id = m.set_work_id join version v on v.work_id = w.id"
        f" where extract(year from v.date_min) = :year and {SHOWN}"
        " group by w.id, w.title having count(*) >= :min_pack",
        scope.params(year=ADOPTION_YEAR, min_pack=MIN_PACK),
    )
    return {"by_year": by_year, "year": ADOPTION_YEAR, **_sauce_packs(packs)}


def _sauce_packs(packs: list[dict[str, Any]]) -> dict[str, Any]:
    full = [p for p in packs if p["share"] == 1]
    one_date = sum(p["dates"] == 1 for p in full) / len(full) if full else 0.0
    groups: dict[str, list[bool]] = defaultdict(list)
    for p in packs:
        if found := PREFIX.match(p["pack"].lower()):
            groups[found.group(0)].append(p["share"] >= MAJORITY)
    kept = {name: g for name, g in groups.items() if len(g) >= MIN_GROUP}
    test = group_agreement_test(list(kept.values()))
    largest = sorted(kept.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:10]
    return {
        "packs": len(packs),
        "shares": histogram([p["share"] for p in packs], 0, 1, SHARE_BINS),
        "none": sum(p["share"] == 0 for p in packs),
        "all": len(full),
        "full_mean_dates": sum(p["dates"] for p in full) / len(full) if full else None,
        "full_mean_files": sum(p["files"] for p in full) / len(full) if full else None,
        "groups": [{"prefix": n, "with": sum(g), "packs": len(g)} for n, g in largest],
        "test": {
            "groups": len(kept),
            "packs": sum(len(g) for g in kept.values()),
            "observed": test.observed,
            "null_mean": test.mean,
            "null_q95": test.q95,
            "p": test.p,
            "null": histogram(test.null, 0.5, 1, 50),
        },
        "checks": {
            "not_packager": {
                "holds": bool(full) and one_date < PACKAGER_ONE_DATE,
                "one_date": one_date,
            },
            "group_choice": {"holds": bool(kept) and test.observed > test.q95, "p": test.p},
        },
    }


TRAIN = f"""with f as (
  select {ERA.format(y="extract(year from v.date_min)")} as era, a.format, d.rows,
    f.cols, f.class_shade, f.high_bg_ratio, {KIND} as kind
  from work_split s
  join artifact a on a.sha256 = s.sha256 and s.split = 'train'
  join version v on v.id = a.version_id
  join work w on w.id = v.work_id and w.kind = 'single'
  join decoding d on d.sha256 = a.sha256 and d.decoder_version = :decoder and d.status = 'ok'
  join features f on f.sha256 = a.sha256 and f.extractor_version = :features
    and f.grid_sha256 = d.grid_sha256
  where v.date_min is not null and {SHOWN})"""


def material(conn: Connection, scope: Scope) -> dict[str, Any]:
    """Grid measures by era and content kind (train packs): what the composition and revival
    chapters read."""
    rows = _rows(
        conn,
        TRAIN + " select era, kind, format = 'ansi' as ansi, count(*) as works,"
        " avg(class_shade)::float as shade,"
        " percentile_cont(0.5) within group (order by rows) as median_rows,"
        " avg((cols > 80)::int)::float as wide,"
        " avg((high_bg_ratio > :bright)::int)::float as ice,"
        " grouping(kind) = 1 as whole_era"
        " from f group by grouping sets ((era, kind, format = 'ansi'), (era)) order by 1, 2, 3",
        scope.params(features=FEATURES_VERSION, bright=BRIGHT),
    )
    cells = [r for r in rows if not r["whole_era"]]
    eras = [
        {k: r[k] for k in ("era", "works", "median_rows", "wide", "ice")}
        for r in rows
        if r["whole_era"]
    ]
    return {"composition": composition(cells), "revival": revival(eras)}


def _kinds(cells: list[dict[str, Any]], era: str) -> dict[str, Kind]:
    mine = [c for c in cells if c["era"] == era and c["ansi"]]
    total = sum(c["works"] for c in mine)
    return {c["kind"]: Kind(c["works"] / total, c["shade"]) for c in mine} if total else {}


def composition(cells: list[dict[str, Any]]) -> dict[str, Any]:
    """Did shading recede, or did the packs fill with text? Mean shade share of ANSI files,
    overall and by kind, and the change between two eras split in two."""
    eras = sorted({c["era"] for c in cells})
    series: list[dict[str, Any]] = []
    for era in eras:
        kinds = _kinds(cells, era)
        series.append(
            {
                "era": era,
                "all": sum(k.share * k.mean for k in kinds.values()),
                "kinds": {name: {"share": k.share, "shade": k.mean} for name, k in kinds.items()},
            }
        )
    split = kitagawa(_kinds(cells, BEFORE), _kinds(cells, AFTER))
    holds = abs(split["composition"]) > abs(split["within"])
    return {
        "eras": series,
        "before": BEFORE,
        "after": AFTER,
        "split": split,
        "checks": {"composition_dominates": {"holds": holds, **split}},
    }


def revival(eras: list[dict[str, Any]]) -> dict[str, Any]:
    """After the quiet years, did the works come back the same?"""
    by = {e["era"]: e for e in eras}
    recent = by.get(RECENT)
    nineties = [by[e] for e in NINETIES if e in by]
    if not recent or not nineties:
        return {"eras": eras, "checks": {}}
    rows = max(e["median_rows"] for e in nineties)
    ice = max(e["ice"] for e in nineties)
    return {
        "eras": eras,
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
