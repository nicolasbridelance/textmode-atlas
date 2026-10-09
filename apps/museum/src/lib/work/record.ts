// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// A work as `tm export` publishes it (ADR 0022): its record, and its grid when it is shown. The
// site never decides what may be shown: a work it cannot fetch is a work it does not show.
import { fileUrl } from '../files';
import { parseTmg, type TmgGrid } from './tmg';

interface WorkRecord {
	schema: 1;
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
	withdraw: string;
}

export interface Work {
	record: WorkRecord;
	grid: TmgGrid | null;
}

const SHA256 = /^[0-9a-f]{64}$/;

export function isWorkId(value: string | null): value is string {
	return value !== null && SHA256.test(value);
}

export async function loadWork(
	sha256: string,
	fetcher: typeof fetch = fetch
): Promise<Work | null> {
	const response = await fetcher(fileUrl(`works/${sha256}/record.json`));
	if (!response.ok) return null;
	const record = (await response.json()) as WorkRecord;
	if (record.shown !== 'files') return { record, grid: null };
	const grid = await fetcher(fileUrl(`works/${sha256}/grid.tmg`));
	return { record, grid: grid.ok ? parseTmg(await grid.arrayBuffer()) : null };
}
