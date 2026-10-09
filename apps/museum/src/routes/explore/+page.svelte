<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { SvelteURLSearchParams } from 'svelte/reactivity';
	import { onMount } from 'svelte';
	import { browser } from '$app/env';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import type { Path } from '$app/types';
	import { localizeHref } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import { isWorkId, loadWork } from '../../lib/work/record';
	import type { ListPaths } from '../../lib/work/visit';
	import Gallery from '../../lib/presentation/Gallery.svelte';
	import SwipeDeck from '../../lib/presentation/SwipeDeck.svelte';
	import CatalogueControls from '../../lib/presentation/CatalogueControls.svelte';
	import DisplayControls from '../../lib/presentation/DisplayControls.svelte';
	import {
		filterEntries,
		readFilters,
		researchQuery,
		type BrowseFilters,
		type ResearchFacets
	} from '../../lib/presentation/catalogue';
	import { CollectionLoader } from '../../lib/presentation/collection.svelte';
	import { displayQuery, readDisplay, type Display } from '../../lib/presentation/display';
	import { selection } from '../../lib/presentation/selection.svelte';
	import { museumContext } from '../../lib/presentation/settings.svelte';
	import { draw, newSeed } from '../../lib/presentation/chance';

	const PAGE_SIZE = 48;
	const RESEARCH_BASE = '';
	const SCOPES = ['days', 'pack', 'author', 'year'] as const;
	const loader = new CollectionLoader(RESEARCH_BASE);
	let paths: ListPaths | null = $state(null);
	let facets: ResearchFacets | null = $state(null);
	let limit = $state(PAGE_SIZE);
	let onlySaved = $state(false);
	let resetSerial = $state(0);
	let drawing = $state(false);
	let nothingToDraw = $state(false);

	const params = $derived(browser ? page.url.searchParams : null);
	const scope = $derived.by(() => {
		const value = params?.get('scope');
		return SCOPES.includes(value as (typeof SCOPES)[number])
			? (value as (typeof SCOPES)[number])
			: 'days';
	});
	const corpus = $derived(facets !== null && params?.get('source') !== 'public');
	const filters = $derived(readFilters(params));
	const display = $derived(readDisplay(params));
	const deck = $derived(display.layout === 'deck');
	const id = $derived(params?.get('w') ?? null);
	const requestKey = $derived(
		corpus ? researchQuery(filters) : scope === 'days' ? 'lists/days.json' : (paths?.[scope] ?? '')
	);
	const browseKey = $derived(JSON.stringify([corpus, requestKey, filters, resetSerial]));
	const matched = $derived(corpus ? loader.works : filterEntries(loader.works, filters));
	const selected = $derived(matched.filter((entry) => selection.has(entry.sha256)));
	const visible = $derived(onlySaved ? selected : matched);
	const total = $derived(onlySaved ? selected.length : corpus ? loader.total : matched.length);
	const shown = $derived(visible.slice(0, limit));
	const heading = $derived(
		{
			wall: m.discovery_pinterest_title,
			grid: m.explore_title,
			feed: m.discovery_instagram_title,
			deck: m.discovery_tinder_title
		}[display.layout]()
	);
	const note = $derived(
		{
			wall: m.discovery_pinterest_note,
			grid: m.discovery_pinterest_note,
			feed: m.discovery_instagram_note,
			deck: m.discovery_tinder_note
		}[display.layout]()
	);

	onMount(() => selection.restore());
	$effect(() => {
		if (!browser) return;
		let active = true;
		paths = null;
		if (isWorkId(id))
			void loadWork(id).then((work) => {
				if (active) paths = work?.record.lists ?? null;
			});
		return () => {
			active = false;
		};
	});
	$effect(() => {
		if (!browser) return;
		void browseKey; // reload when the query, the filters or a reset change
		limit = PAGE_SIZE;
		void loader.load(requestKey, corpus);
		return () => loader.stop();
	});
	$effect(() => {
		if (!browser) return;
		let active = true;
		void fetch(`${RESEARCH_BASE}/api/facets`)
			.then(async (response) => {
				if (response.ok && active) facets = await response.json();
			})
			.catch(() => {
				/* The results report the error; filters remain usable. */
			});
		return () => {
			active = false;
		};
	});

	function href(sha256: string): string {
		return `${resolve(localizeHref('/work') as Path)}?w=${sha256}`;
	}
	function navigate(values: Record<string, string>, clean = false): void {
		const query = new SvelteURLSearchParams(clean ? '' : page.url.search);
		if (params?.get('source') === 'public') query.set('source', 'public');
		if (corpus) query.set('source', 'corpus');
		for (const [key, value] of Object.entries(values)) {
			if (value) query.set(key, value);
			else query.delete(key);
		}
		void goto(`${resolve(localizeHref('/explore') as Path)}?${query}`, {
			replace: true,
			reset: false
		});
	}
	function apply(next: BrowseFilters): void {
		limit = PAGE_SIZE;
		navigate(next);
	}
	function show(next: Display): void {
		navigate(displayQuery(next));
	}
	function reset(): void {
		onlySaved = false;
		limit = PAGE_SIZE;
		resetSerial += 1;
		museumContext.workId = null;
		navigate(displayQuery(display), true);
	}
	function reshuffle(): void {
		apply({ ...filters, order: '', seed: newSeed() });
	}
	/** One work drawn among the current filters; the server draws when it holds the corpus. */
	async function surprise(): Promise<void> {
		const seed = newSeed();
		drawing = true;
		nothingToDraw = false;
		try {
			const sha256 = corpus
				? await fetch(`${RESEARCH_BASE}/api/surprise?${researchQuery({ ...filters, seed })}`).then(
						async (response) =>
							response.ok ? ((await response.json()) as { sha256: string }).sha256 : null
					)
				: (draw(visible, seed)?.sha256 ?? null);
			if (sha256) await goto(href(sha256));
			else nothingToDraw = true;
		} catch {
			nothingToDraw = true;
		} finally {
			drawing = false;
		}
	}
	async function more(): Promise<void> {
		const nextPage = deck || limit >= visible.length;
		if (loader.hasMore && !onlySaved && nextPage) {
			await loader.more();
			limit = Math.max(limit, loader.works.length);
		} else limit += PAGE_SIZE;
	}
