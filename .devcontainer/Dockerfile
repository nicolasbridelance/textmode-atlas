# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
#
# Image shared by development (Codespaces) and CI. Versions are pinned: this image's digest is
# written into every rendering recipe.

FROM mcr.microsoft.com/devcontainers/base:1-bookworm

ARG UV_VERSION=0.12.23
ARG JUST_VERSION=1.58.0
ARG ANSILOVE_VERSION=4.2.2
ARG LIBANSILOVE_VERSION=1.4.2

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential cmake libgd-dev postgresql-client curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# uv and just
COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /uvx /usr/local/bin/
RUN UV_TOOL_DIR=/opt/uv-tools UV_TOOL_BIN_DIR=/usr/local/bin uv tool install "rust-just==${JUST_VERSION}"

# ansilove, built from pinned releases (libansilove, then ansilove)
RUN set -eux; cd /tmp; \
    curl -fsSL "https://github.com/ansilove/libansilove/archive/refs/tags/${LIBANSILOVE_VERSION}.tar.gz" | tar xz; \
    cmake -S "libansilove-${LIBANSILOVE_VERSION}" -B lib-build -DCMAKE_BUILD_TYPE=Release && cmake --build lib-build && cmake --install lib-build; \
    curl -fsSL "https://github.com/ansilove/ansilove/archive/refs/tags/${ANSILOVE_VERSION}.tar.gz" | tar xz; \
    cmake -S "ansilove-${ANSILOVE_VERSION}" -B cli-build -DCMAKE_BUILD_TYPE=Release && cmake --build cli-build && cmake --install cli-build; \
    ldconfig; rm -rf /tmp/*
