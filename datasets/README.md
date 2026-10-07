<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Datasets

Frozen, versioned, reproducible extracts of the museum's data, for research and for deposit on
Zenodo with a DOI.

- A dataset is **defined** here (one `<name>/dataset.yaml` plus its datasheet,
  `<name>/DATASHEET.md`) and **built** by `tm` from the database into `datasets/build/`
  (ignored by Git, published to storage).
- Each build records the database migration, the extractor versions, the query, and the SHA-256
  of every output file. Building twice gives byte-identical files.
- Train / test splits are made **by pack**, never by file, and ship with the dataset.
- Every dataset publishes its coverage of the known corpus (`lost_item`).
- Datasets contain metadata, assertions, features and embeddings (CC0). They contain works only
  when `can_display()` allows it, and say so in the datasheet.
