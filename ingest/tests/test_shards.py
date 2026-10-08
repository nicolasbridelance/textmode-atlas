# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import pytest
from sqlalchemy import Connection, text
from tm.shards import Shard, condition


def test_a_shard_is_parsed_from_i_of_n() -> None:
    assert Shard.parse("2/8") == Shard(2, 8)
    for wrong in ("8/8", "-1/2", "1", "a/b"):
        with pytest.raises(ValueError, match="shard"):
            Shard.parse(wrong)


@pytest.mark.db
def test_shards_are_disjoint_and_cover_everything(db: Connection) -> None:
    query = text(
        "select count(*) from (select encode(sha256(i::text::bytea), 'hex') as sha256"
        f" from generate_series(1, 500) i) d where true{condition('d.sha256')}"
    )
    counts = [db.execute(query, Shard(i, 3).params()).scalar_one() for i in range(3)]
    assert sum(counts) == db.execute(query, Shard().params()).scalar_one() == 500
    assert all(counts)
