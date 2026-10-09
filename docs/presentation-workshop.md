<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Visitor presentation workshop

The work screen and work of the day share a presentation workshop. Visitor settings are stored
locally, survive navigation and language changes, and can be reset. Dark remains the default;
light and system themes change the museum furniture. A custom gallery background surrounds the
image. A thin border or a paper mount frames the image itself. Neither changes the source.

## Scripted interpretations, version 1

All rules read the exported public TMG1 grid and the bundled VGA 8×16 bitmap. They are deliberately
simple experiments, not reconstructions of historical renderings or claims about artistic movements.
No model, image service or new dependency is used.

| Look | Rule at native resolution |
| --- | --- |
| VGA | Bitmap glyphs in their original VGA foreground/background colours |
| White paper | Invert Rec. 709 luminance, `255 − (0.2126 R + 0.7152 G + 0.0722 B)` |
| Density | Replace each cell with `round(255 × (1 − glyph occupancy / 128))`; ignore colours; unwritten cells are white |
| Pointillism | Sample a dot centre on a four-pixel lattice, radius squared ≤ 2, on white paper |
| Impressionist touches | Sample diagonal bands, six pixels wide and three pixels tall |
| Graffiti | Quantize each RGB channel to four levels, darken diagonal edges above luminance difference 90, add a fixed sparse spray pattern |

Glyph occupancy comes from the actual font bitmap, never from the numeric order of CP437 codes.
Density intentionally discards colour and the arrangement of pixels within a cell. Paper is a
luminance inversion, not a replacement of all background colours. These losses are described in
the visitor controls. The points and touches are geometric approximations; aesthetic evaluation
on diverse works is still needed.

## Enlargement and export

Nearest-neighbour enlargement retains crisp pixels. Smooth enlargement uses browser image
interpolation. Gaussian smoothing applies the separable binomial kernel `[1, 4, 6, 4, 1] / 16`
with clamped edges and float intermediates, then rounds to bytes before smooth enlargement.
It approximates a Gaussian with sigma about one source pixel. This is not LCD RGB subpixel
rendering, nor an algorithm that invents higher-resolution detail.

The PNG export always renders the entire work, including the chosen frame, independently of
viewport and modem arrival. Scales 1, 2 and 4 are available, limited to 24 million output pixels.
A companion JSON download records source/grid/font hashes, algorithm version, settings, dimensions,
representation level and browser identity. Browsers may require allowing multiple downloads for
the companion file. Integer nearest-neighbour pixel results are deterministic. Browser smoothing
is environment-dependent; recording the browser does not promise identical PNG bytes across engines.
The gallery backdrop and UI theme are recorded as visit context, not painted over the artwork.

Interpretations and Gaussian smoothing show the whole work immediately; byte-arrival controls are
disabled. Returning to VGA restores arrival. The cell inspector always describes the source grid,
even when an interpretation is selected.

## One public entrance

The header links the work of the day, thumbnails and constellations. The selected work identifier
survives switching views and languages. Exploration reads the existing public day selection and,
when a work supplies them, its pack, signature and year lists. It shows whole-work conservation
thumbnails and loads 48 entries at a time. Constellations are accessible radial diagrams around
a shared metadata value: pack, signature or year. A node opens the same work screen.

This does not publish the private train corpus or its nearest-neighbour graph. The public
feature-similarity graph needs an authorized export, with algorithm provenance, before it can
join this entrance. TMG v2 font/palette assets also need to reach the public frontend before
these rules can apply to non-VGA works.

## Validation

Unit tests cover real glyph occupancy, density tones, luminance inversion, Gaussian impulses,
constant-image preservation, determinism and source immutability. Browser tests cover persistence,
PNG dimensions and recipe hashes, navigation, both locales and desktop/mobile widths. A contact
sheet uses project-made geometry rather than corpus artwork. Initial visual checks used synthetic exported records and grids. A follow-up verified the
real public grid, PNG and gallery through the museum proxy: Garage is reached at
`storage:3902` inside the dev container, not `localhost:3902`. Long-running Vite previews
need restarting after a rebuild so their server manifest matches the current client assets.
