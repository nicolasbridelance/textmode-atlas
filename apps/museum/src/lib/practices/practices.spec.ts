// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { describe, expect, it } from 'vitest';
import type { Work } from '../work/record';
import {
	families,
	inFamily,
	isHeld,
	placeOf,
	practices,
	say,
	standingOf,
	type Practice
} from './practices';

describe('the registry of practices', () => {
	it('puts every practice in a declared family', () => {
		const codes = new Set(families.map((f) => f.code));
		expect(practices.every((p) => codes.has(p.family))).toBe(true);
		expect(families.reduce((n, f) => n + inFamily(f.code).length, 0)).toBe(practices.length);
	});

	it('has both required locales for every label', () => {
		expect(practices.every((p) => p.label.en && p.label.fr)).toBe(true);
	});

	it('shows some practices held and some gaps', () => {
		const held = practices.filter(isHeld).length;
		expect(held).toBeGreaterThan(0);
		expect(held).toBeLessThan(practices.length);
	});
});

describe('placeOf', () => {
	it('splits the source from the path at the first colon', () => {
		expect(placeOf('cs.cmu.edu:~sef/Orig-Smiley.htm#lines=124-127')).toEqual({
			source: 'cs.cmu.edu',
			path: '~sef/Orig-Smiley.htm#lines=124-127'
		});
	});
});

describe('say', () => {
	it('falls back to English', () => {
		expect(say({ en: 'Mosaic', fr: 'Mosaïque' }, 'de')).toBe('Mosaic');
		expect(say({ en: 'Mosaic', fr: 'Mosaïque' }, 'fr')).toBe('Mosaïque');
	});
});

describe('standingOf', () => {
	const held = practices.find(isHeld) as Practice;
	const missing = practices.find((p) => !isHeld(p)) as Practice;
	const published = (shown: 'files' | 'record') => async () =>
		({ record: { shown }, grid: null }) as unknown as Work;

	it('says a practice with no representative is missing, without asking', async () => {
		const load = () => Promise.reject(new Error('not asked'));
		expect(await standingOf(missing, load)).toBe('missing');
	});

	it('reads the export: files published is on show, a record or nothing is the reserve', async () => {
		expect(await standingOf(held, published('files'))).toBe('shown');
		expect(await standingOf(held, published('record'))).toBe('reserve');
		expect(await standingOf(held, async () => null)).toBe('reserve');
	});
});
