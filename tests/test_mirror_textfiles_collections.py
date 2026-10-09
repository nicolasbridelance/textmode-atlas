# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from mirror_textfiles_collections import links  # noqa: E402

BASE = "http://artscene.textfiles.com/asciiart/"


def test_links_keep_the_entries_of_the_listing_only() -> None:
    page = (
        b'<a href="../">up</a> <a href="LOGOS">d</a> <a href=".png/x.txt.png">p</a>'
        b' <a href="http://www.asciipr0n.com">site</a> <a href="a.txt">f</a> <a href="a.txt">f</a>'
    )
    assert links(page, BASE) == [BASE + "LOGOS", BASE + "a.txt"]


def test_latin1_names_travel_percent_encoded() -> None:
    assert links('<a href="caf\xe9\xb7.txt">x</a>'.encode("latin-1"), BASE) == [
        BASE + "caf%E9%B7.txt"
    ]
