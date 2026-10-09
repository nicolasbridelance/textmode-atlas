// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { fileUrl } from '../files';
import type { Entry } from '../work/visit';

export const FILTER_KEYS = [
	'q',
	'words',
	'year',
	'author',
	'group',
	'archive',
	'format',
	'kind',
	'order'
] as const;
export type BrowseFilters = Record<(typeof FILTER_KEYS)[number], string>;
export const UNKNOWN = '__unknown__';
export const emptyFilters = (): BrowseFilters => ({
	q: '',
	words: '',
	year: '',
	author: '',
	group: '',
	archive: '',
	format: '',
	kind: '',
	order: ''
});

export function readFilters(params: Pick<URLSearchParams, 'get'> | null): BrowseFilters {
	return Object.fromEntries(
		FILTER_KEYS.map((key) => [key, params?.get(key) ?? ''])
	) as BrowseFilters;
}
function folded(value: string): string {
	return value.normalize('NFKD').replace(/\p{M}/gu, '').toLowerCase();
}
function exact(actual: string | number | null, wanted: string): boolean {
	if (!wanted) return true;
	return wanted === UNKNOWN ? !actual : String(actual) === wanted;
}
function matches(entry: Entry, filters: BrowseFilters): boolean {
	const text = folded(
		[entry.title, entry.file, entry.path, entry.author, entry.group, entry.pack]
			.filter(Boolean)
			.join(' ')
	);
	const terms = folded(filters.q.trim()).split(/\s+/).filter(Boolean);
	return (
		terms.every((term) => text.includes(term)) &&
		exact(entry.year, filters.year) &&
		exact(entry.author, filters.author) &&
		exact(entry.group, filters.group)
	);
}
export function filterEntries(entries: Entry[], filters: BrowseFilters): Entry[] {
	const filtered = entries.filter((entry) => matches(entry, filters));
	if (filters.order === 'title')
		filtered.sort((a, b) => (a.title || a.file).localeCompare(b.title || b.file));
	if (filters.order === 'year')
		filtered.sort((a, b) => (a.year ?? Infinity) - (b.year ?? Infinity));
	if (filters.order === 'tall') filtered.sort((a, b) => b.rows - a.rows);
	if (filters.order === 'wide') filtered.sort((a, b) => b.cols - a.cols);
	return filtered;
}
export function valuesOf(entries: Entry[], key: 'year' | 'author' | 'group'): string[] {
	return [
		...new Set(entries.map((entry) => (entry[key] === null ? UNKNOWN : String(entry[key]))))
	].sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
}
export function previewUrl(entry: Entry): string | null {
	return entry.preview === undefined
		? fileUrl(`works/${entry.sha256}/conservation.png`)
		: entry.preview;
}

export interface ResearchFacets {
	years: { year: number; works: number }[];
	formats: { format: string; works: number }[];
	archives: { archive: string; works: number }[];
	kinds: { kind: string; works: number }[];
	dataset: { version: string; works: number };
}
interface ResearchEntry {
	sha256: string;
	sauce_title: string | null;
	sauce_author: string | null;
	sauce_group: string | null;
	path: string;
	pack: string | null;
	year: number | null;
	cols: number | null;
	rows: number | null;
	decoding: string;
	display: string;
}
export function researchQuery(filters: BrowseFilters): string {
	const params = new URLSearchParams();
	for (const key of ['q', 'words', 'year', 'archive', 'format', 'kind', 'order'] as const) {
		if (filters[key]) params.set(key, filters[key]);
	}
	return params.toString();
}
export async function researchPage(
	base: string,
	query: string,
	offset: number,
	signal?: AbortSignal
): Promise<{ total: number; works: Entry[] }> {
	const DEFAULT_COLS = 80;
	const DEFAULT_ROWS = 25;
	const response = await fetch(`${base}/api/works?${query}&offset=${offset}`, { signal });
	if (!response.ok) throw new Error(`Corpus ${response.status}`);
	const page = (await response.json()) as { total: number; works: ResearchEntry[] };
	return {
		total: page.total,
		works: page.works.map((entry) => ({
			sha256: entry.sha256,
			title: entry.sauce_title,
			file: entry.path.split('/').at(-1) || entry.path,
			path: entry.path,
			author: entry.sauce_author,
			group: entry.sauce_group,
			pack: entry.pack,
			year: entry.year,
			cols: entry.cols ?? DEFAULT_COLS,
			rows: entry.rows ?? DEFAULT_ROWS,
			level: '',
			preview:
				entry.display === 'files' && entry.decoding === 'ok'
					? `${base}/image/full/${entry.sha256}`
					: null
		}))
	};
}
