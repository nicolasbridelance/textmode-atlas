<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- 3. Who made the art: a few groups, or a crowd? -->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import Bars from '../Bars.svelte';
	import Figure from '../Figure.svelte';
	import Lorenz from '../Lorenz.svelte';
	import Verdict from '../Verdict.svelte';
	import So from './So.svelte';
	import type { Chapters, Format } from '../eda';

	let { chapter, f }: { chapter: Chapters['makers']; f: Format } = $props();

	const crowd = $derived(chapter.checks.peak_is_a_crowd);
	const busiest = $derived(chapter.eras.find((e) => e.era === crowd?.busiest));
	const recent = $derived(chapter.eras.at(-1));
	const curves = $derived(
		chapter.eras
			.filter((e) => e.lorenz)
			.map((e, k) => ({ name: e.era, points: e.lorenz ?? [], colour: `var(--cat-${k + 1})` }))
	);
</script>

<section id="makers">
	<h3>{m.eda_makers_title()}</h3>
	<p>{m.eda_makers_why()}</p>
	<Figure
		caption={m.eda_makers_fig_top()}
		head={[
			m.eda_era(),
			m.eda_groups(),
			m.eda_works(),
			m.eda_top10(),
			m.eda_gini(),
			m.eda_largest()
		]}
		rows={chapter.eras.map((e) => [
			e.era,
			f.n(e.groups),
			f.n(e.works),
			f.pct(e.top),
			f.p(e.gini),
			e.largest.map((g) => g.prefix).join(', ')
		])}
	>
		<Bars
			label={m.eda_makers_fig_top()}
			format={f.pct}
			marked={crowd ? [String(crowd.busiest)] : []}
			points={chapter.eras.map((e) => ({ x: e.era, y: e.top }))}
		/>
	</Figure>
	{#if busiest && recent}
		<p>
			{m.eda_makers_reading({
				busiest: busiest.era,
				top: f.pct(busiest.top),
				groups: f.n(busiest.groups),
				recent: f.pct(recent.top)
			})}
		</p>
	{/if}
	<p class="method">{m.eda_makers_method()}</p>
	<Figure
		caption={m.eda_makers_fig_lorenz()}
		head={[m.eda_era(), m.eda_gini()]}
		rows={chapter.eras.filter((e) => e.lorenz).map((e) => [e.era, f.p(e.gini)])}
	>
		<Lorenz
			label={m.eda_makers_fig_lorenz()}
			{curves}
			names={{ x: m.eda_lorenz_x(), y: m.eda_lorenz_y(), equality: m.eda_lorenz_equality() }}
		/>
	</Figure>
	{#if busiest && recent}
		<p>
			{m.eda_makers_lorenz_reading({
				low: f.p(Math.min(...chapter.eras.map((e) => e.gini))),
				high: f.p(Math.max(...chapter.eras.map((e) => e.gini))),
				groups: f.n(busiest.groups),
				busiest: busiest.era,
				recent_groups: f.n(recent.groups)
			})}
		</p>
	{/if}
	<Verdict check={crowd} hypothesis={m.eda_makers_hyp()}>
		{#snippet evidence()}{m.eda_makers_check({
				busiest: String(crowd?.busiest ?? '–'),
				least: String(crowd?.least ?? '–'),
				top: f.pct(typeof crowd?.top === 'number' ? crowd.top : null)
			})}{/snippet}
	</Verdict>
	<So text={m.eda_makers_so()} />
</section>
