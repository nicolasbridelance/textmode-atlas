<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	let {
		saved,
		onclick,
		compact = false
	}: { saved: boolean; onclick: () => void; compact?: boolean } = $props();
</script>

<button
	type="button"
	class:compact
	class:saved
	aria-pressed={saved}
	aria-label={saved ? m.discovery_unsave() : m.discovery_save()}
	{onclick}
>
	<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h12v18l-6-4-6 4Z" /></svg>
	{#if !compact}<span>{saved ? m.discovery_saved() : m.discovery_save()}</span>{/if}
</button>

<style>
	button {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.45rem;
		border: 1px solid var(--discovery-line, var(--line));
		border-radius: 2rem;
		color: inherit;
		background: var(--discovery-paper, var(--panel));
		padding: 0.6rem 0.9rem;
		font: inherit;
		font-size: 0.8rem;
		cursor: pointer;
		min-height: 44px;
	}
	button:hover {
		border-color: currentColor;
	}
	button.saved {
		background: var(--discovery-accent, #f54770);
		color: var(--discovery-on-accent, #fff);
		border-color: transparent;
	}
	button.compact {
		width: 44px;
		height: 44px;
		padding: 0.6rem;
	}
	svg {
		width: 19px;
		height: 19px;
		fill: none;
		stroke: currentColor;
		stroke-width: 1.7;
	}
	.saved svg {
		fill: currentColor;
	}
</style>
