<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Visitor presentation workshop

The work screen and work of the day share a presentation workshop. Visitor settings are stored
locally, survive navigation and language changes, and can be reset. Dark remains the default;
light and system themes change the museum furniture. A custom gallery background surrounds the
image. A thin border or a paper mount frames the image itself. Neither changes the source.

## Scripted interpretations, version 2

All rules read the exported public TMG1 grid and the bundled VGA 8×16 bitmap. They are deliberately
simple experiments, not reconstructions of historical renderings or claims about artistic movements.
No model, image service or new dependency is used.

| Look | Rule at native resolution |
| --- | --- |
| VGA | Bitmap glyphs in their original VGA foreground/background colours |
| White paper | Invert Rec. 709 luminance, `255 − (0.2126 R + 0.7152 G + 0.0722 B)` |
| Density | Replace each cell with `round(255 × (1 − glyph occupancy / 128))`; ignore colours; unwritten cells are white |
| Colour reconstruction | Mix foreground/background by glyph coverage, then interpolate between cell centres |
| Organic points | Seeded position jitter and variable-area dots, with normalized ink hue and a dark/light support |
| Print halftone | Regular variable-area colour dots |
| Kuwahara | Mean colour of the local quadrant with lowest luminance variance |
| Brushwork | Two layers of elliptical marks oriented along local contours |
| Stencil | Four colour levels, gradient contours and seeded paint speckles |

Glyph occupancy comes from the actual font bitmap, never from the numeric order of CP437 codes.
Density intentionally discards colour and the arrangement of pixels within a cell. Paper is a
luminance inversion, not a replacement of all background colours. These losses are described in
the visitor controls. Six public works and 90 variants have been compared in the
[experiment report](presentation-experiments.md). Size, strength, filter input and artwork support
are configurable. A split comparison keeps the complete original visible alongside the result.

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

### Three discovery layouts

The discovery workshop at `/explore` compares three proposals using the same public selection and
unchanged conservation images. The header directly links **Pinterest**, **Instagram** and
**Tinder**, preserving locale, filters and the starting work. There is one navigation bar;
no duplicate layout tabs or separate research collection switch.

| URL parameter | Proposal | Interaction |
| --- | --- | --- |
| `view=pinterest` | Warm paper, a masonry wall with variable image proportions | Browse many works, open one, save it to a selection |
| `view=instagram` | A centred image feed, signatures, pack/year context, a quiet editorial sidebar | Read each image's context, open it, save it |
| `view=tinder` | A dark deck, one whole image at a time | Pass or keep by button, horizontal drag or arrow keys; undo the last decision |

Images are contained rather than cropped, including unusually tall works. Original pixels retain
their palette and glyph drawing. Opening an image leads to the existing work screen. The wall and
feed load 48 entries at a time; the deck preloads only its next image. Missing images get a readable
fallback, and absent signatures, packs and years remain explicitly unknown.

**My selection** shows saved works in the current collection and is shared across all three layouts.
Only validated SHA identifiers are stored in `textmode-discovery-selection-v1` in local storage.
Saving remains usable for the current visit if storage is blocked. There are no invented engagement
counts or accounts. Passing leaves an already saved work saved; undo restores its preceding saved
state. A hidden deck does not consume keyboard events, and viewing the selection preserves its position.

Browser checks cover shared/persistent selections, undo, end/restart, horizontal gestures without
accidental navigation, unavailable images, empty selections, null metadata and page overflow in both
locales at desktop/mobile widths. Screenshots of the real public collection stay in the ignored
`datasets/build/layout-review/` directory.

The header links the work of the day, thumbnails and related-work diagrams. The selected work identifier
survives switching views and languages. Exploration reads the existing public day selection and,
when a work supplies them, its pack, signature and year lists. It shows whole-work conservation
thumbnails and loads 48 entries at a time. Related-work diagrams are accessible radial diagrams around
a shared metadata value: pack, signature or year. A node opens the same work screen.

Since the unified museum, collection search and discovery layouts use the same origin's
gated corpus API when available and the exported visit lists otherwise. Their work links
open the shared `/work` screen. The scientific feature constellation is the native
`/constellation` room; the former research bridge is unnecessary. Reports and these
experiments are readable in `/research`. This does not publish the private train corpus
or graph as static build assets. Public feature-similarity hosting still requires an
authorized export. TMG v2 font/palette assets also need to reach the public frontend
before these pixel rules can apply to non-VGA works.

## Validation

Unit tests cover real glyph occupancy, density tones, luminance inversion, Gaussian impulses,
constant-image preservation, determinism and source immutability. Browser tests cover persistence,
PNG dimensions and recipe hashes, navigation, both locales and desktop/mobile widths. A contact
sheet uses project-made geometry rather than corpus artwork. Initial visual checks used synthetic exported records and grids. A follow-up verified the
real public grid, PNG and gallery through the museum proxy: Garage is reached at
`storage:3902` inside the dev container, not `localhost:3902`. Long-running Vite previews
need restarting after a rebuild so their server manifest matches the current client assets.
