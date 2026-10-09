// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// A work as `tm export` publishes it (ADR 0022): its record, and its grid when it is shown. The
// site never decides what may be shown: a work it cannot fetch is a work it does not show.
import { fileUrl } from '../files';
import { parseTmg, type TmgGrid } from './tmg';
import type { ListPaths } from './visit';

interface Provenance {
	source: string;
	url: string;
	method: string;
	retrieved_at: string | null;
	via_archive: string | null;
	path_in_archive: string | null;
}

export interface WorkRecord {
	schema: 1 | 2;
	sha256: string;
	title: string | null;
	file: string;
	year: number | null;
	format: string;
	credit: {
		author: string | null;
		group: string | null;
		pack: string | null;
		archive: string | null;
		url: string | null;
	};
	audience: { level: string; descriptors: string[]; notices: string[]; reviewed: boolean };
	shown: 'files' | 'record';
	grid: { cols: number; rows: number; ice: boolean };
	files: Record<string, string>;
	provenance: Provenance[];
	withdraw: string;
	/** Schema 2 (ADR 0023): the words of a shown work, and the lists it belongs to. */
	text?: { row: number; text: string }[];
	lists?: ListPaths | null;
	research?: Research;
}

interface Reading {
	id: string;
	title: string;
	body: string;
	locale: string;
	kind: 'explanation' | 'science' | 'vision';
	nature: 'documented' | 'testified' | 'inferred';
	level: 'interpretation';
	asserted_by: string;
	method: string;
	input_sha256: string;
	sources: string[];
	uncertainty: string;
	model: string | null;
	prompt_sha256: string | null;
	representation_sha256: string | null;
}

export interface Research {
	dataset: { version: string; extractors: Record<string, string> };
	decoding: string;
	features: Record<string, string | number>;
	neighbours: {
		sha256: string;
		path: string;
		sauce_author: string | null;
		sauce_group: string | null;
	}[];
	readings: Reading[];
}

export interface Work {
	record: WorkRecord;
	grid: TmgGrid | null;
}

const SHA256 = /^[0-9a-f]{64}$/;

export function isWorkId(value: string | null): value is string {
	return value !== null && SHA256.test(value);
}

const loaded = new Map<string, Promise<Work | null>>();

/** A work, fetched once: ways out are fetched ahead so the next work opens at once. */
export function loadWork(sha256: string, fetcher: typeof fetch = fetch): Promise<Work | null> {
	let work = loaded.get(sha256);
	if (!work) {
		work = fetchWork(sha256, fetcher).catch(() => null);
		loaded.set(sha256, work);
	}
	return work;
}

async function fetchWork(sha256: string, fetcher: typeof fetch): Promise<Work | null> {
	const response = await fetcher(fileUrl(`works/${sha256}/record.json`));
	if (!response.ok) return null;
	const record = (await response.json()) as WorkRecord;
	if (record.shown !== 'files') return { record, grid: null };
	const grid = await fetcher(fileUrl(`works/${sha256}/grid.tmg`));
	return { record, grid: grid.ok ? parseTmg(await grid.arrayBuffer()) : null };
}
