// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { describe, expect, it } from 'vitest';
import { gaussian, glyphCoverage, renderPixels } from './render';
import { NEVER, type TmgGrid } from '../work/tmg';

function fixture(): { grid: TmgGrid; font: Uint8Array } {
	const font = new Uint8Array(256 * 16);
	font.fill(0xff, 0xdb * 16, 0xdc * 16);
	font.fill(0x0f, 0xb1 * 16, 0xb2 * 16);
	return {
		font,
		grid: {
			cols: 3,
			rows: 1,
			ice: false,
			codepoint: new Uint16Array([0xdb, 0xb1, 0x20]),
			fg: new Uint8Array([15, 12, 0]),
			bg: new Uint8Array(3),
			blink: new Uint8Array(3),
			t: new Uint32Array([0, 1, NEVER])
		}
	};
}

describe('scripted interpretations', () => {
	it('measures actual glyph coverage independently of character code order', () => {
		const { font } = fixture();
		expect(glyphCoverage(font, 0x20)).toBe(0);
		expect(glyphCoverage(font, 0xb1)).toBe(0.5);
		expect(glyphCoverage(font, 0xdb)).toBe(1);
	});
	it('maps full, half and unwritten cells to black, middle grey and white', () => {
		const { grid, font } = fixture();
		const image = renderPixels(grid, font, 'density', 'pixels');
		expect([...image.slice(0, 4)]).toEqual([0, 0, 0, 255]);
		expect([...image.slice(8 * 4, 8 * 4 + 4)]).toEqual([128, 128, 128, 255]);
		expect([...image.slice(16 * 4, 16 * 4 + 4)]).toEqual([255, 255, 255, 255]);
	});
	it('inverts luminance on white paper and preserves the VGA rendering', () => {
		const { grid, font } = fixture();
		const original = renderPixels(grid, font, 'original', 'pixels');
		const paper = renderPixels(grid, font, 'paper', 'pixels');
		expect([...original.slice(0, 4)]).toEqual([255, 255, 255, 255]);
		expect([...paper.slice(0, 4)]).toEqual([0, 0, 0, 255]);
		expect([...paper.slice(16 * 4, 16 * 4 + 4)]).toEqual([255, 255, 255, 255]);
	});
	it('uses a normalized Gaussian kernel with clamped edges', () => {
		const constant = new Uint8ClampedArray(5 * 5 * 4).fill(255);
		expect(gaussian(constant, 5, 5)).toEqual(constant);
		const impulse = new Uint8ClampedArray(5 * 5 * 4);
		impulse[(2 * 5 + 2) * 4] = 255;
		const blurred = gaussian(impulse, 5, 5);
		expect(blurred[(2 * 5 + 2) * 4]).toBe(36);
		expect(blurred[(2 * 5 + 1) * 4]).toBe(24);
	});
	it.each(['pointillism', 'impressionism', 'graffiti'] as const)(
		'%s is repeatable, opaque and leaves source data untouched',
		(style) => {
			const { grid, font } = fixture();
			const before = structuredClone({ grid, font });
			const first = renderPixels(grid, font, style, 'pixels');
			expect(first).toEqual(renderPixels(grid, font, style, 'pixels'));
			expect(first).not.toEqual(renderPixels(grid, font, 'original', 'pixels'));
			expect(first.filter((_, i) => i % 4 === 3).every((value) => value === 255)).toBe(true);
			expect({ grid, font }).toEqual(before);
		}
	);
});
