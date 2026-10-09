<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { browser } from '$app/env';
	import { page } from '$app/state';
	import { m } from '#lib/paraglide/messages.js';
	import { loadFont } from '../../lib/work/font';
	import { isWorkId, loadWork, type Work } from '../../lib/work/record';
	import WorkScreen from '../../lib/work/WorkScreen.svelte';

	// The page is prerendered once; the work comes from `?w=<sha256>` in the browser, read from
	// the files `tm export` published. Ways out change the query, and the page follows it.
	let status: 'loading' | 'missing' | 'ready' = $state('loading');
	let work: Work | null = $state(null);
	let font: Uint8Array | null = $state(null);

	const id = $derived(browser ? page.url.searchParams.get('w') : null);

	$effect(() => {
		if (!browser) return;
		const wanted = id;
		if (!isWorkId(wanted)) {
			status = 'missing';
			return;
		}
		Promise.all([loadWork(wanted), loadFont()])
			.then(([loaded, bytes]) => {
				if (wanted !== id) return; // the visitor has moved on
				work = loaded;
				font = bytes;
				status = loaded ? 'ready' : 'missing';
				window.scrollTo({ top: 0 });
			})
			.catch(() => (status = 'missing')); // files unreachable or not a grid: nothing is shown
	});
</script>

<svelte:head>
	{#if work}<title>{work.record.title || work.record.file} · {m.museum_name()}</title>{/if}
</svelte:head>

{#if status === 'ready' && work && font}
	<WorkScreen {work} {font} />
{:else}
	<main>
		<p>{status === 'loading' ? m.work_loading() : m.work_missing()}</p>
	</main>
{/if}

<style>
	main {
		min-height: 80dvh;
		display: grid;
		place-content: center;
		padding-inline: 1rem;
		text-align: center;
	}
</style>
