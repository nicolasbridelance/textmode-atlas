// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { expect, test, type Page } from '@playwright/test';

const ids = ['a', 'b', 'c'].map((value) => value.repeat(64));
const works = ids.map((sha256, index) => ({
	sha256,
	title: ['Tall work', 'Wide work', 'Square work'][index],
	file: `work-${index}.ANS`,
	path: `work-${index}.ANS`,
	author: index === 0 ? null : 'Artist',
	group: null,
	pack: index === 0 ? null : 'demo96',
	year: index === 0 ? null : 1996,
	cols: [40, 80, 40][index],
	rows: [80, 20, 20][index],
	level: '12'
}));

async function collection(page: Page): Promise<void> {
	const png = await page.evaluate(() => {
		const canvas = document.createElement('canvas');
		canvas.width = 80;
		canvas.height = 80;
		const context = canvas.getContext('2d')!;
		context.fillStyle = '#000';
		context.fillRect(0, 0, 80, 80);
		context.fillStyle = '#55ffff';
		context.fillRect(16, 16, 48, 48);
		return canvas.toDataURL().split(',')[1];
	});
	await page.route('**/files/**', (route) => {
		if (route.request().url().endsWith('/lists/days.json'))
			return route.fulfill({ contentType: 'application/json', body: JSON.stringify({ works }) });
		return route.fulfill({ contentType: 'image/png', body: Buffer.from(png, 'base64') });
	});
}

for (const locale of ['en', 'fr']) {
	for (const width of [1440, 390]) {
		test(`discovery variants share a selection and support undo (${locale}, ${width}px)`, async ({
			page
		}, info) => {
			await page.setViewportSize({ width, height: 900 });
			await collection(page);
			const prefix = locale === 'fr' ? '/fr' : '';
			const errors: string[] = [];
			page.on('pageerror', (error) => errors.push(error.message));
			await page.goto(`${prefix}/explore?view=pinterest`);
			await expect(page.locator('.pin')).toHaveCount(3);
			await page.locator('.pin button').first().click();
			await expect(page.locator('.pin button').first()).toHaveAttribute('aria-pressed', 'true');
			await page.locator('.views a').filter({ hasText: 'Instagram' }).click();
			await expect(page.locator('.post')).toHaveCount(3);
			await expect(page.locator('.post button').first()).toHaveAttribute('aria-pressed', 'true');
			await page.reload();
			await expect(page.locator('.post button').first()).toHaveAttribute('aria-pressed', 'true');
			await page.locator('.views a').filter({ hasText: 'Tinder' }).click();
			await expect(page.locator('.swipe-card h2')).toHaveText('Tall work');
			await page.locator('.pass').click();
			await expect(page.locator('.swipe-card h2')).toHaveText('Wide work');
			await page.locator('.keep-button').click();
			await expect(page.locator('.swipe-card h2')).toHaveText('Square work');
			await page.locator('.undo').click();
			await expect(page.locator('.swipe-card h2')).toHaveText('Wide work');
			await expect(page.locator('.selection-toggle button').last()).toContainText('1');
			await page.keyboard.press('ArrowRight');
			await expect(page.locator('.swipe-card h2')).toHaveText('Square work');
			await page.locator('.selection-toggle button').last().click();
			await expect(page.locator('.pin')).toHaveCount(2);
			await page.keyboard.press('ArrowRight'); // Hidden deck must not react.
			await page.locator('.selection-toggle button').first().click();
			await expect(page.locator('.swipe-card h2')).toHaveText('Square work');
			await page.locator('.pass').click();
			await expect(page.locator('.finished')).toBeVisible();
			await page.locator('.finished button').first().click();
			await expect(page.locator('.swipe-card h2')).toHaveText('Tall work');
			for (const view of ['pinterest', 'instagram', 'tinder']) {
				await page.goto(`${prefix}/explore?view=${view}`);
				await expect(page.locator(`[data-layout="${view}"]`)).toBeVisible();
				expect(
					await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)
				).toBe(true);
				await page.screenshot({ path: info.outputPath(`${view}-${locale}-${width}.png`) });
			}
			expect(errors).toEqual([]);
		});
	}
}

test('swipe gestures keep or pass without opening a work', async ({ page }) => {
	await collection(page);
	await page.goto('/explore?view=tinder');
	await expect(page.locator('.swipe-card h2')).toHaveText('Tall work');
	const surface = page.locator('.swipe-image');
	await surface.scrollIntoViewIfNeeded();
	const box = await surface.boundingBox();
	if (!box) throw new Error('No swipe surface');
	const x = box.x + box.width / 2,
		y = box.y + box.height / 2;
	await page.mouse.move(x, y);
	await page.mouse.down();
	await page.mouse.move(x + 110, y, { steps: 10 });
	await page.mouse.up();
	await expect(page.locator('.swipe-card h2')).toHaveText('Wide work');
	await expect(page).toHaveURL(/view=tinder/);
	await expect(page.locator('.selection-toggle button').last()).toContainText('1');
	await page.mouse.move(x, y);
	await page.mouse.down();
	await page.mouse.move(x - 110, y, { steps: 10 });
	await page.mouse.up();
	await expect(page.locator('.swipe-card h2')).toHaveText('Square work');
	await expect(page).toHaveURL(/view=tinder/);
});

test('a missing image has a readable fallback, and an empty selection can be exited', async ({
	page
}) => {
	await collection(page);
	await page.route(`**/works/${ids[0]}/conservation.png`, (route) =>
		route.fulfill({ status: 404 })
	);
	await page.goto('/fr/explore?view=pinterest');
	await expect(page.locator('.pin').first()).toContainText('Image indisponible');
	await page.locator('.selection-toggle button').last().click();
	await expect(page.locator('.empty-selection')).toBeVisible();
	await page.locator('.selection-toggle button').first().click();
	await expect(page.locator('.pin')).toHaveCount(3);
});
