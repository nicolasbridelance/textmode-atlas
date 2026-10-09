// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { expect, it } from 'vitest';
import { applyEffect, DEFAULT_EFFECT } from './effects';

function solid(width: number, height: number, rgb: number[]): Uint8ClampedArray {
	const pixels = new Uint8ClampedArray(width * height * 4);
	for (let at = 0; at < pixels.length; at += 4) pixels.set([...rgb, 255], at);
	return pixels;
}
it('organic dots leave black areas black, without a fixed white grid', () => {
	const pixels = solid(24, 24, [0, 0, 0]);
	expect(applyEffect(pixels, 24, 24, 'pointillism', DEFAULT_EFFECT)).toEqual(pixels);
});
it('dot area encodes tone once instead of darkening both area and ink', () => {
	const pixels = solid(48, 48, [100, 0, 0]);
	const result = applyEffect(pixels, 48, 48, 'halftone', DEFAULT_EFFECT);
	const mean =
		result.filter((_, i) => i % 4 === 0).reduce((sum, value) => sum + value, 0) / (48 * 48);
	expect(mean).toBeGreaterThan(60);
	expect(mean).toBeLessThan(120);
});
it('Kuwahara preserves a constant colour and a straight two-colour boundary', () => {
	const pixels = solid(24, 24, [255, 0, 0]);
	for (let y = 0; y < 24; y++)
		for (let x = 12; x < 24; x++) pixels.set([0, 0, 255, 255], (y * 24 + x) * 4);
	expect(applyEffect(pixels, 24, 24, 'kuwahara', DEFAULT_EFFECT)).toEqual(pixels);
});
it('zero strength returns the original even when filter input was reconstructed', () => {
	const source = solid(24, 24, [128, 128, 128]);
	const original = solid(24, 24, [255, 0, 0]);
	expect(
		applyEffect(source, 24, 24, 'impressionism', { ...DEFAULT_EFFECT, strength: 0 }, original)
	).toEqual(original);
});
it('size and support change seeded points without changing their inputs', () => {
	const pixels = solid(24, 24, [180, 90, 40]);
	const before = pixels.slice();
	const first = applyEffect(pixels, 24, 24, 'pointillism', DEFAULT_EFFECT);
	expect(first).toEqual(applyEffect(pixels, 24, 24, 'pointillism', DEFAULT_EFFECT));
	expect(first).not.toEqual(
		applyEffect(pixels, 24, 24, 'pointillism', { ...DEFAULT_EFFECT, size: 10 })
	);
	expect(first).not.toEqual(
		applyEffect(pixels, 24, 24, 'pointillism', { ...DEFAULT_EFFECT, paper: 'light' })
	);
	expect(pixels).toEqual(before);
});
