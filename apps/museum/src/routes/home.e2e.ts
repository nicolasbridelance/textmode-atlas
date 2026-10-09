// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { expect, test } from '@playwright/test';

test('without published files, the entrance is the dedication, in both languages', async ({
	page
}) => {
	await page.route('**/files/**', (route) => route.fulfill({ status: 404 }));
	await page.goto('/');
	await expect(page.locator('html')).toHaveAttribute('lang', 'en');
	await expect(page.getByRole('heading', { level: 1 })).toHaveText(
		'Digital Museum of Character Arts'
	);

	await page.getByRole('link', { name: 'Français' }).click();
	await expect(page).toHaveURL(/\/fr\/?$/);
	await expect(page.locator('html')).toHaveAttribute('lang', 'fr');
	await expect(page.getByRole('heading', { level: 1 })).toHaveText(
		'Musée numérique des arts du caractère'
	);
});
