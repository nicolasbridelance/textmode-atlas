# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Languages of the museum.

The repository is written in English; everything a visitor reads is localized. Work titles are
never translated: they are part of the work. A machine translation is an interpretation and is
marked as such wherever it is stored.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import AfterValidator, Field

# Locales every visitor-facing text must provide. Others (ja, ru, de…) are welcome as well.
REQUIRED_LOCALES = ("en", "fr")

LocaleTag = Annotated[str, Field(pattern=r"^[a-z]{2,3}(-[A-Z][a-z]{3})?(-[A-Z]{2})?$")]


def _has_required_locales(text: dict[str, str]) -> dict[str, str]:
    missing = [loc for loc in REQUIRED_LOCALES if not text.get(loc, "").strip()]
    if missing:
        raise ValueError(f"missing translation(s): {', '.join(missing)}")
    return text


LocalizedText = Annotated[dict[LocaleTag, str], AfterValidator(_has_required_locales)]
