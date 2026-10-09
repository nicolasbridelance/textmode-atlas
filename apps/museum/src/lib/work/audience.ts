// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// The audience grid, read from the one source the pipeline writes (`corpus/ratings/grid.json`,
// ADR 0020), with its badges. The site shows a work's level; it never filters by it.
import grid from '../../../../../corpus/ratings/grid.json';

const badges = import.meta.glob<string>('../../../../../corpus/ratings/badges/*.svg', {
	query: '?url',
	import: 'default',
	eager: true
});

type Localized = Record<string, string>;

function badge(name: string): string {
	return badges[`../../../../../corpus/ratings/badges/${name}.svg`];
}

function localized(text: Localized, locale: string): string {
	return text[locale] ?? text.en;
}

export function levelBadge(code: string, locale: string): { src: string; label: string } {
	const level = grid.levels.find((l) => l.code === code);
	return { src: badge(`level-${code}`), label: level ? localized(level.label, locale) : code };
}

export function descriptorBadge(code: string, locale: string): { src: string; label: string } {
	const item = [...grid.descriptors, ...grid.notices].find((d) => d.code === code);
	return { src: badge(code), label: item ? localized(item.label, locale) : code };
}

export const GRID_PAGE: Localized = {
	en: 'https://github.com/nicolasbridelance/textmode-atlas/blob/main/docs/audience-grid.md',
	fr: 'https://github.com/nicolasbridelance/textmode-atlas/blob/main/docs/audience-grid.fr.md'
};
