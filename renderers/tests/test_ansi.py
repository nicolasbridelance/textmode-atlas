# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
import pytest
from conftest import SauceRecord
from tm_render.ansi import DecodeError, decode

ESC = b"\x1b["


def cell(data: bytes, row: int, col: int) -> tuple[int, int, int, bool]:
    found = decode(data).grid.cell(row, col)
    assert found is not None
    return found.codepoint, found.fg, found.bg, found.blink


def test_plain_text_and_offsets() -> None:
    grid = decode(b"AB").grid
    assert (grid.cols, grid.rows) == (80, 1)
    a, b = grid.cell(0, 0), grid.cell(0, 1)
    assert a is not None
    assert b is not None
    assert (a.codepoint, a.t, b.t) == (ord("A"), 0, 1)


def test_sgr_colours_use_vga_order() -> None:
    # SGR 31 is red, 44 is blue; in VGA attribute order red is 4 and blue is 1.
    assert cell(ESC + b"31;44mX", 0, 0) == (ord("X"), 4, 1, False)


def test_bold_brightens_and_reset_restores() -> None:
    assert cell(ESC + b"1;33mX", 0, 0)[1] == 14  # bright brown is yellow
    assert cell(ESC + b"1;33m" + ESC + b"0mX", 0, 0)[1:] == (7, 0, False)


def test_blink_and_inverse() -> None:
    assert cell(ESC + b"5mX", 0, 0)[3]
    assert cell(ESC + b"7;32mX", 0, 0)[1:3] == (0, 2)


def test_default_colour_codes() -> None:
    assert cell(ESC + b"31;44m" + ESC + b"39;49mX", 0, 0)[1:3] == (7, 0)


def test_cursor_position_and_moves() -> None:
    assert cell(ESC + b"3;5HX", 2, 4)[0] == ord("X")
    assert cell(ESC + b"3;5H" + ESC + b"A" + ESC + b"2DX", 1, 2)[0] == ord("X")
    assert cell(ESC + b"2B" + ESC + b"3CX", 2, 3)[0] == ord("X")
    assert cell(ESC + b"HX", 0, 0)[0] == ord("X")


def test_save_and_restore() -> None:
    assert cell(b"ab" + ESC + b"s\r\ncd" + ESC + b"uX", 0, 2)[0] == ord("X")


def test_crlf_and_tab() -> None:
    assert cell(b"a\r\nb", 1, 0)[0] == ord("b")
    assert cell(b"\tX", 0, 8)[0] == ord("X")


def test_full_row_wraps_without_crlf() -> None:
    grid = decode(b"x" * 80 + b"y").grid
    assert grid.cell(1, 0) is not None
    assert grid.rows == 2


def test_canvas_ends_at_the_last_written_row(sauce_record: SauceRecord) -> None:
    decoded = decode(b"a\r\nb\r\n\x1a" + sauce_record(height=25))
    assert decoded.grid.rows == 2
    assert decoded.sauce is not None
    assert decoded.sauce.height == 25


def test_a_wide_canvas_comes_from_a_coherent_sauce(sauce_record: SauceRecord) -> None:
    decoded = decode(b"x" * 100 + b"\x1a" + sauce_record(width=160))
    assert (decoded.grid.cols, decoded.grid.rows) == (160, 1)
    assert decoded.sauce_problems == ()


def test_a_corrupt_sauce_gives_no_width(sauce_record: SauceRecord) -> None:
    decoded = decode(b"x" * 100 + b"\x1a" + sauce_record(width=0x2050, file_size=0x2020_0064))
    assert (decoded.grid.cols, decoded.grid.rows) == (80, 2)
    assert decoded.sauce_problems == ("size_exceeds_file",)
    assert decoded.sauce is not None
    assert decoded.sauce.width == 0x2050


def test_sauce_without_eof_byte_is_not_drawn(sauce_record: SauceRecord) -> None:
    assert len(decode(b"art" + sauce_record()).grid.cells) == len(b"art")


def test_crlf_after_a_full_row_skips_a_row() -> None:
    # Writing column 80 moves the cursor down at once, as ANSI.SYS and ansilove do.
    grid = decode(b"x" * 80 + b"\r\ny").grid
    assert grid.cell(2, 0) is not None
    assert grid.cell(1, 0) is None


def test_erase_line_and_display() -> None:
    assert decode(b"abc\r" + ESC + b"K").grid.cells == {}
    assert decode(b"abc" + ESC + b"1K").grid.cell(0, 0) is None
    assert decode(b"abc" + ESC + b"2Jd").grid.cell(0, 0) is not None
    assert len(decode(b"abc" + ESC + b"2Jd").grid.cells) == 1


def test_unknown_and_private_sequences_are_skipped_and_counted() -> None:
    decoded = decode(ESC + b"?7h" + ESC + b"5nX")
    assert decoded.skipped_sequences == 2
    assert decoded.grid.cell(0, 0) is not None


def test_truncated_sequence_at_end_is_harmless() -> None:
    assert decode(b"X" + ESC + b"1;3").grid.cell(0, 0) is not None


def test_empty_input_is_a_classified_error() -> None:
    with pytest.raises(DecodeError) as error:
        decode(b"\x1aSAUCE")
    assert error.value.kind == "empty"


def test_runaway_input_is_a_classified_error() -> None:
    with pytest.raises(DecodeError) as error:
        decode(b"\n" * 10_001)
    assert error.value.kind == "too_large"


def test_digest_is_stable_and_sensitive() -> None:
    assert decode(b"AB").grid.digest() == decode(b"AB").grid.digest()
    assert decode(b"AB").grid.digest() != decode(b"AC").grid.digest()
