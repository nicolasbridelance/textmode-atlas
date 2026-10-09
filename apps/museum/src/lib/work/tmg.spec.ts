// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { describe, expect, it } from 'vitest';
import { NEVER, arrivalOrder, parseTmg } from './tmg';
import { CELL_WIDTH, paintCell, shownBackground, VGA_PALETTE } from './draw';

/** A 2×1 grid: cell 0 never written, cell 1 a red-on-blue full block with the blink bit. */
function tiny(ice: boolean): ArrayBuffer {
	const buffer = new ArrayBuffer(16 + 2 * 8);
	const view = new DataView(buffer);
	[0x54, 0x4d, 0x47, 0x31].forEach((byte, i) => view.setUint8(i, byte));
	view.setUint8(4, 1);
	view.setUint8(5, ice ? 1 : 0);
	view.setUint16(6, 2, true);
	view.setUint16(8, 1, true);
	view.setUint32(16 + 4, NEVER, true);
	view.setUint16(24, 0xdb, true);
	view.setUint8(26, 12);
	view.setUint8(27, 0x80 | 1);
	view.setUint32(28, 7, true);
	return buffer;
}

describe('grid.tmg', () => {
	it('reads cells, the blink bit and unwritten cells', () => {
		const grid = parseTmg(tiny(false));
		expect([grid.cols, grid.rows, grid.ice]).toEqual([2, 1, false]);
		expect([grid.codepoint[1], grid.fg[1], grid.bg[1], grid.blink[1], grid.t[1]]).toEqual([
			0xdb, 12, 1, 1, 7
		]);
		expect(arrivalOrder(grid)).toEqual([1]);
	});

	it('refuses what is not a grid', () => {
		expect(() => parseTmg(new ArrayBuffer(16))).toThrow('TMG1');
	});

	it('brightens the background under iCE, not under blink', () => {
		expect(shownBackground(parseTmg(tiny(true)), 1)).toBe(9);
		expect(shownBackground(parseTmg(tiny(false)), 1)).toBe(1);
	});

	it('paints a full block in the ink colour', () => {
		const grid = parseTmg(tiny(false));
		const font = new Uint8Array(256 * 16);
		font.fill(0xff, 0xdb * 16, 0xdc * 16);
		const pixels = new Uint8ClampedArray(2 * CELL_WIDTH * 16 * 4);
		paintCell(pixels, 2 * CELL_WIDTH, grid, font, 1);
		expect(Array.from(pixels.slice(CELL_WIDTH * 4, CELL_WIDTH * 4 + 3))).toEqual([
			...VGA_PALETTE[12]
		]);
	});
});
