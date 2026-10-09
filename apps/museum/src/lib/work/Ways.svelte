<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	// Three to five ways out, each with its key, a glimpse of the work and its signature.
	import { m } from '#lib/paraglide/messages.js';
	import { fileUrl } from '../files';
	import type { Entry, Ways } from './visit';

	let { ways, hrefOf }: { ways: Ways; hrefOf: (sha256: string) => string } = $props();

	interface Way {
		key: string;
		label: string;
		entry: Entry | null;
	}

	const items = $derived(
		(
			[
				{ key: '←', label: m.way_previous(), entry: ways.previous },
				{ key: '→', label: m.way_next(), entry: ways.next },
				{
					key: 'a',
					label: m.way_signature({ author: ways.signature?.author ?? '' }),
					entry: ways.signature
				},
				{ key: 'y', label: m.way_year({ year: ways.year?.year ?? '' }), entry: ways.year },
				{ key: 'r', label: m.way_chance(), entry: ways.chance }
			] as Way[]
		).filter((way): way is Way & { entry: Entry } => way.entry !== null)
	);

	function signed(entry: Entry): string {
		return [entry.author, entry.group].filter(Boolean).join(' / ') || m.work_unsigned();
	}
</script>

{#if items.length}
	<nav class="ways" aria-label={m.ways_title()}>
		<h2>{m.ways_title()}</h2>
		<ul>
			{#each items as item (item.key)}
				<li>
					<a href={hrefOf(item.entry.sha256)} data-key={item.key}>
						<img
							src={fileUrl(`works/${item.entry.sha256}/conservation.png`)}
							alt=""
							loading="lazy"
							decoding="async"
						/>
						<span class="text">
							<span class="label"><kbd>{item.key}</kbd> {item.label}</span>
							<span class="title">{item.entry.title || item.entry.file}</span>
							<span class="who">{signed(item.entry)}</span>
						</span>
					</a>
				</li>
			{/each}
		</ul>
	</nav>
{/if}

<style>
	h2 {
		font-size: 0.75rem;
		font-weight: 400;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--dim);
		margin: 0 0 0.6rem;
	}
	ul {
		list-style: none;
		margin: 0;
		padding: 0;
		display: grid;
		gap: 0.6rem;
	}
	a {
		display: grid;
		grid-template-columns: 5.5rem 1fr;
		gap: 0.65rem;
		align-items: start;
		text-decoration: none;
		color: var(--ink);
		padding: 0.3rem;
		margin: -0.3rem;
		border-radius: 2px;
	}
	a:hover,
	a:focus-visible {
		background: var(--panel);
		color: var(--bright);
	}
	img {
		width: 5.5rem;
		aspect-ratio: 8 / 5;
		object-fit: cover;
		object-position: top;
		background: #000;
		outline: 1px solid var(--line);
	}
	.text {
		display: grid;
		gap: 0.1rem;
		min-width: 0;
		font-size: 0.8rem;
	}
	.label {
		color: var(--dim);
		font-size: 0.72rem;
	}
	kbd {
		font-family: var(--mono);
		color: var(--accent);
	}
	.title,
	.who {
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.title {
		color: var(--bright);
	}
	.who {
		color: var(--dim);
	}
</style>
