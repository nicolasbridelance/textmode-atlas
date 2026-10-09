# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The `tm` entry point. Every command is idempotent: run twice, it leaves the same state."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError
from sqlalchemy import create_engine
from tm_render.conservation import MAX_SCALE, BitmapFont

from tm import corpus as corpus_mod
from tm.config import settings
from tm.datasets import DatasetError, build, draw_sample
from tm.decode import decode_artifact, pending_artifacts
from tm.dev import storage_init
from tm.features import extract_artifact, pending_features
from tm.ingest import ingest_golden
from tm.packs import PACK_SOURCES, PackIngested, ingest_pack, pack_archives
from tm.pilots import SampleError
from tm.render import pending_renderings, render_artifact
from tm.shards import Shard
from tm.storage import S3Store, s3_client
from tm.text_layer import pending_text, read_artifact

app = typer.Typer(help="Digital Museum of Character Arts.", no_args_is_help=True)
corpus_app = typer.Typer(help="YAML files in corpus/: validation and schemas.")
dataset_app = typer.Typer(help="Frozen extracts of the database, for research.")
dev_app = typer.Typer(help="Local development environment.")
ingest_app = typer.Typer(help="Bring sources into the museum.", no_args_is_help=True)
app.add_typer(corpus_app, name="corpus")
app.add_typer(dataset_app, name="dataset")
app.add_typer(dev_app, name="dev")
app.add_typer(ingest_app, name="ingest")

CorpusRoot = Annotated[Path, typer.Option(help="Root of the corpus/ directory.")]


@corpus_app.command("check")
def corpus_check(root: CorpusRoot = Path("corpus")) -> None:
    """Validate every profile, collection and the radio list."""
    errors = 0
    for path in corpus_mod.corpus_files(root):
        try:
            corpus_mod.load(path)
        except (ValidationError, ValueError) as err:
            errors += 1
            typer.echo(f"✗ {path}\n{err}", err=True)
        else:
            typer.echo(f"✓ {path}")
    stale = [
        name
        for name, content in corpus_mod.json_schemas().items()
        if not (root / "schema" / name).exists()
        or (root / "schema" / name).read_text(encoding="utf-8") != content
    ]
    for name in stale:
        errors += 1
        typer.echo(f"✗ corpus/schema/{name} is out of date: run `tm corpus schema`", err=True)
    if errors:
        raise typer.Exit(1)


@corpus_app.command("schema")
def corpus_schema(root: CorpusRoot = Path("corpus")) -> None:
    """Regenerate the JSON Schemas in corpus/schema/ from the models."""
    (root / "schema").mkdir(parents=True, exist_ok=True)
    for name, content in corpus_mod.json_schemas().items():
        (root / "schema" / name).write_text(content, encoding="utf-8")
        typer.echo(f"wrote corpus/schema/{name}")


@dataset_app.command("build")
def dataset_build(
    name: Annotated[str, typer.Argument(help="A dataset defined in datasets/<name>/.")],
    definitions: Annotated[Path, typer.Option(help="Where datasets are defined.")] = Path(
        "datasets"
    ),
    out: Annotated[Path, typer.Option(help="Where builds go.")] = Path("datasets/build"),
) -> None:
    """Build a dataset: one Parquet file per table and a manifest, the same bytes every time."""
    # One snapshot for every table, even while an ingestion is writing.
    engine = create_engine(
        settings().database_url,
        isolation_level="REPEATABLE READ",
        execution_options={"postgresql_readonly": True},
    )
    with engine.connect() as conn:
        try:
            built = build(conn, definitions / name, out)
        except (DatasetError, SampleError, ValidationError) as err:
            typer.echo(f"✗ {err}", err=True)
            raise typer.Exit(1) from err
    for table, rows in built.rows.items():
        typer.echo(f"{table}: {rows} rows")
    typer.echo(f"built {built.directory}")


@dataset_app.command("draw")
def dataset_draw(
    name: Annotated[str, typer.Argument(help="A dataset defined in datasets/<name>/.")],
    definitions: Annotated[Path, typer.Option(help="Where datasets are defined.")] = Path(
        "datasets"
    ),
) -> None:
    """Draw a pilot dataset's sample from its frame into sample.yaml, to be committed."""
    engine = create_engine(settings().database_url, execution_options={"postgresql_readonly": True})
    with engine.connect() as conn:
        try:
            path = draw_sample(conn, definitions / name)
        except (DatasetError, SampleError, ValidationError) as err:
            typer.echo(f"✗ {err}", err=True)
            raise typer.Exit(1) from err
    typer.echo(f"drew {path}")


@dev_app.command("storage-init")
def dev_storage_init() -> None:
    """Prepare local Garage storage: node, access key, buckets."""
    for line in storage_init(settings()) or ["already set up"]:
        typer.echo(line)


@ingest_app.command("golden")
def ingest_golden_command(
    root: Annotated[Path, typer.Option(help="Directory of golden artifacts.")] = Path(
        "tests/golden"
    ),
) -> None:
    """Store the project's golden artifacts and record them: source, work, version, artifact."""
    cfg = settings()
    store = S3Store(s3_client(), cfg.originals_bucket)
    engine = create_engine(cfg.database_url)
    with engine.begin() as conn:
        for item in ingest_golden(conn, store, root):
            typer.echo(f"{'ingested' if item.new else 'already known'} {item.path} {item.sha256}")


