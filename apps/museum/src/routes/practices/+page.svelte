<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- The practices of the character arts (ADR 0031): what the museum holds of each, and its gaps. -->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import { getLocale } from '#lib/paraglide/runtime.js';
	import {
		families,
		inFamily,
		isHeld,
		placeOf,
		practices,
		say,
		type Acquired,
		type Holding
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
</script>

<svelte:head><title>{m.atlas_practices()} · {m.museum_name()}</title></svelte:head>
<main>
	<h1>{m.atlas_practices()}</h1>
	<p class="intro">{m.practices_intro()}</p>
	<p class="count">{m.practices_count({ held, total: practices.length })}</p>
	<div class="bar" aria-hidden="true">
		<span style:width={`${(PERCENT * held) / practices.length}%`}></span>
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
					<li class:missing={!isHeld(practice)}>
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
		background: var(--line);
		border-radius: 999px;
		overflow: hidden;
		max-width: 32rem;
	}
	.bar span {
		display: block;
		height: 100%;
		background: var(--bright);
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
