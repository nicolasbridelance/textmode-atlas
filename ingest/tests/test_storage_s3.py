# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Write-once on a real S3 bucket (local Garage or the CI service)."""

import os
import uuid

import pytest
from tm.storage import S3Store, get_original, put_original, s3_client

pytestmark = pytest.mark.storage


@pytest.fixture
def store() -> S3Store:
    if not os.environ.get("TM_STORAGE_KEY"):
        pytest.skip("TM_STORAGE_KEY not set: S3 storage tests skipped")
    return S3Store(s3_client(), "tm-originals")


def test_put_original_is_write_once(store: S3Store) -> None:
    data = f"textmode {uuid.uuid4()}".encode()
    digest, written = put_original(store, data)
    assert written
    assert put_original(store, data) == (digest, False)
    assert get_original(store, digest) == data


def test_missing_key(store: S3Store) -> None:
    assert not store.exists("sha256/00/00/" + "0" * 64)
