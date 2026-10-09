<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { m } from '#lib/paraglide/messages.js';
	import { checkFont } from '../../lib/work/draw';
	import { isWorkId, loadWork, type Work } from '../../lib/work/record';
	import WorkScreen from '../../lib/work/WorkScreen.svelte';
	// The same bitmap font as the pipeline's renderer (corpus/fonts, libansilove's VGA 8×16).
	import fontUrl from '../../../../../corpus/fonts/ibm-vga-8x16.f16?url';

	// The page is prerendered once; the work comes from `?w=<sha256>` in the browser, read from
	// the files `tm export` published.
	let status: 'loading' | 'missing' | 'ready' = $state('loading');
	let work: Work | null = $state(null);
	let font: Uint8Array | null = $state(null);

	onMount(async () => {
		const id = new URL(window.location.href).searchParams.get('w');
		if (!isWorkId(id)) {
			status = 'missing';
			return;
		}
		try {
			const [loaded, bytes] = await Promise.all([
				loadWork(id),
				fetch(fontUrl).then((r) => r.arrayBuffer())
			]);
			work = loaded;
			font = checkFont(new Uint8Array(bytes));
			status = loaded ? 'ready' : 'missing';
		} catch {
			status = 'missing'; // files unreachable or not a grid: nothing is shown
		}
	});
</script>

{#if status === 'ready' && work && font}
	<WorkScreen {work} {font} />
{:else}
	<main>
		<p>{status === 'loading' ? m.work_loading() : m.work_missing()}</p>
	</main>
{/if}

<style>
	main {
		min-height: 100dvh;
		display: grid;
		place-content: center;
	}
</style>
