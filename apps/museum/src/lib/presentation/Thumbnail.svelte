<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { previewUrl } from './catalogue';
	import type { Entry } from '../work/visit';
	let { entry, href }: { entry: Entry; href: string } = $props();
	let failed = $state(false);
</script>

<a {href} class="thumbnail">
	<div class="image">
		{#if !failed && previewUrl(entry)}
			<img src={previewUrl(entry)!} alt="" loading="lazy" onerror={() => (failed = true)} />
		{/if}
	</div>
	<span class="title">{entry.title || entry.file}</span>
	<span class="credit">{[entry.author, entry.group, entry.year].filter(Boolean).join(' · ')}</span>
</a>

<style>
	.thumbnail {
		display: grid;
		gap: 0.4rem;
		min-width: 0;
		text-decoration: none;
	}
	.image {
		height: 12rem;
		background: #000;
		display: flex;
		align-items: center;
		justify-content: center;
		border: 1px solid var(--line);
	}
	img {
		max-width: 100%;
		max-height: 100%;
		object-fit: contain;
	}
	.title {
		color: var(--bright);
		overflow-wrap: anywhere;
		font-size: 0.85rem;
	}
	.credit {
		color: var(--dim);
		font-size: 0.75rem;
		overflow-wrap: anywhere;
	}
</style>
