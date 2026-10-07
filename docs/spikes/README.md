<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Spikes

A spike answers one question that blocks a decision, by trying, within a time box. Its code is
an instrument, not a product: it is never merged (ADR 0001, 0002).

1. **Before**: add the spike to the roadmap with its question and time box (usually one to three
   hours of work).
2. **During**: work on a `spike/NNNN-topic` branch. Anything goes there, except committing
   artworks (third-party files stay in `data/`, ignored by Git) and touching shared services in
   ways that are not reset afterwards.
3. **After**: write `docs/spikes/NNNN-topic.md` on a normal branch, delete the spike branch. If
   the answer leads to a decision, write the ADR; the production code is then written anew,
   with tests, on a feature branch.

A spike that runs out of time still gets its report: what was learned, and what remains unknown.

## Report template

```markdown
# NNNN. Question as a question?

- Date: YYYY-MM-DD · Time box: … · Time spent: …
- Branch: spike/NNNN-topic (deleted)

## Question
## Method
## Findings
Measured, with the numbers.
## Recommendation
And the ADR it leads to, if any.
```

## Index

| Spike | Question | Outcome |
| --- | --- | --- |
| [0001](0001-ansilove-parity.md) | Does our grid renderer match ansilove pixel for pixel? | yes, 96 of 99 VGA files; the rest explained → [ADR 0010](../adr/0010-render-from-the-grid.md) |
