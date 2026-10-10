// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// One page per study of the registry (ADR 0029), prerendered with its Markdown.
import { error } from '@sveltejs/kit';
import { findStudy, loadBody, studies } from '../../../lib/research/studies';
import type { EntryGenerator, PageLoad } from './$types';

const NOT_FOUND = 404;
// The page gives the study's title itself: the Markdown's own first heading would repeat it.
const FIRST_HEADING = /^((?:<!--[\s\S]*?-->\s*)?)# [^\n]*\n/;

export const entries: EntryGenerator = () => studies.map(({ id }) => ({ id }));

export const load: PageLoad = async ({ params }) => {
	const study = findStudy(params.id);
	if (!study) error(NOT_FOUND, `No study named ${params.id}`);
	const body = await loadBody(study);
	return { study, body: body?.replace(FIRST_HEADING, '$1') ?? null };
};
