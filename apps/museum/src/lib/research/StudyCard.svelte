<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- One study in the research room's index: what it is, where it stands, what it found. -->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import { localizeHref } from '#lib/paraglide/runtime.js';
	import StudyFacts from './StudyFacts.svelte';
	import { localized, type Study } from './studies';

	let { study, locale }: { study: Study; locale: string } = $props();
</script>

<article class:programme={study.kind === 'programme'}>
	<p class="kind">{m[`research_kind_${study.kind}`]()}</p>
	<h2><a href={localizeHref(`/research/${study.id}`)}>{localized(study.title, locale)}</a></h2>
	<p class="summary">{localized(study.summary, locale)}</p>
	<StudyFacts {study} {locale} />
</article>

<style>
	article {
		height: 100%;
		box-sizing: border-box;
		border: 1px solid var(--line);
		padding: 1rem 1.25rem;
		position: relative;
	}
	article.programme {
		border-color: var(--bright);
	}
	.kind {
		margin: 0;
		color: var(--dim);
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}
	h2 {
		font-weight: 400;
		font-size: 1.2rem;
		margin: 0.25rem 0 0.5rem;
	}
	h2 a {
		color: var(--bright);
		text-decoration: none;
	}
	/* The whole card opens the study. */
	h2 a::after {
		content: '';
		position: absolute;
		inset: 0;
	}
	h2 a:focus-visible {
		outline: none;
	}
	article:has(h2 a:focus-visible),
	article:hover {
		border-color: var(--bright);
	}
	.summary {
		line-height: 1.6;
		margin: 0 0 0.75rem;
	}
</style>
