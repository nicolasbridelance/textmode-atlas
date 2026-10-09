// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { describe, expect, it } from 'vitest';
import { draw, newSeed, shuffled } from './chance';

const works = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].map((sha256) => ({ sha256 }));
const order = (seed: string) => shuffled(works, seed).map((work) => work.sha256);

describe('chance', () => {
	it('shuffles the same way for the same seed, so a draw can be shared', () => {
		expect(order('abc234')).toEqual(order('abc234'));
		expect([...order('abc234')].sort()).toEqual(works.map((work) => work.sha256));
	});
	it('shuffles differently for another seed', () => {
		expect(order('abc234')).not.toEqual(order('xyz789'));
	});
	it('draws the first work of the shuffle, or nothing from nothing', () => {
		expect(draw(works, 'abc234')?.sha256).toBe(order('abc234')[0]);
		expect(draw([], 'abc234')).toBeNull();
	});
	it('makes short readable seeds the server accepts', () => {
		expect(newSeed(() => 0)).toBe('aaaaaa');
		expect(newSeed()).toMatch(/^[a-z2-9]{6}$/);
	});
});
