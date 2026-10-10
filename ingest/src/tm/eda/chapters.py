# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The chapters read from the catalogue (ADR 0028): each returns its figures and its checks.

A check is what a written reading rests on. It is recomputed with the figures, so that the
page can say when a reading no longer matches the data. Catalogue metadata is read over every
pack; grid measures (`tm.eda.grids`) over the `train` packs only (research programme, rule 3).
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

from sqlalchemy import Connection
from tm_analysis.versions import FEATURES_VERSION

from tm.eda.base import SHOWN, Scope, rows_of
from tm.eda.stats import gini, group_agreement_test, histogram, lorenz, quantile

ADOPTION_YEAR = 1994  # the year SAUCE appears in the archive (catalogue note)
SPREAD = (1993, 1998)  # the years the SAUCE map follows
MAP_GROUPS = 12  # name prefixes on the SAUCE map
MIN_PACK = 5  # ANSI files a pack needs for its SAUCE share to mean something
MIN_GROUP = 3  # packs a name prefix needs to count as a group
SHARE_BINS = 5
NULL_BINS = 50
MAJORITY = 0.5  # a pack "has SAUCE" when most of its ANSI files do
PACKAGER_ONE_DATE = 0.25  # above this share of single-date packs, a packager stamped SAUCE
LATE_YEAR = 2000  # the decline is read from the peak to this year
MIN_PACKS = 50  # a year with fewer packs says little about their size
MIN_YEAR = 100  # works a year needs for its mix of formats to count
QUANTILES = (0.1, 0.25, 0.5, 0.75, 0.9)
TOP = 10  # the largest groups whose share the makers chapter follows
LORENZ_ERAS = ("1996-97", "2000-04", "2013-26")
ERA_STARTS = ((1994, "1990-93"), (1996, "1994-95"), (1998, "1996-97"), (2000, "1998-99"),
              (2005, "2000-04"), (2013, "2005-12"))  # fmt: skip
LAST_ERA = "2013-26"
ART = "('ansi', 'ascii', 'rip', 'xbin', 'bin', 'adf', 'tundra', 'pcboard', 'idf')"
FAMILIES = {"ansi": "ansi", "ascii": "ascii"}  # every other art format is "other"
SINGLE = """artifact a join version v on v.id = a.version_id
  join work w on w.id = v.work_id and w.kind = 'single'"""
PACKS = f"""select w.title as pack, extract(year from v.date_min)::int as year,
  count(distinct m.sha256) filter (where a.format in {ART} and {SHOWN}) as art
from work w join version v on v.work_id = w.id
left join set_member m on m.set_work_id = w.id
left join artifact a on a.sha256 = m.sha256
where w.kind = 'set' group by w.id, 1, 2"""
PREFIX = re.compile(r"[a-z]{2,}")


def era_of(year: int) -> str:
    return next((name for start, name in ERA_STARTS if year < start), LAST_ERA)


def prefix_of(pack: str) -> str | None:
    """The letters a pack's name starts with: the group, as the archive names its packs."""
    found = PREFIX.match(pack.lower())
    return found.group(0) if found else None


