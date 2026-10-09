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
	const json = (value: object) => ({
		contentType: 'application/json',
		body: JSON.stringify(value)
	});
	const files: Record<string, () => object> = {
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
