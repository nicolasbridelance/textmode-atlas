<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import {
		AUTO,
		CAPTIONS,
		FITS,
		LAYOUTS,
		MAX_COLUMNS,
		PAPERS,
		PRESETS,
		type Display,
		type Layout
	} from './display';
	let { display, apply }: { display: Display; apply: (display: Display) => void } = $props();
	const layoutNames: Record<Layout, () => string> = {
		wall: m.display_wall,
		grid: m.display_grid,
		feed: m.display_feed,
		deck: m.display_deck
	};
	const names: Record<string, () => string> = {
		whole: m.display_fit_whole,
		crop: m.display_fit_crop,
		none: m.display_caption_none,
		short: m.display_caption_short,
		full: m.display_caption_full,
		light: m.display_paper_light,
		dark: m.display_paper_dark,
		museum: m.display_paper_museum
	};
	const columnChoices = Array.from({ length: MAX_COLUMNS + 1 }, (_, count) => count);
	function choose(layout: Layout): void {
		apply({ layout, ...PRESETS[layout] });
	}
	function change<K extends keyof Display>(key: K, value: Display[K]): void {
		apply({ ...display, [key]: value });
	}
</script>

<div class="display-controls">
	<div class="layouts" role="group" aria-label={m.display_layout()}>
		{#each LAYOUTS as layout (layout)}
			<button
				type="button"
				aria-pressed={display.layout === layout}
				data-layout={layout}
				onclick={() => choose(layout)}>{layoutNames[layout]()}</button
			>
		{/each}
	</div>
	{#if display.layout !== 'deck'}
		<details class="settings">
			<summary>{m.display_settings()}</summary>
			<div class="fields">
				<label
					>{m.display_columns()}<select
						name="cols"
						value={String(display.cols)}
						onchange={(event) => change('cols', Number(event.currentTarget.value))}
					>
						{#each columnChoices as count (count)}<option value={String(count)}
								>{count === AUTO ? m.display_columns_auto() : count}</option
							>{/each}
					</select></label
				>
				<label
					>{m.display_fit()}<select
						name="fit"
						value={display.fit}
						onchange={(event) => change('fit', event.currentTarget.value as Display['fit'])}
					>
						{#each FITS as fit (fit)}<option value={fit}>{names[fit]()}</option>{/each}
					</select></label
				>
				<label
					>{m.display_caption()}<select
						name="caption"
						value={display.caption}
						onchange={(event) => change('caption', event.currentTarget.value as Display['caption'])}
					>
						{#each CAPTIONS as caption (caption)}<option value={caption}>{names[caption]()}</option
							>{/each}
					</select></label
				>
				<label
					>{m.display_paper()}<select
						name="paper"
						value={display.paper}
						onchange={(event) => change('paper', event.currentTarget.value as Display['paper'])}
					>
						{#each PAPERS as paper (paper)}<option value={paper}>{names[paper]()}</option>{/each}
					</select></label
				>
			</div>
		</details>
	{/if}
</div>

<style>
	.display-controls {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.8rem 1.2rem;
	}
	.layouts {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}
	button,
	select {
		font: inherit;
		border: 1px solid var(--line);
		color: var(--ink);
		background: transparent;
		min-height: 44px;
	}
	button {
		border-radius: 2rem;
		font-size: 0.75rem;
		padding: 0.7rem 0.9rem;
		cursor: pointer;
	}
	button[aria-pressed='true'] {
		border-color: var(--accent);
		color: var(--accent);
	}
	summary {
		cursor: pointer;
		font-size: 0.8rem;
	}
	.fields {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
		gap: 0.8rem;
		padding-top: 0.8rem;
	}
	label {
		display: grid;
		gap: 0.4rem;
		color: var(--dim);
		font-size: 0.72rem;
	}
	select {
		padding: 0.6rem;
		border-radius: 0.4rem;
		font-size: 0.85rem;
		background: var(--panel);
	}
</style>
