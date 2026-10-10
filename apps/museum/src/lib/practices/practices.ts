// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// The registry of practices (ADR 0031), read from corpus/practices.json, which `tm corpus
// practices --write` derives from corpus/practices.yaml and the acquisitions manifest.
import registry from '../../../../../corpus/practices.json';

const HOLDINGS = ['file', 'excerpt', 'capture', 'reproduction', 'record'] as const;
export type Holding = (typeof HOLDINGS)[number];
type Localized = Record<string, string>;

export interface Family {
	code: string;
	label: Localized;
}

export interface Practice {
	code: string;
	label: Localized;
	family: string;
	holding: Holding[];
	representative: { sha256: string; path: string } | null;
	acquired: Acquired | null;
}

/** A representative the museum acquired one by one, and the basis on which it holds it. */
export interface Acquired {
	title: string;
	why: Localized;
	url: string;
	basis: 'scene' | 'license' | 'public-domain' | 'excerpt';
	license: string | null;
	credit: string | null;
}

export const families: Family[] = registry.families;
export const practices = registry.practices as Practice[];

export const inFamily = (family: string): Practice[] =>
	practices.filter((p) => p.family === family);

export const isHeld = (practice: Practice): boolean => practice.representative !== null;

/** Text in the visitor's locale, else English: every text of the registry has both. */
export const say = (text: Localized, locale: string): string => text[locale] ?? text.en;

/** Where a representative from the holdings sits: the archive and the path, from `source:path`. */
export function placeOf(path: string): { source: string; path: string } {
	const colon = path.indexOf(':');
	return { source: path.slice(0, colon), path: path.slice(colon + 1) };
}
