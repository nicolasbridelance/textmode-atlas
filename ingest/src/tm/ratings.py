# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""What the audience grid (`corpus/ratings/grid.yaml`, ADR 0020) publishes: its badges and its
documents, one per required locale.

Badges are drawn cell by cell in the VGA font and palette of the works, as SVG rectangles, so
that they look the same everywhere and need no font. Everything here is derived from the grid:
`tm corpus ratings` writes it, and `tm corpus check` fails when a written file differs. The
site reads `grid.json`, the same grid as JSON.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tm_render.conservation import VGA_PALETTE, BitmapFont

from tm.corpus import Descriptor, Grid, Level, Notice
from tm.i18n import REQUIRED_LOCALES

CELL_WIDTH, CELL_HEIGHT = 8, 16
PIXEL = 4  # badge pixels per font pixel, for the SVG's nominal size
SHADE = 0xB1  # ▒: the withheld badge is masked
WHITE, BLACK = 15, 0
LEVEL_SIZE = 32  # a level badge is a square of 4 × 2 cells
SYMBOL_PADDING = 4  # pixels around a descriptor's glyph
DOC_NAMES = {"en": "audience-grid.md", "fr": "audience-grid.fr.md"}
WORDS = {
    "en": {
        "title": "Audience grid",
        "intro": (
            "What the museum shows to whom. Adapted from PEGI, the European consensus on what"
            " is acceptable for protected audiences; not PEGI itself, which rates games and"
            " whose marks belong to it. Generated from"
            " [corpus/ratings/grid.yaml](../corpus/ratings/grid.yaml) by `tm corpus ratings`:"
            " edit the grid, not this page. Decided in"
            " [ADR 0020](adr/0020-the-audience-grid.md)."
        ),
        "levels": "Levels",
        "descriptors": "Descriptors",
        "notices": "Notices",
        "rules": "Rules",
        "level": "Level",
        "descriptor": "Descriptor",
        "means": "What it means",
        "other": "Version française",
    },
    "fr": {
        "title": "Grille des publics",
        "intro": (
            "Ce que le musée montre, et à qui. Adaptée de PEGI, le consensus européen sur ce qui"
            " est acceptable pour les publics protégés ; ce n'est pas PEGI, qui classe les jeux et"
            " dont les marques lui appartiennent. Générée depuis"
            " [corpus/ratings/grid.yaml](../corpus/ratings/grid.yaml) par `tm corpus ratings` :"
            " on modifie la grille, pas cette page. Décidée dans"
            " l'[ADR 0020](adr/0020-the-audience-grid.md)."
        ),
        "levels": "Niveaux",
        "descriptors": "Descripteurs",
        "notices": "Avertissements",
        "rules": "Règles",
        "level": "Niveau",
        "descriptor": "Descripteur",
        "means": "Ce que cela veut dire",
        "other": "English version",
    },
}
# REUSE-IgnoreStart: the header of the pages this module writes, not this file's license.
HEADER = (
    "<!--\nSPDX-FileCopyrightText: 2026 textmode-atlas contributors\n"
    "SPDX-License-Identifier: CC-BY-4.0\n-->\n"
)
# REUSE-IgnoreEnd


@dataclass(frozen=True)
class Badge:
    """Glyphs placed at pixel positions (x, y, code point) on a background, in one ink."""

    width: int
    height: int
    glyphs: list[tuple[int, int, int]]
    background: int
    ink: int
    title: str
    border: bool = False


def level_badge(level: Level) -> Badge:
    """A square of 32 pixels: the age centred, or the shade pattern when withheld."""
    size = LEVEL_SIZE
    if level.code == "withheld":
        glyphs = [
            (x, y, SHADE) for y in range(0, size, CELL_HEIGHT) for x in range(0, size, CELL_WIDTH)
        ]
    else:
        x0 = (size - CELL_WIDTH * len(level.code)) // 2
        y0 = (size - CELL_HEIGHT) // 2
        glyphs = [(x0 + i * CELL_WIDTH, y0, ord(ch)) for i, ch in enumerate(level.code)]
    colour = level.colour
    return Badge(size, size, glyphs, colour.background, colour.ink, level.label["en"])


def symbol_badge(item: Descriptor | Notice) -> Badge:
    pad = SYMBOL_PADDING
    width, height = CELL_WIDTH + 2 * pad, CELL_HEIGHT + 2 * pad
    glyphs = [(pad, pad, item.glyph)]
    return Badge(width, height, glyphs, WHITE, BLACK, item.label["en"], border=True)


