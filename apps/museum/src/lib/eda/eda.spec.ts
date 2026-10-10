// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { describe, expect, it, vi } from 'vitest';
vi.mock('$app/env/public', () => ({ FILES_BASE: '/files' }));

import { checkState, everyYear, formatter, labelEvery, loadSnapshot, ticks } from './eda';

describe('exploration helpers', () => {
	it('tells a missing check from a broken one', () => {
		expect(checkState(undefined)).toBe('unknown');
		expect(checkState({ holds: false })).toBe('broken');
		expect(checkState({ holds: true })).toBe('holds');
	});

	it('draws round ticks up to the maximum', () => {
		expect(ticks(20600)).toEqual([0, 10000, 20000, 30000]);
		expect(ticks(120983)).toEqual([0, 50000, 100000, 150000]);
		expect(ticks(1)).toEqual([0, 0.5, 1]);
		expect(ticks(0)).toEqual([0]);
	});

	it('keeps axis labels apart and gaps in years visible', () => {
		expect(labelEvery(10, 30)).toBe(4);
		expect(labelEvery(100, 30, 2)).toBe(2);
		expect(everyYear([2006, 2004])).toEqual([2004, 2005, 2006]);
	});

	it('formats shares as signed points', () => {
		const f = formatter('en');
		expect(f.pts(-0.0589)).toBe('-5.9');
		expect(f.pts(0.02)).toBe('+2');
		expect(f.pct(0.338)).toBe('33.8%');
		expect(f.p(0.0004)).toBe('< 0.001');
		expect(f.pIs(0.03)).toBe('= 0.03');
	});

	it('reads nothing from an older host', async () => {
		const old = async () => new Response(JSON.stringify({ schema: 1 }), { status: 200 });
		expect(await loadSnapshot(old as typeof fetch)).toBeNull();
	});

	it('falls back to the published snapshot without a live host', async () => {
		const published = JSON.stringify({ schema: 2, computed_at: '2026-10-10' });
		const site = async (url: string) =>
			url === '/files/eda/snapshot.json'
				? new Response(published, { status: 200 })
				: new Response('', { status: 404 });
		const found = await loadSnapshot(site as typeof fetch);
		expect(found?.live).toBe(false);
		expect(found?.snapshot.computed_at).toBe('2026-10-10');
	});

	it('prefers the live host', async () => {
		const host = async () => new Response(JSON.stringify({ schema: 2 }), { status: 200 });
		expect((await loadSnapshot(host as typeof fetch))?.live).toBe(true);
	});

	it('reads nothing when neither answers', async () => {
		const none = async () => new Response('', { status: 404 });
		expect(await loadSnapshot(none as typeof fetch)).toBeNull();
	});
});
