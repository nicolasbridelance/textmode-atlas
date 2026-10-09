<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { localizeHref } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import { fileUrl } from '../../lib/files';
	import { collection, facets, type Facets, type Specimen } from '../../lib/atlas/collection';

	let catalogue: Facets | null = $state(null);
	let works: Specimen[] = $state([]);
	let total = $state(0);
	let busy = $state(true);
	let failed = $state(false);
	let query = $state('');
	let words = $state('');
	let archive = $state('');
	let year = $state('');
	let format = $state('');
	let kind = $state('');
	let order = $state('random');
	let thumbnail = $state('whole');
	let request = 0;
	const sortLabels: Record<string, () => string> = {
		random: m.atlas_sort_random,
		year: m.atlas_sort_year,
		colours: m.atlas_sort_colours,
		entropy: m.atlas_sort_entropy,
		shade: m.atlas_sort_shade,
		half_block: m.atlas_sort_half_block,
		letters: m.atlas_sort_letters,
		drawn: m.atlas_sort_drawn,
		tall: m.atlas_sort_tall,
		wide: m.atlas_sort_wide,
		fill: m.atlas_sort_fill,
		redrawn: m.atlas_sort_redrawn,
		clears: m.atlas_sort_clears
	};

	function parameters(offset = 0): URLSearchParams {
		return new URLSearchParams({
			q: query,
			words,
			archive,
			year,
			format,
			kind,
			order,
			offset: String(offset),
			thumbnail
		});
	}

	async function load(more = false): Promise<void> {
		const token = ++request;
		busy = true;
		failed = false;
		try {
			const result = await collection(parameters(more ? works.length : 0), catalogue !== null);
			if (token !== request) return;
			works = more ? [...works, ...result.works] : result.works;
			total = result.total;
		} catch {
			failed = true;
		} finally {
			if (token === request) busy = false;
		}
	}

	function search(event: SubmitEvent): void {
		event.preventDefault();
		void goto(`${page.url.pathname}?${parameters()}`, { replaceState: true });
		void load();
	}

	function saved(name: string, fallback = ''): string {
		return page.url.searchParams.get(name) ?? fallback;
	}

	onMount(async () => {
		query = saved('q');
		words = saved('words');
		archive = saved('archive');
		year = saved('year');
		format = saved('format');
		kind = saved('kind');
		order = saved('order', 'random');
		thumbnail = saved('thumbnail', 'whole');
		catalogue = await facets();
		await load();
	});

	function image(work: Specimen): string {
		return catalogue
			? `/image/${thumbnail}/${work.sha256}`
			: fileUrl(`works/${work.sha256}/conservation.png`);
	}
</script>

