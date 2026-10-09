<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<script lang="ts">
	import { localizeHref } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import type { Research } from '../work/record';
	let { research, locale }: { research: Research; locale: string } = $props();
	const SIGNIFICANT_DIGITS = 5;
	const readings = $derived(research.readings.filter((reading) => reading.locale === locale));
</script>

<section class="research" aria-labelledby="research-title">
	<h2 id="research-title">{m.atlas_research()}</h2>
	<p class="note">{m.atlas_science_note()}</p>
	<details>
		<summary>{m.atlas_measures()}</summary>
		<p class="note">
			works v{research.dataset.version} · {JSON.stringify(research.dataset.extractors)}
		</p>
		<dl>
			{#each Object.entries(research.features) as [name, value] (name)}<dt>{name}</dt>
				<dd>
					{typeof value === 'number'
						? value.toLocaleString(locale, { maximumSignificantDigits: SIGNIFICANT_DIGITS })
						: value}
				</dd>{/each}
		</dl>
	</details>
	{#if research.neighbours.length}
		<details open>
			<summary>{m.atlas_neighbours()}</summary>
			<p class="note">{m.atlas_similarity_note()}</p>
			<ul>
				{#each research.neighbours as neighbour (neighbour.sha256)}<li>
						<a href={`${localizeHref('/work')}?w=${neighbour.sha256}`}
							>{neighbour.path} · {neighbour.sauce_author || m.work_unsigned()}</a
						>
					</li>{/each}
			</ul>
		</details>
	{/if}
	<h3>{m.atlas_readings()}</h3>
	{#if !readings.length}<p class="note">{m.atlas_no_readings()}</p>{/if}
	{#each readings as reading (reading.id)}
		<article>
			<h4>{reading.title}</h4>
			<p class="origin">{m.atlas_interpretation()} · {reading.asserted_by} · {reading.nature}</p>
			<p class="body">{reading.body}</p>
			<dl>
				<dt>{m.atlas_method()}</dt>
				<dd>{reading.method}</dd>
				<dt>{m.atlas_limits()}</dt>
				<dd>{reading.uncertainty}</dd>
				{#if reading.model}<dt>{m.atlas_model()}</dt>
					<dd>{reading.model}</dd>
					<dt>{m.atlas_input()}</dt>
					<dd>{reading.input_sha256}</dd>
					<dt>{m.atlas_prompt()}</dt>
					<dd>{reading.prompt_sha256}</dd>
					<dt>{m.atlas_rendering()}</dt>
					<dd>{reading.representation_sha256}</dd>{/if}
			</dl>
			<ul>
				{#each reading.sources as source (source)}<li>
						<a href={source} rel="external noopener">{source}</a>
					</li>{/each}
			</ul>
		</article>
	{/each}
	<a href={localizeHref('/research')}>{m.atlas_publications()}</a>
</section>

<style>
	.research {
		border-top: 1px solid var(--line);
		padding-top: 1rem;
		line-height: 1.5;
	}
	h2,
	h3,
	h4 {
		font-weight: 400;
		color: var(--bright);
	}
	h2 {
		font-size: 1.1rem;
	}
	h3 {
		font-size: 1rem;
	}
	h4 {
		font-size: 0.9rem;
	}
	.note {
		color: var(--dim);
		font-size: 0.8rem;
		overflow-wrap: anywhere;
	}
	details {
		margin: 0.75rem 0;
	}
	summary {
		cursor: pointer;
	}
	dl {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		gap: 0.4rem 1rem;
		font: 0.75rem/1.5 var(--mono);
	}
	dt {
		color: var(--dim);
	}
	dd {
		margin: 0;
		overflow-wrap: anywhere;
	}
	ul {
		padding-left: 1.2rem;
		font-size: 0.8rem;
		overflow-wrap: anywhere;
	}
	article {
		border-left: 1px dotted var(--accent);
		padding: 0 1rem;
		margin-block: 1.5rem;
	}
	.origin {
		color: var(--accent);
		font: 0.75rem/1.5 var(--mono);
	}
	.body {
		white-space: pre-wrap;
		font-size: 0.875rem;
	}
</style>
