<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- 7. After the quiet years, did the same art come back? -->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import Bars from '../Bars.svelte';
	import Figure from '../Figure.svelte';
	import Verdict from '../Verdict.svelte';
	import So from './So.svelte';
	import type { Chapters, Format } from '../eda';

	let {
		chapter,
		years,
		f
	}: { chapter: Chapters['revival']; years: Chapters['peak']['years']; f: Format } = $props();

	const REVIVAL_FROM = 2000;
	const RECENT = '2013-26';
	const PANEL = 120; // height of one small multiple
	const recent = $derived(years.filter((y) => y.year >= REVIVAL_FROM));
	const eras = $derived(chapter.eras);
	const bins = $derived((eras[0]?.heights ?? []).map((_, i) => String(2 ** i)));
	const taller = $derived(chapter.checks.taller);
	const ice = $derived(chapter.checks.ice_later);
	/** One scale for every panel, so that their heights compare. */
	const shared = $derived(Math.max(0, ...eras.flatMap((e) => e.heights.map((n) => n / e.works))));
	const num = (value: unknown) => (typeof value === 'number' ? value : 0);
</script>

<section id="revival">
	<h3>{m.eda_rev_title()}</h3>
	<p>{m.eda_rev_why()}</p>
	<Figure
		caption={m.eda_rev_fig_years()}
		head={[m.eda_year(), m.eda_works()]}
		rows={recent.map((y) => [y.year, f.n(y.works)])}
	>
		<Bars
			label={m.eda_rev_fig_years()}
			format={f.n}
			points={recent.map((y) => ({ x: String(y.year), y: y.works }))}
		/>
	</Figure>
	<Figure
		caption={m.eda_rev_fig_heights()}
		head={[m.eda_era(), ...bins]}
		rows={eras.map((e) => [e.era, ...e.heights.map((n) => f.pct(n / e.works))])}
	>
		<div class="multiples">
			{#each eras as e (e.era)}
				<div class="panel" class:recent={e.era === RECENT}>
					<p class="name">{e.era} · {f.n(e.works)}</p>
					<Bars
						label={`${m.eda_rev_fig_heights()}: ${e.era}`}
						format={f.pct}
						height={PANEL}
						max={shared}
						marked={e.era === RECENT ? bins : []}
						points={e.heights.map((n, i) => ({ x: bins[i], y: n / e.works }))}
					/>
				</div>
			{/each}
		</div>
	</Figure>
	<p>{m.eda_rev_heights_reading()}</p>
	<Verdict check={taller} hypothesis={m.eda_rev_hyp1()}>
		{#snippet evidence()}{m.eda_rev_check1({
				recent: f.d(num(taller?.recent)),
				nineties: f.d(num(taller?.nineties))
			})}{/snippet}
	</Verdict>
	<Figure
		caption={m.eda_rev_fig_ice()}
		head={[m.eda_era(), m.eda_ice()]}
		rows={eras.map((e) => [e.era, f.pct(e.ice)])}
	>
		<Bars
			label={m.eda_rev_fig_ice()}
			format={f.pct}
			marked={[RECENT]}
			points={eras.map((e) => ({ x: e.era, y: e.ice }))}
		/>
	</Figure>
	<Verdict check={ice} hypothesis={m.eda_rev_hyp2()}>
		{#snippet evidence()}{m.eda_rev_check2({
				recent: f.pct(num(ice?.recent)),
				nineties: f.pct(num(ice?.nineties))
			})}{/snippet}
	</Verdict>
	<So text={m.eda_rev_so()} />
</section>

<style>
	.multiples {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr));
		gap: 0.8rem 1.5rem;
	}
	.name {
		font-family: var(--mono);
		font-size: 0.72rem;
		color: var(--dim);
		margin: 0 0 0.2rem;
	}
	.recent .name {
		color: var(--bright);
	}
</style>
