<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	// Room 1, the gallery: one work at a time, on black, at full scale; the label beside it, the
	// ways out on the other side, everything on a key (foundation document, "Expérience du
	// visiteur"). The site shows what the export published and decides nothing.
	import type { Path } from '$app/types';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { getLocale, localizeHref } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import Cartel from './Cartel.svelte';
	import CellInspector from './CellInspector.svelte';
	import Help from './Help.svelte';
	import { loadWork, type Work } from './record';
	import { BBS_BAUD, lastByte, secondsAt } from './time';
	import { type Lists, loadList, seedOf, type Ways as WaysOut, waysOut } from './visit';
	import Ways from './Ways.svelte';
	import WorkCanvas from './WorkCanvas.svelte';
	import ResearchPanel from '../atlas/ResearchPanel.svelte';
	import { fileUrl } from '../files';

	// Modem speeds of the BBS years, and whole zooms down to the cell.
	const SPEEDS = [300, 1200, BBS_BAUD, 9600, 14400, 28800, 57600]; // eslint-disable-line @typescript-eslint/no-magic-numbers
	const ZOOMS = [1, 2, 3, 4, 6, 8, 12, 16]; // eslint-disable-line @typescript-eslint/no-magic-numbers
	const PERCENT = 100;
	const SWIPE_PX = 60;
	const EPSILON = 1e-9;
	const DAYS = 'lists/days.json';

	let {
		work,
		font,
		eyebrow = null
	}: { work: Work; font: Uint8Array; eyebrow?: string | null } = $props();

	const locale = $derived(getLocale());
	const record = $derived(work.record);
	const title = $derived(record.title || record.file);
	const signed = $derived(
		[record.credit.author, record.credit.group].filter(Boolean).join(' / ') || m.work_unsigned()
	);

	let showAll = $state(false);
	let replay = $state(0);
	let baud = $state(BBS_BAUD);
	let zoom = $state(0);
	let scale = $state(1);
	let cell: number | null = $state(null);
	let help = $state(false);
	let lists: Lists = $state({ pack: null, author: null, year: null, days: null });

	const seconds = $derived(work.grid ? secondsAt(lastByte(work.grid), baud) : null);
	const ways: WaysOut = $derived(
		waysOut(record.sha256, record.credit.pack, lists, seedOf(record.sha256))
	);

	$effect(() => {
		const paths = record.lists;
		void record.sha256; // a new work starts its arrival again, with nothing pointed at
		showAll = false;
		cell = null;
		Promise.all([
			loadList(paths?.pack ?? null),
			loadList(paths?.author ?? null),
			loadList(paths?.year ?? null),
			loadList(DAYS)
		]).then(([pack, author, year, days]) => (lists = { pack, author, year, days }));
	});

	// The ways out are a few kilobytes each: fetched ahead, they open at once.
	$effect(() => {
		for (const entry of Object.values(ways)) if (entry) void loadWork(entry.sha256);
	});

	function hrefOf(sha256: string): string {
		return `${resolve(localizeHref('/work') as Path)}?w=${sha256}`;
	}

	function go(key: keyof WaysOut): void {
		const entry = ways[key];
		if (entry) void goto(hrefOf(entry.sha256));
	}

	function zoomBy(step: number): void {
		const larger = ZOOMS.find((z) => z > scale + EPSILON);
		const smaller = [...ZOOMS].reverse().find((z) => z < scale - EPSILON);
		const next = step > 0 ? larger : smaller;
		if (next !== undefined) zoom = next;
	}

	const KEYS: Record<string, () => void> = {
		' ': () => (showAll = true),
		ArrowLeft: () => go('previous'),
		ArrowRight: () => go('next'),
		a: () => go('signature'),
		y: () => go('year'),
		r: () => go('chance'),
		'+': () => zoomBy(1),
		'=': () => zoomBy(1),
		'-': () => zoomBy(-1),
		'0': () => (zoom = 0),
		'?': () => (help = !help)
	};

	function onkeydown(event: KeyboardEvent): void {
		const target = event.target as HTMLElement | null;
		const typing = target?.closest('input, select, textarea, dialog');
		const action = KEYS[event.key];
		if (!action || typing || event.ctrlKey || event.metaKey || event.altKey) return;
		event.preventDefault();
		action();
	}

	let touchX = 0;
	let touchY = 0;
	function ontouchstart(event: TouchEvent): void {
		touchX = event.touches[0].clientX;
		touchY = event.touches[0].clientY;
	}
	function ontouchend(event: TouchEvent): void {
		if (scale > 1) return; // zoomed in, a swipe pans the work
		const dx = event.changedTouches[0].clientX - touchX;
		const dy = event.changedTouches[0].clientY - touchY;
		if (Math.abs(dx) > SWIPE_PX && Math.abs(dx) > 2 * Math.abs(dy)) {
			go(dx < 0 ? 'next' : 'previous');
		}
	}
