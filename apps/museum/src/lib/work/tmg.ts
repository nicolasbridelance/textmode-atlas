// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// Reader of the compact grid exported by `tm export` (`grid.tmg`, ADR 0022): a 16-byte header,
// then 8 bytes per cell, row by row. The site never reads ANSI: this is all it knows of a work.

export const NEVER = 0xffffffff;
const HEADER_BYTES = 16;
const CELL_BYTES = 8;
const BLINK = 0x80;
const ICE = 0x01;
const MAGIC = 'TMG1';
const VERSION = 1;
// Byte offsets in the header, then in a cell.
const HEADER = { version: 4, flags: 5, cols: 6, rows: 8 } as const;
const CELL = { codepoint: 0, fg: 2, bg: 3, t: 4 } as const;

export interface TmgGrid {
	cols: number;
	rows: number;
	ice: boolean;
	codepoint: Uint16Array;
	fg: Uint8Array;
	bg: Uint8Array;
	blink: Uint8Array;
	t: Uint32Array; // NEVER for a cell no byte wrote
}

export function parseTmg(buffer: ArrayBuffer): TmgGrid {
	const view = new DataView(buffer);
	const magic = String.fromCharCode(...new Uint8Array(buffer, 0, MAGIC.length));
	if (magic !== MAGIC || view.getUint8(HEADER.version) !== VERSION) {
		throw new Error(`not a ${MAGIC} grid`);
	}
	const cols = view.getUint16(HEADER.cols, true);
	const rows = view.getUint16(HEADER.rows, true);
	const count = cols * rows;
	if (buffer.byteLength !== HEADER_BYTES + count * CELL_BYTES) throw new Error('truncated grid');
	const grid: TmgGrid = {
		cols,
		rows,
		ice: (view.getUint8(HEADER.flags) & ICE) !== 0,
		codepoint: new Uint16Array(count),
		fg: new Uint8Array(count),
		bg: new Uint8Array(count),
		blink: new Uint8Array(count),
		t: new Uint32Array(count)
	};
	for (let i = 0; i < count; i++) {
		const at = HEADER_BYTES + i * CELL_BYTES;
		const bg = view.getUint8(at + CELL.bg);
		grid.codepoint[i] = view.getUint16(at + CELL.codepoint, true);
		grid.fg[i] = view.getUint8(at + CELL.fg);
		grid.bg[i] = bg & ~BLINK;
		grid.blink[i] = bg & BLINK ? 1 : 0;
		grid.t[i] = view.getUint32(at + CELL.t, true);
	}
	return grid;
}

/** Cell indexes in the order the bytes wrote them: the arrival of the work. */
export function arrivalOrder(grid: TmgGrid): number[] {
	const written: number[] = [];
	for (let i = 0; i < grid.t.length; i++) if (grid.t[i] !== NEVER) written.push(i);
	return written.sort((a, b) => grid.t[a] - grid.t[b] || a - b);
}