def contents(conn: Connection, scope: Scope) -> dict[str, Any]:
    """Before counting: what the database holds, and what it cannot read yet."""
    sources = rows_of(
        conn,
        "select s.name as source, count(*) as files from artifact a"
        f" join source s on s.id = a.source_id where {SHOWN} group by 1 order by 2 desc",
        scope.params(),
    )
    [funnel] = rows_of(
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
    unread = rows_of(
        conn,
        "select a.format, d.error_class, count(*) as works from "
        f"{SINGLE} join decoding d on d.sha256 = a.sha256 and d.decoder_version = :decoder"
        f" where d.status = 'error' and {SHOWN} group by 1, 2 order by 3 desc",
        scope.params(),
    )
    by_year = rows_of(
        conn,
        "select extract(year from v.date_min)::int as year, a.format,"
        " count(*) as works, count(*) filter (where d.status = 'ok') as grids"
        f" from {SINGLE} left join decoding d on d.sha256 = a.sha256"
        "   and d.decoder_version = :decoder"
        f" where a.format in {ART} and v.date_min is not null and {SHOWN} group by 1, 2",
        scope.params(),
    )
    missing = funnel["art"] - funnel["decoding"]
    years = _formats_by_year(by_year)
    return {
        "sources": sources,
        "funnel": funnel,
        "unread": unread,
        "years": years,
        "checks": {
            "every_work_decoded": {"holds": missing == 0, "missing": missing},
            **_ascii_wave(years),
        },
    }


def _ascii_wave(years: list[dict[str, Any]]) -> dict[str, Any]:
    """The years when ASCII files outnumber ANSI ones, among years with enough works."""
    wave = [y["year"] for y in years if y["ascii"] > y["ansi"] and _total(y) >= MIN_YEAR]
    if not wave:
        return {"ascii_wave": {"holds": False, "first": None, "last": None}}
    return {"ascii_wave": {"holds": True, "first": wave[0], "last": wave[-1]}}


def _total(year: dict[str, Any]) -> int:
    return year["ansi"] + year["ascii"] + year["other"]


def _formats_by_year(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Works per year by format family, and how many of them the museum reads as a grid."""
    years: dict[int, dict[str, Any]] = {}
    for row in rows:
        year = years.setdefault(
            row["year"], {"year": row["year"], "ansi": 0, "ascii": 0, "other": 0, "grids": 0}
        )
        year[FAMILIES.get(row["format"], "other")] += row["works"]
        year["grids"] += row["grids"]
    return [years[y] for y in sorted(years)]


def peak(conn: Connection, scope: Scope) -> dict[str, Any]:
    """Is the peak of the archive more packs, or bigger packs?"""
    packs = rows_of(conn, PACKS, scope.params())
    works = rows_of(
        conn,
        "select extract(year from v.date_min)::int as year, count(*) as works"
        f" from {SINGLE} where a.format in {ART} and {SHOWN} and v.date_min is not null"
        " group by 1",
        scope.params(),
    )
    sizes: dict[int, list[int]] = defaultdict(list)
    for pack in packs:
        if pack["year"] is not None:
            sizes[pack["year"]].append(pack["art"])
    count = {w["year"]: w["works"] for w in works}
    years: list[dict[str, Any]] = []
    for year in sorted(sizes):
        ordered = sorted(sizes[year])
        spread = [quantile(ordered, q) for q in QUANTILES]
        years.append(
            {
                "year": year,
                "packs": len(ordered),
                "works": count.get(year, 0),
                "median_art": spread[len(QUANTILES) // 2],
                "spread": spread,
            }
        )
    return {"years": years, "min_packs": MIN_PACKS, "checks": _peak_checks(years)}


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


def makers(conn: Connection, scope: Scope) -> dict[str, Any]:
    """Who made the art: a few large groups, or a crowd? Works per group (pack-name prefix)."""
    held: dict[str, Counter[str]] = defaultdict(Counter)
    for pack in rows_of(conn, PACKS, scope.params()):
        group = prefix_of(pack["pack"])
        if pack["year"] is not None and group and pack["art"]:
            held[era_of(pack["year"])][group] += pack["art"]
    eras: list[dict[str, Any]] = []
    for era in sorted(held):
        sizes = list(held[era].values())
        total = sum(sizes)
        eras.append(
            {
                "era": era,
                "groups": len(sizes),
                "works": total,
                "top": sum(n for _, n in held[era].most_common(TOP)) / total,
                "gini": gini(sizes),
                "largest": [{"prefix": g, "works": n} for g, n in held[era].most_common(3)],
                "lorenz": lorenz(sizes) if era in LORENZ_ERAS else None,
            }
        )
    return {"eras": eras, "top": TOP, "checks": _crowd_check(eras)}


def _crowd_check(eras: list[dict[str, Any]]) -> dict[str, Any]:
    if not eras:
        return {}
    busiest = max(eras, key=lambda e: e["works"])
    least = min(eras, key=lambda e: e["top"])
    return {
        "peak_is_a_crowd": {
            "holds": busiest["era"] == least["era"],
            "busiest": busiest["era"],
            "least": least["era"],
            "top": busiest["top"],
        }
    }


def sauce(conn: Connection, scope: Scope) -> dict[str, Any]:
    """Who wrote the SAUCE records: the artists' tools, the packagers, or the groups?"""
    by_year = rows_of(
        conn,
        "select extract(year from v.date_min)::int as year, a.format, count(*) as works,"
        " avg((a.sauce is not null)::int)::float as share"
        f" from {SINGLE} where a.format in ('ansi', 'ascii') and v.date_min is not null"
        f" and {SHOWN} group by 1, 2 having count(*) >= 100 order by 1, 2",
        scope.params(),
    )
    packs = rows_of(
        conn,
        "select w.title as pack, extract(year from v.date_min)::int as year,"
        " avg((a.sauce is not null)::int)::float as share,"
        " count(*) as files, count(distinct a.sauce ->> 'date') as dates"
        " from set_member m join artifact a on a.sha256 = m.sha256 and a.format = 'ansi'"
        " join work w on w.id = m.set_work_id join version v on v.work_id = w.id"
        f" where extract(year from v.date_min) between :first and :last and {SHOWN}"
        " group by w.id, w.title, 2 having count(*) >= :min_pack",
        scope.params(first=SPREAD[0], last=SPREAD[1], min_pack=MIN_PACK),
    )
    adoption = [p for p in packs if p["year"] == ADOPTION_YEAR]
    return {
        "by_year": by_year,
        "year": ADOPTION_YEAR,
        "map": _sauce_map(packs),
        **_sauce_packs(adoption),
    }


def _sauce_map(packs: list[dict[str, Any]]) -> dict[str, Any]:
    """The largest groups by year: how many of their packs carry SAUCE, out of how many."""
    cells: dict[tuple[str, int], list[bool]] = defaultdict(list)
    for pack in packs:
        if group := prefix_of(pack["pack"]):
            cells[group, pack["year"]].append(pack["share"] >= MAJORITY)
    sizes = Counter[str]()
    for (group, _), choices in cells.items():
        sizes[group] += len(choices)
    groups = [g for g, _ in sizes.most_common(MAP_GROUPS)]
    years = list(range(SPREAD[0], SPREAD[1] + 1))
    return {
        "groups": groups,
        "years": years,
        "cells": [
            [{"with": sum(cells[g, y]), "packs": len(cells[g, y])} for y in years] for g in groups
        ],
    }


def _sauce_packs(packs: list[dict[str, Any]]) -> dict[str, Any]:
    full = [p for p in packs if p["share"] == 1]
    one_date = sum(p["dates"] == 1 for p in full) / len(full) if full else 0.0
    groups: dict[str, list[bool]] = defaultdict(list)
    for p in packs:
        if group := prefix_of(p["pack"]):
            groups[group].append(p["share"] >= MAJORITY)
    kept = {name: g for name, g in groups.items() if len(g) >= MIN_GROUP}
    test = group_agreement_test(list(kept.values()))
    largest = sorted(kept.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:TOP]
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
            "null": histogram(test.null, MAJORITY, 1, NULL_BINS),
        },
        "checks": {
            "not_packager": {
                "holds": bool(full) and one_date < PACKAGER_ONE_DATE,
                "one_date": one_date,
            },
            "group_choice": {"holds": bool(kept) and test.observed > test.q95, "p": test.p},
        },
    }