</script>

<svelte:window {onkeydown} />

<div class="screen">
	<aside class="cartel">
		<Cartel {record} {locale} seconds={work.grid ? seconds : null} {baud} {eyebrow} />
		{#if record.research}<ResearchPanel research={record.research} {locale} />{/if}
	</aside>

	<!-- A swipe is a shortcut for the arrow keys and the ways out: nothing is reachable only by it. -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="stage" {ontouchstart} {ontouchend}>
		{#if work.grid}
			<WorkCanvas
				grid={work.grid}
				{font}
				label={`${title}, ${signed}`}
				{showAll}
				{replay}
				{baud}
				{zoom}
				bind:scale
				bind:cell
			/>
		{:else if record.shown === 'files'}
			<img
				class="conservation"
				src={fileUrl(`works/${record.sha256}/conservation.png`)}
				alt={`${title}, ${signed}`}
			/>
		{:else}
			<p class="not-shown">{m.work_not_shown()}</p>
		{/if}
	</div>

	<aside class="tools">
		{#if work.grid}
			<div class="controls">
				<button type="button" onclick={() => (showAll = true)}>{m.work_show_all()}</button>
				<button
					type="button"
					onclick={() => {
						showAll = false;
						replay += 1;
					}}>{m.work_replay()}</button
				>
				<label>
					<span class="visually-hidden">{m.work_speed()}</span>
					<select bind:value={baud}>
						{#each SPEEDS as speed (speed)}
							<option value={speed}>{m.work_baud({ baud: speed })}</option>
						{/each}
					</select>
				</label>
			</div>
			<div class="controls zoom" role="group" aria-label={m.work_zoom()}>
				<button type="button" onclick={() => zoomBy(-1)} aria-label={m.work_zoom_out()}>−</button>
				<button
					type="button"
					onclick={() => (zoom = 0)}
					aria-label={m.work_zoom_fit()}
					aria-pressed={zoom === 0}
					class="scale">{scale >= 1 ? `${scale}×` : `${Math.round(scale * PERCENT)} %`}</button
				>
				<button type="button" onclick={() => zoomBy(1)} aria-label={m.work_zoom_in()}>+</button>
				<button type="button" class="help" onclick={() => (help = true)}>{m.help_open()}</button>
			</div>
			<CellInspector grid={work.grid} {cell} {baud} {locale} />
		{/if}
		<Ways {ways} {hrefOf} />
	</aside>
</div>

<Help bind:open={help} />

<style>
	.screen {
		display: grid;
		grid-template-areas: 'stage' 'cartel' 'tools';
		gap: 1.5rem;
		padding: 0 0 4rem;
	}
	.stage {
		grid-area: stage;
		min-width: 0;
	}
	.conservation {
		max-width: 100%;
		height: auto;
		image-rendering: pixelated;
		display: block;
		margin-inline: auto;
	}
	.cartel {
		grid-area: cartel;
		padding-inline: 1rem;
	}
	.tools {
		grid-area: tools;
		padding-inline: 1rem;
		display: grid;
		gap: 1rem;
		align-content: start;
	}
	@media (min-width: 1100px) {
		.screen {
			grid-template-columns: minmax(14rem, 19rem) minmax(0, 1fr) minmax(14rem, 19rem);
			grid-template-areas: 'cartel stage tools';
			gap: 2rem;
			padding: 0 1.5rem 3rem;
		}
		.cartel,
		.tools {
			position: sticky;
			top: 3.5rem;
			align-self: start;
			max-height: calc(100dvh - 4.5rem);
			overflow: auto;
			padding-inline: 0;
			scrollbar-width: thin;
		}
	}
	.controls {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		align-items: center;
	}
	button,
	select {
		background: none;
		border: 1px solid var(--line);
		color: var(--ink);
		font: inherit;
		font-size: 0.75rem;
		padding: 0.3rem 0.55rem;
		border-radius: 2px;
		cursor: pointer;
	}
	select {
		background: #000;
	}
	button:hover,
	button:focus-visible,
	select:hover,
	select:focus-visible {
		color: var(--bright);
		border-color: var(--dim);
	}
	.zoom button {
		min-width: 2rem;
	}
	.scale {
		font-family: var(--mono);
		min-width: 3.6rem;
	}
	.help {
		margin-inline-start: auto;
	}
	.not-shown {
		min-height: 40dvh;
		display: grid;
		place-items: center;
		text-align: center;
		color: var(--dim);
		border: 1px dashed var(--line);
		margin: 0 1rem;
		padding: 2rem;
	}
	.visually-hidden {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip-path: inset(50%);
		white-space: nowrap;
	}
</style>
