<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0003. Use Garage for local S3 storage

- Status: Accepted
- Date: 2026-10-07
- Deciders: Claude, approved by Nicolas Bridelance

## Context

The foundation document chose MinIO for the local S3-compatible store. In October 2026 the
`minio/minio` image is no longer published on Docker Hub and `quay.io/minio/minio` requires
authentication. Production targets Scaleway Object Storage; local storage only needs to speak S3.

## Decision

Use [Garage](https://garagehq.deuxfleurs.fr/) (Deuxfleurs, a French non-profit), pinned image
`dxflrs/garage`. `tm dev storage-init` sets it up through its admin API: node layout, a fixed
local key, the private and public buckets, and anonymous reads of the public bucket through
Garage's web endpoint, which the site's dev server reaches by a `/files` proxy.

## Alternatives considered

- **SeaweedFS**: S3 gateway works, heavier to configure, larger surface.
- **RustFS**: young project.
- **Build MinIO from source**: maintenance burden for a dev-only service.

## Consequences

- Garage has no object versioning: write-once originals are guaranteed by
  `tm.storage.put_original`, which never writes an existing key. Production keeps versioning.
- Garage has no web console; its bucket is served by Host header (`tm-public.web.localhost`).
