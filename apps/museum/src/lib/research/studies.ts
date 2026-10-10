// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// The research room's registry (ADR 0029): every public study, read from research/studies.json.
// A study's body is a Markdown file of the repository, loaded lazily, or a live component.
import registry from '../../../../../research/studies.json';

export const KINDS = ['programme', 'exploration', 'study', 'trial'] as const;
export const STRANDS = [
	'programme',
	'linkage',
	'description',
	'W1',
	'W2',
	'W3',
	'W4',
	'W5',
	'W6',
	'W7',
	'museum'
] as const;
export const STATUSES = [
	'exploratory',
	'preregistered',
	'confirmed',
	'refuted',
	'ongoing'
] as const;
export const LIVE = 'live:';

type Kind = (typeof KINDS)[number];
export type Strand = (typeof STRANDS)[number];
type Status = (typeof STATUSES)[number];
type Localized = Record<string, string>;

export interface Study {
	id: string;
	date: string;
	kind: Kind;
	strand: Strand;
	status: Status;
	dataset: string | null;
	leads: string[];
	source: string;
	language: string;
	title: Localized;
	summary: Localized;
}

/** Newest first; the programme, which frames the others, always leads. */
export const studies: Study[] = (registry.studies as Study[]).toSorted(
	(a, b) =>
		Number(b.kind === 'programme') - Number(a.kind === 'programme') || b.date.localeCompare(a.date)
);

export const findStudy = (id: string): Study | undefined => studies.find((s) => s.id === id);

export const localized = (text: Localized, locale: string): string => text[locale] ?? text.en;

export const isStrand = (value: string | null): value is Strand =>
	STRANDS.includes(value as Strand);

const ROOT = /^(\.\.\/)+/;
// Every folder a study may live in; the registry test fails when a source is outside them.
const bodies = import.meta.glob(
	[
		'../../../../../research/exploration/*.md',
		'../../../../../docs/spikes/[0-9]*.md',
		'../../../../../docs/research-program.md',
		'../../../../../docs/presentation-*.md'
	],
	{ query: '?raw', import: 'default' }
);
const loaders = new Map(
	Object.entries(bodies).map(([path, load]) => [
		path.replace(ROOT, ''),
		load as () => Promise<string>
	])
);

export const hasBody = (study: Study): boolean => loaders.has(study.source);

/** The study's Markdown, or null for a live study. */
export async function loadBody(study: Study): Promise<string | null> {
	if (study.source.startsWith(LIVE)) return null;
	const load = loaders.get(study.source);
	if (!load) throw new Error(`study ${study.id}: no Markdown at ${study.source}`);
	return load();
}
