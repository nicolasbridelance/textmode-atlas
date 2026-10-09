# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Versions of the extractors (ADR 0012): raise one when what its module computes changes.

`tests/test_versions.py` fails until you do. The `features`, `text_layer` and `content_rating`
rows record them.
"""

FEATURES_VERSION = "1"  # features.py
TEXT_VERSION = "2"  # text.py
RATING_VERSION = "2"  # ratings.py
NEIGHBOURS_VERSION = "1"  # neighbours.py
