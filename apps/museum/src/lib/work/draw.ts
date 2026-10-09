// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// Draws a grid cell by cell from a raw `.f16` bitmap font (256 glyphs × 16 rows, one byte per
// row, leftmost pixel in the top bit) in the VGA palette, as the pipeline's renderer does.
import type { TmgGrid } from './tmg';

export const CELL_WIDTH = 8;
export const CELL_HEIGHT = 16;
const GLYPHS = 256;
const HIGH = 8; // the bright bit of a VGA colour
const COLOUR = 0x0f; // the 16 colours of an attribute nibble
const CODEPOINT = 0xff; // CP437: one byte per glyph
const LEFTMOST = 0x80; // a glyph row's leftmost pixel, in the top bit
const RGBA = 4;
const OPAQUE = 255;
const ALPHA = 3;
// VGA's four levels of a channel.
const O = 0x00;
const L = 0x55;
const M = 0xaa;
const F = 0xff;

// prettier-ignore
export const VGA_PALETTE: readonly (readonly [number, number, number])[] = [
	[O, O, O], [O, O, M], [O, M, O], [O, M, M], [M, O, O], [M, O, M], [M, L, O], [M, M, M],
	[L, L, L], [L, L, F], [L, F, L], [L, F, F], [F, L, L], [F, L, F], [F, F, L], [F, F, F]
];

export function checkFont(font: Uint8Array): Uint8Array {
	if (font.length !== GLYPHS * CELL_HEIGHT) throw new Error(`font of ${font.length} bytes`);
	return font;
}

/** The background as shown: with blink (not iCE), the high bit blinks instead of brightening. */
export function shownBackground(grid: TmgGrid, i: number): number {
	return grid.ice ? grid.bg[i] | (grid.blink[i] ? HIGH : 0) : grid.bg[i];
}

/** Paint one cell into RGBA pixels of a canvas `width` pixels wide. */
export function paintCell(
	pixels: Uint8ClampedArray,
	width: number,
	grid: TmgGrid,
	font: Uint8Array,
	i: number
): void {
	const x0 = (i % grid.cols) * CELL_WIDTH;
	const y0 = Math.floor(i / grid.cols) * CELL_HEIGHT;
	const ink = VGA_PALETTE[grid.fg[i] & COLOUR];
	const paper = VGA_PALETTE[shownBackground(grid, i) & COLOUR];
	const glyph = (grid.codepoint[i] & CODEPOINT) * CELL_HEIGHT;
	for (let y = 0; y < CELL_HEIGHT; y++) {
		const bits = font[glyph + y];
		for (let x = 0; x < CELL_WIDTH; x++) {
			const [r, g, b] = bits & (LEFTMOST >> x) ? ink : paper;
			const at = ((y0 + y) * width + x0 + x) * RGBA;
			pixels[at] = r;
			pixels[at + 1] = g;
			pixels[at + 2] = b;
			pixels[at + ALPHA] = OPAQUE;
		}
	}
}
