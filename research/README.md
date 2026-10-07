<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Research

Hypotheses, pre-registered **before** looking at the data, and the notebooks that test them.

- One directory per hypothesis: `research/NNNN-short-name/`, with `hypothesis.md` committed
  first (question, measure, null model, test that could fail, date). The commit date is the proof
  of pre-registration.
- Notebooks are [marimo](https://marimo.io/) files (plain Python, reviewable in a diff):
  `just notebook research/NNNN-short-name`.
- Notebooks read built datasets (`datasets/`), never the production database directly.
- Method rules (foundation document): split by pack, compare to a null model, resample by pack
  for intervals, publish coverage.
