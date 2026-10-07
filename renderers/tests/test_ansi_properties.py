# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""No byte stream makes the decoder crash: it returns a grid or a classified error."""

from hypothesis import given, settings
from hypothesis import strategies as st
from tm_render.ansi import DecodeError, decode

# Bytes biased toward what ANSI files contain: escapes, digits, separators, controls.
ansi_like = st.lists(
    st.one_of(
        st.binary(max_size=8),
        st.sampled_from([b"\x1b[", b";", b"m", b"H", b"J", b"K", b"\r\n", b"\x1a", b"\t"]),
        st.integers(0, 120).map(lambda n: str(n).encode()),
    ),
    max_size=200,
).map(b"".join)


@settings(max_examples=400)
@given(st.one_of(st.binary(max_size=2000), ansi_like))
def test_decoder_never_crashes(data: bytes) -> None:
    try:
        grid = decode(data).grid
    except DecodeError as error:
        kind = error.kind
    else:
        kind = None
    if kind is not None:
        assert kind in {"empty", "too_large"}
        return
    for (row, col), cell in grid.cells.items():
        assert 0 <= row < grid.rows
        assert 0 <= col < grid.cols
        assert 0 <= cell.fg < 16
        assert 0 <= cell.bg < 8
        assert 0 <= cell.t < len(data)
