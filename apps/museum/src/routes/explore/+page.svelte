<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { SvelteMap, SvelteURLSearchParams } from 'svelte/reactivity';
	import { onMount } from 'svelte';
	import { browser } from '$app/env';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import type { Path } from '$app/types';
	import { localizeHref } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import { isWorkId, loadWork } from '../../lib/work/record';
	import { loadList, type List, type ListPaths } from '../../lib/work/visit';
	import Constellation from '../../lib/presentation/Constellation.svelte';
	import Thumbnail from '../../lib/presentation/Thumbnail.svelte';
	import DiscoveryLayouts from '../../lib/presentation/DiscoveryLayouts.svelte';
	import SwipeDeck from '../../lib/presentation/SwipeDeck.svelte';
	import CatalogueControls from '../../lib/presentation/CatalogueControls.svelte';
	import {
		filterEntries,
		readFilters,
		researchPage,
		researchQuery,
		type BrowseFilters,
		type ResearchFacets
	} from '../../lib/presentation/catalogue';
	import { museumContext } from '../../lib/presentation/settings.svelte';
	import { draw, newSeed } from '../../lib/presentation/chance';

	const PAGE_SIZE = 48;
	const RESEARCH_BASE = '';
	let collection = $state<List | null>(null);
	let paths: ListPaths | null = $state(null);
	const SCOPES = ['days', 'pack', 'author', 'year'] as const;
	const scope = $derived.by(() => {
		const value = browser ? page.url.searchParams.get('scope') : null;
		return SCOPES.includes(value as (typeof SCOPES)[number])
			? (value as (typeof SCOPES)[number])
			: 'days';
	});
	let groupBy: 'pack' | 'author' | 'year' = $state('pack');
	let limit = $state(PAGE_SIZE);
	let loading = $state(true);
	let saved: string[] = $state([]);
	let restored = $state(false);
	let onlySaved = $state(false);
	let clearedSaved: string[] | null = $state(null);
	let resultTotal = $state(0);
	let loadingMore = $state(false);
	let failed = $state(false);
	let facets: ResearchFacets | null = $state(null);
	let resetSerial = $state(0);
	let drawing = $state(false);
	let nothingToDraw = $state(false);
	const corpus = $derived(
		facets !== null && browser && page.url.searchParams.get('source') !== 'public'
	);
	const filters = $derived(readFilters(browser ? page.url.searchParams : null));
	const requestKey = $derived(
		corpus ? researchQuery(filters) : scope === 'days' ? 'lists/days.json' : (paths?.[scope] ?? '')
	);
	const browseKey = $derived(JSON.stringify([corpus, requestKey, filters, resetSerial]));
	const SAVED_KEY = 'textmode-discovery-selection-v1';
	const VIEWS = ['pinterest', 'instagram', 'tinder', 'grid', 'relations'] as const;
	type View = (typeof VIEWS)[number];
	const id = $derived(browser ? page.url.searchParams.get('w') : null);
	const view = $derived.by((): View => {
		const requested = browser ? page.url.searchParams.get('view') : null;
		return VIEWS.includes(requested as View) ? (requested as View) : 'pinterest';
	});
	const constellation = $derived(view === 'relations');
	const discovery = $derived(view === 'pinterest' || view === 'instagram' || view === 'tinder');
	const works = $derived(collection?.works ?? []);
	const matched = $derived(corpus ? works : filterEntries(works, filters));
	const selected = $derived(matched.filter((entry) => saved.includes(entry.sha256)));
	const visible = $derived(discovery && onlySaved ? selected : matched);
	const total = $derived(
		discovery && onlySaved ? selected.length : corpus ? resultTotal : matched.length
	);
	const hasMore = $derived(corpus && works.length < resultTotal);
	const shown = $derived(visible.slice(0, limit));
	const heading = $derived.by(() => {
		if (view === 'pinterest') return m.discovery_pinterest_title();
		if (view === 'instagram') return m.discovery_instagram_title();
		if (view === 'tinder') return m.discovery_tinder_title();
		return m.explore_title();
	});
	const note = $derived.by(() => {
		if (view === 'pinterest') return m.discovery_pinterest_note();
		if (view === 'instagram') return m.discovery_instagram_note();
		return m.discovery_tinder_note();
	});
	const groups = $derived.by(() => {
		const result = new SvelteMap<string, typeof shown>();
		for (const entry of shown) {
			const key = String(entry[groupBy] ?? m.explore_unknown());
			result.set(key, [...(result.get(key) ?? []), entry]);
		}
		return [...result];
	});
	onMount(() => {
		try {
			const value: unknown = JSON.parse(localStorage.getItem(SAVED_KEY) ?? '[]');
			if (Array.isArray(value))
				saved = [
					...new Set(value.filter((id): id is string => typeof id === 'string' && isWorkId(id)))
				];
		} catch {
			/* Selection still works when storage is unavailable. */
		}
		restored = true;
	});
	$effect(() => {
		if (!restored) return;
		try {
			localStorage.setItem(SAVED_KEY, JSON.stringify(saved));
		} catch {
			/* Keep the selection for this visit. */
		}
	});
	function setSaved(sha256: string, value: boolean): void {
		saved = value ? [...new Set([...saved, sha256])] : saved.filter((id) => id !== sha256);
	}
	function toggle(sha256: string): void {
		setSaved(sha256, !saved.includes(sha256));
	}
	function navigate(values: Record<string, string>, clean = false): void {
		const query = new SvelteURLSearchParams(clean ? '' : page.url.search);
		query.set('view', view);
		if (page.url.searchParams.get('source') === 'public') query.set('source', 'public');
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
	function apply(filters: BrowseFilters): void {
		limit = PAGE_SIZE;
		navigate(filters);
	}
	function reset(): void {
		onlySaved = false;
		groupBy = 'pack';
		limit = PAGE_SIZE;
		resetSerial += 1;
		museumContext.workId = null;
		navigate({}, true);
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

	function clearSelection(): void {
		clearedSaved = [...saved];
		saved = [];
	}
	function restoreSelection(): void {
		if (clearedSaved) saved = [...new Set([...saved, ...clearedSaved])];
		clearedSaved = null;
	}
	async function more(): Promise<void> {
		const nextPage = view === 'tinder' || limit >= visible.length;
		if (hasMore && !onlySaved && nextPage) await appendPage();
		else limit += PAGE_SIZE;
	}
	async function appendPage(): Promise<void> {
		if (loadingMore) return;
		const key = browseKey;
		const query = requestKey;
		loadingMore = true;
		try {
			const result = await researchPage(RESEARCH_BASE, query, works.length);
			if (browseKey !== key) return;
			collection = { works: [...works, ...result.works] };
			resultTotal = result.total;
			limit += PAGE_SIZE;
		} catch {
			if (browseKey === key) failed = true;
		} finally {
			if (browseKey === key) loadingMore = false;
		}
	}

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
		let active = true;
		const controller = new AbortController();
		const research = corpus;
		const key = requestKey;
		const serial = resetSerial;
		loading = true;
		failed = false;
		loadingMore = false;
		collection = null;
		resultTotal = 0;
		limit = PAGE_SIZE;
		const request = research
			? researchPage(RESEARCH_BASE, key, 0, controller.signal)
			: loadList(key || null);
		void request
			.then((list) => {
				if (active && resetSerial === serial) {
					collection = list;
					resultTotal =
						research && list && 'total' in list ? Number(list.total) : (list?.works.length ?? 0);
					failed = list === null;
					loading = false;
				}
			})
			.catch(() => {
				if (active) {
					failed = true;
					loading = false;
				}
			});
		return () => {
			active = false;
			controller.abort();
		};
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
</script>

<svelte:head><title>{m.nav_explore()} · {m.museum_name()}</title></svelte:head>

<main
	class:discovery
	class:pinterest={view === 'pinterest'}
	class:instagram={view === 'instagram'}
	class:tinder={view === 'tinder'}
>
	<div class="explore-inner">
		{#if discovery}<p class="eyebrow">{m.discovery_eyebrow()}</p>{/if}
		<div class="intro">
			<h1>{heading}</h1>
			{#if discovery}<p>{note}</p>{/if}
		</div>
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
			{#if constellation}<label
					>{m.explore_group()}
					<select bind:value={groupBy}
						><option value="pack">{m.explore_group_pack()}</option><option value="author"
							>{m.explore_group_author()}</option
						><option value="year">{m.explore_group_year()}</option></select
					></label
				>{/if}
			{#if !corpus && isWorkId(id)}<a href={href(id)}>{m.explore_back()}</a>{/if}
			<div class="chance">
				<button type="button" onclick={reshuffle}>{m.explore_reshuffle()}</button>
				<button type="button" disabled={drawing} onclick={() => void surprise()}
					>{m.explore_surprise()}</button
				>
			</div>
			{#if discovery}
				<div class="selection-toggle" role="group" aria-label={m.discovery_collection_label()}>
					<button type="button" aria-pressed={!onlySaved} onclick={() => (onlySaved = false)}
						>{m.discovery_all()}</button
					>
					<button type="button" aria-pressed={onlySaved} onclick={() => (onlySaved = true)}
						>{m.discovery_selection({ count: selected.length })}</button
					>
				</div>
			{/if}
		</div>
		<p class="scope-note">
			{#if corpus}{m.browse_corpus_note({ count: facets?.dataset.works ?? resultTotal })}
			{:else if scope === 'days'}{m.browse_days_note()}
			{:else if scope === 'year'}{m.browse_year_note()}
			{:else}{m.browse_collection_note()}{/if}
		</p>
		<CatalogueControls {filters} entries={works} {corpus} {facets} {apply} {reset} />
		{#if onlySaved && saved.length}<button
				class="clear-selection"
				type="button"
				onclick={clearSelection}>{m.browse_clear_selection()}</button
			>{/if}
		{#if clearedSaved}<p class="selection-cleared" role="status">
				{m.browse_selection_cleared()}
				<button type="button" onclick={restoreSelection}>{m.browse_undo_clear()}</button>
			</p>{/if}
		{#if nothingToDraw}<p role="status">{m.explore_surprise_none()}</p>{/if}
		{#if loading}<p role="status">{m.explore_loading()}</p>
		{:else if failed && !works.length}<p role="alert">{m.browse_unavailable()}</p>
		{:else if !matched.length}<p class="empty-selection">{m.browse_no_results()}</p>
		{:else}
			<p class="count">
				{m.browse_results({ count: total })}
			</p>
			{#if view === 'tinder'}
				{#if onlySaved}
					{#if selected.length}<DiscoveryLayouts
							entries={shown}
							total={selected.length}
							view="pinterest"
							{saved}
							{toggle}
							{href}
						/>
					{:else}<p class="empty-selection">{m.discovery_selection_empty()}</p>{/if}
				{/if}
				<div hidden={onlySaved}>
					{#key browseKey}<SwipeDeck
							entries={matched}
							{total}
							{hasMore}
							{loadingMore}
							{more}
							{saved}
							{setSaved}
							{href}
							active={!onlySaved}
						/>{/key}
				</div>
			{:else if discovery && !visible.length}
				<p class="empty-selection">{m.discovery_selection_empty()}</p>
			{:else if view === 'pinterest' || view === 'instagram'}
				<DiscoveryLayouts entries={shown} {total} {view} {saved} {toggle} {href} />
			{:else if constellation}
				<p class="explanation">{m.explore_relations()}</p>
				<div class="constellations">
					{#each groups as [name, entries] (name)}
						<section class="cluster" aria-label={name}>
							<h2>{name}</h2>
							<Constellation {name} {entries} {href} />
						</section>
					{/each}
				</div>
			{:else}
				<div class="grid">
					{#each shown as entry (entry.sha256)}<Thumbnail
							{entry}
							href={href(entry.sha256)}
						/>{/each}
				</div>
			{/if}
			{#if (view !== 'tinder' || onlySaved) && (limit < visible.length || (!onlySaved && hasMore))}<button
					class="more"
					type="button"
					disabled={loadingMore}
					onclick={() => void more()}>{loadingMore ? m.explore_loading() : m.explore_more()}</button
				>{/if}
			{#if failed}<p role="alert">{m.browse_unavailable()}</p>{/if}
		{/if}
	</div>
</main>

<style>
	main {
		max-width: 90rem;
		margin: auto;
		padding: 1rem 1.5rem 4rem;
	}
	.discovery {
		max-width: none;
		min-height: calc(100dvh - 5rem);
		padding: 2rem 1.5rem 5rem;
		background: var(--discovery-bg);
		color: var(--discovery-ink);
		--bright: var(--discovery-ink);
		--ink: var(--discovery-ink);
		--dim: var(--discovery-dim);
		--line: var(--discovery-line);
		--panel: var(--discovery-paper);
	}
	.pinterest {
		--discovery-bg: #f5f3ee;
		--discovery-paper: #fffdf9;
		--discovery-ink: #292a25;
		--discovery-dim: #6e6e65;
		--discovery-line: #d9d7cf;
		--discovery-accent: #a53d32;
		--discovery-on-accent: #fff;
		--accent: #a53d32;
	}
	.instagram {
		--discovery-bg: #f8f8fa;
		--discovery-paper: #fff;
		--discovery-ink: #28242c;
		--discovery-dim: #716b78;
		--discovery-line: #dedbe2;
		--discovery-accent: #775074;
		--discovery-on-accent: #fff;
		--accent: #775074;
	}
	.tinder {
		--discovery-bg: #110e17;
		--discovery-paper: #211824;
		--discovery-ink: #fff0f5;
		--discovery-dim: #b5a0b1;
		--discovery-line: #513343;
		--discovery-accent: #f75380;
		--discovery-on-accent: #160c13;
		--accent: #f75380;
	}
	.explore-inner {
		max-width: 82rem;
		margin: auto;
	}
	.eyebrow {
		font: 0.65rem var(--mono);
		letter-spacing: 0.14em;
		color: var(--discovery-dim);
		margin: 0 0 1.5rem;
	}
	.intro {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 2rem;
		margin-bottom: 1.8rem;
	}
	.discovery h1 {
		font-size: clamp(2rem, 4vw, 3.3rem);
		letter-spacing: -0.055em;
		font-weight: 600;
		line-height: 1.1;
		margin: 0;
	}
	.intro > p {
		max-width: 22rem;
		font-size: 0.85rem;
		line-height: 1.6;
		color: var(--dim);
		margin: 0;
	}

	.chance {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}
	.selection-toggle {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		margin-left: auto;
	}
	.chance button,
	.selection-toggle button {
		margin: 0;
		border-radius: 2rem;
		font-size: 0.75rem;
		padding: 0.7rem 0.9rem;
		min-height: 44px;
	}
	.selection-toggle button[aria-pressed='true'] {
		border-color: var(--accent);
		color: var(--accent);
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
		margin-inline: auto;
		border-radius: 2rem;
		padding: 0.8rem 1.5rem;
	}
	h1 {
		font-size: clamp(1.3rem, 3vw, 2rem);
		font-weight: 400;
		color: var(--bright);
	}
	.toolbar {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
		align-items: center;
	}

	.scope-note {
		color: var(--dim);
		font-size: 0.75rem;
		line-height: 1.6;
		margin: 1rem 0;
		max-width: 65rem;
	}
	.clear-selection,
	.selection-cleared button {
		margin-top: 0;
		border-radius: 2rem;
		font-size: 0.75rem;
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
	}
	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr));
		gap: 1.5rem;
	}
	.explanation {
		max-width: 48rem;
		font-size: 0.85rem;
		line-height: 1.6;
		color: var(--dim);
	}
	.constellations {
		display: grid;
		gap: 2rem;
	}
	.cluster {
		border: 1px solid var(--line);
		border-radius: 1rem;
		padding: 1rem;
		background: var(--panel);
	}
	h2 {
		font: 1rem var(--mono);
		color: var(--accent);
		margin-block: 0 1.5rem;
		overflow-wrap: anywhere;
	}
	button {
		margin-top: 2rem;
		cursor: pointer;
	}
	@media (max-width: 760px) {
		.discovery {
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

		.tinder .eyebrow,
		.tinder .intro > p,
		.tinder .count {
			display: none;
		}
		.tinder .intro {
			margin-bottom: 1rem;
		}
		.tinder h1 {
			font-size: 1.5rem;
		}

		.tinder .toolbar {
			gap: 0.6rem;
			margin-bottom: 1rem;
		}
	}
</style>
