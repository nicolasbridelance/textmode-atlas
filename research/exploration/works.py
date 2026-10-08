# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Works exploration: the art of 16colo as images and measurements (roadmap step 5).

Exploratory: no hypothesis is tested here, and what it shows are leads. Reads the `works`
dataset (`uv run tm dataset build works`), which holds the train packs only; the renderings
come from the private derived bucket, so the contact sheets need the local storage (`TM_*`).
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import io
    import json
    from pathlib import Path

    import altair as alt
    import duckdb
    import marimo as mo

    build = Path(__file__).resolve().parents[2] / "datasets" / "build" / "works" / "1"
    manifest = json.loads((build / "manifest.json").read_text())
    db = duckdb.connect()
    db.execute(f"create view works as select * from '{build / 'works.parquet'}'")
    db.execute(f"create view features as select * from '{build / 'features.parquet'}'")
    # One row per decoded work, with its metadata: what most views read.
    db.execute("create view w as select * from works join features using (sha256, cols, rows)")

    def q(sql):
        return db.sql(sql).to_arrow_table()

    alt.data_transformers.disable_max_rows()
    mo.md(
        f"# 16colo works\n\nDataset `works` v{manifest['version']}, migration"
        f" {manifest['migration']}, extractors {manifest['extractors']}:"
        f" {manifest['tables']['works']['rows']:,} art files of the train packs,"
        f" {manifest['tables']['features']['rows']:,} measured grids. *Exploratory: the test"
        " packs are not here, and stay unexamined.*"
    )
    return alt, io, mo, q


@app.cell
def _(alt, mo, q):
    per_year = q(
        "select year, format, count(*) as works from works where year is not null group by all"
    )
    mo.vstack(
        [
            mo.md("## Works per year, by format"),
            alt.Chart(per_year)
            .mark_bar()
            .encode(x="year:O", y="works:Q", color="format:N", tooltip=["format", "works"])
            .properties(width="container", height=260),
        ]
    )
    return


@app.cell
def _(alt, mo, q):
    canvas = q(
        """
        select year,
          avg((cols > 80)::int) as wider_than_80,
          quantile_cont(rows, 0.5) as median_rows,
          quantile_cont(rows, 0.9) as p90_rows,
          avg((bytes::double / (cols * rows) > 20)::int) as animation_like
        from w where year is not null group by year order by year
        """
    )
    _base = alt.Chart(canvas).encode(x="year:O").properties(width=420, height=220)
    mo.vstack(
        [
            mo.md(
                "## Canvas\n\nMedian and 90th percentile of rows; share wider than 80 columns;"
                " share *animation-like* (over 20 bytes of file per cell: the screen is"
                " redrawn, and the grid shows only its last state)."
            ),
            mo.hstack(
                [
                    _base.mark_line(point=True).encode(y="median_rows:Q")
                    + _base.mark_line(strokeDash=[4, 2]).encode(y="p90_rows:Q"),
                    _base.mark_line(point=True).encode(y="wider_than_80:Q")
                    + _base.mark_line(color="firebrick").encode(y="animation_like:Q"),
                ]
            ),
        ]
    )
    return


@app.cell
def _(alt, mo, q):
    classes = q(
        """
        unpivot (
          select year, avg(class_block) as block, avg(class_half_block) as half_block,
            avg(class_shade) as shade, avg(class_box) as box,
            avg(class_alphanumeric) as alphanumeric, avg(class_punctuation) as punctuation,
            avg(class_other) as other
          from w where year is not null and format = 'ansi' group by year
        ) on block, half_block, shade, box, alphanumeric, punctuation, other
        into name class value share
        """
    )
    mo.vstack(
        [
            mo.md(
                "## What ANSI is drawn with\n\nMean share of each glyph class among visible"
                " glyphs, per year (ANSI files; ASCII is in the next view)."
            ),
            alt.Chart(classes)
            .mark_area()
            .encode(
                x="year:O",
                y=alt.Y("share:Q", stack="normalize"),
                color=alt.Color("class:N", sort=["block", "half_block", "shade", "box"]),
                tooltip=["class", alt.Tooltip("share:Q", format=".1%")],
            )
            .properties(width="container", height=280),
        ]
    )
    return


@app.cell
def _(alt, mo, q):
    colour = q(
        """
        select year, format,
          quantile_cont(n_colors, 0.5) as median_colours,
          avg((high_bg_ratio > 0)::int) as uses_bright_bg,
          avg(coalesce(sauce_ice, false)::int) as sauce_says_ice,
          avg((draw_order < 0.9)::int) as drawn_not_typed,
          count(*) as works
        from w where year is not null group by all order by year
        """
    )
    _base = alt.Chart(colour).encode(x="year:O", color="format:N").properties(width=330, height=220)
    mo.vstack(
        [
            mo.md(
                "## Colour and drawing\n\nThe catalogue found the SAUCE iCE flag almost never"
                " set before 1998. Here, against it: the share of works whose grid *uses* the"
                " blink bit under ink (a bright background in iCE, blinking otherwise). And the"
                " share of works not written in reading order (draw order < 0.9)."
            ),
            mo.hstack(
                [
                    _base.mark_line(point=True).encode(y="uses_bright_bg:Q")
                    + _base.mark_line(strokeDash=[4, 2]).encode(y="sauce_says_ice:Q"),
                    _base.mark_line(point=True).encode(y="drawn_not_typed:Q"),
                    _base.mark_line(point=True).encode(y="median_colours:Q"),
                ]
            ),
        ]
    )
    return


