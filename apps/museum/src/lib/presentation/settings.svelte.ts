// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
export const STYLES = [
	'original',
	'paper',
	'density',
	'reconstruction',
	'pointillism',
	'halftone',
	'kuwahara',
	'impressionism',
	'graffiti'
] as const;
export const SAMPLING = ['pixels', 'smooth', 'gaussian'] as const;
export const FRAMES = ['none', 'line', 'mat'] as const;
export const FRAME_PADDING = { none: 0, line: 1, mat: 24 } as const;
export const FRAME_COLOUR = { none: '#000000', line: '#808080', mat: '#f4efdf' } as const;
export const THEMES = ['dark', 'light', 'system'] as const;
export type ArtStyle = (typeof STYLES)[number];
export type Sampling = (typeof SAMPLING)[number];

export const preferences = $state({
	theme: 'dark' as (typeof THEMES)[number],
	background: '#000000',
	frame: 'none' as (typeof FRAMES)[number],
	style: 'original' as ArtStyle,
	sampling: 'pixels' as Sampling,
	size: 6,
	strength: 100,
	paper: 'dark' as 'dark' | 'light',
	preparation: 'coverage' as 'pixels' | 'coverage'
});

export const museumContext = $state({ workId: null as string | null });

const KEY = 'textmode-presentation-v1';

const LIMITS = { minSize: 3, maxSize: 12, maxStrength: 100 };
function validRange(value: number, min: number, max: number): boolean {
	return Number.isFinite(value) && value >= min && value <= max;
}
function applyEffectPreferences(value: typeof preferences): void {
	if (validRange(value.size, LIMITS.minSize, LIMITS.maxSize))
		preferences.size = Math.round(value.size);
	if (validRange(value.strength, 0, LIMITS.maxStrength)) preferences.strength = value.strength;
	if (value.paper === 'dark' || value.paper === 'light') preferences.paper = value.paper;
	if (value.preparation === 'pixels' || value.preparation === 'coverage')
		preferences.preparation = value.preparation;
}

function applyPreferences(value: typeof preferences): void {
	if (THEMES.includes(value.theme)) preferences.theme = value.theme;
	if (FRAMES.includes(value.frame)) preferences.frame = value.frame;
	if (STYLES.includes(value.style)) preferences.style = value.style;
	if (SAMPLING.includes(value.sampling)) preferences.sampling = value.sampling;
	if (typeof value.background === 'string' && /^#[0-9a-f]{6}$/i.test(value.background)) {
		preferences.background = value.background;
	}
}

export function restorePreferences(): void {
	try {
		const value = JSON.parse(localStorage.getItem(KEY) ?? '{}');
		applyPreferences(value);
		applyEffectPreferences(value);
	} catch {
		// Storage may be unavailable; the controls still work for this visit.
	}
}

export function savePreferences(value: typeof preferences): void {
	try {
		localStorage.setItem(KEY, JSON.stringify(value));
	} catch {
		// Private browsing can disallow storage.
	}
}