SHARD_HELP = "Take only shard i of n (i/n): run n processes, one per index, to share the work."


def _shard(text: str) -> Shard:
    try:
        return Shard.parse(text)
    except ValueError as err:
        raise typer.BadParameter(str(err)) from err


@app.command("decode")
def decode_command(
    shard: Annotated[str, typer.Option(help=SHARD_HELP)] = "0/1",
) -> None:
    """Decode every stored artifact that has no result yet: a grid, or a classified error."""
    cfg = settings()
    client = s3_client()
    originals = S3Store(client, cfg.originals_bucket)
    derived = S3Store(client, cfg.derived_bucket)
    engine = create_engine(cfg.database_url)
    with engine.connect() as conn:
        todo = pending_artifacts(conn, _shard(shard))
    for artifact in todo:
        with engine.begin() as conn:  # one transaction per artifact: a long run keeps its work
            item = decode_artifact(conn, originals, derived, artifact)
        outcome = (
            f"error {item.error_class}"
            if item.error_class
            else f"ok {item.cols}x{item.rows} {item.grid_sha256}"
        )
        typer.echo(f"{item.path} {outcome}")
    typer.echo(f"{len(todo)} decoded")


@app.command("render")
def render_command(
    scale: Annotated[int, typer.Option(min=1, max=MAX_SCALE, help="Integer scale.")] = 1,
    font: Annotated[Path, typer.Option(help="Bitmap font (.f16).")] = Path(
        "corpus/fonts/ibm-vga-8x16.f16"
    ),
    shard: Annotated[str, typer.Option(help=SHARD_HELP)] = "0/1",
) -> None:
    """Draw a conservation PNG of every decoded grid not yet rendered with these settings."""
    cfg = settings()
    derived = S3Store(s3_client(), cfg.derived_bucket)
    bitmap = BitmapFont.load(font)
    engine = create_engine(cfg.database_url)
    with engine.connect() as conn:
        todo = pending_renderings(conn, bitmap, scale, _shard(shard))
    for row in todo:
        with engine.begin() as conn:  # one transaction per rendering
            item = render_artifact(conn, derived, bitmap, scale, row)
        recipe = item.recipe
        typer.echo(f"{item.path} {recipe['width']}x{recipe['height']} {recipe['pixels_sha256']}")
    typer.echo(f"{len(todo)} rendered")


@app.command("features")
def features_command(
    shard: Annotated[str, typer.Option(help=SHARD_HELP)] = "0/1",
) -> None:
    """Measure every decoded grid that has no features from this extractor version yet."""
    cfg = settings()
    derived = S3Store(s3_client(), cfg.derived_bucket)
    engine = create_engine(cfg.database_url)
    with engine.connect() as conn:
        todo = pending_features(conn, _shard(shard))
    for row in todo:
        with engine.begin() as conn:  # one transaction per grid
            features = extract_artifact(conn, derived, row)
        typer.echo(f"{row.source_path} fill {features.fill_ratio:.2f} colours {features.n_colors}")
    typer.echo(f"{len(todo)} measured")


@app.command("text")
def text_command(
    shard: Annotated[str, typer.Option(help=SHARD_HELP)] = "0/1",
) -> None:
    """Read the text layer of every decoded grid that has none from this extractor version yet."""
    cfg = settings()
    derived = S3Store(s3_client(), cfg.derived_bucket)
    engine = create_engine(cfg.database_url)
    with engine.connect() as conn:
        todo = pending_text(conn, _shard(shard))
    for row in todo:
        with engine.begin() as conn:  # one transaction per grid
            lines = read_artifact(conn, derived, row)
        typer.echo(f"{row.source_path} {len(lines)} lines")
    typer.echo(f"{len(todo)} read")


@ingest_app.command("pack")
def ingest_pack_command(
    paths: Annotated[list[Path], typer.Argument(help="Pack archives, or directories of them.")],
    source: Annotated[
        str, typer.Option(help=f"Archive mirrored: {', '.join(PACK_SOURCES)}.")
    ] = "16colo",
) -> None:
    """Store packs from a local mirror and record them: the set, its files, the art."""
    if source not in PACK_SOURCES:
        raise typer.BadParameter(f"unknown source {source!r}", param_hint="--source")
    cfg = settings()
    store = S3Store(s3_client(), cfg.originals_bucket)
    engine = create_engine(cfg.database_url)
    archives = pack_archives(paths)
    for archive in archives:
        with engine.begin() as conn:  # one transaction per pack
            typer.echo(_pack_summary(ingest_pack(conn, store, archive, PACK_SOURCES[source])))
    typer.echo(f"{len(archives)} packs")


def _pack_summary(item: PackIngested) -> str:
    if not item.new and not item.members:
        return f"already known {item.path}"
    parts = [f"{'ingested' if item.new else 'completed'} {item.path} {item.members} members"]
    if item.error_class:
        parts.append(f"error {item.error_class}")
    if item.unreadable:
        parts.append(f"{len(item.unreadable)} unreadable: {', '.join(item.unreadable)}")
    return "; ".join(parts)
