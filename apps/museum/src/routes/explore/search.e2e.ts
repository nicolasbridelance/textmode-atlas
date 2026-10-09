// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { expect, test, type Page } from '@playwright/test';

const entries = ['a', 'b', 'c', 'd', 'e'].map((id, index) => ({
	sha256: id.repeat(64),
	title: `Work ${index + 1}`,
	file: `work-${index + 1}.ANS`,
	path: `work-${index + 1}.ANS`,
	author: index === 0 ? null : 'Artist',
	group: index === 0 ? null : 'Fire',
	pack: null,
	year: index === 0 ? null : 1996,
	cols: 80,
	rows: 25,
	level: '12'
}));

async function files(page: Page): Promise<void> {
	const image = await page.evaluate(() => {
		const canvas = document.createElement('canvas');
		canvas.width = 80;
		canvas.height = 80;
		const ctx = canvas.getContext('2d')!;
		ctx.fillStyle = '#55ffff';
		ctx.fillRect(0, 0, 80, 80);
		return canvas.toDataURL().split(',')[1];
	});
	await page.route('**/files/**', (route) =>
		route.request().url().endsWith('days.json')
			? route.fulfill({
					contentType: 'application/json',
					body: JSON.stringify({ works: entries.slice(0, 3) })
				})
			: route.fulfill({ contentType: 'image/png', body: Buffer.from(image, 'base64') })
	);
	await page.route('**/image/**', (route) =>
		route.fulfill({ contentType: 'image/png', body: Buffer.from(image, 'base64') })
	);
	await page.route('**/api/facets', (route) =>
		route.fulfill({
			contentType: 'application/json',
			body: JSON.stringify({
				years: [{ year: 1996, works: 4 }],
				archives: [{ archive: '16colo', works: 5 }],
				formats: [{ format: 'ansi', works: 5 }],
				kinds: [{ kind: 'coloured_blocks', works: 5 }],
				dataset: { works: 5, version: '5' }
			})
		})
	);
	await page.route('**/api/works?*', (route) => {
		const query = new URL(route.request().url()).searchParams;
		const filtered = query.get('year') ? entries.slice(1) : entries;
		const offset = Number(query.get('offset') ?? 0);
		return route.fulfill({
			contentType: 'application/json',
			body: JSON.stringify({
				total: filtered.length,
				works: filtered.slice(offset, offset + 3).map((entry) => ({
					...entry,
					sauce_title: entry.title,
					sauce_author: entry.author,
					sauce_group: entry.group,
					decoding: 'ok',
					display: 'files'
				}))
			})
		});
	});
}

for (const locale of ['en', 'fr']) {
	test(`public search, metadata filters, reset and selection clearing (${locale})`, async ({
		page
	}) => {
		await page.setViewportSize({ width: 390, height: 844 });
		await files(page);
		const prefix = locale === 'fr' ? '/fr' : '';
		await page.goto(`${prefix}/explore?view=pinterest&source=public`);
		await expect(page.locator('.pin')).toHaveCount(3);
		await page.locator('.pin button').first().click();
		await page.locator('input[name=q]').fill('Artist');
		await page.locator('.search-submit').click();
		await expect(page.locator('.pin')).toHaveCount(2);
		await expect(page).toHaveURL(/q=Artist/);
		await page.locator('.views a').filter({ hasText: 'Instagram' }).click();
		await expect(page.locator('.post')).toHaveCount(2);
		await expect(page.locator('input[name=q]')).toHaveValue('Artist');
		await page.locator('.reset').click();
		await expect(page.locator('.post')).toHaveCount(3);
		await page.locator('.catalogue-controls summary').click();
		await page.locator('select[name=year]').selectOption('__unknown__');
		await expect(page.locator('.post')).toHaveCount(1);
		await page.locator('.reset').click();
		await expect(page.locator('.post button').first()).toHaveAttribute('aria-pressed', 'true');
		await page.locator('.selection-toggle button').last().click();
		await expect(page.locator('.post')).toHaveCount(1);
		await page.locator('.clear-selection').click();
		await expect(page.locator('.empty-selection')).toBeVisible();
		await page.locator('.selection-cleared button').click();
		await expect(page.locator('.post')).toHaveCount(1);
		expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
			true
		);
	});
}

