<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Scripted image experiments, 2026-10-09

At the owner's request, replace the initial geometric placeholders with image-processing methods
and compare them on actual public works. No model is used. The workshop implements its own
adaptations; it does not claim pixel equivalence to GIMP or imitate a particular artist.

## Sample and reproducibility

Six works selected at chronological quantiles from the existing public day list, restricted to
40–160 columns and 16–140 rows. This is a small aesthetic study, not an evaluation on held-out
research packs. Eight default looks plus six size trials and one light-support trial per work
produce 90 outputs. Native grids, the bundled font and settings are the inputs. Each output has a
pixel hash and render timing in `recipes.json`; PNGs and HTML stay in ignored `datasets/build/`.
The source files and public bucket are never written.

| Work | Year | Native pixels | Useful observation |
| --- | --- | --- | --- |
| ANARCHY.ANS | 1990 | 640×336 | Regular halftones suit the geometric letterwork; guided strokes retain its broad forms |
| CD-TP05.TLY | 1995 | 640×368 | Useful check of how small lettering survives filtering |
| DD-MSKP.ANS | 1996 | 640×336 | Coloured drawn lettering is a good candidate for stippling, brushwork and stencil |
| RS-BIOH.ASC | 1997 | 640×544 | Character-based detail needs comparison against the source before choosing reconstructed input |
| S1-MNK.ANS | 2001 | 640×336 | Cell coverage reveals the large image encoded by ASCII density but destroys literal text |
| CT-EUGENE_IONESCO-RHINOCEROS.ANS | 2026 | 640×944 | A taller work tests whole-image layouts, size choices and runtime |

Regenerate from the visualization worktree:

```sh
pnpm --dir apps/museum presentation:review
```

The script temporarily starts Vite on 5173 and terminates it afterwards. It uses only the public
export and does not require the private research corpus. The local review is available at
`/research/review/index.html` when the optional research bridge is enabled.

## Findings and implemented changes

The fixed four-pixel point lattice produced the white grille visible in the owner's screenshot.
A colour sample was placed on every lattice site without considering the work's tonal structure.
The new organic points jitter their positions with a fixed coordinate hash, encode local peak
intensity in mark area, and normalize ink hue so intensity is not multiplied twice. Dark and
light image supports are explicit choices, separate from the gallery background. A regular
halftone remains as a deliberate printing treatment, rather than masquerading as pointillism.

Bitmap shading itself is another source of interference. Artistic filters can now read either
the literal pixels or colours reconstructed from each glyph's foreground/background mixture,
weighted by lit-pixel coverage and interpolated between cells. Reconstruction is also a standalone
look. It exposes broad shapes in density-based ASCII but softens text and small contours. Visitors
can preserve literal pixels or mix the filtered result with the original using effect strength.

The first impressionist mode merely sampled diagonal bands. Its replacement paints two scales of
seeded elliptical marks, oriented along local luminance contours. The stencil treatment replaces
the periodic black speckle with seeded spray, posterized ink and gradient contours. Both remain
experiments: neither deserves an unqualified claim of historical painting or graffiti authenticity.

Classic Kuwahara filtering selects the least-variable of four local quadrants and uses its mean
colour. Summed-area tables keep the neighbourhood calculation bounded. It preserves simple sharp
boundaries while smoothing surfaces; on this sample it is often subtler than the brush treatment.
Observed default runtimes in local Chromium: points 34–174 ms, Kuwahara 295–718 ms, brushwork
97–420 ms, stencil 117–471 ms. These single-run figures depend on the device and warm-up state.

A split comparison reveals the complete original VGA rendering on the left and the interpretation
on the right. It changes neither the source nor the exported interpretation. Size (3–12 pixels),
strength (0–100%), input reconstruction and image support are persistent visitor choices included
in the version-2 export recipe.

## Priorities

1. Keep organic stippling, contour brushwork and stencil as the most promising expressive trials;
   expose the original alongside them, because their suitability varies by work.
2. Keep reconstruction and Kuwahara as analytical or preparation tools. Avoid applying them by
   default to text that needs to remain legible.
3. Next compare contrast curves for paper, difference-of-Gaussians ink contours and anisotropic
   Kuwahara against the current outputs. These are candidates, not methods already tested here.
4. The upscaling controls still offer nearest-neighbour, browser interpolation and fixed Gaussian
   smoothing. Lanczos/area reconstruction and Scale2x require a separate enlargement study.

## Constellation naming and common navigation

The museum's radial diagrams were metadata groups in a small public selection; the explorer's
constellation is the train-corpus nearest-neighbour graph, with feature-derived positions and
communities. Calling both “constellation” was misleading. Metadata diagrams are now “Related
works” / “Parcours”. The opt-in local “Constellation” link opens the actual explorer graph through
the same origin, preserves the starting work and language, and offers a return to the museum.
It reuses the existing nodes, edges and communities rather than computing a second graph.

Enable only for the local workspace:

```sh
RESEARCH_BASE=/research TM_RESEARCH_ORIGIN=http://localhost:8737 pnpm --dir apps/museum build
TM_RESEARCH_ORIGIN=http://localhost:8737 pnpm --dir apps/museum exec vite preview --port 4174 --strictPort
```

The research bridge defaults to disabled outside the dev container. It is an exploration of the
private train corpus, not a public museum export. Public similarity navigation still needs a
proper authorized export with algorithm provenance; this local bridge does not replace it.

## Method references

[GIMP Newsprint](https://docs.gimp.org/3.0/en/gimp-filter-newsprint.html) explains variable-area
screening. [GIMP GIMPressionist](https://docs.gimp.org/3.0/en/plug-in-gimpressionist.html) documents
brush size and orientation choices. [GIMP Oilify](https://docs.gimp.org/3.0/en/gimp-filter-oilify.html)
provides a comparison point for neighbourhood painting filters. The workshop's code and parameters,
rather than these product names, define its reproducible algorithms.
