<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- The research room: the live exploration of the corpus, then the dated studies. -->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import { reports } from '../../lib/atlas/reports';
	import Markdown from '../../lib/atlas/Markdown.svelte';
	import Exploration from '../../lib/eda/Exploration.svelte';
</script>

<svelte:head><title>{m.atlas_research()} · {m.museum_name()}</title></svelte:head>
<main>
	<h1>{m.atlas_research()}</h1>
	<p class="intro">{m.research_intro()}</p>
	<nav class="parts" aria-label={m.atlas_research()}>
		<a href="#corpus">{m.eda_title()}</a>
		<a href="#studies">{m.atlas_publications()}</a>
	</nav>

	<Exploration />

	<section id="studies" aria-labelledby="studies-title">
		<h2 id="studies-title">{m.atlas_publications()}</h2>
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
	</section>
</main>

<style>
	main {
		max-width: 52rem;
		margin: auto;
		padding: 1.5rem 1rem 5rem;
	}
	h1,
	h2 {
		font-weight: 400;
		color: var(--bright);
	}
	h2 {
		margin-top: 4rem;
		padding-top: 1rem;
		border-top: 1px solid var(--line);
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
	.parts {
		margin-block: 1rem 0;
		font-size: 0.9rem;
	}
	section {
		scroll-margin-top: 1rem;
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
	@media (min-width: 900px) {
		main {
			max-width: 64rem;
			padding-inline: 2rem;
		}
	}
</style>
