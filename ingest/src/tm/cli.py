# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""The `tm` entry point. Every command is idempotent: run twice, it leaves the same state."""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError
from sqlalchemy import create_engine
from tm_render.conservation import MAX_SCALE, BitmapFont

from tm import corpus as corpus_mod
from tm import ratings
from tm.acquire import acquire
from tm.acquisitions import load_acquisitions
from tm.audience import rate_flashing, rate_words
from tm.budget import BudgetError, Ledger
from tm.config import settings
from tm.datasets import DatasetError, build, draw_sample
from tm.decode import decode_artifact, pending_artifacts
from tm.dev import storage_init
from tm.eda import publish, snapshot
from tm.export import ExportError, Outcome, export_work, exportable
from tm.features import extract_artifact, pending_features
from tm.ingest import ingest_golden
from tm.lists import collect, write_lists
from tm.loose import LooseIngested, ingest_loose, loose_files
from tm.packs import PACK_SOURCES, PackIngested, PackSource, ingest_pack, pack_archives
from tm.pilots import SampleError
from tm.render import pending_renderings, render_artifact
from tm.shards import Shard
from tm.storage import S3Store, s3_client
from tm.text_layer import pending_text, read_artifact

app = typer.Typer(help="Digital Museum of Character Arts.", no_args_is_help=True)
corpus_app = typer.Typer(help="YAML files in corpus/: validation and schemas.")
dataset_app = typer.Typer(help="Frozen extracts of the database, for research.")
dev_app = typer.Typer(help="Local development environment.")
budget_app = typer.Typer(help="Paid model calls: the owner's grants and what was spent.")
ingest_app = typer.Typer(help="Bring sources into the museum.", no_args_is_help=True)
app.add_typer(corpus_app, name="corpus")
app.add_typer(dataset_app, name="dataset")
app.add_typer(dev_app, name="dev")
app.add_typer(budget_app, name="budget")
app.add_typer(ingest_app, name="ingest")

CorpusRoot = Annotated[Path, typer.Option(help="Root of the corpus/ directory.")]
DocsRoot = Annotated[Path, typer.Option(help="Where the grid's pages are written.")]
SiteRoot = Annotated[
    Path | None, typer.Option(help="Root of a mirror laid out as the archive's site (ADR 0024).")
]
FONT = Path("ibm-vga-8x16.f16")
ACQUIRE_PAUSE_SECONDS = 2  # one request at a time, politely


@corpus_app.command("check")
def corpus_check(root: CorpusRoot = Path("corpus"), docs: DocsRoot = Path("docs")) -> None:
    """Validate every corpus file, and check that what is derived from them is current."""
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
    for problem in corpus_mod.broken_references(root):
        errors += 1
        typer.echo(f"✗ {problem}", err=True)
    for path in _stale_ratings(root, docs):
        errors += 1
        typer.echo(f"✗ {path} is out of date: run `tm corpus ratings`", err=True)
    if errors:
        raise typer.Exit(1)


@corpus_app.command("schema")
def corpus_schema(root: CorpusRoot = Path("corpus")) -> None:
    """Regenerate the JSON Schemas in corpus/schema/ from the models."""
    (root / "schema").mkdir(parents=True, exist_ok=True)
    for name, content in corpus_mod.json_schemas().items():
        (root / "schema" / name).write_text(content, encoding="utf-8")
        typer.echo(f"wrote corpus/schema/{name}")


@corpus_app.command("practices")
def corpus_practices(root: CorpusRoot = Path("corpus")) -> None:
    """Say which practices of the character arts the holdings represent, family by family."""
    registry = corpus_mod.load_practices(root / "practices.yaml")
    held = {practice.code for practice in registry.held()}
    for family in registry.families:
        codes = [p.code for p in registry.practices if p.family == family.code]
        missing = [code for code in codes if code not in held]
        typer.echo(f"{family.code}: {len(codes) - len(missing)} of {len(codes)} held")
        if missing:
            typer.echo(f"  missing: {', '.join(missing)}")
    typer.echo(f"{len(held)} of {len(registry.practices)} practices have a representative")


@corpus_app.command("ratings")
def corpus_ratings(root: CorpusRoot = Path("corpus"), docs: DocsRoot = Path("docs")) -> None:
    """Write the audience grid's badges and pages from corpus/ratings/grid.yaml."""
    for path, content in _ratings_files(root, docs).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        typer.echo(f"wrote {path}")


