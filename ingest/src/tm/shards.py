# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Shards: split a corpus-wide run over several processes, each taking its own artifacts.

An artifact belongs to shard `i` of `n` when the second byte of its SHA-256 is `i` modulo `n`
(the first byte draws the test split). Shards are disjoint and cover everything, so `n`
processes, one per index, do the whole run once.
"""

from __future__ import annotations

from dataclasses import dataclass


def condition(column: str) -> str:
    """SQL to append to a query's conditions: the artifact hash in `column` is in the shard."""
    return f" and get_byte(decode({column}, 'hex'), 1) % :shard_count = :shard_index"


@dataclass(frozen=True)
class Shard:
    index: int = 0
    count: int = 1

    @classmethod
    def parse(cls, text: str) -> Shard:
        """`i/n`, with 0 <= i < n."""
        try:
            index, count = (int(part) for part in text.split("/"))
        except ValueError:
            raise ValueError(f"shard {text!r} is not of the form i/n") from None
        if not 0 <= index < count:
            raise ValueError(f"shard {text!r}: the index must be in 0..{count - 1}")
        return cls(index, count)

    def params(self) -> dict[str, int]:
        return {"shard_index": self.index, "shard_count": self.count}


EVERYTHING = Shard()
