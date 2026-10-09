<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { previewUrl } from './catalogue';
	import type { Entry } from '../work/visit';
	import { m } from '#lib/paraglide/messages.js';
	let {
		entry,
		eager = false,
		crop = false
	}: { entry: Entry; eager?: boolean; crop?: boolean } = $props();
	let failed = $state(false);
	const CELL_WIDTH = 8;
	const CELL_HEIGHT = 16;
	$effect(() => {
		if (entry.sha256) failed = false;
	});
</script>

<div
	class="artwork"
	class:crop
	style:--ratio={`${Math.max(1, entry.cols) * CELL_WIDTH} / ${Math.max(1, entry.rows) * CELL_HEIGHT}`}
>
	{#if failed || previewUrl(entry) === null}
		<span class="unavailable">{m.discovery_image_missing()}</span>
	{:else}
		<img
			src={previewUrl(entry)!}
			alt={entry.title || entry.file}
			loading={eager ? 'eager' : 'lazy'}
			decoding="async"
			onerror={() => (failed = true)}
		/>
	{/if}
</div>

<style>
	.artwork {
		width: 100%;
		aspect-ratio: var(--ratio);
		max-height: var(--art-height, 34rem);
		min-height: 5rem;
		background: #000;
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: hidden;
	}
	img {
		display: block;
		width: 100%;
		height: 100%;
		object-fit: contain;
		image-rendering: pixelated;
	}
	/* Cropped: every card the same shape, the work seen from its first screen. */
	.crop {
		aspect-ratio: 4 / 3;
	}
	.crop img {
		object-fit: cover;
		object-position: top;
	}
	.unavailable {
		padding: 2rem;
		font-size: 0.85rem;
		color: #aaa;
		text-align: center;
	}
</style>
