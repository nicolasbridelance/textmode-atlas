// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { CELL_HEIGHT, CELL_WIDTH, paintCell, shownBackground, VGA_PALETTE } from '../work/draw';
import { NEVER, type TmgGrid } from '../work/tmg';
import { applyEffect, DEFAULT_EFFECT, type EffectOptions } from './effects';
import type { ArtStyle, Sampling } from './settings.svelte';

const RGBA = 4;
const WHITE = 255;
const CHANNELS = 3;
const GLYPH_MASK = 0xff;
const KERNEL = [1, 4, 6, 4, 1]; // eslint-disable-line @typescript-eslint/no-magic-numbers
const KERNEL_SUM = 16;
const LUMA = [0.2126, 0.7152, 0.0722]; // eslint-disable-line @typescript-eslint/no-magic-numbers

/** Occupancy of the actual bitmap, not the ordinal value of a CP437 code. */
export function glyphCoverage(font: Uint8Array, code: number): number {
	let lit = 0;
	const start = (code & GLYPH_MASK) * CELL_HEIGHT;
	for (const bits of font.subarray(start, start + CELL_HEIGHT)) {
		let remaining = bits;
		while (remaining) {
			lit += remaining & 1;
			remaining >>>= 1;
		}
	}
	return lit / (CELL_WIDTH * CELL_HEIGHT);
}

function density(pixels: Uint8ClampedArray, grid: TmgGrid, font: Uint8Array): void {
	const tones = Array.from({ length: GLYPH_MASK + 1 }, (_, code) =>
		Math.round(WHITE * (1 - glyphCoverage(font, code)))
	);
	const width = grid.cols * CELL_WIDTH;
	for (let at = 0; at < pixels.length; at += RGBA) {
		const pixel = at / RGBA;
		const cell =
			Math.floor(pixel / width / CELL_HEIGHT) * grid.cols +
			Math.floor((pixel % width) / CELL_WIDTH);
		const tone = grid.t[cell] === NEVER ? WHITE : tones[grid.codepoint[cell] & GLYPH_MASK];
		pixels.fill(tone, at, at + CHANNELS);
	}
}

function paper(pixels: Uint8ClampedArray): void {
	for (let at = 0; at < pixels.length; at += RGBA) {
		const tone =
			WHITE - Math.round(LUMA.reduce((sum, weight, c) => sum + weight * pixels[at + c], 0));
		pixels.fill(tone, at, at + CHANNELS);
	}
}

function sampleAt(x: number, y: number, width: number, height: number): number {
	return (
		(Math.min(height - 1, Math.max(0, y)) * width + Math.min(width - 1, Math.max(0, x))) * RGBA
	);
}

function blurAxis(
	source: ArrayLike<number>,
	width: number,
	height: number,
	vertical: boolean
): Float32Array {
	const result = new Float32Array(source.length);
	for (let at = 0; at < source.length; at++) {
		const pixel = Math.floor(at / RGBA);
		const x = pixel % width;
		const y = Math.floor(pixel / width);
		result[at] =
			KERNEL.reduce((sum, weight, k) => {
				const offset = k - 2;
				const sampled = sampleAt(
					x + (vertical ? 0 : offset),
					y + (vertical ? offset : 0),
					width,
					height
				);
				return sum + weight * source[sampled + (at % RGBA)];
			}, 0) / KERNEL_SUM;
	}
	return result;
}

/** Separable 5-tap binomial approximation to a Gaussian, sigma ≈ 1 source pixel. */
export function gaussian(
	source: Uint8ClampedArray,
	width: number,
	height: number
): Uint8ClampedArray {
	return new Uint8ClampedArray(
		blurAxis(blurAxis(source, width, height, false), width, height, true)
	);
}

/** Cell-average foreground/background colour, smoothly interpolated between cell centres. */
function reconstruct(grid: TmgGrid, font: Uint8Array): Uint8ClampedArray {
	const colours = Array.from(grid.codepoint, (code, i) => {
		if (grid.t[i] === NEVER) return [0, 0, 0];
		const coverage = glyphCoverage(font, code);
		const ink = VGA_PALETTE[grid.fg[i] & 0x0f]; // eslint-disable-line @typescript-eslint/no-magic-numbers
		const paper = VGA_PALETTE[shownBackground(grid, i) & 0x0f]; // eslint-disable-line @typescript-eslint/no-magic-numbers
		return ink.map((value, c) => value * coverage + paper[c] * (1 - coverage));
	});
	const width = grid.cols * CELL_WIDTH;
	const height = grid.rows * CELL_HEIGHT;
	const output = new Uint8ClampedArray(width * height * RGBA);
	for (let pixel = 0; pixel < width * height; pixel++) {
		const x = Math.max(0, Math.min(grid.cols - 1, (pixel % width) / CELL_WIDTH - 0.5)); // eslint-disable-line @typescript-eslint/no-magic-numbers
		const y = Math.max(0, Math.min(grid.rows - 1, Math.floor(pixel / width) / CELL_HEIGHT - 0.5)); // eslint-disable-line @typescript-eslint/no-magic-numbers
		const col = Math.floor(x);
		const row = Math.floor(y);
		const nextCol = Math.min(grid.cols - 1, col + 1);
		const nextRow = Math.min(grid.rows - 1, row + 1);
		for (let c = 0; c < CHANNELS; c++) {
			const top =
				colours[row * grid.cols + col][c] * (1 - x + col) +
				colours[row * grid.cols + nextCol][c] * (x - col);
			const bottom =
				colours[nextRow * grid.cols + col][c] * (1 - x + col) +
				colours[nextRow * grid.cols + nextCol][c] * (x - col);
			output[pixel * RGBA + c] = top * (1 - y + row) + bottom * (y - row);
		}
		output[pixel * RGBA + CHANNELS] = WHITE;
	}
	return output;
}

/** Full work from the public grid. Inputs stay untouched; all rules use native VGA pixels. */
function interpret(
	pixels: Uint8ClampedArray,
	grid: TmgGrid,
	font: Uint8Array,
	style: ArtStyle,
	options: EffectOptions
): Uint8ClampedArray {
	const width = grid.cols * CELL_WIDTH;
	const height = grid.rows * CELL_HEIGHT;
	if (style === 'paper') paper(pixels);
	if (style === 'density') density(pixels, grid, font);
	if (style === 'original' || style === 'paper' || style === 'density') return pixels;
	const prepared = reconstruct(grid, font);
	if (style === 'reconstruction') return prepared;
	return applyEffect(
		options.preparation === 'coverage' ? prepared : pixels,
		width,
		height,
		style,
		options,
		pixels
	);
}

export function renderPixels(
	grid: TmgGrid,
	font: Uint8Array,
	style: ArtStyle,
	sampling: Sampling,
	options: EffectOptions = DEFAULT_EFFECT
): Uint8ClampedArray {
	const width = grid.cols * CELL_WIDTH;
	const height = grid.rows * CELL_HEIGHT;
	let pixels: Uint8ClampedArray = new Uint8ClampedArray(width * height * RGBA);
	for (let at = CHANNELS; at < pixels.length; at += RGBA) pixels[at] = WHITE;
	for (let cell = 0; cell < grid.t.length; cell++) {
		if (grid.t[cell] !== NEVER) paintCell(pixels, width, grid, font, cell);
	}
	pixels = interpret(pixels, grid, font, style, options);
	return sampling === 'gaussian' ? gaussian(pixels, width, height) : pixels;
}