def _ratings_files(root: Path, docs: Path) -> dict[Path, str]:
    grid = corpus_mod.load_grid(root / "ratings" / "grid.yaml")
    font = BitmapFont.load(root / "fonts" / FONT)
    return ratings.written(grid, font, root, docs)


def _stale_ratings(root: Path, docs: Path) -> list[Path]:
    if not (root / "ratings" / "grid.yaml").exists():
        return []
    return [
        path
        for path, content in _ratings_files(root, docs).items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]


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


@app.command("acquire")
def acquire_command(
    manifest: Annotated[Path, typer.Option(help="Manifest of single acquisitions.")] = Path(
        "corpus/acquisitions.yaml"
    ),
    practice: Annotated[
        str | None, typer.Option(help="Only the entries for this practice.")
    ] = None,
) -> None:
    """Fetch and store the files the manifest names, one at a time (ADR 0031)."""
    registry = corpus_mod.load_acquisitions(manifest)
    entries = [e for e in registry.entries if practice in (None, e.practice)]
    cfg = settings()
    store = S3Store(s3_client(), cfg.originals_bucket)
    engine = create_engine(cfg.database_url)
    for entry in entries:
        with engine.begin() as conn:  # one transaction per file
            got = acquire(conn, store, entry, registry.source(entry.source))
        state = "new work" if got.new_work else "fetched" if got.fetched else "already held"
        typer.echo(f"{entry.practice}: {state} {got.sha256} {got.url}")
        if got.fetched:
            time.sleep(ACQUIRE_PAUSE_SECONDS)


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


@app.command("export")
def export_command(
    shard: Annotated[str, typer.Option(help=SHARD_HELP)] = "0/1",
    limit: Annotated[int, typer.Option(help="Stop after this many works (0: all).")] = 0,
) -> None:
    """Publish what may be shown to the public bucket, and remove what may no longer be."""
    cfg = settings()
    client = s3_client()
    derived = S3Store(client, cfg.derived_bucket)
    public = S3Store(client, cfg.public_bucket)
    engine = create_engine(cfg.database_url)
    with engine.connect() as conn:
        rows = exportable(conn, _shard(shard))
    outcomes: Counter[Outcome] = Counter()
    refused = 0
    for row in rows[:limit] if limit else rows:
        with engine.begin() as conn:
            try:
                outcomes[export_work(conn, derived, public, row, cfg.withdraw_url)] += 1
            except ExportError as err:
                refused += 1
                typer.echo(f"refused {err}", err=True)
    shown = ", ".join(f"{name}: {outcomes[name]}" for name in ("files", "record", "nothing"))
    typer.echo(f"{shown}, refused: {refused}")


@app.command("eda")
def eda_command(
    publish_it: Annotated[
        bool, typer.Option("--publish", help="Write it to the public bucket for the static site.")
    ] = False,
) -> None:
    """Print the live exploration (ADR 0028) as JSON: figures and checks, read from the database
    now; the museum serves the same at /api/eda. With --publish, write it where the static site
    reads it instead."""
    cfg = settings()
    engine = create_engine(cfg.database_url, execution_options={"postgresql_readonly": True})
    with engine.connect() as conn:
        found = snapshot(conn)
    if not publish_it:
        typer.echo(json.dumps(found, default=str, indent=1))
        return
    key = publish(found, S3Store(s3_client(), cfg.public_bucket))
    typer.echo(f"published {key} ({found['computed_at']})")


@app.command("lists")
def lists_command() -> None:
    """Write the lists a visit walks through (packs, signatures, years, the work of the day),
    naming only works whose files are shown (ADR 0023). Run after `tm export`."""
    cfg = settings()
    public = S3Store(s3_client(), cfg.public_bucket)
    with create_engine(cfg.database_url).connect() as conn:
        lists = collect(exportable(conn))
    counts = write_lists(lists, public)
    typer.echo(", ".join(f"{name}: {count}" for name, count in counts.items()))


@app.command("rate")
def rate_command() -> None:
    """Infer content ratings for review (ADR 0020): descriptors from words, flashing."""
    engine = create_engine(settings().database_url)
    with engine.begin() as conn:
        found = rate_words(conn)
        flashing = rate_flashing(conn)
    for (descriptor, level), count in sorted(found.items()):
        typer.echo(f"{descriptor} {level}: {count}")
    typer.echo(f"flashing: {flashing}")


