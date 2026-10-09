<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import { reports } from '../../lib/atlas/reports';
	import Markdown from '../../lib/atlas/Markdown.svelte';
</script>

<svelte:head><title>{m.atlas_research()} · {m.museum_name()}</title></svelte:head>
<main>
	<h1>{m.atlas_research()}</h1>
	<p class="intro">{m.atlas_reports_note()}</p>
	<p class="intro">{m.atlas_vision_note()}</p>
	<nav aria-label={m.atlas_publications()}>
		{#each reports as report (report.id)}<a href={`#${report.id}`}>{report.title}</a>{/each}
	</nav>
	{#each reports as report (report.id)}
		<article id={report.id}>
			<details>
				<summary>{report.title}</summary>
				<p class="note">{m.atlas_original_language()}</p>
				<Markdown text={report.text} />
			</details>
		</article>
	{/each}
</main>

<style>
	main {
		max-width: 80rem;
		margin: auto;
		padding: 2rem clamp(1rem, 4vw, 4rem) 5rem;
	}
	h1 {
		font-weight: 400;
		color: var(--bright);
	}
	.intro {
		max-width: 65ch;
		line-height: 1.7;
	}
	nav {
		display: flex;
		gap: 1rem;
		flex-wrap: wrap;
		margin-block: 2rem;
	}
	article {
		border-top: 1px solid var(--line);
		padding-block: 1rem;
		scroll-margin-top: 1rem;
	}
	summary {
		cursor: pointer;
		color: var(--bright);
		font-size: 1.15rem;
	}
	.note {
		color: var(--dim);
		font-size: 0.75rem;
	}
</style>
