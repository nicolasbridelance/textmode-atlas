#!/bin/sh
# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
#
# Archive readers for artpacks (ADR 0013), installed the same way in the development image and
# in CI: Info-ZIP unzip (old ZIP methods), arj (ARJ), and the official 7-Zip console build, whose
# RAR decoder the Debian package lacks (RAR, LHA, LZH). Run as root. Idempotent.
set -eu

SEVENZIP_VERSION=2301
SEVENZIP_SHA256=23babcab045b78016e443f862363e4ab63c77d75bc715c0b3463f6134cbcf318

apt-get update
apt-get install -y --no-install-recommends unzip arj curl ca-certificates xz-utils
rm -rf /var/lib/apt/lists/*

if [ "$(7zz i 2>/dev/null | head -n 2 | grep -c "23.01")" = 0 ]; then
  tmp=$(mktemp -d)
  curl -fsSL -o "$tmp/7z.tar.xz" "https://www.7-zip.org/a/7z${SEVENZIP_VERSION}-linux-x64.tar.xz"
  echo "${SEVENZIP_SHA256}  $tmp/7z.tar.xz" | sha256sum -c -
  tar -xJf "$tmp/7z.tar.xz" -C "$tmp" 7zz License.txt
  install -m 0755 "$tmp/7zz" /usr/local/bin/7zz
  install -D -m 0644 "$tmp/License.txt" /usr/local/share/doc/7zip/License.txt
  rm -rf "$tmp"
fi
