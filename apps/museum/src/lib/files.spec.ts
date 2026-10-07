// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { describe, expect, it, vi } from 'vitest';

vi.mock('$app/env/public', () => ({ FILES_BASE: '/files' }));

describe('fileUrl', () => {
	it('joins keys under the files base without doubling slashes', async () => {
		const { fileUrl } = await import('./files');
		expect(fileUrl('grids/abc.json')).toBe('/files/grids/abc.json');
		expect(fileUrl('/grids/abc.json', 'https://cdn.example')).toBe(
			'https://cdn.example/grids/abc.json'
		);
	});
});
