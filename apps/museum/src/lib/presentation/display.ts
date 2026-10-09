// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
// How the collection is shown: one gallery, a few presets, every setting in the URL.

export const LAYOUTS = ['wall', 'grid', 'feed', 'deck'] as const;
export type Layout = (typeof LAYOUTS)[number];
export const FITS = ['whole', 'crop'] as const;
export const CAPTIONS = ['none', 'short', 'full'] as const;
export const PAPERS = ['light', 'dark', 'museum'] as const;
export const MAX_COLUMNS = 6;
export const AUTO = 0;

export interface Display {
	layout: Layout;
	/** Columns of the wall or the grid; `AUTO` follows the screen width. */
	cols: number;
	fit: (typeof FITS)[number];
	caption: (typeof CAPTIONS)[number];
	paper: (typeof PAPERS)[number];
}
type Settings = Omit<Display, 'layout'>;

/** What each way of looking starts with; any setting can then be changed. */
export const PRESETS: Record<Layout, Settings> = {
	wall: { cols: AUTO, fit: 'whole', caption: 'short', paper: 'light' },
	grid: { cols: AUTO, fit: 'crop', caption: 'short', paper: 'museum' },
	feed: { cols: 1, fit: 'whole', caption: 'full', paper: 'light' },
	deck: { cols: 1, fit: 'whole', caption: 'full', paper: 'dark' }
};

/** Addresses of the former separate views keep working. */
const FORMER_VIEWS: Record<string, Layout> = {
	pinterest: 'wall',
	instagram: 'feed',
	tinder: 'deck',
	grid: 'grid',
	relations: 'wall'
};

function oneOf<T extends string>(values: readonly T[], value: string | null): T | null {
	return values.includes(value as T) ? (value as T) : null;
}
function columns(value: string | null): number | null {
	const count = Number(value);
	return value !== null && Number.isInteger(count) && count >= AUTO && count <= MAX_COLUMNS
		? count
		: null;
}

function layoutOf(get: (key: string) => string | null): Layout {
	return oneOf(LAYOUTS, get('layout')) ?? FORMER_VIEWS[get('view') ?? ''] ?? 'wall';
}

export function readDisplay(params: Pick<URLSearchParams, 'get'> | null): Display {
	const get = (key: string) => params?.get(key) ?? null;
	const layout = layoutOf(get);
	const preset = PRESETS[layout];
	return {
		layout,
		cols: columns(get('cols')) ?? preset.cols,
		fit: oneOf(FITS, get('fit')) ?? preset.fit,
		caption: oneOf(CAPTIONS, get('caption')) ?? preset.caption,
		paper: oneOf(PAPERS, get('paper')) ?? preset.paper
	};
}

/** URL values for a display: only what differs from its preset, so addresses stay short. */
export function displayQuery(display: Display): Record<string, string> {
	const preset = PRESETS[display.layout];
	const differs = (key: keyof Settings) => display[key] !== preset[key];
	return {
		view: '',
		layout: display.layout,
		cols: differs('cols') ? String(display.cols) : '',
		fit: differs('fit') ? display.fit : '',
		caption: differs('caption') ? display.caption : '',
		paper: differs('paper') ? display.paper : ''
	};
}