def svg(badge: Badge, font: BitmapFont) -> str:
    """The badge as SVG: one rectangle per horizontal run of ink pixels."""
    runs = [
        _run(x, y + dy, length)
        for x0, y, code in badge.glyphs
        for dy in range(CELL_HEIGHT)
        for x, length in _runs(font.row(code, dy), x0)
    ]
    width, height = badge.width, badge.height
    border = (
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" fill="none"'
        f' stroke="{_hex(badge.ink)}"/>'
        if badge.border
        else ""
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"'
        f' width="{width * PIXEL}" height="{height * PIXEL}" role="img"'
        ' shape-rendering="crispEdges">'
        f"<title>{badge.title}</title>"
        f'<rect width="{width}" height="{height}" fill="{_hex(badge.background)}"/>'
        f'<g fill="{_hex(badge.ink)}">{"".join(runs)}</g>{border}</svg>\n'
    )


def _runs(bits: int, x: int) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    start = None
    for i in range(CELL_WIDTH + 1):
        on = i < CELL_WIDTH and bits & (0x80 >> i)
        if on and start is None:
            start = i
        elif not on and start is not None:
            runs.append((x + start, i - start))
            start = None
    return runs


def _run(x: int, y: int, length: int) -> str:
    return f'<rect x="{x}" y="{y}" width="{length}" height="1"/>'


def _hex(index: int) -> str:
    return "#{:02X}{:02X}{:02X}".format(*VGA_PALETTE[index])


def badges(grid: Grid, font: BitmapFont) -> dict[str, str]:
    """Every badge of the grid, by file name."""
    found = {f"level-{level.code}.svg": svg(level_badge(level), font) for level in grid.levels}
    for item in [*grid.descriptors, *grid.notices]:
        found[f"{item.code}.svg"] = svg(symbol_badge(item), font)
    return found


def documents(grid: Grid) -> dict[str, str]:
    """The grid as a page per required locale, by file name in `docs/`."""
    return {DOC_NAMES[locale]: _document(grid, locale) for locale in REQUIRED_LOCALES}


def _document(grid: Grid, locale: str) -> str:
    words = WORDS[locale]
    other = next(loc for loc in REQUIRED_LOCALES if loc != locale)
    lines = [
        HEADER + f"# {words['title']} (v{grid.version})",
        "",
        f"[{words['other']}]({DOC_NAMES[other]})",
        "",
        words["intro"],
        "",
        f"## {words['levels']}",
        "",
        f"| | {words['level']} | {words['means']} |",
        "| --- | --- | --- |",
        *(
            f"| {_image(f'level-{lv.code}', lv.label[locale])} | **{lv.label[locale]}** |"
            f" {lv.summary[locale]} |"
            for lv in grid.levels
        ),
        "",
        f"## {words['descriptors']}",
        "",
        *_descriptor_table(grid, locale),
        "",
        f"## {words['notices']}",
        "",
        *(
            f"- {_image(n.code, n.label[locale])} **{n.label[locale]}**: {n.text[locale]}"
            for n in grid.notices
        ),
        "",
        f"## {words['rules']}",
        "",
        *(f"{i}. {rule[locale]}" for i, rule in enumerate(grid.rules, start=1)),
        "",
    ]
    return "\n".join(lines)


def _descriptor_table(grid: Grid, locale: str) -> list[str]:
    graded = [lv for lv in grid.levels if lv.code != "3"]
    head = " | ".join(_image(f"level-{lv.code}", lv.label[locale]) for lv in graded)
    rows = [
        f"| {_image(d.code, d.label[locale])} **{d.label[locale]}** | "
        + " | ".join(d.levels[lv.code][locale] if lv.code in d.levels else "" for lv in graded)
        + " |"
        for d in grid.descriptors
    ]
    words = WORDS[locale]
    return [f"| {words['descriptor']} | {head} |", "|" + " --- |" * (len(graded) + 1), *rows]


def _image(name: str, alt: str) -> str:
    return f'<img src="../corpus/ratings/badges/{name}.svg" alt="{alt}" height="32">'


def written(grid: Grid, font: BitmapFont, corpus: Path, docs: Path) -> dict[Path, str]:
    """Every file the grid publishes, by path."""
    folder = corpus / "ratings" / "badges"
    files = {folder / name: text for name, text in badges(grid, font).items()}
    # For the site, which reads JSON: the same grid, nothing added.
    files[corpus / "ratings" / "grid.json"] = grid.model_dump_json(indent=2) + "\n"
    files.update({docs / name: text for name, text in documents(grid).items()})
    return files
