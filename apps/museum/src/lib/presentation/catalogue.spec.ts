// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { describe, expect, it } from 'vitest';
import { emptyFilters, filterEntries, readFilters, researchQuery, UNKNOWN } from './catalogue';
import type { Entry } from '../work/visit';

const works: Entry[] = [
	{
		sha256: 'a',
		title: 'Étoiles',
		file: 'sky.ANS',
		path: 'sky.ANS',
		author: 'Artist',
		group: 'Fire',
		pack: 'fire-96',
		year: 1996,
		cols: 80,
		rows: 60,
		level: '12'
	},
	{
		sha256: 'b',
		title: null,
		file: 'night.ASC',
		path: 'night.ASC',
		author: null,
		group: null,
		pack: null,
		year: null,
		cols: 40,
		rows: 20,
		level: '12'
	},
	{
		sha256: 'c',
		title: 'Sky',
		file: 'sky2.ANS',
		path: 'sky2.ANS',
		author: 'Artist',
		group: 'Ice',
		pack: 'ice-97',
		year: 1997,
		cols: 80,
		rows: 30,
		level: '12'
	}
];

describe('public collection search', () => {
	it('combines words and metadata filters, with accent-insensitive title matching', () => {
		expect(
			filterEntries(works, {
				...emptyFilters(),
				q: 'etoiles ARTIST',
				group: 'Fire',
				year: '1996'
			}).map((entry) => entry.sha256)
		).toEqual(['a']);
		expect(
			filterEntries(works, { ...emptyFilters(), q: 'sky', group: 'Ice' }).map(
				(entry) => entry.sha256
			)
		).toEqual(['c']);
	});
	it('can find missing metadata and sorts without changing source order', () => {
		expect(
			filterEntries(works, { ...emptyFilters(), year: UNKNOWN, author: UNKNOWN }).map(
				(entry) => entry.sha256
			)
		).toEqual(['b']);
		expect(
			filterEntries(works, { ...emptyFilters(), order: 'year' }).map((entry) => entry.sha256)
		).toEqual(['a', 'c', 'b']);
		expect(works.map((entry) => entry.sha256)).toEqual(['a', 'b', 'c']);
	});
	it('round-trips global corpus queries without transferring public-only signature filters', () => {
		const input = new URLSearchParams('q=A%26B&year=1996&format=ansi&words=hello&author=Artist');
		const result = new URLSearchParams(researchQuery(readFilters(input)));
		expect(result.get('q')).toBe('A&B');
		expect(result.get('words')).toBe('hello');
		expect(result.get('format')).toBe('ansi');
		expect(result.has('author')).toBe(false);
	});
	it('shuffles by the seed when no order is chosen, and sends the seed to the corpus', () => {
		const seeded = { ...emptyFilters(), seed: 'abc234' };
		const once = filterEntries(works, seeded).map((entry) => entry.sha256);
		expect(filterEntries(works, seeded).map((entry) => entry.sha256)).toEqual(once);
		expect([...once].sort()).toEqual(['a', 'b', 'c']);
		expect(filterEntries(works, { ...seeded, order: 'year' }).map((entry) => entry.sha256)).toEqual(
			['a', 'c', 'b']
		);
		expect(new URLSearchParams(researchQuery(seeded)).get('seed')).toBe('abc234');
	});
});
