// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
// Scripted raster effects: seeded stippling, screened halftones, edge-oriented brush marks,
// Kuwahara quadrant filtering and a posterized stencil. No trained model is involved.
import type { ArtStyle } from './settings.svelte';

export interface EffectOptions {
	size: number;
	strength: number;
	paper: 'dark' | 'light';
	preparation: 'pixels' | 'coverage';
}
export const DEFAULT_EFFECT: EffectOptions = {
	size: 6,
	strength: 100,
	paper: 'dark',
	preparation: 'coverage'
};
const RGBA = 4;
const CHANNELS = 3;
const WHITE = 255;
const INK_FLOOR = 8;
const LUMA = [0.2126, 0.7152, 0.0722]; // eslint-disable-line @typescript-eslint/no-magic-numbers
const HASH_A = 0x45d9f3b;
const HASH_B = 0x27d4eb2d;
const UINT_MAX = 0xffffffff;
const HALF_PIXEL = 0.5;
const JITTER = 0.8;
const POINT_RADIUS = 0.55;
const PAPER_COLOUR = [247, 244, 235]; // eslint-disable-line @typescript-eslint/no-magic-numbers
const WHITE_INK = 0.65;
const EDGE_GAIN = 2;
const POSTER_STEP = 85;
const SPRAY_CHANCE = 0.025;
const SPRAY_GAIN = 0.5;

function at(x: number, y: number, width: number, height: number): number {
	return (
		(Math.min(height - 1, Math.max(0, Math.round(y))) * width +
			Math.min(width - 1, Math.max(0, Math.round(x)))) *
		RGBA
	);
}
function luminance(source: Uint8ClampedArray, index: number): number {
	return LUMA.reduce((sum, weight, c) => sum + source[index + c] * weight, 0);
}
function random(x: number, y: number, salt: number): number {
	let value = Math.imul(x + salt, HASH_A) ^ Math.imul(y + 1, HASH_B);
	value ^= value >>> 16; // eslint-disable-line @typescript-eslint/no-magic-numbers
	return (Math.imul(value, HASH_A) >>> 0) / UINT_MAX;
}
function support(length: number, paper: EffectOptions['paper']): Uint8ClampedArray {
	const pixels = new Uint8ClampedArray(length);
	for (let i = 0; i < length; i += RGBA) {
		if (paper === 'light') pixels.set(PAPER_COLOUR, i);
		pixels[i + CHANNELS] = WHITE;
	}
	return pixels;
}
function ink(source: Uint8ClampedArray, index: number, paper: EffectOptions['paper']): number[] {
	return Array.from(source.subarray(index, index + CHANNELS), (value) =>
		paper === 'light' ? value * WHITE_INK : value
	);
}

/** Antialiased oriented ellipse; clipped to the image, composited over the chosen support. */
function brush(
	output: Uint8ClampedArray,
	width: number,
	height: number,
	x: number,
	y: number,
	radius: number,
	aspect: number,
	angle: number,
	colour: number[]
): void {
	const reach = radius * Math.max(1, aspect) + 1;
	const cosine = Math.cos(angle);
	const sine = Math.sin(angle);
	for (let py = Math.max(0, Math.floor(y - reach)); py <= Math.min(height - 1, y + reach); py++) {
		for (let px = Math.max(0, Math.floor(x - reach)); px <= Math.min(width - 1, x + reach); px++) {
			const dx = px - x;
			const dy = py - y;
			const u = (dx * cosine + dy * sine) / aspect;
			const v = -dx * sine + dy * cosine;
			const alpha = Math.min(1, Math.max(0, radius + HALF_PIXEL - Math.hypot(u, v)));
			const index = (py * width + px) * RGBA;
			for (let c = 0; c < CHANNELS; c++)
				output[index + c] = output[index + c] * (1 - alpha) + colour[c] * alpha;
		}
	}
}

/** Same pseudo-random seed on every run; occupancy controls mark area, not a white grid mask. */
function pointField(
	source: Uint8ClampedArray,
	width: number,
	height: number,
	options: EffectOptions,
	regular: boolean
): Uint8ClampedArray {
	const output = support(source.length, options.paper);
	const step = options.size;
	for (let y = step / 2; y < height; y += step) {
		for (let x = step / 2; x < width; x += step) {
			const jx = regular ? 0 : (random(x, y, 1) - HALF_PIXEL) * step * JITTER;
			const jy = regular ? 0 : (random(x, y, 2) - HALF_PIXEL) * step * JITTER;
			const index = at(x + jx, y + jy, width, height);
			const light = luminance(source, index);
			if (light < INK_FLOOR) continue;
			const peak = Math.max(...source.subarray(index, index + CHANNELS));
			const radius = step * POINT_RADIUS * Math.sqrt(peak / WHITE);
			const colour = ink(source, index, options.paper).map((value) => (value * WHITE) / peak);
			brush(output, width, height, x + jx, y + jy, radius, 1, 0, colour);
		}
	}
	return output;
}

