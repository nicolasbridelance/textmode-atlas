// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { NEVER, type TmgGrid } from './tmg';

/** The speed works arrive at by default: a common modem of the early BBS years. */
export const BBS_BAUD = 2400;
const BITS_PER_BYTE = 10; // 8 data bits, a start bit and a stop bit
const S_PER_MIN = 60;
const PAD = 2;

/** Seconds a modem at `baud` takes to send `bytes`. */
export function secondsAt(bytes: number, baud: number): number {
	return bytes / (baud / BITS_PER_BYTE);
}

/** The offset of the last byte that wrote a cell: how long the work takes to arrive. */
export function lastByte(grid: TmgGrid): number {
	let last = 0;
	for (const t of grid.t) if (t !== NEVER && t > last) last = t;
	return last;
}

/** `42 s`, `3 min 05 s`: the same in English and French. */
export function duration(seconds: number): string {
	const s = Math.round(seconds);
	if (s < S_PER_MIN) return `${s} s`;
	return `${Math.floor(s / S_PER_MIN)} min ${String(s % S_PER_MIN).padStart(PAD, '0')} s`;
}