<svelte:head><title>{m.atlas_collection()} · {m.museum_name()}</title></svelte:head>
<main>
	<div class="intro">
		<h1>{m.atlas_collection()}</h1>
		<p>{m.atlas_intro()}</p>
	</div>
	<form onsubmit={search}>
		<label>{m.atlas_search()}<input type="search" bind:value={query} /></label>
		{#if catalogue}
			<label>{m.atlas_words()}<input type="search" bind:value={words} /></label>
			<label
				>{m.atlas_archive()}<select bind:value={archive}
					><option value="">{m.atlas_all()}</option
					>{#each catalogue.archives as item (item.archive)}<option value={item.archive}
							>{item.archive} · {item.works.toLocaleString()}</option
						>{/each}</select
				></label
			>
			<label
				>{m.atlas_year()}<select bind:value={year}
					><option value="">{m.atlas_all()}</option
					>{#each catalogue.years as item (item.year)}<option value={String(item.year)}
							>{item.year}</option
						>{/each}</select
				></label
			>
			<label
				>{m.work_format()}<select bind:value={format}
					><option value="">{m.atlas_all()}</option
					>{#each catalogue.formats as item (item.format)}<option value={item.format}
							>{item.format}</option
						>{/each}</select
				></label
			>
			<label
				>{m.atlas_kind()}<select bind:value={kind}
					><option value="">{m.atlas_all()}</option
					>{#each catalogue.kinds as item (item.kind)}<option value={item.kind}
							>{item.kind.replaceAll('_', ' ')}</option
						>{/each}</select
				></label
			>
			<label
				>{m.atlas_order()}<select bind:value={order}
					>{#each catalogue.orders as value (value)}<option {value}>{sortLabels[value]()}</option
						>{/each}</select
				></label
			>
		{/if}
		<label
			>{m.atlas_thumbnails()}<select bind:value={thumbnail}
				><option value="whole">{m.atlas_whole()}</option><option value="best"
					>{m.atlas_best()}</option
				><option value="screen">{m.atlas_first()}</option></select
			></label
		>
		<button type="submit" disabled={busy}>{m.atlas_search_button()}</button>
	</form>
	<p class="count" aria-live="polite">
		{busy ? m.work_loading() : m.atlas_count({ count: total.toLocaleString() })}
	</p>
	{#if catalogue}<details class="method">
			<summary>{m.atlas_method()}</summary>
			<p>{m.atlas_train()}</p>
			<p>works v{catalogue.dataset.version} · {JSON.stringify(catalogue.dataset.extractors)}</p>
		</details>{/if}
	{#if failed}<p role="alert">{m.atlas_unavailable()}</p>
		<button onclick={() => load()}>{m.atlas_retry()}</button>{/if}
	<div class="wall">
		{#each works as work (work.sha256)}
			<a class="card" href={`${localizeHref('/work')}?w=${work.sha256}`}>
				<div class="thumb">
					{#if work.decoding === 'ok' && work.display !== 'record'}<img
							src={image(work)}
							alt=""
							loading="lazy"
						/>{:else}<span>{work.decoding === 'ok' ? m.work_not_shown() : work.decoding}</span>{/if}
				</div>
				<div class="label">
					<h2>{work.sauce_title || work.path.split('/').pop()}</h2>
					<p>
						{work.sauce_author || m.work_unsigned()}
						{work.sauce_group ? `/ ${work.sauce_group}` : ''}
					</p>
					<p>{work.pack || m.atlas_loose()} · {work.archive || ''} · {work.year ?? '?'}</p>
					{#if work.hit}<p class="hit">{work.hit}</p>{/if}
				</div>
			</a>
		{/each}
	</div>
	{#if works.length < total}<button class="more" onclick={() => load(true)} disabled={busy}
			>{m.atlas_more()}</button
		>{/if}
</main>

<style>
	main {
		padding: 1rem clamp(1rem, 3vw, 3rem) 4rem;
	}
	h1 {
		font-weight: 400;
		color: var(--bright);
		margin: 0;
	}
	.intro p {
		color: var(--dim);
		max-width: 65ch;
		line-height: 1.5;
	}
	form {
		display: flex;
		gap: 0.75rem;
		flex-wrap: wrap;
		align-items: end;
		margin-block: 1.5rem;
	}
	label {
		display: grid;
		gap: 0.4rem;
		font-size: 0.75rem;
		min-width: 9rem;
		flex: 1;
	}
	input,
	select,
	button {
		font: inherit;
		color: var(--ink);
		background: var(--panel);
		border: 1px solid var(--line);
		padding: 0.6rem;
		border-radius: 0.2rem;
		min-width: 0;
	}
	button {
		cursor: pointer;
	}
	.count,
	.method {
		color: var(--dim);
		font: 0.75rem/1.5 var(--mono);
		overflow-wrap: anywhere;
	}
	.method {
		margin-bottom: 1rem;
	}
	.wall {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(min(100%, 240px), 1fr));
		gap: 1rem;
	}
	.card {
		display: block;
		text-decoration: none;
		border: 1px solid var(--line);
		background: var(--panel);
		min-width: 0;
	}
	.card:hover {
		border-color: var(--accent);
	}
	.thumb {
		aspect-ratio: 8 / 5;
		background: #000;
		display: grid;
		place-items: center;
		overflow: hidden;
	}
	.thumb img {
		width: 100%;
		height: 100%;
		object-fit: contain;
		image-rendering: pixelated;
	}
	.thumb span {
		color: var(--dim);
		padding: 1rem;
		font-size: 0.75rem;
	}
	.label {
		padding: 0.75rem;
		font: 0.75rem/1.5 var(--mono);
		overflow-wrap: anywhere;
	}
	h2 {
		margin: 0;
		font-size: 0.85rem;
		font-weight: 400;
		color: var(--bright);
	}
	.label p {
		margin: 0.25rem 0 0;
		color: var(--dim);
	}
	.label .hit {
		color: var(--accent);
	}
	.more {
		display: block;
		margin: 2rem auto;
	}
	@media (max-width: 500px) {
		label {
			flex-basis: 40%;
		}
	}
</style>
