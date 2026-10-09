# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The nearest-works graph read as a social network (roadmap step 12, leads I48).

Exploratory: no hypothesis is tested here. Reads the `graph` build (`just graph`) and the
`works` dataset it was made from (train packs only). Countries come from Demozoo when the local
`demozoo_raw` database is there: a group's country is the country of most of its members (60% at
least, two members at least), matched by name. It is an inference, kept in this notebook.

    uv run --group research marimo edit research/exploration/neighbours.py
    uv run --group research python research/exploration/neighbours.py   # prints the tables
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import collections
    import json
    import os
    from pathlib import Path

    import duckdb
    import igraph as ig
    import marimo as mo
    import numpy as np

    root = Path(__file__).resolve().parents[2]
    graph_dir = root / "datasets" / "build" / "graph" / "1"
    manifest = json.loads((graph_dir / "manifest.json").read_text())
    works_dir = root / "datasets" / "build" / "works" / str(manifest["works"]["version"])
    db = duckdb.connect()
    db.execute(f"create view works as select * from '{works_dir / 'works.parquet'}'")
    db.execute(f"create view nodes as select * from '{graph_dir / 'nodes.parquet'}'")
    db.execute(f"create view edges as select * from '{graph_dir / 'edges.parquet'}'")
    mo.md(
        f"# The nearest-works graph\n\nGraph build {manifest['version']} (neighbours"
        f" v{manifest['neighbours']}, k = {manifest['k']}, {manifest['communities']['method']}),"
        f" from `works` v{manifest['works']['version']}. *Exploratory: train packs only.*"
    )
    return collections, db, ig, mo, np, os


@app.cell
def _(collections, db, os):
    def group_countries():
        """Group name (lower case) → the country of most of its members, from Demozoo."""
        url = os.environ.get("TM_DATABASE_URL", "").replace("+psycopg", "")
        if not url:
            return {}
        import psycopg

        sql = (
            "select lower(n.name), m.country_code from demoscene_nick n"
            " join demoscene_releaser g on g.id = n.releaser_id and g.is_group"
            " join demoscene_membership s on s.group_id = g.id"
            " join demoscene_releaser m on m.id = s.member_id where m.country_code <> ''"
        )
        votes = collections.defaultdict(collections.Counter)
        try:
            with psycopg.connect(url.rsplit("/", 1)[0] + "/demozoo_raw") as conn:
                for name, country in conn.execute(sql):
                    votes[name][country] += 1
        except psycopg.OperationalError:
            return {}
        found = {}
        for name, counts in votes.items():
            country, top = counts.most_common(1)[0]
            total = sum(counts.values())
            if total >= 2 and top / total >= 0.6:  # noqa: PLR2004
                found[name] = country
        return found

    countries = group_countries()
    rows = db.execute(
        "select n.sha256, w.year, lower(trim(w.sauce_group)), lower(trim(w.sauce_author)),"
        " w.pack, w.content_kind, w.grid_sha256, n.in_degree, n.community"
        " from nodes n join works w using (sha256) order by n.sha256"
    ).fetchall()
    index = {row[0]: i for i, row in enumerate(rows)}
    attrs = {
        "year": [r[1] for r in rows],
        "era": [r[1] // 5 * 5 if r[1] else None for r in rows],
        "group": [r[2] or None for r in rows],
        "author": [r[3] or None for r in rows],
        "pack": [r[4] for r in rows],
        "kind": [r[5] for r in rows],
        "country": [countries.get(r[2]) if r[2] else None for r in rows],
        "same grid": [r[6] for r in rows],
    }
    edges = [
        (index[s], index[t]) for s, t in db.execute("select source, target from edges").fetchall()
    ]
    return attrs, edges, rows


@app.cell
def _(edges, ig, mo, np, rows):
    count = len(rows)
    graph = ig.Graph(n=count, edges=edges, directed=True)
    indegree = np.array([r[7] for r in rows])
    ties = graph.as_undirected(mode="collapse")
    membership = np.array([r[8] for r in rows])
    top = int(count / 100)
    held = np.sort(indegree)[::-1][:top].sum() / indegree.sum()
    mo.md(
        f"""## Shape

| Measure | Value |
| --- | ---: |
| works | {count:,} |
| edges (each work → its 10 nearest) | {len(edges):,} |
| mutual (reciprocity) | {graph.reciprocity():.3f} |
| works nobody has as a neighbour | {(indegree == 0).mean():.1%} |
| largest in-degree | {indegree.max()} |
| share of in-edges held by the top 1% | {held:.1%} |
| connected components | {len(ties.connected_components())} |
| transitivity | {ties.transitivity_undirected():.3f} |
| communities (Leiden) | {membership.max() + 1} |
| modularity | {ties.modularity(membership.tolist()):.3f} |
"""
    )
    return (membership,)


@app.cell
def _(attrs, collections, edges, mo):
    def _lift(_values, _cells=None):
        """Share of edges joining two works of the same value, against chance: picking the
        target at random among works with a known value (in the source's cell, if given)."""
        _known = collections.defaultdict(collections.Counter)
        for _i, _value in enumerate(_values):
            if _value is not None:
                _known[_cells[_i] if _cells else None][_value] += 1
        _same = _expected = _pairs = 0
        for _a, _b in edges:
            if _values[_a] is None or _values[_b] is None:
                continue
            _counts = _known[_cells[_a] if _cells else None]
            _expected += _counts[_values[_a]] / sum(_counts.values())
            _same += _values[_a] == _values[_b]
            _pairs += 1
        return _pairs, _same / _pairs, _expected / _pairs

    _cells = list(zip(attrs["kind"], attrs["era"], strict=True))
    _lines = []
    for _name, _values in attrs.items():
        _pairs, _same, _chance = _lift(_values)
        _controlled = _lift(_values, _cells)[2] if _name not in ("kind", "era") else None
        _within = f"{_same / _controlled:.1f}" if _controlled else "–"
        _lines.append(
            f"| {_name} | {_pairs:,} | {_same:.1%} | {_chance:.2%} | {_same / _chance:.1f}"
            f" | {_within} |"
        )
    mo.md(
        "## Homophily: do neighbours share a year, a group, an author?\n\n"
        "| Attribute | Edges with both known | Same | Chance | Lift | Lift within kind and"
        " five-year era |\n| --- | ---: | ---: | ---: | ---: | ---: |\n" + "\n".join(_lines)
    )
    return


@app.cell
def _(attrs, collections, membership, mo, np, rows):
    _lines = []
    for _community in range(min(15, membership.max() + 1)):
        _members = np.flatnonzero(membership == _community)
        _years = [attrs["year"][_i] for _i in _members if attrs["year"][_i]]
        _kind, _kinds = collections.Counter(attrs["kind"][_i] for _i in _members).most_common(1)[0]
        _groups = collections.Counter(attrs["group"][_i] for _i in _members if attrs["group"][_i])
        _hub = _members[np.argmax([rows[_i][7] for _i in _members])]
        _lines.append(
            f"| {_community} | {len(_members):,} | {np.percentile(_years, 25):.0f}–"
            f"{np.median(_years):.0f}–{np.percentile(_years, 75):.0f}"
            f" | {_kind} {_kinds / len(_members):.0%}"
            f" | {', '.join(g for g, _ in _groups.most_common(3))} | {rows[_hub][4]} |"
        )
    mo.md(
        "## The largest communities\n\n| Community | Works | Years (quartiles) | Main kind |"
        " Most frequent groups | Most central work's pack |\n"
        "| ---: | ---: | --- | --- | --- | --- |\n" + "\n".join(_lines)
    )
    return


if __name__ == "__main__":
    app.run()
