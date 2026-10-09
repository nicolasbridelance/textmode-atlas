// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// The ways out of a work and the work of the day, from the lists `tm lists` publishes (ADR 0023).
// A list names only works the museum may show: the site picks among them, it never filters.
import { fileUrl } from '../files';

export interface Entry {
	sha256: string;
	title: string | null;
	file: string;
	path: string;
	author: string | null;
	group: string | null;
	pack: string | null;
	year: number | null;
	cols: number;
	rows: number;
	level: string;
	/** Optional local-research rendering. Undefined uses the public conservation PNG. */
	preview?: string | null;
}

export interface List {
	works: Entry[];
	pack?: string;
	archive?: string;
	url?: string;
	author?: string;
	year?: number;
}

export interface ListPaths {
	pack: string | null;
	author: string | null;
	year: string | null;
}

export interface Lists {
	pack: List | null;
	author: List | null;
	year: List | null;
	days: List | null;
}

/** Previous and next in the pack, another work with the same signature, the same year
 * elsewhere, and a work drawn by chance. */
export interface Ways {
	previous: Entry | null;
	next: Entry | null;
	signature: Entry | null;
	year: Entry | null;
	chance: Entry | null;
}

export async function loadList(
	path: string | null,
	fetcher: typeof fetch = fetch
): Promise<List | null> {
	if (!path) return null;
	try {
		const response = await fetcher(fileUrl(path));
		return response.ok ? ((await response.json()) as List) : null;
	} catch {
		return null; // a way out the museum cannot read is a way out it does not offer
	}
}

const SEED_HEX_DIGITS = 8;
const HEX = 16;
const SECOND_DRAW = 8; // bits shifted off the seed, so chance and the year do not move together

/** A stable number from a work's hash, so a work offers the same ways out on every visit. */
export function seedOf(sha256: string): number {
	return Number.parseInt(sha256.slice(0, SEED_HEX_DIGITS), HEX) || 0;
}

/** The first entry from `start` on (going round) that `keep` accepts; null in an empty list. */
function round(works: Entry[], start: number, keep: (e: Entry) => boolean): Entry | null {
	for (let k = 0; k < works.length; k++) {
		const entry = works[(start + k) % works.length];
		if (keep(entry)) return entry;
	}
	return null;
}

/** The entry `step` places away from the work in the list, without going round. */
function beside(list: List | null, sha256: string, step: number): Entry | null {
	const works = list?.works ?? [];
	const here = works.findIndex((e) => e.sha256 === sha256);
	return here < 0 ? null : (works[here + step] ?? null);
}

export function waysOut(sha256: string, pack: string | null, lists: Lists, seed: number): Ways {
	const other = (e: Entry): boolean => e.sha256 !== sha256;
	const elsewhere = (e: Entry): boolean => other(e) && e.pack !== pack;
	const signed = lists.author?.works ?? [];
	const after = signed.findIndex((e) => e.sha256 === sha256) + 1;
	return {
		previous: beside(lists.pack, sha256, -1),
		next: beside(lists.pack, sha256, 1),
		signature: round(signed, after, elsewhere) ?? round(signed, after, other),
		year: round(lists.year?.works ?? [], seed, elsewhere),
		chance: round(lists.days?.works ?? [], seed >>> SECOND_DRAW, other)
	};
}

const MS_PER_DAY = 86_400_000;

/** Day of the year, from 0 on 1 January (local time): the index of the work of the day. */
export function dayOfYear(date: Date): number {
	const start = new Date(date.getFullYear(), 0, 1);
	const today = new Date(date.getFullYear(), date.getMonth(), date.getDate());
	return Math.round((today.getTime() - start.getTime()) / MS_PER_DAY);
}

export function workOfTheDay(days: List | null, date: Date): Entry | null {
	const works = days?.works ?? [];
	return works.length ? works[dayOfYear(date) % works.length] : null;
}
