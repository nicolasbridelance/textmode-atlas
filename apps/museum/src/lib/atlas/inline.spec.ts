// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { describe, expect, it } from 'vitest';
import { inline } from './inline';

describe('inline Markdown', () => {
	it('reads code, bold and italics', () => {
		expect(inline('a `b` **c** *d* e')).toEqual([
			{ kind: 'text', text: 'a ' },
			{ kind: 'code', text: 'b' },
			{ kind: 'text', text: ' ' },
			{ kind: 'strong', text: 'c' },
			{ kind: 'text', text: ' ' },
			{ kind: 'em', text: 'd' },
			{ kind: 'text', text: ' e' }
		]);
	});

	it('links only to the web; a repository path keeps its text', () => {
		expect(inline('[site](https://16colo.rs) and [note](../works.md)')).toEqual([
			{ kind: 'link', text: 'site', href: 'https://16colo.rs' },
			{ kind: 'text', text: ' and ' },
			{ kind: 'text', text: 'note' }
		]);
	});

	it('leaves a lone star and plain text alone', () => {
		expect(inline('3 * 4 = 12')).toEqual([{ kind: 'text', text: '3 * 4 = 12' }]);
	});
});
