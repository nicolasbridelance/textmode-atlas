# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Object storage addressed by SHA-256.

Invariant: an original is never modified. `put_original` writes only when the key is absent and
checks that stored content matches its hash.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

import boto3
from botocore.exceptions import ClientError

from tm.config import settings

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class IntegrityError(Exception):
    """A stored object does not match its hash."""


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def original_key(sha256: str) -> str:
    """Key of an original: `sha256/ab/cd/abcd…`, fanned out to avoid huge prefixes."""
    if len(sha256) != 64 or any(c not in "0123456789abcdef" for c in sha256):
        raise ValueError(f"invalid SHA-256 hash: {sha256!r}")
    return f"sha256/{sha256[:2]}/{sha256[2:4]}/{sha256}"


class ObjectStore(Protocol):
    def exists(self, key: str) -> bool: ...
    def get(self, key: str) -> bytes: ...
    def put(self, key: str, data: bytes, content_type: str = ...) -> None: ...
    def delete(self, key: str) -> None: ...


def put_original(store: ObjectStore, data: bytes) -> tuple[str, bool]:
    """Store an original. Return its hash and `True` if it was just written.

    Idempotent: an original already present is not rewritten, but its content is verified.
    """
    digest = sha256_hex(data)
    key = original_key(digest)
    if store.exists(key):
        if sha256_hex(store.get(key)) != digest:
            raise IntegrityError(f"object {key} does not match its hash")
        return digest, False
    store.put(key, data, "application/octet-stream")
    return digest, True


def get_original(store: ObjectStore, sha256: str) -> bytes:
    data = store.get(original_key(sha256))
    if sha256_hex(data) != sha256:
        raise IntegrityError(f"original {sha256} has been altered")
    return data


class LocalStore:
    """On-disk store, for tests and offline work."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def _path(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if not path.is_relative_to(self.root.resolve()):
            raise ValueError(f"key outside the store: {key!r}")
        return path

    def exists(self, key: str) -> bool:
        return self._path(key).is_file()

    def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(path)

    def delete(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)


class S3Store:
    """S3-compatible bucket (Garage locally, Scaleway Object Storage in production)."""

    def __init__(self, client: S3Client, bucket: str) -> None:
        self.client = client
        self.bucket = bucket

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
        except ClientError as err:
            if err.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise
        return True

    def get(self, key: str) -> bytes:
        return self.client.get_object(Bucket=self.bucket, Key=key)["Body"].read()

    def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)


def s3_client() -> S3Client:
    cfg = settings()
    client: S3Client = boto3.client(  # pyright: ignore[reportUnknownMemberType]
        "s3",
        endpoint_url=cfg.storage_endpoint,
        region_name=cfg.storage_region,
        aws_access_key_id=cfg.storage_key,
        aws_secret_access_key=cfg.storage_secret,
    )
    return client