@app.cell
def _(mo, q):
    years = q(
        "select year, count(rendering_sha256) as rendered from works where year is not null"
        " group by year order by year"
    ).to_pylist()
    year_list = [str(y["year"]) for y in years]
    busiest = max(years, key=lambda y: y["rendered"])["year"]
    year = mo.ui.dropdown(year_list, value=str(busiest), label="Year")
    order = mo.ui.dropdown(
        {
            "random (fixed seed)": "hash(sha256)",
            "most colours": "n_colors desc",
            "most glyph entropy": "glyph_entropy desc",
            "most shades": "class_shade desc",
            "most half blocks": "class_half_block desc",
            "least linear drawing": "draw_order",
            "tallest": "rows desc",
        },
        value="random (fixed seed)",
        label="Order",
    )
    group = mo.ui.text(label="Group or pack contains", value="")
    count = mo.ui.slider(12, 96, step=12, value=36, label="Works")
    mo.vstack([mo.md("## Contact sheet"), mo.hstack([year, order, group, count])])
    return count, group, order, year


@app.cell
def _(count, group, io, mo, order, q, year):
    from PIL import Image
    from tm.config import settings
    from tm.storage import S3Store, rendering_key, s3_client

    store = S3Store(s3_client(), settings().derived_bucket)
    needle = group.value.replace("'", "''").lower()
    picked = q(
        f"""
        select pack, path, sauce_author, sauce_group, cols, rows, rendering_sha256 from w
        where year = {int(year.value)} and rendering_sha256 is not null
          and (lower(coalesce(sauce_group, '')) like '%{needle}%' or lower(pack) like '%{needle}%')
        order by {order.value}, sha256 limit {count.value}
        """
    ).to_pylist()

    def thumbnail(sha):
        """The first screen (25 rows) of the rendering, at half size."""
        image = Image.open(io.BytesIO(store.get(rendering_key(sha))))
        screen = image.crop((0, 0, image.width, min(image.height, 16 * 25)))
        screen.thumbnail((image.width // 2, 200))
        out = io.BytesIO()
        screen.save(out, "PNG")
        return out.getvalue()

    cards = [
        mo.vstack(
            [
                mo.image(thumbnail(p["rendering_sha256"])),
                mo.md(
                    f"<small>**{p['path'].rsplit('/', 1)[-1]}** {p['pack']}<br>"
                    f"{p['sauce_author'] or '?'} / {p['sauce_group'] or '?'} ·"
                    f" {p['cols']}×{p['rows']}</small>"
                ),
            ]
        )
        for p in picked
    ]
    mo.vstack(
        [mo.md(f"{len(picked)} works shown."), mo.hstack(cards, wrap=True, justify="start")]
        if cards
        else [mo.md("No rendered work matches.")]
    )
    return


@app.cell
def _(alt, mo, q):
    import numpy as np
    from sklearn.decomposition import PCA

    sample = q(
        """
        select sha256, year, pack, coalesce(sauce_group, '?') as grp, fill_ratio, glyph_entropy,
          class_block, class_half_block, class_shade, class_box, class_alphanumeric,
          class_punctuation, n_colors / 16.0 as colours, high_bg_ratio, symmetry_h, draw_order
        from w where year is not null using sample reservoir(20000 rows) repeatable (42)
        """
    )
    columns = sample.column_names[4:]
    matrix = np.column_stack([sample.column(c).to_numpy() for c in columns]).astype(float)
    matrix = (matrix - matrix.mean(axis=0)) / (matrix.std(axis=0) + 1e-9)
    pca = PCA(n_components=2, random_state=0).fit(matrix)
    xy = pca.transform(matrix)
    points = sample.select(["year", "pack", "grp"]).append_column("x", [xy[:, 0]])
    points = points.append_column("y", [xy[:, 1]])
    loadings = {name: np.round(pca.components_[:, i], 2).tolist() for i, name in enumerate(columns)}
    mo.vstack(
        [
            mo.md(
                "## A first map\n\n20,000 decoded works (fixed sample), on the first two"
                " principal components of standardized features, coloured by year. A linear"
                f" view: it explains {pca.explained_variance_ratio_.sum():.0%} of the variance."
                f" Loadings (PC1, PC2): `{loadings}`"
            ),
            alt.Chart(points)
            .mark_circle(size=6, opacity=0.4)
            .encode(
                x="x:Q",
                y="y:Q",
                color=alt.Color("year:Q", scale=alt.Scale(scheme="viridis")),
                tooltip=["pack", "grp", "year"],
            )
            .properties(width="container", height=520)
            .interactive(),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