@ingest_app.command("acquisitions")
def ingest_acquisitions_command(
    record: Annotated[Path, typer.Argument(help="A mirror's acquisitions.tsv.")],
    source: Annotated[str, typer.Option(help="The archive the mirror copies.")],
) -> None:
    """Record where and when each held file was fetched (ADR 0021)."""
    with create_engine(settings().database_url).begin() as conn:
        loaded = load_acquisitions(conn, record, source)
    typer.echo(
        f"{loaded.recorded} recorded, {loaded.already} already known,"
        f" {loaded.not_held} not held by the museum"
    )


@ingest_app.command("pack")
def ingest_pack_command(
    paths: Annotated[list[Path], typer.Argument(help="Pack archives, or directories of them.")],
    source: Annotated[
        str, typer.Option(help=f"Archive mirrored: {', '.join(PACK_SOURCES)}.")
    ] = "16colo",
    site_root: SiteRoot = None,
) -> None:
    """Store packs from a local mirror and record them: the set, its files, the art."""
    pack_source = _pack_source(source)
    cfg = settings()
    store = S3Store(s3_client(), cfg.originals_bucket)
    engine = create_engine(cfg.database_url)
    archives = pack_archives(paths)
    for archive in archives:
        with engine.begin() as conn:  # one transaction per pack
            ingested = ingest_pack(conn, store, archive, pack_source, site_root)
            typer.echo(_pack_summary(ingested))
    typer.echo(f"{len(archives)} packs")


@ingest_app.command("files")
def ingest_files_command(
    paths: Annotated[list[Path], typer.Argument(help="Loose files, or directories of them.")],
    site_root: Annotated[
        Path, typer.Option(help="Root of the mirror, laid out as the archive's site.")
    ],
    source: Annotated[
        str, typer.Option(help=f"Archive mirrored: {', '.join(PACK_SOURCES)}.")
    ] = "textfiles",
    declared: Annotated[
        str | None,
        typer.Option(help="Art kind the archive gives these trees, for text files (ascii, rtty)."),
    ] = None,
) -> None:
    """Store the files an archive holds loose, outside packs (ADR 0024): art becomes works."""
    pack_source = _pack_source(source)
    cfg = settings()
    store = S3Store(s3_client(), cfg.originals_bucket)
    engine = create_engine(cfg.database_url)
    files = loose_files(paths)
    results: list[LooseIngested] = []
    with engine.begin() as conn:
        for path in files:
            results.append(
                ingest_loose(
                    conn, store, path, site_root=site_root, source=pack_source, declared=declared
                )
            )
    new = [r for r in results if r.new]
    typer.echo(
        f"{len(files)} files: {len(new)} new, {sum(r.work for r in new)} works,"
        f" {len(files) - len(new)} already held"
    )


def _pack_source(name: str) -> PackSource:
    if name not in PACK_SOURCES:
        raise typer.BadParameter(f"unknown source {name!r}", param_hint="--source")
    return PACK_SOURCES[name]


def _pack_summary(item: PackIngested) -> str:
    if not item.new and not item.members:
        return f"already known {item.path}"
    parts = [f"{'ingested' if item.new else 'completed'} {item.path} {item.members} members"]
    if item.error_class:
        parts.append(f"error {item.error_class}")
    if item.unreadable:
        parts.append(f"{len(item.unreadable)} unreadable: {', '.join(item.unreadable)}")
    return "; ".join(parts)


def _ledger() -> Ledger:
    return Ledger(Path(settings().model_ledger))


@budget_app.command("status")
def budget_status() -> None:
    """What each scope was granted, spent and has left."""
    ledger = _ledger()
    if not ledger.scopes():
        typer.echo("no grant: no paid model call is allowed")
    for scope in ledger.scopes():
        b = ledger.balance(scope)
        typer.echo(
            f"{scope}: granted ${b.granted:.2f}, spent ${b.spent:.4f},"
            f" reserved ${b.reserved:.4f}, left ${b.left:.4f}"
        )


@budget_app.command("grant")
def budget_grant(
    scope: Annotated[str, typer.Option(help="What the money is for, e.g. spike-0005-q33")],
    usd: Annotated[float, typer.Option(help="The most that scope may spend, in dollars")],
    note: Annotated[str, typer.Option(help="The owner's words or decision reference")],
    by: Annotated[str, typer.Option(help="Who authorizes")] = "owner",
) -> None:
    """Record the owner's authorization. Asks for confirmation on the terminal, always."""
    typer.confirm(f"Grant ${usd:.2f} to {scope!r} as {by}?", abort=True)
    try:
        _ledger().grant(scope, usd, by, note)
    except BudgetError as err:
        typer.echo(f"✗ {err}", err=True)
        raise typer.Exit(1) from err
    typer.echo(f"granted ${usd:.2f} to {scope}")