function gradient(
	source: Uint8ClampedArray,
	width: number,
	height: number,
	x: number,
	y: number
): [number, number] {
	const gx =
		luminance(source, at(x + 1, y, width, height)) - luminance(source, at(x - 1, y, width, height));
	const gy =
		luminance(source, at(x, y + 1, width, height)) - luminance(source, at(x, y - 1, width, height));
	return [gx, gy];
}
function paint(
	source: Uint8ClampedArray,
	width: number,
	height: number,
	options: EffectOptions
): Uint8ClampedArray {
	const output = support(source.length, options.paper);
	// Coarse marks lay down the masses; fine marks follow the contours.
	for (const size of [options.size * 2, options.size])
		paintLayer(output, source, width, height, options.paper, size);
	return output;
}
function paintLayer(
	output: Uint8ClampedArray,
	source: Uint8ClampedArray,
	width: number,
	height: number,
	paper: EffectOptions['paper'],
	size: number
): void {
	for (let y = size / 2; y < height; y += size) {
		for (let x = size / 2; x < width; x += size) {
			const jx = x + (random(x, y, size) - HALF_PIXEL) * size;
			const jy = y + (random(x, y, size + 1) - HALF_PIXEL) * size;
			const index = at(jx, jy, width, height);
			if (luminance(source, index) < INK_FLOOR) continue;
			const [gx, gy] = gradient(source, width, height, jx, jy);
			const angle = Math.atan2(gy, gx) + Math.PI / 2;
			brush(output, width, height, jx, jy, size / 2, 2, angle, ink(source, index, paper));
		}
	}
}

/** Integral image of each channel and squared luminance: bounded O(width × height). */
function integrals(source: Uint8ClampedArray, width: number, height: number): Float64Array[] {
	const stride = width + 1;
	const sums = Array.from({ length: RGBA }, () => new Float64Array(stride * (height + 1)));
	for (let y = 0; y < height; y++) {
		for (let x = 0; x < width; x++) {
			const pixel = (y * width + x) * RGBA;
			const i = (y + 1) * stride + x + 1;
			const values = [...source.subarray(pixel, pixel + CHANNELS), luminance(source, pixel) ** 2];
			for (let c = 0; c < RGBA; c++)
				sums[c][i] = values[c] + sums[c][i - 1] + sums[c][i - stride] - sums[c][i - stride - 1];
		}
	}
	return sums;
}
function rectangle(
	sum: Float64Array,
	stride: number,
	x0: number,
	y0: number,
	x1: number,
	y1: number
): number {
	return (
		sum[y1 * stride + x1] - sum[y0 * stride + x1] - sum[y1 * stride + x0] + sum[y0 * stride + x0]
	);
}
function region(
	sums: Float64Array[],
	width: number,
	height: number,
	x: number,
	y: number,
	dx: number,
	dy: number,
	radius: number
): { mean: number[]; variance: number } {
	const x0 = Math.max(0, x + Math.min(0, dx * radius));
	const y0 = Math.max(0, y + Math.min(0, dy * radius));
	const x1 = Math.min(width, x + Math.max(0, dx * radius) + 1);
	const y1 = Math.min(height, y + Math.max(0, dy * radius) + 1);
	const count = (x1 - x0) * (y1 - y0);
	const means = sums.map((sum) => rectangle(sum, width + 1, x0, y0, x1, y1) / count);
	const light = LUMA.reduce((total, weight, c) => total + weight * means[c], 0);
	return { mean: means.slice(0, CHANNELS), variance: Math.max(0, means[CHANNELS] - light ** 2) };
}
function kuwahara(
	source: Uint8ClampedArray,
	width: number,
	height: number,
	options: EffectOptions
): Uint8ClampedArray {
	const sums = integrals(source, width, height);
	const output = new Uint8ClampedArray(source);
	const radius = Math.round(options.size / 2);
	for (let pixel = 0; pixel < width * height; pixel++) {
		const x = pixel % width;
		const y = Math.floor(pixel / width);
		const quadrants = [
			[-1, -1],
			[1, -1],
			[-1, 1],
			[1, 1]
		];
		const samples = quadrants.map(([dx, dy]) => region(sums, width, height, x, y, dx, dy, radius));
		const best = samples.reduce((a, b) => (b.variance < a.variance ? b : a));
		output.set(best.mean, pixel * RGBA);
	}
	return output;
}
function stencil(
	source: Uint8ClampedArray,
	width: number,
	height: number,
	options: EffectOptions
): Uint8ClampedArray {
	const output = support(source.length, options.paper);
	for (let pixel = 0; pixel < width * height; pixel++) {
		const x = pixel % width;
		const y = Math.floor(pixel / width);
		const index = pixel * RGBA;
		if (luminance(source, index) < INK_FLOOR) continue;
		const [gx, gy] = gradient(source, width, height, x, y);
		const edge = Math.min(1, (Math.hypot(gx, gy) * EDGE_GAIN) / WHITE);
		const colour = ink(source, index, options.paper).map(
			(value) => Math.round(value / POSTER_STEP) * POSTER_STEP
		);
		for (let c = 0; c < CHANNELS; c++) output[index + c] = colour[c] * (1 - edge);
		if (random(x, y, options.size) < SPRAY_CHANCE) {
			for (let c = 0; c < CHANNELS; c++) output[index + c] *= SPRAY_GAIN;
		}
	}
	return output;
}

export function applyEffect(
	source: Uint8ClampedArray,
	width: number,
	height: number,
	style: ArtStyle,
	options: EffectOptions,
	baseline: Uint8ClampedArray = source
): Uint8ClampedArray {
	const filters: Partial<Record<ArtStyle, () => Uint8ClampedArray>> = {
		pointillism: () => pointField(source, width, height, options, false),
		halftone: () => pointField(source, width, height, options, true),
		impressionism: () => paint(source, width, height, options),
		kuwahara: () => kuwahara(source, width, height, options),
		graffiti: () => stencil(source, width, height, options)
	};
	const filtered = filters[style]?.() ?? source;
	const strength = options.strength / 100; // eslint-disable-line @typescript-eslint/no-magic-numbers
	const output = new Uint8ClampedArray(source.length);
	for (let i = 0; i < source.length; i++)
		output[i] = baseline[i] * (1 - strength) + filtered[i] * strength;
	return output;
}
