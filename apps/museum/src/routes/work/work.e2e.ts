// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { expect, type Page, test } from '@playwright/test';

const A = 'a'.repeat(64);
const B = 'b'.repeat(64);

/** A 2×1 grid: a white `A`, then a red full block (grid.tmg, ADR 0022). */
function grid(): Buffer {
	const buffer = Buffer.alloc(16 + 2 * 8);
	buffer.write('TMG1', 0, 'latin1');
	buffer.writeUInt8(1, 4);
	buffer.writeUInt16LE(2, 6);
	buffer.writeUInt16LE(1, 8);
	buffer.writeUInt16LE(0x41, 16);
	buffer.writeUInt8(15, 18);
	buffer.writeUInt32LE(0, 20);
	buffer.writeUInt16LE(0xdb, 24);
	buffer.writeUInt8(4, 26);
	buffer.writeUInt32LE(9, 28);
	return buffer;
}

function record(sha256: string, title: string): object {
	return {
		schema: 2,
		sha256,
		title,
		file: `${title}.ANS`,
		year: 1996,
		format: 'ansi',
		credit: {
			author: 'tester',
			group: 'golden',
			pack: 'demo96',
			archive: '16colo',
			url: 'https://16colo.rs/pack/demo96/'
		},
		audience: { level: '12', descriptors: [], notices: [], reviewed: false },
		shown: 'files',
		grid: { cols: 2, rows: 1, ice: false },
		files: { 'grid.tmg': '0', 'conservation.png': '0' },
		provenance: [],
		withdraw: 'https://example.org/withdraw',
		text: [{ row: 0, text: 'A' }],
		lists: { pack: 'lists/packs/16colo-demo96.json', author: null, year: null }
	};
}

function entry(sha256: string, title: string): object {
	return {
		sha256,
		title,
		file: `${title}.ANS`,
		path: `${title}.ANS`,
		author: 'tester',
		group: 'golden',
		pack: 'demo96',
		year: 1996,
		cols: 2,
		rows: 1,
		level: '12'
	};
}

