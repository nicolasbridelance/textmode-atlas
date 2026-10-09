<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { getLocale } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import { loadFont } from '../lib/work/font';
	import { loadWork, type Work } from '../lib/work/record';
	import { loadList, workOfTheDay } from '../lib/work/visit';
	import WorkScreen from '../lib/work/WorkScreen.svelte';
	import { localizeHref } from '#lib/paraglide/runtime.js';

	// The entrance is a work, the same for everyone today (foundation document, "Arriver"),
	// drawn by `tm lists` among works the museum may show. Without it, the dedication.
	let work: Work | null = $state(null);
	let font: Uint8Array | null = $state(null);
	const today = new Date();

	onMount(async () => {
		const entry = workOfTheDay(await loadList('lists/days.json'), today);
		if (!entry) return;
		const [loaded, bytes] = await Promise.all([loadWork(entry.sha256), loadFont()]);
		if (loaded?.grid) [work, font] = [loaded, bytes];
	});

	const date = $derived(
		new Intl.DateTimeFormat(getLocale(), { day: 'numeric', month: 'long' }).format(today)
	);
</script>

{#if work && font}
	<WorkScreen {work} {font} eyebrow={m.day_label({ date })} />
{:else}
	<main>
		<h1>{m.museum_name()}</h1>
		<p>{m.dedication()}</p>
		<p><a href={localizeHref('/explore')}>{m.atlas_enter()}</a></p>
	</main>
{/if}

<style>
	main {
		min-height: 80dvh;
		display: grid;
		place-content: center;
		text-align: center;
		padding-inline: 1rem;
	}
	h1 {
		font-weight: 400;
		font-size: 1.25rem;
		color: var(--bright);
	}
</style>
