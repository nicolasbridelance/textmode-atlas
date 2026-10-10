// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { describe, expect, it } from 'vitest';
import { families, inFamily, isHeld, placeOf, practices, say } from './practices';

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
