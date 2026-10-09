# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Indexes for the lookups `tm export` and the provenance view make for every work.

Which packs hold a file (`set_member.sha256`), which version a work has (`version.work_id`),
which artifact a version is (`artifact.version_id`): without them each lookup scanned its table,
about 130 ms per work.

Revision ID: 0013
Revises: 0012
"""

from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "create index set_member_sha256 on set_member (sha256);"
        "create index version_work_id on version (work_id);"
        "create index artifact_version_id on artifact (version_id);"
    )


def downgrade() -> None:
    op.execute(
        "drop index if exists artifact_version_id;"
        "drop index if exists version_work_id;"
        "drop index if exists set_member_sha256;"
    )
