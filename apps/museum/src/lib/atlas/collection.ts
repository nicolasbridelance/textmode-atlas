// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { loadList } from '../work/visit';

export interface Specimen {
	sha256: string;
	path: string;
	archive: string | null;
	pack: string | null;
	year: number | null;
	format: string;
	content_kind: string | null;
	sauce_title: string | null;
	sauce_author: string | null;
	sauce_group: string | null;
	cols: number | null;
	rows: number | null;
	decoding: string;
	display?: string;
	hit: string | null;
}

export interface Facets {
	years: { year: number; works: number }[];
	formats: { format: string; works: number }[];
	archives: { archive: string; works: number }[];
	kinds: { kind: string; works: number }[];
	orders: string[];
	dataset: { version: string; extractors: Record<string, string>; works: number; measured: number };
}

export interface Collection {
	total: number;
	works: Specimen[];
}

export async function facets(): Promise<Facets | null> {
	try {
		const response = await fetch('/api/facets');
		return response.ok ? await response.json() : null;
	} catch {
		return null;
	}
}

export async function collection(query: URLSearchParams, live: boolean): Promise<Collection> {
	if (live) {
		const response = await fetch(`/api/works?${query}`);
		if (!response.ok) throw new Error('Collection unavailable');
		return response.json();
	}
	const list = await loadList('lists/days.json');
	const search = (query.get('q') ?? '').toLowerCase();
	const works = (list?.works ?? [])
		.filter((entry) =>
			[entry.title, entry.file, entry.author, entry.group].join(' ').toLowerCase().includes(search)
		)
		.map((entry) => ({
			...entry,
			path: entry.path || entry.file,
			archive: null,
			format: '',
			content_kind: null,
			sauce_title: entry.title,
			sauce_author: entry.author,
			sauce_group: entry.group,
			decoding: 'ok',
			display: 'files',
			hit: null
		}));
	return { total: works.length, works };
}
