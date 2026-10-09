// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { describe, expect, it } from 'vitest';
import { glyph, hex } from './cp437';
import { dayOfYear, type Entry, type List, waysOut, workOfTheDay } from './visit';

function entry(sha: string, pack: string, author = 'a'): Entry {
	return {
		sha256: sha,
		title: sha,
		file: `${sha}.ANS`,
		path: `${sha}.ANS`,
		author,
		group: null,
		pack,
		year: 1996,
		cols: 80,
		rows: 25,
		level: '12'
	};
}

const list = (...works: Entry[]): List => ({ works });

describe('ways out', () => {
	const pack = list(entry('a', 'p'), entry('b', 'p'), entry('c', 'p'));

	it('steps through the pack in its order', () => {
		const ways = waysOut('b', 'p', { pack, author: null, year: null, days: null }, 0);
		expect([ways.previous?.sha256, ways.next?.sha256]).toEqual(['a', 'c']);
		const first = waysOut('a', 'p', { pack, author: null, year: null, days: null }, 0);
		expect(first.previous).toBeNull();
	});

	it('prefers a work of the same signature from another pack', () => {
		const author = list(entry('b', 'p'), entry('c', 'p'), entry('x', 'q'));
		const ways = waysOut('b', 'p', { pack, author, year: null, days: null }, 0);
		expect(ways.signature?.sha256).toBe('x');
	});

	it('falls back to the same pack, and offers nothing for a lone signature', () => {
		const author = list(entry('b', 'p'), entry('c', 'p'));
		expect(waysOut('b', 'p', { pack, author, year: null, days: null }, 0).signature?.sha256).toBe(
			'c'
		);
		const alone = list(entry('b', 'p'));
		expect(
			waysOut('b', 'p', { pack, author: alone, year: null, days: null }, 0).signature
		).toBeNull();
	});

	it('takes the same year from elsewhere, and chance never returns the work itself', () => {
		const year = list(entry('a', 'p'), entry('y', 'q'));
		const days = list(entry('b', 'p'));
		const ways = waysOut('b', 'p', { pack, author: null, year, days }, 0);
		expect(ways.year?.sha256).toBe('y');
		expect(ways.chance).toBeNull();
	});
});

describe('the work of the day', () => {
	it('is the same for everyone on a day, and changes the next day', () => {
		const days = list(entry('a', 'p'), entry('b', 'p'), entry('c', 'p'));
		expect(dayOfYear(new Date(2026, 0, 1))).toBe(0);
		expect(dayOfYear(new Date(2026, 9, 9, 23, 30))).toBe(281);
		expect(workOfTheDay(days, new Date(2026, 0, 2))?.sha256).toBe('b');
		expect(workOfTheDay(list(), new Date())).toBeNull();
	});
});

describe('cp437', () => {
	it('names a glyph and its code', () => {
		expect([glyph(0xdb), glyph(0x41), glyph(0x01), hex(0xb0)]).toEqual(['█', 'A', '☺', '0xB0']);
	});
});
