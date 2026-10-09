<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Corpus lexicon and concordance

A local research tool over the frozen **train-only works dataset**, not the production
database. Exploratory: frequencies are leads, credits are unresolved SAUCE strings, and no
author, alias or country is inferred. No model or external service is used.

## Build and read

```sh
just lexicon
# Open datasets/build/lexicon/1/output/report.html in a browser; no server is needed.
just concordance sysop --year-max 1993 --limit 10
just concordance greets --group mistigris --limit 10
just lexicon-shots  # needs the museum's installed Playwright browser
```

The builder defaults to `datasets/build/works/5`, verifies both Parquet files against their
manifest SHA-256 and copies them into `datasets/build/lexicon/1/snapshot/`. Computation uses one
DuckDB thread and a 512 MB DuckDB memory limit. Its scratch files also stay in this build.
Scripts and the HTML template are versioned; datasets, excerpts, CSVs, renderings and the
generated report stay in ignored `datasets/build/`. The report is private: it quotes works,
and the research dataset is not the rights- and audience-filtered public export.

An explicit source is useful in an independent worktree:

```sh
uv run --group research python research/lexicon/build.py --source /path/to/works/5
uv run --group research python research/lexicon/build.py \
  --source datasets/build/lexicon/1/snapshot
```

`--output /path/to/build` selects another local build directory. Search it with
`research/lexicon/concordance.py --snapshot /path/to/build/snapshot TERM`. A year filter
excludes unknown years; no year filter includes them. Credit filters refer to raw SAUCE
strings, ignoring case and surrounding spaces, not to resolved identities. The concordance
emits JSON lines on stdout with the original grid row, text, hash and file metadata.

## Outputs

| File in `output/` | Meaning |
| --- | --- |
| `report.html` | Standalone French research report, top 2,000 forms and top 300 credited strings |
| `analysis.json` | Report data, source manifest and analysis recipe |
| `lexicon.csv` | Every retained form: occurrences, file frequency and counts per era |
| `works.csv` | File catalogue, original SAUCE credits and text availability |
| `authors.csv`, `groups.csv` | All unresolved credited strings, variants and review flags |
| `eras.csv` | Coverage and marker counts, with explicit denominators |
| `decoding.csv` | Classified decoding failures by format |
| `METHODS.md` | Copy of this method note |

The report works offline. Clicking an explicit work link opens the existing local explorer
at port 8737. It initiates no other requests, starts no server and changes no source files.

## Counting rules and limits

- Normalize text to Unicode NFC and casefold. Split into Unicode letter/digit tokens;
  underscores and other punctuation separate them. Keep at least three characters, excluding
  numeric-only tokens. Thus `sysop` differs from `cosysop`; accented forms remain accented.
- Count occurrences separately from file frequency: repeated words and rows in one SHA-256
  file count once in the latter. A form is not necessarily a word: handles and drawing noise
  remain. The small English common-word list affects display only, never exported counts.
- Lexical rates use files with extracted text in the selected era. BBS/greets marker rates
  instead use **all successfully decoded ANSI** in that era, including those without text.
  Unknown and out-of-range years occupy a separate bin. Missing denominators show no rate.
- BBS markers: `sysop`, `node`, `baud`, `running`, `bbs`, `call`. Greets markers: `greets`,
  `greetings`, `hellos`. These are searches, not validated genre labels: `call` has other uses.
- Years are filing years, not established creation dates. Pack counts use the dataset's
  representative pack, not all historical memberships. Repeated text and equal-grid variants
  may inflate counts; files are not resolved unique creative works.
- Credit keys normalize only NFC, casefold and outer spaces. Alias/homonym resolution remains
  open. Generic-value flags request review; they neither reject a credit nor assert identity.
- Context examples cover the top 250 forms, at most three representative packs per form,
  chosen deterministically by SHA then row. They span all periods regardless of the table's
  filter, are not representative samples, and preserve stored row positions and source text.
- Block lettering, two-character signatures, non-CP437 code pages and dynamic screens can
  escape extraction. Counts describe the train dataset, not all of the scene.

## Next research steps

Annotate text zones across packs and eras before measuring language or genre accuracy. Resolve
credits against NFO and in-grid signatures with source evidence. For attribution, compare
against group/year baselines on held-out packs, control duplicate grids and allow unknown
authors and abstention. Preregister tests before opening held-out data.

For publication, pair a short visual account with coverage, method, reproducible code and
aggregates. Full text and context excerpts are a separate publication decision. This report
does not change public display rights or audience decisions.