test('global corpus pagination and filters survive layout, reload and locale changes', async ({
	page
}) => {
	await files(page);
	await page.goto('/explore?view=pinterest');
	await expect(page.locator('.pin')).toHaveCount(3);
	await expect(page.locator('.count')).toContainText('5 results');
	await page.locator('.more').click();
	await expect(page.locator('.pin')).toHaveCount(5);
	await page.locator('.catalogue-controls summary').click();
	await page.locator('select[name=year]').selectOption('1996');
	await expect(page).toHaveURL(/year=1996/);
	await expect(page.locator('.count')).toContainText('4 results');
	await page.locator('.views a').filter({ hasText: 'Instagram' }).click();
	await expect(page.locator('.post')).toHaveCount(3);
	await expect(page.locator('select[name=year]')).toHaveValue('1996');
	await page.locator('.locales a[lang=fr]').click();
	await expect(page.locator('.count')).toContainText('4 résultats');
	await expect(page.locator('select[name=year]')).toHaveValue('1996');
	await page.reload();
	await expect(page.locator('select[name=year]')).toHaveValue('1996');
	await expect(page.locator('.post-image').first()).toHaveAttribute('href', /^\/fr\/work\?w=/);
	await page.locator('.reset').click();
	await expect(page.locator('.count')).toContainText('5 résultats');
	await expect(page).toHaveURL(/source=corpus/);
});

test('the deck continues past the first corpus page, and reset restarts it', async ({ page }) => {
	await files(page);
	await page.goto('/explore?view=tinder&source=corpus');
	await expect(page.locator('.swipe-card h2')).toHaveText('Work 1');
	for (let i = 0; i < 3; i++) await page.locator('.pass').click();
	await expect(page.locator('.finished')).toContainText('Keep exploring.');
	await page.locator('.finished button').first().click();
	await expect(page.locator('.swipe-card h2')).toHaveText('Work 4');
	await page.locator('.reset').click();
	await expect(page.locator('.swipe-card h2')).toHaveText('Work 1');
});

test('a failed corpus request is visible and reset retries it', async ({ page }) => {
	await files(page);
	let fail = true;
	await page.route('**/api/works?*', (route) => {
		if (fail) return route.fulfill({ status: 503 });
		return route.fallback();
	});
	await page.goto('/explore?view=pinterest&source=corpus');
	await expect(page.getByRole('alert')).toBeVisible();
	fail = false;
	await page.locator('.reset').click();
	await expect(page.locator('.pin')).toHaveCount(3);
});

test('chance: reshuffle keeps the filters, and a draw opens one work', async ({ page }) => {
	await files(page);
	let drawn = '';
	await page.route('**/api/surprise?*', (route) => {
		const query = new URL(route.request().url()).searchParams;
		drawn = `${query.get('year')}:${query.get('seed')}`;
		return route.fulfill({
			contentType: 'application/json',
			body: JSON.stringify({ sha256: 'c'.repeat(64), seed: query.get('seed') })
		});
	});
	await page.goto('/explore?view=pinterest&year=1996');
	await expect(page.locator('.pin')).toHaveCount(3);
	await page.locator('.chance button').first().click();
	await expect(page).toHaveURL(/seed=[a-z2-9]{6}/);
	await expect(page).toHaveURL(/year=1996/);
	await expect(page.locator('.filter-chips button')).toHaveCount(1); // the seed is no filter
	await page.locator('.chance button').last().click();
	await expect(page).toHaveURL(/\/work\?w=c{64}/);
	expect(drawn).toMatch(/^1996:[a-z2-9]{6}$/);
});

test('chance in the public collection draws among the listed works', async ({ page }) => {
	await files(page);
	await page.goto('/explore?view=pinterest&source=public');
	await expect(page.locator('.pin')).toHaveCount(3);
	await page.locator('.chance button').last().click();
	await expect(page).toHaveURL(/\/work\?w=(a{64}|b{64}|c{64})/);
});
