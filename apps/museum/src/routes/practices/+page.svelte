<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- The practices of the character arts (ADR 0031): what the museum holds of each, and its gaps. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import type { Path } from '$app/types';
	import { m } from '#lib/paraglide/messages.js';
	import { getLocale, localizeHref } from '#lib/paraglide/runtime.js';
	import { fileUrl } from '../../lib/files';
	import {
		families,
		inFamily,
		isHeld,
		placeOf,
		practices,
		say,
		standingOf,
		type Acquired,
		type Holding,
		type Practice,
		type Standing
	} from '../../lib/practices/practices';

	const locale = getLocale();
	const held = practices.filter(isHeld).length;
	const holdingName = (h: Holding) => m[`practices_holding_${h}`]();
	const PERCENT = 100;
	const BASIS: Record<Acquired['basis'], (a: Acquired) => string> = {
		scene: () => m.practices_basis_scene(),
		license: (a) => m.work_license({ license: a.license ?? '' }),
		'public-domain': () => m.work_public_domain(),
		excerpt: (a) => m.practices_basis_excerpt({ credit: a.credit ?? '?' })
	};
	const basisName = (a: Acquired) => BASIS[a.basis](a);

	// What the export published decides what is on show; until it is read, a held practice
	// counts as in the reserve.
	let standing: Record<string, Standing> = $state({});
	const standingFor = (p: Practice): Standing =>
		standing[p.code] ?? (isHeld(p) ? 'reserve' : 'missing');
	const count = (state: Standing) => practices.filter((p) => standingFor(p) === state).length;
	const share = (state: Standing) => `${(PERCENT * count(state)) / practices.length}%`;
	const workHref = (sha256: string) => `${resolve(localizeHref('/work') as Path)}?w=${sha256}`;
	onMount(() => {
		for (const practice of practices.filter(isHeld)) {
			void standingOf(practice).then((found) => (standing[practice.code] = found));
		}
	});
</script>

<svelte:head><title>{m.atlas_practices()} · {m.museum_name()}</title></svelte:head>
<main>
	<h1>{m.atlas_practices()}</h1>
	<p class="intro">{m.practices_intro()}</p>
	<p class="count">{m.practices_count({ held, total: practices.length })}</p>
	<p class="count">
		{m.practices_standing({
			shown: count('shown'),
			reserve: count('reserve'),
			missing: count('missing')
		})}
	</p>
	<div class="bar" aria-hidden="true">
		<span class="shown" style:width={share('shown')}></span>
		<span class="reserve" style:width={share('reserve')}></span>
	</div>

	<nav class="families" aria-label={m.practices_families()}>
		{#each families as family (family.code)}
			{@const all = inFamily(family.code)}
			<a href={`#${family.code}`} class:empty={!all.some(isHeld)}>
				{say(family.label, locale)}
				<span class="n">{all.filter(isHeld).length}/{all.length}</span>
			</a>
		{/each}
	</nav>

	{#each families as family (family.code)}
		{@const all = inFamily(family.code)}
		<section id={family.code}>
			<h2>
				{say(family.label, locale)}
				<span class="n">{all.filter(isHeld).length}/{all.length}</span>
			</h2>
			<ul>
				{#each all as practice (practice.code)}
					{@const state = standingFor(practice)}
					<li class:missing={state === 'missing'} class:reserve={state === 'reserve'}>
						{#if state === 'shown' && practice.representative}
							<a class="thumb" href={workHref(practice.representative.sha256)}>
								<img
									src={fileUrl(`works/${practice.representative.sha256}/conservation.png`)}
									alt=""
									loading="lazy"
									decoding="async"
								/>
							</a>
						{/if}
						<h3>{say(practice.label, locale)}</h3>
						{#if practice.acquired}
							<p class="title">{practice.acquired.title}</p>
							<p>{say(practice.acquired.why, locale)}</p>
							<p class="source">
								<a href={practice.acquired.url} rel="external">{m.practices_source()}</a>
								· {basisName(practice.acquired)}
							</p>
						{:else if practice.representative}
							{@const place = placeOf(practice.representative.path)}
							<p class="title">{place.path.split('/').at(-1)}</p>
							<p class="source">{m.practices_in_holdings({ source: place.source })}</p>
						{:else}
							<p class="gap">{m.practices_missing()}</p>
						{/if}
						{#if state === 'shown' && practice.representative}
							<p class="source">
								<a href={workHref(practice.representative.sha256)}>{m.practices_see_work()}</a>
							</p>
						{:else if state === 'reserve'}
							<p class="gap">{m.practices_reserve()}</p>
						{/if}
						<p class="holding">
							{m.practices_holding()}
							{practice.holding.map(holdingName).join(', ')}
						</p>
					</li>
				{/each}
			</ul>
		</section>
	{/each}
</main>

<style>
	main {
		max-width: 64rem;
		margin: auto;
		padding: 1.5rem 1rem 5rem;
	}
	h1,
	h2 {
		font-weight: 400;
		color: var(--bright);
	}
	h2 {
		margin-top: 3rem;
		border-bottom: 1px solid var(--line);
		padding-bottom: 0.25rem;
	}
	h3 {
		font-size: 1rem;
		font-weight: 600;
		margin: 0 0 0.25rem;
		color: var(--bright);
	}
	.intro {
		max-width: 65ch;
		line-height: 1.7;
	}
	.count,
	.n,
	.holding,
	.source,
	.gap {
		color: var(--dim);
		font-size: 0.85rem;
	}
	.bar {
		height: 0.4rem;
		display: flex;
		background: var(--line);
		border-radius: 999px;
		overflow: hidden;
		max-width: 32rem;
	}
	.bar span {
		height: 100%;
	}
	.bar .shown {
		background: var(--bright);
	}
	.bar .reserve {
		background: var(--dim);
	}
	.families {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-block: 2rem 1rem;
		font-size: 0.85rem;
	}
	.families a {
		border: 1px solid var(--line);
		border-radius: 999px;
		padding: 0.25rem 0.75rem;
		text-decoration: none;
		color: inherit;
	}
	.families a.empty {
		border-style: dashed;
		color: var(--dim);
	}
	ul {
		list-style: none;
		padding: 0;
		display: grid;
		gap: 1rem;
	}
	li {
		border: 1px solid var(--line);
		border-radius: 0.5rem;
		padding: 0.75rem 1rem;
		overflow-wrap: anywhere;
	}
	li.missing {
		border-style: dashed;
	}
	li.reserve {
		color: var(--dim);
	}
	.thumb {
		display: block;
		max-height: 12rem;
		overflow: hidden;
		margin: -0.75rem -1rem 0.75rem;
		border-radius: 0.5rem 0.5rem 0 0;
		background: #000;
	}
	.thumb img {
		display: block;
		width: 100%;
		image-rendering: pixelated;
	}
	li p {
		margin: 0.25rem 0;
		line-height: 1.5;
	}
	.title {
		font-style: italic;
	}
	@media (min-width: 900px) {
		main {
			padding-inline: 2rem;
		}
		ul {
			grid-template-columns: 1fr 1fr;
		}
	}
</style>
