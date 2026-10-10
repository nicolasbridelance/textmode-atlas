<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- The corpus, explored (ADR 0028): a path of questions through the live database,
     the first part of the research room. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { getLocale } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import Composition from '../../lib/eda/chapters/Composition.svelte';
	import Contents from '../../lib/eda/chapters/Contents.svelte';
	import Makers from '../../lib/eda/chapters/Makers.svelte';
	import Palette from '../../lib/eda/chapters/Palette.svelte';
	import Peak from '../../lib/eda/chapters/Peak.svelte';
	import Revival from '../../lib/eda/chapters/Revival.svelte';
	import Sauce from '../../lib/eda/chapters/Sauce.svelte';
	import { REFRESH_MS, formatter, loadSnapshot, type Snapshot } from '../../lib/eda/eda';

	// A study page gives the title and summary itself (ADR 0029).
	let { titled = true }: { titled?: boolean } = $props();
	const WRITTEN = '2026-10-10'; // when the readings below were written
	let snap = $state<Snapshot | null>(null);
	let live = $state(true);
	let failed = $state(false);
	const f = formatter(getLocale());
	const when = (iso: string) =>
		new Intl.DateTimeFormat(getLocale(), { dateStyle: 'medium', timeStyle: 'medium' }).format(
			new Date(iso)
		);

	onMount(() => {
		let gone = false;
		const tick = async () => {
			try {
				const found = await loadSnapshot();
				if (gone) return;
				if (found) {
					snap = found.snapshot;
					live = found.live;
				}
				failed = !found && !snap;
			} catch {
				failed = !snap;
			}
		};
		void tick();
		const timer = setInterval(() => {
			if (document.visibilityState === 'visible') void tick();
		}, REFRESH_MS);
		return () => {
			gone = true;
			clearInterval(timer);
		};
	});

	const c = $derived(snap?.chapters);
</script>

<section class="exploration" id="corpus" aria-labelledby="corpus-title">
	<header class="intro">
		<h2 id="corpus-title" class:hidden={!titled}>{m.eda_title()}</h2>
		{#if titled}<p class="lede">{m.eda_lede()}</p>{/if}
		<p>{m.eda_live({ date: WRITTEN })}</p>
		<p class="rules">{m.eda_rules()}</p>
		{#if snap}
			<p class="status" aria-live="polite">
				<span class="pulse" class:still={!live} aria-hidden="true"></span>
				{#if live}
					{m.eda_status({
						when: when(snap.computed_at),
						seconds: f.d(snap.seconds),
						hidden: f.n(snap.hidden)
					})}
				{:else}
					{m.eda_status_published({ when: when(snap.computed_at) })}
				{/if}
			</p>
		{:else if failed}
			<p class="status">{m.eda_unavailable()}</p>
		{:else}
			<p class="status">{m.eda_loading()}</p>
		{/if}
	</header>

	{#if c}
		<Contents chapter={c.contents} {f} />
		<Peak chapter={c.peak} {f} />
		<Makers chapter={c.makers} {f} />
		<Sauce chapter={c.sauce} {f} />
		<Composition chapter={c.composition} {f} />
		<Palette chapter={c.palette} {f} />
		<Revival chapter={c.revival} years={c.peak.years} {f} />

		<section id="next">
			<h3>{m.eda_next_title()}</h3>
			<ul>
				<li>{m.eda_next_q21()}</li>
				<li>{m.eda_next_sauce()}</li>
				<li>{m.eda_next_tools()}</li>
				<li>{m.eda_next_test()}</li>
			</ul>
		</section>
	{/if}
</section>

<style>
	.exploration {
		/* The categorical slots of every chart, in a fixed order: validated for colour vision
		   deficiency on each surface (the dataviz palette check). Series 1 and 2 are slots 1, 2. */
		--cat-1: #11a3ad;
		--cat-2: #cc7a12;
		--cat-3: #9085e9;
		--cat-4: #d55181;
		--cat-5: #5f9e2a;
		--series-1: var(--cat-1);
		--series-2: var(--cat-2);
		line-height: 1.65;
	}
	:global(:root[data-theme='light']) .exploration {
		--cat-1: #007f9a;
		--cat-2: #b35900;
		--cat-3: #4a3aa7;
		--cat-4: #c2416f;
		--cat-5: #3d7d12;
	}
	@media (prefers-color-scheme: light) {
		:global(:root[data-theme='system']) .exploration {
			--cat-1: #007f9a;
			--cat-2: #b35900;
			--cat-3: #4a3aa7;
			--cat-4: #c2416f;
			--cat-5: #3d7d12;
		}
	}
	h2,
	.exploration :global(h3) {
		font-weight: 400;
		color: var(--bright);
	}
	.exploration :global(h3) {
		margin-top: 3.5rem;
		padding-top: 1rem;
		border-top: 1px solid var(--line);
		font-size: 1.35rem;
	}
	.exploration :global(section) {
		scroll-margin-top: 1rem;
	}
	.exploration :global(p) {
		max-width: 68ch;
	}
	.hidden {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip-path: inset(50%);
	}
	.lede {
		font-size: 1.1rem;
		color: var(--bright);
	}
	.rules,
	.exploration :global(.caution),
	.exploration :global(.method) {
		font-size: 0.9rem;
		color: var(--dim);
	}
	.exploration :global(.method) {
		border-left: 1px solid var(--line);
		padding-left: 0.8rem;
	}
	.status {
		font-family: var(--mono);
		font-size: 0.75rem;
		color: var(--dim);
	}
	.pulse {
		display: inline-block;
		width: 0.5rem;
		height: 0.5rem;
		border-radius: 50%;
		background: var(--series-1);
		margin-right: 0.4rem;
		animation: pulse 2.4s ease-in-out infinite;
	}
	.pulse.still {
		animation: none;
		background: var(--dim);
	}
	@media (prefers-reduced-motion: reduce) {
		.pulse {
			animation: none;
		}
	}
	@keyframes pulse {
		50% {
			opacity: 0.25;
		}
	}
	.exploration :global(.tag) {
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--dim);
		margin-right: 0.3rem;
	}
	ul {
		padding-left: 1.2rem;
	}
</style>
