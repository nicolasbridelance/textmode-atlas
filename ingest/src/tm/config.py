# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Settings read from the environment (Codespaces secrets, CI or job variables)."""

from __future__ import annotations

import os
from functools import cache

from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = "postgresql+psycopg://tm:tm@localhost:5432/tm"
    storage_endpoint: str = "http://localhost:3900"
    storage_region: str = "garage"
    storage_key: str = ""
    storage_secret: str = ""
    originals_bucket: str = "tm-originals"
    derived_bucket: str = "tm-derived"
    public_bucket: str = "tm-public"
    # Where a visitor asks for a work to be withdrawn or rated again (ADR 0009, 0020).
    withdraw_url: str = "https://github.com/nicolasbridelance/textmode-atlas/blob/main/TAKEDOWN.md"
    # Garage administration: local environment only.
    garage_admin_url: str = "http://localhost:3903"
    garage_admin_token: str = "tm-local-admin-token"


@cache
def settings() -> Settings:
    """Build settings from `TM_*` environment variables."""
    values = {
        name: os.environ[f"TM_{name.upper()}"]
        for name in Settings.model_fields
        if f"TM_{name.upper()}" in os.environ
    }
    return Settings.model_validate(values)
