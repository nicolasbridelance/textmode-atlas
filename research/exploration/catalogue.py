# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Catalogue exploration: what 16colo holds, before anything is chosen from it (roadmap step 2).

Exploratory: no hypothesis is tested here, and what it shows are leads. Reads the `catalogue`
dataset (`uv run tm dataset build catalogue`), never the database.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    from pathlib import Path

    import altair as alt
    import duckdb
    import marimo as mo

    build = Path(__file__).resolve().parents[2] / "datasets" / "build" / "catalogue" / "1"
    manifest = json.loads((build / "manifest.json").read_text())
    db = duckdb.connect()
    db.execute(f"create view packs as select * from '{build / 'packs.parquet'}'")
    db.execute(f"create view files as select * from '{build / 'files.parquet'}'")

    def q(sql):
        return db.sql(sql).to_arrow_table()

    mo.md(
        f"# 16colo catalogue\n\nDataset `catalogue` v{manifest['version']}, migration"
        f" {manifest['migration']}, decoder {manifest['extractors']['decoder']}:"
        f" {manifest['tables']['packs']['rows']:,} pack archives,"
        f" {manifest['tables']['files']['rows']:,} files in them."
    )
    return alt, mo, q


@app.cell
def _(alt, mo, q):
    per_year = q(
        "select year, count(*) as packs, sum(members)::bigint as files from packs group by year"
        " order by year"
    )
    mo.vstack(
        [
            mo.md("## Packs per year\n\nThe year is the one 16colo files the pack under."),
            alt.Chart(per_year).mark_bar().encode(x="year:O", y="packs:Q", tooltip=["files:Q"]),
        ]
    )
    return


@app.cell
def _(mo, q):
    mo.vstack(
        [
            mo.md("## Reading the archives"),
            mo.ui.table(
                q(
                    "select archive_format, expansion, expansion_error, count(*) as packs,"
                    " sum(unreadable)::bigint as unreadable_members from packs"
                    " group by all order by packs desc"
                )
            ),
        ]
    )
    return


@app.cell
def _(alt, mo, q):
    kinds = q(
        """
        select p.year,
          case when f.is_art then 'art (' || f.format || ')'
               when f.format in ('nfo', 'diz', 'text') then 'document'
               else 'other' end as kind,
          count(*) as files
        from files f join packs p using (pack_sha256)
        group by all
        """
    )
    mo.vstack(
        [
            mo.md("## What packs contain\n\nArt by format, NFO / DIZ / text, everything else."),
            alt.Chart(kinds)
            .mark_bar()
            .encode(x="year:O", y=alt.Y("files:Q", stack="normalize"), color="kind:N"),
        ]
    )
    return


@app.cell
def _(alt, mo, q):
    sauce = q(
        """
        select p.year, avg(f.has_sauce::int) as share_with_sauce, count(*) as art_files
        from files f join packs p using (pack_sha256)
        where f.is_art group by p.year order by p.year
        """
    )
    mo.vstack(
        [
            mo.md("## SAUCE records\n\nShare of art files ending with a SAUCE record."),
            alt.Chart(sauce)
            .mark_line(point=True)
            .encode(x="year:O", y="share_with_sauce:Q", tooltip=["art_files:Q"]),
        ]
    )
    return


@app.cell
def _(alt, mo, q):
    widths = q(
        """
        select case when cols <= 80 then cols::text else 'over 80' end as width, count(*) as files
        from files where decoding = 'ok' group by all order by files desc limit 20
        """
    )
    errors = q(
        "select decoding_error, count(*) as files from files where decoding = 'error'"
        " group by all order by files desc"
    )
    mo.vstack(
        [
            mo.md("## Canvas widths (decoded ANSI)"),
            alt.Chart(widths).mark_bar().encode(x=alt.X("width:N", sort="-y"), y="files:Q"),
            mo.md("Decoding errors"),
            mo.ui.table(errors),
        ]
    )
    return


@app.cell
def _(alt, mo, q):
    ice = q(
        """
        select p.year, avg((f.sauce_flags & 1)::int) as share_ice, count(*) as files
        from files f join packs p using (pack_sha256)
        where f.has_sauce and f.sauce_data_type in (1, 5, 6) group by p.year order by p.year
        """
    )
    fonts = q(
        "select coalesce(sauce_font, '(none)') as font, count(*) as files from files"
        " where has_sauce group by all order by files desc limit 15"
    )
    mo.vstack(
        [
            mo.md("## iCE colours and fonts (SAUCE)\n\niCE: TFlags bit 0, character files."),
            alt.Chart(ice).mark_line(point=True).encode(x="year:O", y="share_ice:Q"),
            mo.ui.table(fonts),
        ]
    )
    return


@app.cell
def _(mo, q):
    groups = q(
        """
        select f.sauce_group as sauce_group, count(*) as files,
          count(distinct f.pack_sha256) as packs,
          min(p.year) as first_year, max(p.year) as last_year
        from files f join packs p using (pack_sha256)
        where f.is_art and coalesce(f.sauce_group, '') <> ''
        group by all order by files desc limit 40
        """
    )
    mo.vstack(
        [
            mo.md(
                "## Groups, as SAUCE names them\n\nSpelling is not normalised: one group may"
                " appear under several names. NFO credits come later (roadmap, R1)."
            ),
            mo.ui.table(groups),
        ]
    )
    return


@app.cell
def _(mo, q):
    documents = q(
        """
        select p.year,
          avg((exists (select 1 from files d where d.pack_sha256 = p.pack_sha256
                       and d.format = 'nfo'))::int) as with_nfo,
          avg((exists (select 1 from files d where d.pack_sha256 = p.pack_sha256
                       and d.format = 'diz'))::int) as with_diz
        from packs p where p.members > 0 group by p.year order by p.year
        """
    )
    shared = q(
        """
        select packs_holding, count(*) as files from (
          select sha256, count(distinct pack_sha256) as packs_holding from files group by sha256
        ) group by all order by packs_holding
        """
    )
    mo.vstack(
        [
            mo.md("## NFO and DIZ per pack, by year"),
            mo.ui.table(documents),
            mo.md("## Files found in several packs"),
            mo.ui.table(shared),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
