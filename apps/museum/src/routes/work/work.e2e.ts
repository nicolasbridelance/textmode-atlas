// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { expect, test } from '@playwright/test';

test('a work the museum does not hold is said to be missing, in both languages', async ({
	page
}) => {
	await page.goto('/work?w=not-a-work');
	await expect(page.getByText('This work is not in the museum, or no longer.')).toBeVisible();
	await page.goto('/fr/work?w=' + '0'.repeat(64));
	await expect(page.getByText("Cette œuvre n'est pas au musée, ou ne l'est plus.")).toBeVisible();
});
