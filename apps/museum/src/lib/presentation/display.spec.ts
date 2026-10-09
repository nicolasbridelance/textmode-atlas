// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { describe, expect, it } from 'vitest';
import { displayQuery, PRESETS, readDisplay } from './display';

const read = (query: string) => readDisplay(new URLSearchParams(query));

describe('collection display', () => {
	it('starts on the wall, and each layout from its preset', () => {
		expect(readDisplay(null)).toEqual({ layout: 'wall', ...PRESETS.wall });
		expect(read('layout=feed')).toEqual({ layout: 'feed', ...PRESETS.feed });
	});
	it('keeps the former view addresses', () => {
		expect(read('view=pinterest').layout).toBe('wall');
		expect(read('view=instagram').layout).toBe('feed');
		expect(read('view=tinder').layout).toBe('deck');
		expect(read('view=relations').layout).toBe('wall');
	});
	it('lets any setting override the preset, and ignores invalid values', () => {
		expect(read('layout=grid&cols=3&fit=whole&caption=none&paper=dark')).toEqual({
			layout: 'grid',
			cols: 3,
			fit: 'whole',
			caption: 'none',
			paper: 'dark'
		});
		expect(read('layout=grid&cols=9&fit=zoom').cols).toBe(PRESETS.grid.cols);
		expect(read('layout=grid&fit=zoom').fit).toBe(PRESETS.grid.fit);
	});
	it('writes only what differs from the preset, and round-trips', () => {
		const display = read('layout=grid&cols=3');
		const query = displayQuery(display);
		expect(query).toMatchObject({ layout: 'grid', cols: '3', fit: '', view: '' });
		const params = new URLSearchParams(
			Object.entries(query).filter(([, value]) => value) as [string, string][]
		);
		expect(readDisplay(params)).toEqual(display);
	});
});
