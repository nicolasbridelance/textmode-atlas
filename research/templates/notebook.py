# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Notebook template: copy to `research/NNNN-short-name/notebook.py` (or `research/exploration/`).

It reads one built dataset, checks its manifest, and gives the two estimates the research
program asks for: a design-weighted mean for a pilot drawn by stratum (ADR 0017), and an
interval from resampling packs within their strata, never files.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import json
    from pathlib import Path

    import duckdb
    import marimo as mo
    import numpy as np

    DATASET, VERSION = "d1", "1"  # edit: the dataset this notebook reads
    build = Path(__file__).resolve().parents[2] / "datasets" / "build" / DATASET / VERSION
    manifest = json.loads((build / "manifest.json").read_text())
    db = duckdb.connect()
    for table in manifest["tables"]:
        db.execute(f"create view {table} as select * from '{build / f'{table}.parquet'}'")

    def q(sql):
        return db.sql(sql).to_arrow_table()

    mo.md(
        f"# <title>\n\nDataset `{DATASET}` v{manifest['version']}, migration"
        f" {manifest['migration']}, extractors {manifest['extractors']}."
        " *State here whether this notebook is exploratory or tests a pre-registered hypothesis.*"
    )
    return db, mo, np, q


@app.cell
def _(np):
    def weighted_mean(values, weights):
        """Design-weighted mean: each drawn pack counts for the packs it stands for (N/n)."""
        values, weights = np.asarray(values, float), np.asarray(weights, float)
        return float((values * weights).sum() / weights.sum())

    def pack_bootstrap(values, weights, strata, resamples=2000, seed=0):
        """95% interval of the weighted mean, resampling packs with replacement within each
        stratum, so that the design is kept."""
        rng = np.random.default_rng(seed)
        values, weights, strata = (np.asarray(x) for x in (values, weights, strata))
        groups = [np.flatnonzero(strata == s) for s in np.unique(strata)]
        means = []
        for _ in range(resamples):
            idx = np.concatenate([rng.choice(g, size=len(g)) for g in groups])
            means.append(weighted_mean(values[idx], weights[idx]))
        return tuple(np.percentile(means, [2.5, 97.5]))

    return pack_bootstrap, weighted_mean


@app.cell
def _(mo, pack_bootstrap, q, weighted_mean):
    # Example on a pilot: the share of coloured block art per pack, reweighted to the frame.
    # Packs added by hand have no weight and stay out of every reweighted figure.
    per_pack = q(
        "select s.pack_sha256, s.stratum, s.weight,"
        " avg((w.content_kind = 'coloured_blocks')::int) as share"
        " from sample s join files f using (pack_sha256) join works w on w.sha256 = f.sha256"
        " where s.selection = 'drawn' and w.content_kind is not null group by all"
    ).to_pydict()
    estimate = weighted_mean(per_pack["share"], per_pack["weight"])
    low, high = pack_bootstrap(per_pack["share"], per_pack["weight"], per_pack["stratum"])
    mo.md(
        f"Coloured block art: **{estimate:.0%}** of a pack's works"
        f" (95% interval {low:.0%}–{high:.0%})."
    )
    return


if __name__ == "__main__":
    app.run()
