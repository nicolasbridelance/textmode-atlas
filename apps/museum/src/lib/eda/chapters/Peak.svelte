<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- 2. A peak in the mid-nineties: more packs, or bigger packs? -->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import Bars from '../Bars.svelte';
	import Boxes from '../Boxes.svelte';
	import Figure from '../Figure.svelte';
	import Verdict from '../Verdict.svelte';
	import So from './So.svelte';
	import type { Chapters, Format } from '../eda';

	let { chapter, f }: { chapter: Chapters['peak']; f: Format } = $props();

	const { P25, P75 } = { P25: 1, P75: 3 }; // places in a year's spread
	const years = $derived(chapter.years);
	const sized = $derived(years.filter((y) => y.packs >= chapter.min_packs));
	const peak = $derived(chapter.checks.peaks_differ);
	const late = $derived(chapter.checks.fewer_and_smaller);
	const yearOf = (year: unknown) => sized.find((y) => y.year === year);
	const num = (value: unknown) => (typeof value === 'number' ? value : 0);
</script>

<section id="peak">
	<h3>{m.eda_peak_title()}</h3>
	<p>{m.eda_peak_why()}</p>
	<Figure
		caption={m.eda_peak_fig_works()}
		head={[m.eda_year(), m.eda_works(), m.eda_packs()]}
		rows={years.map((y) => [y.year, f.n(y.works), f.n(y.packs)])}
	>
		<Bars
			label={m.eda_peak_fig_works()}
			format={f.n}
			marked={peak ? [String(peak.works_year)] : []}
			points={years.map((y) => ({ x: String(y.year), y: y.works }))}
		/>
	</Figure>
	<Figure
		caption={m.eda_peak_fig_packs()}
		head={[m.eda_year(), m.eda_packs()]}
		rows={years.map((y) => [y.year, f.n(y.packs)])}
	>
		<Bars
			label={m.eda_peak_fig_packs()}
			format={f.n}
			marked={peak ? [String(peak.packs_year)] : []}
			points={years.map((y) => ({ x: String(y.year), y: y.packs }))}
		/>
	</Figure>
	{#if peak}
		<p>
			{m.eda_peak_reading({
				works_year: String(peak.works_year),
				works: f.n(num(peak.works)),
				packs_year: String(peak.packs_year),
				packs: f.n(num(peak.packs)),
				size_year: String(peak.size_year),
				size: f.d(num(peak.size))
			})}
		</p>
	{/if}
	<Figure
		caption={m.eda_peak_fig_spread()}
		head={[
			m.eda_year(),
			m.eda_packs(),
			m.eda_p10(),
			m.eda_p25(),
			m.eda_median(),
			m.eda_p75(),
			m.eda_p90()
		]}
		rows={sized.map((y) => [y.year, f.n(y.packs), ...y.spread.map(f.d)])}
	>
		<Boxes
			label={m.eda_peak_fig_spread()}
			format={f.d}
			spreads={sized.map((y) => ({
				x: String(y.year),
				q: y.spread,
				marked: y.year === peak?.size_year
			}))}
			names={{
				p10: m.eda_p10(),
				p25: m.eda_p25(),
				median: m.eda_median(),
				p75: m.eda_p75(),
				p90: m.eda_p90()
			}}
		/>
	</Figure>
	{#if peak && late && yearOf(peak.size_year) && yearOf(late.year)}
		<p>
			{m.eda_peak_spread_reading({
				year: String(peak.size_year),
				low: f.d(yearOf(peak.size_year)?.spread[P25]),
				high: f.d(yearOf(peak.size_year)?.spread[P75]),
				late: String(late.year),
				late_low: f.d(yearOf(late.year)?.spread[P25]),
				late_high: f.d(yearOf(late.year)?.spread[P75])
			})}
		</p>
	{/if}
	<p class="caution">{m.eda_peak_caution()}</p>
	<Verdict check={late} hypothesis={m.eda_peak_hyp()}>
		{#snippet evidence()}{m.eda_peak_check({
				year: String(late?.year ?? ''),
				late_packs: f.n(num(late?.packs)),
				packs: f.n(num(peak?.packs)),
				late_size: f.d(num(late?.size)),
				size: f.d(num(peak?.size))
			})}{/snippet}
	</Verdict>
	<So text={m.eda_peak_so()} />
</section>
