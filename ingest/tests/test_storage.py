# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import pytest
from tm.storage import IntegrityError, LocalStore, get_original, original_key, put_original


def test_key_layout() -> None:
    digest = "ab" * 32
    assert original_key(digest) == f"sha256/ab/ab/{digest}"


@pytest.mark.parametrize("bad", ["", "AB" * 32, "zz" * 32, "ab" * 31, "../" + "a" * 61])
def test_key_rejects_invalid_hash(bad: str) -> None:
    with pytest.raises(ValueError, match="invalid"):
        original_key(bad)


def test_put_is_idempotent(tmp_path: Path) -> None:
    store = LocalStore(tmp_path)
    digest, written = put_original(store, b"\x1b[1;34mtextmode")
    again, written_again = put_original(store, b"\x1b[1;34mtextmode")
    assert (digest, written) == (again, True)
    assert written_again is False
    assert get_original(store, digest) == b"\x1b[1;34mtextmode"


def test_altered_original_is_detected(tmp_path: Path) -> None:
    store = LocalStore(tmp_path)
    digest, _ = put_original(store, b"original")
    store.put(original_key(digest), b"altered")
    with pytest.raises(IntegrityError):
        get_original(store, digest)
    with pytest.raises(IntegrityError):
        put_original(store, b"original")


def test_local_store_refuses_escaping_keys(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="outside the store"):
        LocalStore(tmp_path / "root").put("../outside", b"x")