/** The public bucket as `tm export` and `tm lists` would fill it, for two works of one pack. */
async function serveFiles(page: Page): Promise<void> {
	const thumbnail = await page.evaluate(() => {
		const canvas = document.createElement('canvas');
		canvas.width = 16;
		canvas.height = 16;
		const context = canvas.getContext('2d')!;
		context.fillStyle = '#aa0000';
		context.fillRect(0, 0, 16, 16);
		return canvas.toDataURL().split(',')[1];
	});
	const json = (value: object) => ({
		contentType: 'application/json',
		body: JSON.stringify(value)
	});
	const files: Record<string, () => object> = {
		[`works/${A}/conservation.png`]: () => ({
			contentType: 'image/png',
			body: Buffer.from(thumbnail, 'base64')
		}),
		[`works/${B}/conservation.png`]: () => ({
			contentType: 'image/png',
			body: Buffer.from(thumbnail, 'base64')
		}),
		[`works/${A}/record.json`]: () => json(record(A, 'first')),
		[`works/${B}/record.json`]: () => json(record(B, 'second')),
		[`works/${A}/grid.tmg`]: () => ({ body: grid() }),
		[`works/${B}/grid.tmg`]: () => ({ body: grid() }),
		'lists/packs/16colo-demo96.json': () =>
			json({ pack: 'demo96', works: [entry(A, 'first'), entry(B, 'second')] }),
		'lists/days.json': () => json({ works: [entry(A, 'first')] })
	};
	await page.route('**/files/**', (route) => {
		const key = new URL(route.request().url()).pathname.replace(/^\/files\//, '');
		const found = files[key];
		return found ? route.fulfill(found()) : route.fulfill({ status: 404 });
	});
}

test('a work the museum does not hold is said to be missing, in both languages', async ({
	page
}) => {
	await page.goto('/work?w=not-a-work');
	await expect(page.getByText('This work is not in the museum, or no longer.')).toBeVisible();
	await page.goto('/fr/work?w=' + '0'.repeat(64));
	await expect(page.getByText("Cette œuvre n'est pas au musée, ou ne l'est plus.")).toBeVisible();
});

test('a work shows its label, its words, and leads to the next in its pack', async ({ page }) => {
	await serveFiles(page);
	await page.goto(`/work?w=${A}`);
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('first');
	await expect(
		page.getByRole('region', { name: 'first' }).getByText('tester / golden')
	).toBeVisible();
	await page.getByText('The words of the work').click();
	await expect(page.getByRole('listitem').filter({ hasText: /^A$/ })).toBeVisible();
	await expect(page.getByRole('link', { name: /Next in the pack/ })).toBeVisible();
	await page.keyboard.press('ArrowRight');
	await expect(page).toHaveURL(new RegExp(`w=${B}`));
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('second');
});

test('zoom goes down to the cell, and the inspector says how it is made', async ({ page }) => {
	await serveFiles(page);
	await page.goto(`/fr/work?w=${A}`);
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('first');
	await page.keyboard.press(' ');
	for (let i = 0; i < 4; i++) await page.keyboard.press('+'); // 2× fitted, then 3, 4, 6, 8
	await expect(page.getByRole('group', { name: 'Zoom' })).toContainText('8×');
	const canvas = page.locator('canvas');
	const box = await canvas.boundingBox();
	if (!box) throw new Error('no canvas');
	await page.mouse.move(box.x + box.width * 0.75, box.y + box.height / 2);
	await expect(page.getByText('Glyphe █ (0xDB)')).toBeVisible();
	await expect(page.getByText(/octet 9/)).toBeVisible();
});

test('the entrance opens on the work of the day, and the help is one key away', async ({
	page
}) => {
	await serveFiles(page);
	await page.goto('/');
	await expect(page.getByText(/Work of the day/)).toBeVisible();
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('first');
	await page.keyboard.press('?');
	await expect(page.getByRole('dialog', { name: 'Keys' })).toBeVisible();
	await page.keyboard.press('Escape');
	await expect(page.getByRole('dialog')).toBeHidden();
});

for (const [locale, width] of [
	['en', 1280],
	['en', 390],
	['fr', 1280],
	['fr', 390]
] as const) {
	test(`presentation settings, PNG recipe and shared exploration (${locale}, ${width}px)`, async ({
		page
	}, testInfo) => {
		await page.setViewportSize({ width, height: 844 });
		await serveFiles(page);
		const prefix = locale === 'fr' ? '/fr' : '';
		await page.goto(`${prefix}/work?w=${A}`);
		await expect(page.getByRole('heading', { level: 1 })).toHaveText('first');
		await page.locator('.theme select').selectOption('light');
		await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
		await page.locator('.workshop summary').click();
		const selects = page.locator('.workshop select[data-control]');
		await selects.nth(0).selectOption('mat');
		await selects.nth(1).selectOption('density');
		await expect(page.locator('.badge')).toBeVisible();
		await expect
			.poll(() =>
				page
					.locator('canvas')
					.evaluate(
						(canvas: HTMLCanvasElement) => canvas.getContext('2d')!.getImageData(8, 0, 1, 1).data[0]
					)
			)
			.toBe(0);
		await selects.nth(2).selectOption('gaussian');
		await selects.nth(3).selectOption('2');
		const downloads: import('@playwright/test').Download[] = [];
		page.on('download', (download) => downloads.push(download));
		await page.locator('.workshop button').first().click();
		await expect.poll(() => downloads.length).toBe(2);
		const { readFile } = await import('node:fs/promises');
		const recipeDownload = downloads.find((download) =>
			download.suggestedFilename().endsWith('.json')
		)!;
		const recipe = JSON.parse(await readFile((await recipeDownload.path())!, 'utf8'));
		expect(recipe).toMatchObject({
			level: 'interpretation',
			source_sha256: A,
			width: 128,
			height: 128,
			settings: { style: 'density', sampling: 'gaussian', scale: 2 }
		});
		expect(recipe.font_sha256).toMatch(/^[0-9a-f]{64}$/);
		const pngDownload = downloads.find((download) =>
			download.suggestedFilename().endsWith('.png')
		)!;
		const png = await readFile((await pngDownload.path())!);
		expect(png.readUInt32BE(16)).toBe(128);
		expect(png.readUInt32BE(20)).toBe(128);
		await page.screenshot({ path: testInfo.outputPath(`workshop-${locale}.png`), fullPage: true });
		await page.reload();
		await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
		await page.locator('.workshop summary').click();
		await expect(selects.nth(1)).toHaveValue('density');
		await page.locator('.views a').nth(1).click();
		await expect(page).toHaveURL(new RegExp(`/explore\\?w=${A}`));
		await page.locator('.toolbar select').first().selectOption('pack');
		await expect(page.locator('.card')).toHaveCount(2);
		await page.goto(`${locale === 'fr' ? '/fr' : ''}/explore?view=relations&w=${A}&scope=pack`);
		await expect(page.locator('.card')).toHaveCount(2); // the former view's address still works
		await page.screenshot({
			path: testInfo.outputPath(`constellation-${locale}.png`),
			fullPage: true
		});
		await page.locator('.card .title').last().click();
		await expect(page.getByRole('heading', { level: 1 })).toHaveText('second');
	});
}

/** Project-made geometry for visual review, with no corpus artwork embedded in Git. */
function geometricGrid(): Buffer {
	const cols = 40;
	const rows = 24;
	const buffer = Buffer.alloc(16 + cols * rows * 8);
	buffer.write('TMG1', 0, 'latin1');
	buffer.writeUInt8(1, 4);
	buffer.writeUInt16LE(cols, 6);
	buffer.writeUInt16LE(rows, 8);
	for (let row = 0; row < rows; row++) {
		for (let col = 0; col < cols; col++) {
			const at = 16 + (row * cols + col) * 8;
			const circle = (col - 20) ** 2 + (row - 11) ** 2 < 80;
			const glyph = circle ? 0xdb : [0xb0, 0xb1, 0xb2][Math.floor(col / 5) % 3];
			buffer.writeUInt16LE(glyph, at);
			buffer.writeUInt8(circle ? 14 : row > col / 3 + 8 ? 11 : 9, at + 2);
		}
	}
	return buffer;
}

test('visual review of six scripted looks on project-made geometry', async ({ page }, testInfo) => {
	await serveFiles(page);
	await page.route(`**/works/${A}/record.json`, (route) =>
		route.fulfill({
			contentType: 'application/json',
			body: JSON.stringify({ ...record(A, 'first'), grid: { cols: 40, rows: 24, ice: false } })
		})
	);
	await page.route(`**/works/${A}/grid.tmg`, (route) => route.fulfill({ body: geometricGrid() }));
	await page.goto(`/work?w=${A}`);
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('first');
	await page.keyboard.press(' ');
	await page.locator('.workshop summary').click();
	const looks: { style: string; url: string }[] = [];
	for (const style of [
		'original',
		'paper',
		'density',
		'pointillism',
		'impressionism',
		'graffiti'
	]) {
		await page.locator('.workshop select[data-control=style]').selectOption(style);
		await page.waitForTimeout(50);
		looks.push({
			style,
			url: await page.locator('canvas').evaluate((canvas: HTMLCanvasElement) => canvas.toDataURL())
		});
	}
	expect(new Set(looks.map((look) => look.url)).size).toBe(6);
	await page.evaluate((looks) => {
		const sheet = document.createElement('div');
		sheet.style.cssText =
			'position:absolute;inset:0;background:#eee;color:#111;padding:20px;display:grid;grid-template-columns:repeat(3,320px);gap:20px;z-index:1000;width:1020px';
		for (const look of looks) {
			const figure = document.createElement('figure');
			figure.style.margin = '0';
			const caption = document.createElement('figcaption');
			caption.textContent = look.style;
			const image = document.createElement('img');
			image.src = look.url;
			image.style.cssText = 'width:320px;image-rendering:pixelated';
			figure.append(caption, image);
			sheet.append(figure);
		}
		document.body.append(sheet);
	}, looks);
	await page.setViewportSize({ width: 1060, height: 850 });
	await page.screenshot({ path: testInfo.outputPath('scripted-looks.png') });
});

test('comparison reveals the complete original and effect controls reach the PNG recipe', async ({
	page
}) => {
	await serveFiles(page);
	await page.goto(`/work?w=${A}`);
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('first');
	await page.locator('.workshop summary').click();
	await page.locator('[data-control=style]').selectOption('pointillism');
	await page.getByLabel('Compare with the VGA rendering').check();
	await expect(page.locator('.original canvas')).toBeVisible();
	await expect
		.poll(() =>
			page
				.locator('.original canvas')
				.evaluate(
					(canvas: HTMLCanvasElement) => canvas.getContext('2d')!.getImageData(8, 0, 1, 1).data[0]
				)
		)
		.toBe(170);
	await page.getByLabel('Comparison divider').fill('75');
	await expect(page.locator('.original')).toHaveCSS('width', '24px');
	await page.locator('.effect-settings input').first().fill('10');
	await page.locator('.effect-settings input').nth(1).fill('65');
	await page.locator('.effect-settings select').first().selectOption('pixels');
	await page.locator('.effect-settings select').last().selectOption('light');
	const downloads: import('@playwright/test').Download[] = [];
	page.on('download', (value) => downloads.push(value));
	await page.locator('.workshop button').first().click();
	await expect.poll(() => downloads.length).toBe(2);
	const { readFile } = await import('node:fs/promises');
	const download = downloads.find((value) => value.suggestedFilename().endsWith('.json'))!;
	const recipe = JSON.parse(await readFile((await download.path())!, 'utf8'));
	expect(recipe).toMatchObject({
		asserted_by: 'algo:museum-presentation-v2',
		settings: { size: 10, strength: 65, preparation: 'pixels', paper: 'light' }
	});
	await page.locator('.workshop button').last().click();
	await expect(page.locator('[data-control=style]')).toHaveValue('original');
});
