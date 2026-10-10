// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// The registry of practices (ADR 0031), read from corpus/practices.json, which `tm corpus
// practices --write` derives from corpus/practices.yaml and the acquisitions manifest.
import registry from '../../../../../corpus/practices.json';
import { loadWork, type Work } from '../work/record';

export type Holding = 'file' | 'excerpt' | 'capture' | 'reproduction' | 'record';
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

/**
 * Where a practice stands for a visitor: its representative on show (exported with its files),
 * in the reserve (held, but `tm export` published no file of it, or nothing at all), or missing.
 * The site does not decide: it reads what the export published (ADR 0022).
 */
export type Standing = 'shown' | 'reserve' | 'missing';

export async function standingOf(
	practice: Practice,
	load: (sha256: string) => Promise<Work | null> = loadWork
): Promise<Standing> {
	if (!practice.representative) return 'missing';
	const work = await load(practice.representative.sha256);
	return work?.record.shown === 'files' ? 'shown' : 'reserve';
}
