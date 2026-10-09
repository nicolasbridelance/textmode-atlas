<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import type { Entry } from '../work/visit';
	import ArtworkPreview from './ArtworkPreview.svelte';
	import SaveButton from './SaveButton.svelte';
	import { AUTO, type Display } from './display';
	import { selection } from './selection.svelte';
	let {
		entries,
		display,
		href
	}: { entries: Entry[]; display: Display; href: (id: string) => string } = $props();
	function credit(entry: Entry): string {
		return [entry.author, entry.group].filter(Boolean).join(' / ') || m.explore_unknown();
	}
</script>

<div
	class="gallery"
	data-layout={display.layout}
	class:auto={display.cols === AUTO}
	class:many={display.cols > 2}
	style:--cols={display.cols || null}
>
	{#each entries as entry, index (entry.sha256)}
		<article class="card">
			<a class="image" href={href(entry.sha256)}
				><ArtworkPreview {entry} crop={display.fit === 'crop'} eager={index === 0} /></a
			>
			<div class="caption" class:none={display.caption === 'none'}>
				{#if display.caption !== 'none'}
					<div>
						<a class="title" href={href(entry.sha256)}>{entry.title || entry.file}</a>
						<p>
							{credit(entry)}{#if entry.year}
								· {entry.year}{/if}
						</p>
						{#if display.caption === 'full'}
							<p class="more">
								{entry.pack || m.discovery_archive()} · {entry.file} · {entry.cols} × {entry.rows}
							</p>
						{/if}
					</div>
				{/if}
				<SaveButton
					saved={selection.has(entry.sha256)}
					onclick={() => selection.toggle(entry.sha256)}
					compact={display.caption !== 'full'}
				/>
			</div>
		</article>
	{/each}
</div>

<style>
	.gallery {
		--gap: 1.2rem;
		gap: var(--gap);
	}
	/* The wall: whole works in columns, each as tall as it is. */
	[data-layout='wall'] {
		columns: var(--cols, 4);
		column-gap: var(--gap);
	}
	[data-layout='wall'] .card {
		break-inside: avoid;
		margin-bottom: 1.7rem;
	}
	/* The grid and the feed: aligned rows. */
	[data-layout='grid'],
	[data-layout='feed'] {
		display: grid;
		grid-template-columns: repeat(var(--cols, 4), minmax(0, 1fr));
		align-items: start;
	}
	[data-layout='grid'].auto {
		grid-template-columns: repeat(auto-fill, minmax(12rem, 1fr));
	}
	[data-layout='feed'] {
		--gap: 2.5rem;
		max-width: calc(var(--cols, 1) * 38rem);
		margin: auto;
	}
	.image {
		display: block;
		border-radius: 0.8rem;
		overflow: hidden;
		background: #000;
		transition: box-shadow 0.2s;
	}
	[data-layout='feed'] .image {
		--art-height: 42rem;
	}
	.image:hover {
		box-shadow: 0 7px 22px #0002;
	}
	.caption {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 0.5rem;
		padding: 0.7rem 0.2rem 0;
	}
	.caption.none {
		justify-content: flex-end;
		padding-top: 0.3rem;
	}
	.caption > div {
		min-width: 0;
	}
	.title {
		display: block;
		font-size: 0.94rem;
		font-weight: 650;
		text-decoration: none;
		overflow-wrap: anywhere;
		color: var(--ink);
	}
	.caption p {
		font-size: 0.75rem;
		line-height: 1.5;
		margin: 0.3rem 0 0;
		color: var(--dim);
		overflow-wrap: anywhere;
	}
	@media (max-width: 1100px) {
		[data-layout='wall'].auto {
			columns: 3;
		}
	}
	@media (max-width: 760px) {
		.gallery {
			--gap: 0.8rem;
		}
		[data-layout='wall'].auto,
		[data-layout='wall'].many {
			columns: 2;
		}
		[data-layout='grid'].auto,
		[data-layout='grid'].many {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
		[data-layout='feed'] {
			grid-template-columns: minmax(0, 1fr);
		}
		.title {
			font-size: 0.8rem;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.image {
			transition: none;
		}
	}
</style>
