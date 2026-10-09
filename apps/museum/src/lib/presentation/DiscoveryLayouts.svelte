<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import type { Entry } from '../work/visit';
	import ArtworkPreview from './ArtworkPreview.svelte';
	import SaveButton from './SaveButton.svelte';
	let {
		entries,
		total,
		view,
		saved,
		toggle,
		href
	}: {
		entries: Entry[];
		total: number;
		view: 'pinterest' | 'instagram';
		saved: string[];
		toggle: (id: string) => void;
		href: (id: string) => string;
	} = $props();
	function credit(entry: Entry): string {
		return [entry.author, entry.group].filter(Boolean).join(' / ') || m.explore_unknown();
	}
</script>

{#if view === 'pinterest'}
	<div class="masonry" data-layout="pinterest">
		{#each entries as entry (entry.sha256)}
			<article class="pin">
				<a class="pin-image" href={href(entry.sha256)}><ArtworkPreview {entry} /></a>
				<div class="pin-caption">
					<div>
						<a class="title" href={href(entry.sha256)}>{entry.title || entry.file}</a>
						<p>
							{credit(entry)}{#if entry.year}
								· {entry.year}{/if}
						</p>
					</div>
					<SaveButton
						saved={saved.includes(entry.sha256)}
						onclick={() => toggle(entry.sha256)}
						compact
					/>
				</div>
			</article>
		{/each}
	</div>
{:else}
	<div class="feed-layout" data-layout="instagram">
		<div class="feed">
			{#each entries as entry, index (entry.sha256)}
				<article class="post">
					<header class="post-head">
						<span class="avatar" aria-hidden="true"
							>{(entry.author || entry.group || '?').slice(0, 1).toUpperCase()}</span
						>
						<div>
							<strong>{credit(entry)}</strong><span
								>{entry.pack || m.discovery_archive()}{#if entry.year}
									· {entry.year}{/if}</span
							>
						</div>
						<span class="post-number">{String(index + 1).padStart(2, '0')}</span>
					</header>
					<a class="post-image" href={href(entry.sha256)}
						><ArtworkPreview {entry} eager={index === 0} /></a
					>
					<div class="post-body">
						<div class="post-actions">
							<a class="open" href={href(entry.sha256)}
								>{m.discovery_open()} <span aria-hidden="true">↗</span></a
							>
							<SaveButton
								saved={saved.includes(entry.sha256)}
								onclick={() => toggle(entry.sha256)}
							/>
						</div>
						<h2>{entry.title || entry.file}</h2>
						<p>{entry.file} <span>· {entry.cols} × {entry.rows}</span></p>
					</div>
				</article>
			{/each}
		</div>
		<aside class="feed-aside">
			<span class="aside-mark" aria-hidden="true">Aa<span>█</span></span>
			<h2>{m.discovery_feed_aside_title()}</h2>
			<p>{m.discovery_feed_aside_note()}</p>
			<hr />
			<span class="aside-label">{m.discovery_collection_label()}</span>
			<strong>{m.explore_count({ count: total })}</strong>
			<p class="local-note">{m.discovery_local_note()}</p>
		</aside>
	</div>
{/if}

<style>
	.masonry {
		columns: 4;
		column-gap: 1.2rem;
	}
	.pin {
		break-inside: avoid;
		margin-bottom: 1.7rem;
	}
	.pin-image {
		display: block;
		border-radius: 1rem;
		overflow: hidden;
		background: #000;
		transition: box-shadow 0.2s;
	}
	.pin-image:hover {
		box-shadow: 0 7px 22px #0002;
	}
	.pin-caption {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 0.5rem;
		padding: 0.8rem 0.25rem 0;
	}
	.pin-caption > div {
		min-width: 0;
	}
	.title {
		display: block;
		font-size: 0.94rem;
		font-weight: 650;
		text-decoration: none;
		overflow-wrap: anywhere;
		color: var(--discovery-ink);
	}
	.pin-caption p {
		font-size: 0.75rem;
		line-height: 1.5;
		margin: 0.35rem 0 0;
		color: var(--discovery-dim);
		overflow-wrap: anywhere;
	}
	.feed-layout {
		display: grid;
		grid-template-columns: minmax(0, 580px) 250px;
		gap: 5rem;
		justify-content: center;
		align-items: start;
	}
	.feed {
		display: grid;
		gap: 2.5rem;
		min-width: 0;
	}
	.post {
		background: var(--discovery-paper);
		border: 1px solid var(--discovery-line);
		border-radius: 0.8rem;
		overflow: hidden;
	}
	.post-head {
		display: flex;
		align-items: center;
		gap: 0.8rem;
		padding: 1rem 1.2rem;
	}
	.avatar {
		width: 37px;
		height: 37px;
		border-radius: 50%;
		display: grid;
		place-items: center;
		flex-shrink: 0;
		background: #f0e5f1;
		color: #754a76;
		border: 1px solid #dbc9df;
		font: 600 1rem var(--mono);
	}
	.post-head > div {
		display: grid;
		gap: 0.2rem;
		min-width: 0;
		overflow-wrap: anywhere;
	}
	.post-head strong {
		font-size: 0.82rem;
	}
	.post-head div span {
		font-size: 0.72rem;
		color: var(--discovery-dim);
	}
	.post-number {
		margin-left: auto;
		font: 0.75rem var(--mono);
		color: var(--discovery-dim);
	}
	.post-image {
		display: block;
		--art-height: 42rem;
	}
	.post-body {
		padding: 1rem 1.2rem 1.2rem;
	}
	.post-actions {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
	}
	.open {
		font-size: 0.8rem;
		text-decoration: none;
		color: var(--discovery-ink);
		padding: 0.7rem 0;
	}
	.open span {
		margin-left: 0.4rem;
		font-size: 1rem;
	}
	.post-body h2 {
		margin: 0.8rem 0 0.4rem;
		font-size: 1rem;
		overflow-wrap: anywhere;
	}
	.post-body p {
		font-size: 0.75rem;
		margin: 0;
		overflow-wrap: anywhere;
	}
	.post-body p span {
		color: var(--discovery-dim);
	}
	.feed-aside {
		position: sticky;
		top: 2rem;
		padding-top: 1rem;
	}
	.aside-mark {
		display: block;
		font: 3rem var(--mono);
		letter-spacing: -0.15em;
	}
	.aside-mark span {
		color: #b285b0;
	}
	.feed-aside h2 {
		font-size: 1.4rem;
		line-height: 1.3;
		letter-spacing: -0.035em;
		margin: 1rem 0;
	}
	.feed-aside p {
		color: var(--discovery-dim);
		font-size: 0.85rem;
		line-height: 1.7;
	}
	.feed-aside hr {
		border: 0;
		border-top: 1px solid var(--discovery-line);
		margin: 2rem 0;
	}
	.aside-label {
		display: block;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		font-size: 0.6rem;
		margin-bottom: 0.6rem;
		color: var(--discovery-dim);
	}
	.feed-aside > strong {
		font-size: 0.9rem;
	}
	.feed-aside .local-note {
		font-size: 0.72rem;
		margin-top: 2rem;
	}
	@media (max-width: 1100px) {
		.masonry {
			columns: 3;
		}
		.feed-layout {
			gap: 2.5rem;
		}
	}
	@media (max-width: 760px) {
		.masonry {
			columns: 2;
			column-gap: 0.8rem;
		}
		.feed-layout {
			display: block;
			max-width: 580px;
			margin: auto;
		}
		.feed-aside {
			display: none;
		}
		.pin-caption {
			padding-inline: 0;
		}
		.title {
			font-size: 0.8rem;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.pin-image {
			transition: none;
		}
	}
</style>