</script>

<svelte:head><title>{m.nav_explore()} · {m.museum_name()}</title></svelte:head>

<main data-paper={display.paper} class:deck>
	<div class="explore-inner">
		<p class="eyebrow">{m.discovery_eyebrow()}</p>
		<div class="intro">
			<h1>{heading}</h1>
			<p>{note}</p>
		</div>
		<DisplayControls {display} apply={show} />
		<div class="toolbar">
			{#if !corpus}<label
					>{m.explore_scope()}
					<select
						value={scope}
						onchange={(event) => navigate({ scope: event.currentTarget.value })}
					>
						<option value="days">{m.explore_days()}</option>
						{#if paths?.pack}<option value="pack">{m.explore_pack()}</option>{/if}
						{#if paths?.author}<option value="author">{m.explore_author()}</option>{/if}
						{#if paths?.year}<option value="year">{m.explore_year()}</option>{/if}
					</select></label
				>{/if}
			{#if !corpus && isWorkId(id)}<a href={href(id)}>{m.explore_back()}</a>{/if}
			<div class="chance">
				<button type="button" onclick={reshuffle}>{m.explore_reshuffle()}</button>
				<button type="button" disabled={drawing} onclick={() => void surprise()}
					>{m.explore_surprise()}</button
				>
			</div>
			<div class="selection-toggle" role="group" aria-label={m.discovery_collection_label()}>
				<button type="button" aria-pressed={!onlySaved} onclick={() => (onlySaved = false)}
					>{m.discovery_all()}</button
				>
				<button type="button" aria-pressed={onlySaved} onclick={() => (onlySaved = true)}
					>{m.discovery_selection({ count: selected.length })}</button
				>
			</div>
		</div>
		<p class="scope-note">
			{#if corpus}{m.browse_corpus_note({ count: facets?.dataset.works ?? loader.total })}
			{:else if scope === 'days'}{m.browse_days_note()}
			{:else if scope === 'year'}{m.browse_year_note()}
			{:else}{m.browse_collection_note()}{/if}
		</p>
		<CatalogueControls {filters} entries={loader.works} {corpus} {facets} {apply} {reset} />
		{#if onlySaved && selection.ids.length}<button
				class="clear-selection"
				type="button"
				onclick={() => selection.clear()}>{m.browse_clear_selection()}</button
			>{/if}
		{#if selection.cleared}<p class="selection-cleared" role="status">
				{m.browse_selection_cleared()}
				<button type="button" onclick={() => selection.undoClear()}>{m.browse_undo_clear()}</button>
			</p>{/if}
		{#if nothingToDraw}<p role="status">{m.explore_surprise_none()}</p>{/if}
		{#if loader.loading}<p role="status">{m.explore_loading()}</p>
		{:else if loader.failed && !loader.works.length}<p role="alert">{m.browse_unavailable()}</p>
		{:else if !matched.length}<p class="empty-selection">{m.browse_no_results()}</p>
		{:else}
			<p class="count">{m.browse_results({ count: total })}</p>
			{#if onlySaved && !selected.length}
				<p class="empty-selection">{m.discovery_selection_empty()}</p>
			{:else if !deck || onlySaved}
				<Gallery entries={shown} display={deck ? { ...display, layout: 'wall' } : display} {href} />
			{/if}
			{#if deck}
				<!-- Kept mounted while the selection is shown, so the deck resumes where it was. -->
				<div hidden={onlySaved}>
					{#key browseKey}<SwipeDeck
							entries={matched}
							{total}
							hasMore={loader.hasMore}
							loadingMore={loader.loadingMore}
							{more}
							saved={selection.ids}
							setSaved={(sha256, value) => selection.set(sha256, value)}
							{href}
							active={!onlySaved}
						/>{/key}
				</div>
			{/if}
			{#if (!deck || onlySaved) && (limit < visible.length || (!onlySaved && loader.hasMore))}<button
					class="more"
					type="button"
					disabled={loader.loadingMore}
					onclick={() => void more()}
					>{loader.loadingMore ? m.explore_loading() : m.explore_more()}</button
				>{/if}
			{#if loader.failed}<p role="alert">{m.browse_unavailable()}</p>{/if}
		{/if}
	</div>
</main>

<style>
	main {
		min-height: calc(100dvh - 5rem);
		padding: 2rem 1.5rem 5rem;
		background: var(--paper-bg, var(--surface));
		color: var(--ink);
		/* The deck and the controls read these names. */
		--discovery-bg: var(--paper-bg, var(--surface));
		--discovery-paper: var(--panel);
		--discovery-ink: var(--ink);
		--discovery-dim: var(--dim);
		--discovery-line: var(--line);
		--discovery-accent: var(--accent);
	}
	/* Papers set the room's colours; `museum` keeps the site's theme. */
	[data-paper='light'] {
		--paper-bg: #f5f3ee;
		--panel: #fffdf9;
		--ink: #292a25;
		--bright: #292a25;
		--dim: #6e6e65;
		--line: #d9d7cf;
		--accent: #a53d32;
		--discovery-on-accent: #fff;
	}
	[data-paper='dark'] {
		--paper-bg: #110e17;
		--panel: #211824;
		--ink: #fff0f5;
		--bright: #fff0f5;
		--dim: #b5a0b1;
		--line: #513343;
		--accent: #f75380;
		--discovery-on-accent: #160c13;
	}
	.explore-inner {
		max-width: 82rem;
		margin: auto;
	}
	.eyebrow {
		font: 0.65rem var(--mono);
		letter-spacing: 0.14em;
		color: var(--dim);
		margin: 0 0 1.5rem;
	}
	.intro {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 2rem;
		margin-bottom: 1.4rem;
	}
	h1 {
		font-size: clamp(2rem, 4vw, 3.3rem);
		letter-spacing: -0.055em;
		font-weight: 600;
		line-height: 1.1;
		margin: 0;
		color: var(--bright);
	}
	.intro > p {
		max-width: 22rem;
		font-size: 0.85rem;
		line-height: 1.6;
		color: var(--dim);
		margin: 0;
	}
	.toolbar {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
		align-items: center;
		margin-top: 1rem;
	}
	.chance,
	.selection-toggle {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}
	.selection-toggle {
		margin-left: auto;
	}
	.chance button,
	.selection-toggle button,
	.clear-selection,
	.selection-cleared button,
	.more {
		border-radius: 2rem;
		font-size: 0.75rem;
		padding: 0.7rem 0.9rem;
		min-height: 44px;
	}
	.selection-toggle button[aria-pressed='true'] {
		border-color: var(--accent);
		color: var(--accent);
	}
	.scope-note {
		color: var(--dim);
		font-size: 0.75rem;
		line-height: 1.6;
		margin: 1rem 0;
		max-width: 65rem;
	}
	.count {
		color: var(--dim);
		font: 0.7rem var(--mono);
		margin-block: 1.3rem 1.7rem;
	}
	.empty-selection {
		text-align: center;
		padding: 4rem 1rem;
		color: var(--dim);
	}
	.more {
		display: block;
		margin: 2rem auto 0;
		padding: 0.8rem 1.5rem;
	}
	.selection-cleared {
		font-size: 0.8rem;
	}
	label {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		align-items: center;
		font-size: 0.85rem;
	}
	select,
	button {
		font: inherit;
		color: var(--ink);
		background: var(--panel);
		border: 1px solid var(--line);
		padding: 0.5rem;
		max-width: 100%;
		cursor: pointer;
	}
	@media (max-width: 760px) {
		main {
			padding: 1.5rem 1rem 3rem;
		}
		.intro {
			display: block;
		}
		.intro > p {
			margin-top: 0.9rem;
			max-width: 100%;
		}
		.eyebrow {
			font-size: 0.55rem;
			letter-spacing: 0.1em;
		}
		.selection-toggle {
			margin-left: 0;
			width: 100%;
		}
		.deck .eyebrow,
		.deck .intro > p,
		.deck .count {
			display: none;
		}
		.deck h1 {
			font-size: 1.5rem;
		}
	}
</style>
