// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { describe, expect, it } from 'vitest';
import { locales } from '#lib/paraglide/runtime.js';
import { KINDS, LIVE, STATUSES, STRANDS, hasBody, loadBody, studies } from './studies';

const LIVE_SOURCES = ['live:corpus'];
const DATE = /^\d{4}-\d{2}-\d{2}$/;

describe('the research registry', () => {
	it('gives every study a unique id usable as an address', () => {
		const ids = studies.map((s) => s.id);
		expect(new Set(ids).size).toBe(ids.length);
		for (const id of ids) expect(id).toMatch(/^[a-z0-9-]+$/);
	});

	it('uses only known kinds, strands, statuses and dates', () => {
		for (const s of studies) {
			expect(KINDS).toContain(s.kind);
			expect(STRANDS).toContain(s.strand);
			expect(STATUSES).toContain(s.status);
			expect(s.date).toMatch(DATE);
		}
	});

	it('titles and summarises every study in every locale', () => {
		for (const s of studies)
			for (const locale of locales) {
				expect(s.title[locale]?.trim(), `${s.id} title ${locale}`).toBeTruthy();
				expect(s.summary[locale]?.trim(), `${s.id} summary ${locale}`).toBeTruthy();
			}
	});

	it('finds the body of every study', async () => {
		for (const s of studies) {
			if (s.source.startsWith(LIVE)) {
				expect(LIVE_SOURCES).toContain(s.source);
				continue;
			}
			expect(hasBody(s), `${s.id}: ${s.source}`).toBe(true);
			expect(await loadBody(s)).toMatch(/^[\s\S]*# /);
		}
	});

	it('puts the programme first, then the newest', () => {
		expect(studies[0]?.kind).toBe('programme');
		const dates = studies.slice(1).map((s) => s.date);
		expect(dates).toEqual(dates.toSorted().reverse());
	});
});
