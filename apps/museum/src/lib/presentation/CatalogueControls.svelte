<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import type { Entry } from '../work/visit';
	import {
		FILTER_KEYS,
		UNKNOWN,
		valuesOf,
		type BrowseFilters,
		type ResearchFacets
	} from './catalogue';
	let {
		filters,
		entries,
		corpus,
		facets,
		apply,
		reset
	}: {
		filters: BrowseFilters;
		entries: Entry[];
		corpus: boolean;
		facets: ResearchFacets | null;
		apply: (filters: BrowseFilters) => void;
		reset: () => void;
	} = $props();
	const labels: Record<string, () => string> = {
		q: m.browse_search,
		words: m.browse_words,
		year: m.browse_year,
		author: m.browse_author,
		group: m.browse_group,
		archive: m.browse_archive,
		format: m.browse_format,
		kind: m.browse_kind,
		order: m.browse_sort,
		seed: m.explore_reshuffle
	};
	const kinds: Record<string, () => string> = {
		coloured_blocks: m.browse_coloured_blocks,
		text: m.browse_text,
		coloured_text: m.browse_coloured_text,
		blocks: m.browse_blocks,
		empty: m.browse_empty_kind
	};
	const fields = $derived(
		corpus
			? [
					{ key: 'year', values: facets?.years.map((v) => String(v.year)) ?? [] },
					{ key: 'archive', values: facets?.archives.map((v) => v.archive) ?? [] },
					{ key: 'format', values: facets?.formats.map((v) => v.format) ?? [] },
					{ key: 'kind', values: facets?.kinds.map((v) => v.kind) ?? [] }
				]
			: [
					{ key: 'year', values: valuesOf(entries, 'year') },
					{ key: 'author', values: valuesOf(entries, 'author') },
					{ key: 'group', values: valuesOf(entries, 'group') }
				]
	);
	const active = $derived(FILTER_KEYS.filter((key) => key !== 'seed' && filters[key]));
	const advanced = $derived(active.some((key) => key !== 'q'));
	function submit(event: SubmitEvent): void {
		event.preventDefault();
		const data = new FormData(event.currentTarget as HTMLFormElement);
		apply(
			Object.fromEntries(
				FILTER_KEYS.map((key) => [key, String(data.get(key) ?? '')])
			) as BrowseFilters
		);
	}
	function changed(event: Event): void {
		(event.currentTarget as HTMLSelectElement).form?.requestSubmit();
	}
	function remove(key: keyof BrowseFilters): void {
		apply({ ...filters, [key]: '' });
	}
	function optionLabel(key: string, value: string): string {
		if (value === UNKNOWN) return m.explore_unknown();
		if (key === 'kind') return kinds[value]?.() ?? value.replaceAll('_', ' ');
		return value;
	}
</script>

<form class="catalogue-controls" onsubmit={submit} role="search" aria-label={m.browse_search()}>
	<input type="hidden" name="seed" value={filters.seed} />
	<div class="search-line">
		<label class="search-box"
			><span>{m.browse_search()}</span>
			<input
				type="search"
				name="q"
				value={filters.q}
				placeholder={corpus ? m.browse_corpus_placeholder() : m.browse_placeholder()}
			/>
		</label>
		<button class="search-submit" type="submit">{m.browse_search()}</button>
		<button type="button" class="reset" onclick={reset}>{m.browse_reset()}</button>
	</div>
	<details open={advanced}>
		<summary
			>{m.browse_filters_sort()}{#if active.length}<span>{active.length}</span>{/if}</summary
		>
		<div class="filter-fields">
			{#each fields as field (field.key)}
				<label
					>{labels[field.key]()}<select
						name={field.key}
						value={filters[field.key as keyof BrowseFilters]}
						onchange={changed}
					>
						<option value="">{m.browse_any()}</option>
						{#each field.values as value (value)}<option {value}
								>{optionLabel(field.key, value)}</option
							>{/each}
					</select></label
				>
			{/each}
			{#if corpus}<label class="words"
					>{m.browse_words()}<input
						name="words"
						type="search"
						value={filters.words}
						placeholder={m.browse_words_placeholder()}
					/></label
				>{/if}
			<label
				>{m.browse_sort()}<select name="order" value={filters.order} onchange={changed}>
					<option value="">{m.browse_discovery_order()}</option>
					{#if !corpus}<option value="title">{m.browse_sort_title()}</option>{/if}
					<option value="year">{m.browse_sort_year()}</option>
					<option value="tall">{m.browse_sort_tall()}</option>
					<option value="wide">{m.browse_sort_wide()}</option>
				</select></label
			>
		</div>
	</details>
	{#if active.length}<div class="filter-chips" aria-label={m.browse_active_filters()}>
			{#each active as key (key)}<button
					type="button"
					onclick={() => remove(key)}
					aria-label={m.browse_remove_filter({ name: labels[key]() })}
				>
					{labels[key]()} : {key === 'order'
						? m.browse_sort()
						: optionLabel(key, filters[key])}<span aria-hidden="true">×</span>
				</button>{/each}
		</div>{/if}
</form>

<style>
	.catalogue-controls {
		margin-block: 1.2rem;
		padding: 1rem;
		border: 1px solid var(--line);
		border-radius: 0.75rem;
		background: var(--panel);
	}
	.search-line {
		display: flex;
		align-items: end;
		gap: 0.7rem;
	}
	label {
		display: grid;
		gap: 0.4rem;
		color: var(--dim);
		font-size: 0.72rem;
		min-width: 0;
	}
	.search-box {
		flex: 1;
	}
	input,
	select,
	button {
		font: inherit;
		border: 1px solid var(--line);
		color: var(--ink);
		background: var(--discovery-bg, var(--surface));
		padding: 0.7rem 0.8rem;
		border-radius: 0.4rem;
		min-height: 44px;
		box-sizing: border-box;
	}
	input,
	select {
		width: 100%;
		font-size: 0.85rem;
	}
	button {
		font-size: 0.8rem;
		cursor: pointer;
	}
	.search-submit {
		background: var(--ink);
		color: var(--discovery-bg, var(--surface));
		border-color: var(--ink);
	}
	.reset {
		background: transparent;
	}
	details {
		margin-top: 1rem;
	}
	summary {
		cursor: pointer;
		font-size: 0.8rem;
		color: var(--ink);
	}
	summary span {
		display: inline-block;
		margin-left: 0.6rem;
		border-radius: 1rem;
		background: var(--line);
		padding: 0.1rem 0.5rem;
		font: 0.65rem var(--mono);
	}
	.filter-fields {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
		gap: 0.8rem;
		padding-top: 1rem;
	}
	.words {
		grid-column: span 2;
	}
	.filter-chips {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-top: 1rem;
	}
	.filter-chips button {
		font-size: 0.7rem;
		min-height: 32px;
		padding: 0.4rem 0.7rem;
		border-radius: 2rem;
	}
	.filter-chips span {
		margin-left: 0.7rem;
	}
	@media (max-width: 600px) {
		.search-line {
			flex-wrap: wrap;
		}
		.search-box {
			flex-basis: 100%;
		}
		.search-line button {
			flex: 1;
		}
		.words {
			grid-column: 1 / -1;
		}
	}
</style>
