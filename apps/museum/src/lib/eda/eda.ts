// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// The live exploration served by the museum host at /api/eda (ADR 0028). The host computes
// every number and every check; the page only formats and draws them.

export type Check = { holds: boolean } & Record<string, number | boolean | null>;
type Checks = Record<string, Check>;

interface Year {
	year: number;
	works: number;
	packs: number;
	median_art: number;
}

interface SauceYear {
	year: number;
	format: 'ansi' | 'ascii';
	works: number;
	share: number;
}

interface Era {
	era: string;
	works: number;
	median_rows: number;
	wide: number;
	ice: number;
}

interface KindShare {
	share: number;
	shade: number;
}

export interface Snapshot {
	schema: number;
	computed_at: string;
	seconds: number;
	fingerprint: number;
	hidden: number;
	chapters: {
		contents: {
			sources: { source: string; files: number }[];
			funnel: Record<'art' | 'decoding' | 'grids' | 'rendered' | 'measured' | 'packs', number>;
			unread: { format: string; error_class: string; works: number }[];
			checks: Checks;
		};
		peak: { years: Year[]; checks: Checks };
		sauce: {
			by_year: SauceYear[];
			year: number;
			packs: number;
			shares: number[];
			none: number;
			all: number;
			full_mean_dates: number | null;
			full_mean_files: number | null;
			groups: { prefix: string; with: number; packs: number }[];
			test: {
				groups: number;
				packs: number;
				observed: number;
				null_mean: number;
				null_q95: number;
				p: number;
				null: number[];
			};
			checks: Checks;
		};
		composition: {
			eras: { era: string; all: number; kinds: Record<string, KindShare> }[];
			before: string;
			after: string;
			split: { total: number; within: number; composition: number };
			checks: Checks;
		};
		revival: { eras: Era[]; checks: Checks };
	};
}

export type CheckState = 'holds' | 'broken' | 'unknown';

/** A missing check means the data cannot support it yet, not that it failed. */
export function checkState(check: Check | undefined): CheckState {
	if (!check) return 'unknown';
	return check.holds ? 'holds' : 'broken';
}

export const REFRESH_MS = 30_000; // as often as the host looks at the database
const PERCENT = 100;
const TICKS = 3;
const NICE = Object.freeze({ one: 1, two: 2, quarter: 2.5, five: 5, ten: 10 }); // round steps, times a power of ten
const BASE = 10;
const EPSILON = 1e-6;
const DIGITS = 10;
const P_FLOOR = 0.001;
const LABEL_ROOM = 8; // pixels between two axis labels
export const CHAR_PX = 7; // width of a character of the axis font

export async function loadSnapshot(fetcher: typeof fetch = fetch): Promise<Snapshot | null> {
	const response = await fetcher('/api/eda');
	if (!response.ok) return null;
	const found = (await response.json()) as Snapshot;
	return found.schema === 1 ? found : null;
}

export function formatter(locale: string) {
	const integer = new Intl.NumberFormat(locale, { maximumFractionDigits: 0 });
	const decimal = new Intl.NumberFormat(locale, { maximumFractionDigits: 1 });
	const percent = new Intl.NumberFormat(locale, { style: 'percent', maximumFractionDigits: 1 });
	const fine = new Intl.NumberFormat(locale, { maximumFractionDigits: 3 });
	return {
		n: (value: number | null | undefined) => (value == null ? '–' : integer.format(value)),
		d: (value: number | null | undefined) => (value == null ? '–' : decimal.format(value)),
		pct: (value: number | null | undefined) => (value == null ? '–' : percent.format(value)),
		/** A share as points of percentage, signed: −5.9 */
		pts: (value: number) => `${value > 0 ? '+' : ''}${decimal.format(value * PERCENT)}`,
		/** A p-value: below what the shuffles can resolve, say so rather than print 0. */
		p: (value: number) => (value < P_FLOOR ? `< ${fine.format(P_FLOOR)}` : fine.format(value)),
		/** The same, as a relation to write after “p”: `< 0.001`, `= 0.03`. */
		pIs: (value: number) =>
			value < P_FLOOR ? `< ${fine.format(P_FLOOR)}` : `= ${fine.format(value)}`
	};
}

/** How many categories to skip between two labels so that they do not touch. */
export function labelEvery(band: number, widest: number, atLeast = 1): number {
	return Math.max(atLeast, Math.ceil((widest + LABEL_ROOM) / Math.max(1, band)));
}

/** Every year from the first to the last, so that a gap in the data stays a gap on the axis. */
export function everyYear(years: number[]): number[] {
	if (!years.length) return [];
	const first = Math.min(...years);
	return Array.from({ length: Math.max(...years) - first + 1 }, (_, i) => first + i);
}

/** Ticks for an axis from 0 to at least `max`: about `count` round steps. */
export function ticks(max: number, count = TICKS): number[] {
	if (max <= 0) return [0];
	const raw = max / count;
	const magnitude = BASE ** Math.floor(Math.log10(raw));
	const step =
		Object.values(NICE)
			.map((m) => m * magnitude)
			.find((s) => s >= raw) ?? raw;
	const steps = Math.ceil(max / step - EPSILON);
	return Array.from({ length: steps + 1 }, (_, i) => Number((i * step).toFixed(DIGITS)));
}
