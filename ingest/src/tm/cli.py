# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The `tm` entry point. Every command is idempotent: run twice, it leaves the same state."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError
from sqlalchemy import create_engine
from tm_render.grid import Grid

from tm import corpus as corpus_mod
from tm.config import settings
from tm.decode import decode_pending
from tm.dev import storage_init
from tm.ingest import ingest_golden
from tm.storage import S3Store, s3_client

app = typer.Typer(help="Digital Museum of Character Arts.", no_args_is_help=True)
corpus_app = typer.Typer(help="YAML files in corpus/: validation and schemas.")
dev_app = typer.Typer(help="Local development environment.")
ingest_app = typer.Typer(help="Bring sources into the museum.", no_args_is_help=True)
app.add_typer(corpus_app, name="corpus")
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


@dev_app.command("storage-init")
def dev_storage_init() -> None:
    """Prepare local Garage storage: node, access key, buckets."""
    for line in storage_init(settings()) or ["already set up"]:
        typer.echo(line)


def _grid_summary(grid: Grid) -> str:
    return f"ok {grid.cols}x{grid.rows} {grid.digest()}"


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


@app.command("decode")
def decode_command() -> None:
    """Decode every stored artifact that has no result yet: a grid, or a classified error."""
    cfg = settings()
    client = s3_client()
    originals = S3Store(client, cfg.originals_bucket)
    derived = S3Store(client, cfg.derived_bucket)
    engine = create_engine(cfg.database_url)
    with engine.begin() as conn:
        results = decode_pending(conn, originals, derived)
    for item in results:
        outcome = f"error {item.error_class}" if item.grid is None else _grid_summary(item.grid)
        typer.echo(f"{item.path} {outcome}")
    typer.echo(f"{len(results)} decoded")
