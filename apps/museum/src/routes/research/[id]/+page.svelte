<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- One study of the research room: where it stands, then its text or its live chapters. -->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import { getLocale, localizeHref } from '#lib/paraglide/runtime.js';
	import Markdown from '../../../lib/atlas/Markdown.svelte';
	import Exploration from '../../../lib/eda/Exploration.svelte';
	import StudyFacts from '../../../lib/research/StudyFacts.svelte';
	import { localized } from '../../../lib/research/studies';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const locale = getLocale();
	const study = $derived(data.study);
	const title = $derived(localized(study.title, locale));
</script>

<svelte:head>
	<title>{title} · {m.atlas_research()} · {m.museum_name()}</title>
	<meta name="description" content={localized(study.summary, locale)} />
</svelte:head>
<main>
	<nav class="back"><a href={localizeHref('/research')}>← {m.research_back()}</a></nav>
	<header>
		<p class="kind">{m[`research_kind_${study.kind}`]()}</p>
		<h1>{title}</h1>
		<p class="summary">{localized(study.summary, locale)}</p>
		<StudyFacts {study} {locale} leads />
	</header>

	{#if data.body === null}
		<Exploration titled={false} />
	{:else}
		{#if study.language !== locale}<p class="note">{m.atlas_original_language()}</p>{/if}
		<Markdown text={data.body} />
	{/if}
</main>

<style>
	main {
		max-width: 52rem;
		margin: auto;
		padding: 1.5rem 1rem 5rem;
	}
	.back {
		font-size: 0.85rem;
	}
	header {
		border-bottom: 1px solid var(--line);
		padding-bottom: 1.5rem;
		margin-bottom: 2rem;
	}
	.kind {
		margin: 1.5rem 0 0;
		color: var(--dim);
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}
	h1 {
		font-weight: 400;
		color: var(--bright);
		margin-top: 0.25rem;
	}
	.summary {
		max-width: 65ch;
		line-height: 1.7;
	}
	.note {
		color: var(--dim);
		font-size: 0.75rem;
	}
	@media (min-width: 900px) {
		main {
			max-width: 64rem;
			padding-inline: 2rem;
		}
	}
</style>
