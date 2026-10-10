<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- The research room (ADR 0029): every study of the registry, filtered by programme strand. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/env';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { m } from '#lib/paraglide/messages.js';
	import { getLocale, localizeHref } from '#lib/paraglide/runtime.js';
	import StudyCard from '../../lib/research/StudyCard.svelte';
	import { STRANDS, isStrand, studies, type Strand } from '../../lib/research/studies';

	const locale = getLocale();
	const base = localizeHref('/research');
	const strandName = (s: Strand) => m[`research_strand_${s}`]();
	const question = (s: Strand) => m[`research_question_${s}`]();
	const count = (s: Strand) => studies.filter((study) => study.strand === s).length;

	const asked = $derived(browser ? page.url.searchParams.get('strand') : null);
	const strand = $derived(isStrand(asked) ? asked : null);
	const shown = $derived(strand ? studies.filter((s) => s.strand === strand) : studies);

	onMount(() => {
		// The exploration had this room's #corpus anchor before it got its own page (ADR 0029).
		if (location.hash === '#corpus')
			void goto(localizeHref('/research/corpus'), { replaceState: true });
	});
</script>

<svelte:head><title>{m.atlas_research()} · {m.museum_name()}</title></svelte:head>
<main>
	<h1>{m.atlas_research()}</h1>
	<p class="intro">{m.research_intro()}</p>

	<nav class="strands" aria-label={m.research_strands()}>
		<a href={base} aria-current={strand === null ? 'page' : undefined}>
			{m.research_all()} <span class="n">{studies.length}</span>
		</a>
		{#each STRANDS as s (s)}
			<a
				href={`${base}?strand=${s}`}
				class:empty={count(s) === 0}
				aria-current={strand === s ? 'page' : undefined}
				title={question(s)}
			>
				{#if s.startsWith('W')}<span class="code">{s}</span>{/if}
				{strandName(s)} <span class="n">{count(s)}</span>
			</a>
		{/each}
	</nav>

	{#if strand}
		<p class="question">{question(strand)}</p>
	{/if}
	<p class="shown" aria-live="polite">
		{m.research_shown({ count: shown.length, total: studies.length })}
	</p>

	{#if shown.length}
		<ol class="studies">
			{#each shown as study (study.id)}
				<li><StudyCard {study} {locale} /></li>
			{/each}
		</ol>
	{:else}
		<p class="empty-note">{m.research_empty()}</p>
	{/if}

	<p class="note">{m.atlas_vision_note()}</p>
</main>

<style>
	main {
		max-width: 52rem;
		margin: auto;
		padding: 1.5rem 1rem 5rem;
	}
	h1 {
		font-weight: 400;
		color: var(--bright);
	}
	.intro,
	.question {
		max-width: 65ch;
		line-height: 1.7;
	}
	.question {
		color: var(--bright);
		font-style: italic;
	}
	.strands {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-block: 2rem 1rem;
		font-size: 0.85rem;
	}
	.strands a {
		border: 1px solid var(--line);
		border-radius: 999px;
		padding: 0.25rem 0.75rem;
		text-decoration: none;
		color: inherit;
		white-space: nowrap;
	}
	.strands a[aria-current='page'] {
		border-color: var(--bright);
		color: var(--bright);
	}
	.strands a.empty {
		color: var(--dim);
		border-style: dashed;
	}
	.code {
		font-family: var(--mono, monospace);
		color: var(--dim);
		margin-right: 0.25rem;
	}
	.n {
		color: var(--dim);
		margin-left: 0.25rem;
	}
	.shown,
	.note,
	.empty-note {
		color: var(--dim);
		font-size: 0.85rem;
	}
	.studies {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 1rem;
	}
	.note {
		margin-top: 3rem;
		max-width: 65ch;
	}
	@media (min-width: 900px) {
		main {
			max-width: 64rem;
			padding-inline: 2rem;
		}
		.studies {
			grid-template-columns: 1fr 1fr;
		}
	}
</style>
