# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Local Garage storage setup, through Garage's admin API.

In staging and production, buckets are declared in OpenTofu (`infra/`), not here.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any

from tm.config import Settings

# Fixed local access key, so the devcontainer environment variables stay stable.
LOCAL_KEY_ID = "GK746d6c6f63616c6f6e6c7900"
LOCAL_SECRET = "746d2d6c6f63616c2d6f6e6c792d6e6f742d612d7265616c2d7365637265742e"
BUCKETS = ("tm-originals", "tm-derived", "tm-public")
# The public bucket is served for anonymous reads by Garage's web endpoint (port 3902), as the
# CDN will do in production. Garage picks the bucket from the Host header:
# `tm-public.web.localhost`.
PUBLIC_BUCKET = "tm-public"


def _call(cfg: Settings, endpoint: str, body: Any = None) -> Any:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        f"{cfg.garage_admin_url}/v2/{endpoint}",
        data=data,
        method="GET" if body is None else "POST",
        headers={
            "Authorization": f"Bearer {cfg.garage_admin_token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = resp.read()
    return json.loads(raw) if raw else None


def storage_init(cfg: Settings) -> list[str]:
    """Create the node layout, the local key and the three buckets. Idempotent."""
    done: list[str] = []
    status = _call(cfg, "GetClusterStatus")
    node = status["nodes"][0]
    if node.get("role") is None:
        tags: list[str] = []
        role = {"id": node["id"], "zone": "local", "capacity": 10 * 1024**3, "tags": tags}
        _call(cfg, "UpdateClusterLayout", {"roles": [role]})
        layout = _call(cfg, "GetClusterLayout")
        _call(cfg, "ApplyClusterLayout", {"version": layout["version"] + 1})
        done.append("node layout applied")

    keys = _call(cfg, "ListKeys")
    if not any(k["id"] == LOCAL_KEY_ID for k in keys):
        _call(
            cfg,
            "ImportKey",
            {"accessKeyId": LOCAL_KEY_ID, "secretAccessKey": LOCAL_SECRET, "name": "tm-local"},
        )
        done.append("local key imported")

    existing = {
        alias: b["id"] for b in _call(cfg, "ListBuckets") for alias in b.get("globalAliases", [])
    }
    for name in BUCKETS:
        if name not in existing:
            bucket = _call(cfg, "CreateBucket", {"globalAlias": name})
            existing[name] = bucket["id"]
            permissions = {"read": True, "write": True, "owner": True}
            _call(
                cfg,
                "AllowBucketKey",
                {"bucketId": bucket["id"], "accessKeyId": LOCAL_KEY_ID, "permissions": permissions},
            )
            done.append(f"bucket {name} created")

    public = _call(cfg, f"GetBucketInfo?id={existing[PUBLIC_BUCKET]}")
    if not public["websiteAccess"]:
        _call(
            cfg,
            f"UpdateBucket?id={existing[PUBLIC_BUCKET]}",
            {"websiteAccess": {"enabled": True, "indexDocument": "index.html"}},
        )
        done.append(f"bucket {PUBLIC_BUCKET} served for public reads")
    return done
