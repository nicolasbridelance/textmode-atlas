# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Descriptors of the audience grid (ADR 0020) inferred from the words of a work.

A first pass for human review, not a judgement: words say what a work talks about, rarely
what it shows. Each rule gives a descriptor at the level its words most plausibly call for,
erring high, since an inferred descriptor counts until a person reviews it (grid rule 4).
Words are matched whole, in lower case, accents folded, in the text layer, the file name and
the SAUCE title. Leetspeak and words drawn in blocks escape it.

Left out on purpose, after reading the corpus: `xxx` alone (a placeholder in phone numbers
and a texture far more often than a sign of porn), and `lsd` (mostly a BBS program,
"Running LSD 1.42").
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass

# (descriptor, level, words). A word ending in `*` matches any ending.
RULES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("sexual", "18", (
        "porn*", "xxx gif*", "xxx pic*", "xxx area*", "xxx section*", "xxx file*", "hentai",
        "blowjob*", "cumshot*", "gangbang*", "dildo*", "orgasm*", "pussy", "pussies", "cock",
        "cocks", "cunnilingus", "fellatio", "rape", "raped",
    )),
    ("sexual", "16", (
        "nude", "nudes", "naked", "tits", "titties", "boobs", "nipple*", "topless", "playboy",
        "playmate*", "erotic*", "strip*tease",
    )),
    ("sexual", "12", ("sexy", "lingerie", "bikini*", "babe", "babes")),
    ("violence", "18", (
        "gore", "gory", "mutilat*", "tortur*", "dismember*", "decapitat*", "massacre*",
        "rape", "raped",
    )),
    ("violence", "16", ("blood", "bloody", "bleed*", "murder*", "slaughter*", "stab*")),
    ("fear", "12", (
        "skull*", "demon*", "satan*", "devil*", "undead", "zombie*", "horror", "lucifer",
        "necro*", "occult", "666", "ghoul*", "coffin*", "hell",
    )),
    ("language", "16", ("fuck*", "motherfuck*", "cunt*")),
    ("language", "12", ("shit*", "bitch*", "asshole*", "bastard*", "damn", "crap")),
    ("drugs", "16", (
        "weed", "marijuana", "cannabis", "cocaine", "heroin", "ecstasy", "mdma",
        "stoned", "ganja", "shrooms", "drugs",
    )),
    ("drugs", "12", (
        "beer*", "booze", "alcohol*", "vodka", "whisk*y", "drunk", "cigarette*",
    )),
    ("discrimination", "18", (
        "nigger*", "nigga*", "faggot*", "kike*", "heil", "hitler", "nazi*", "kkk",
        "swastika*",
    )),
    ("crime", "16", (
        "carding", "carder*", "phreak*", "credit card*", "calling card*", "blue box*",
        "red box*",
    )),
    ("crime", "12", ("warez", "0day*", "0-day*", "courier*", "cracked by", "pirat*")),
)  # fmt: skip


@dataclass(frozen=True)
class Inference:
    descriptor: str
    level: str
    words: tuple[str, ...]  # the words found, for the reviewer


def _pattern(words: tuple[str, ...]) -> re.Pattern[str]:
    parts = (re.escape(word).replace(r"\*", r"\w*") for word in words)
    return re.compile(r"(?<![a-z0-9])(" + "|".join(parts) + r")(?![a-z0-9])")


PATTERNS = tuple((d, level, _pattern(words)) for d, level, words in RULES)
LEVEL_RANK = {"3": 0, "7": 1, "12": 2, "16": 3, "18": 4, "withheld": 5}


def fold(text: str) -> str:
    """Lower case without accents: `Grüße` reads `grusse`… and `naïve` reads `naive`."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def infer(texts: Iterable[str]) -> list[Inference]:
    """One inference per descriptor found, at the highest level its words call for."""
    folded = [fold(t) for t in texts if t]
    best: dict[str, Inference] = {}
    for descriptor, level, pattern in PATTERNS:
        words = sorted({m.group(1) for t in folded for m in pattern.finditer(t)})
        if not words:
            continue
        found = best.get(descriptor)
        if found is None or LEVEL_RANK[level] > LEVEL_RANK[found.level]:
            best[descriptor] = Inference(descriptor, level, tuple(words))
    return sorted(best.values(), key=lambda i: i.descriptor)
