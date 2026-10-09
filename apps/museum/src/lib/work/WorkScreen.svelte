<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { getLocale } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import { descriptorBadge, GRID_PAGE, levelBadge } from './audience';
	import type { Work } from './record';
	import WorkCanvas from './WorkCanvas.svelte';

	let { work, font }: { work: Work; font: Uint8Array } = $props();

	const locale = $derived(getLocale());
	const record = $derived(work.record);
	const credit = $derived(record.credit);
	const signed = $derived(
		[credit.author, credit.group].filter(Boolean).join(' / ') || m.work_unsigned()
	);
	const title = $derived(record.title || record.file);
	const level = $derived(levelBadge(record.audience.level, locale));
	const marks = $derived(
		[...record.audience.descriptors, ...record.audience.notices].map((code) =>
			descriptorBadge(code, locale)
		)
	);

	let showAll = $state(false);
	let replay = $state(0);

	function onkeydown(event: KeyboardEvent): void {
		if (event.key === ' ' && event.target === document.body) {
			event.preventDefault();
			showAll = true;
		}
	}
</script>

<svelte:window {onkeydown} />

<article>
	{#if work.grid}
		<WorkCanvas grid={work.grid} {font} label={`${title}, ${signed}`} {showAll} {replay} />
		<p class="controls">
			<button type="button" onclick={() => (showAll = true)}>{m.work_show_all()}</button>
			<button
				type="button"
				onclick={() => {
					showAll = false;
					replay += 1;
				}}>{m.work_replay()}</button
			>
		</p>
	{:else}
		<p class="not-shown">{m.work_not_shown()}</p>
	{/if}

	<header>
		<h1>{title}</h1>
		<p class="credit">{signed}</p>
		{#if credit.pack}
			<p>{m.work_in_pack({ pack: credit.pack, year: record.year ?? '?' })}</p>
		{/if}
		<p>{m.work_size({ cols: record.grid.cols, rows: record.grid.rows })}</p>
	</header>

	<section class="audience" aria-label={m.work_audience()}>
		<img src={level.src} alt={level.label} title={level.label} height="32" />
		{#each marks as mark (mark.src)}
			<img src={mark.src} alt={mark.label} title={mark.label} height="24" />
		{/each}
		{#if !record.audience.reviewed}
			<span class="note">{m.work_unreviewed()}</span>
		{/if}
		<a href={GRID_PAGE[locale] ?? GRID_PAGE.en}>{m.work_grid_link()}</a>
	</section>

	<nav class="links">
		{#if credit.url && credit.archive}
			<a href={credit.url} rel="external">{m.work_source({ archive: credit.archive })}</a>
		{/if}
		<a href={record.withdraw} rel="external">{m.work_withdraw()}</a>
	</nav>
</article>

<style>
	article {
		max-width: 72rem;
		margin-inline: auto;
		padding: 1rem;
		padding-block-end: 4rem;
	}
	header h1 {
		font-weight: 400;
		font-size: 1.1rem;
		color: #fff;
		margin-block: 1rem 0.25rem;
	}
	header p {
		margin: 0.15rem 0;
	}
	.credit {
		color: #ddd;
	}
	.controls {
		display: flex;
		gap: 0.75rem;
		justify-content: center;
	}
	button {
		background: none;
		border: 1px solid #333;
		color: #aaa;
		font: inherit;
		font-size: 0.8rem;
		padding: 0.3rem 0.6rem;
		cursor: pointer;
	}
	.audience {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.5rem;
		margin-block: 1rem;
		font-size: 0.85rem;
	}
	.audience img {
		image-rendering: pixelated;
	}
	.note {
		color: #777;
	}
	a {
		color: #aaa;
	}
	.links {
		display: flex;
		flex-wrap: wrap;
		gap: 1.25rem;
		font-size: 0.9rem;
	}
	.not-shown {
		padding: 3rem 0;
		text-align: center;
	}
</style>
