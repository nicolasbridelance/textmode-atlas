<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- 4. Who wrote the SAUCE records? -->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import Bars from '../Bars.svelte';
	import Figure from '../Figure.svelte';
	import Heatmap from '../Heatmap.svelte';
	import Lines from '../Lines.svelte';
	import NullPlot from '../NullPlot.svelte';
	import Verdict from '../Verdict.svelte';
	import So from './So.svelte';
	import { HALF } from '../geometry';
	import { everyYear, type Chapters, type Format } from '../eda';

	let { chapter, f }: { chapter: Chapters['sauce']; f: Format } = $props();

	const SHARE_BINS = ['0–20 %', '20–40 %', '40–60 %', '60–80 %', '80–100 %'];
	const years = $derived(everyYear(chapter.by_year.map((y) => y.year)));
	const shareOf = (format: 'ansi' | 'ascii') =>
		years.map(
			(year) => chapter.by_year.find((y) => y.year === year && y.format === format)?.share ?? null
		);
	const adoption = $derived(
		chapter.by_year.find((y) => y.year === chapter.year && y.format === 'ansi')?.share
	);
	const groupShare = (prefix: string) => {
		const g = chapter.groups.find((x) => x.prefix === prefix);
		return g ? `${f.n(g.with)} / ${f.n(g.packs)}` : '–';
	};
	const map = $derived(chapter.map);
	const num = (value: unknown) => (typeof value === 'number' ? value : 0);
</script>

<section id="sauce">
	<h2>{m.eda_sauce_title()}</h2>
	<p>{m.eda_sauce_why()}</p>
	<Figure
		caption={m.eda_sauce_fig_years()}
		head={[m.eda_year(), 'ANSI', 'ASCII']}
		rows={years.map((y, i) => [y, f.pct(shareOf('ansi')[i]), f.pct(shareOf('ascii')[i])])}
	>
		<Lines
			label={m.eda_sauce_fig_years()}
			format={f.pct}
			max={1}
			x={years.map(String)}
			series={[
				{ name: 'ANSI', values: shareOf('ansi') },
				{ name: 'ASCII', values: shareOf('ascii') }
			]}
		/>
	</Figure>
	<p>{m.eda_sauce_reading_years({ year: String(chapter.year), share: f.pct(adoption) })}</p>
	<Figure
		caption={m.eda_sauce_fig_packs({ year: String(chapter.year) })}
		head={[m.eda_share(), m.eda_packs()]}
		rows={chapter.shares.map((n, i) => [SHARE_BINS[i], f.n(n)])}
	>
		<Bars
			label={m.eda_sauce_fig_packs({ year: String(chapter.year) })}
			format={f.n}
			points={chapter.shares.map((n, i) => ({ x: SHARE_BINS[i], y: n }))}
		/>
	</Figure>
	<p>
		{m.eda_sauce_reading_packs({
			year: String(chapter.year),
			none: f.n(chapter.none),
			packs: f.n(chapter.packs),
			all: f.n(chapter.all)
		})}
	</p>
	<Verdict check={chapter.checks.not_packager} hypothesis={m.eda_sauce_hyp1()} refutes>
		{#snippet evidence()}{m.eda_sauce_check1({
				dates: f.d(chapter.full_mean_dates),
				files: f.d(chapter.full_mean_files),
				one_date: f.pct(num(chapter.checks.not_packager?.one_date))
			})}{/snippet}
	</Verdict>
	<p>{m.eda_sauce_hyp2()}</p>
	<p class="method">{m.eda_sauce_method()}</p>
	<Figure
		caption={m.eda_sauce_fig_null()}
		head={[m.eda_null_observed(), m.eda_null_chance(), m.eda_null_q95(), 'p']}
		rows={[
			[
				f.pct(chapter.test.observed),
				f.pct(chapter.test.null_mean),
				f.pct(chapter.test.null_q95),
				f.p(chapter.test.p)
			]
		]}
	>
		<NullPlot
			label={m.eda_sauce_fig_null()}
			counts={chapter.test.null}
			low={HALF}
			high={1}
			observed={chapter.test.observed}
			q95={chapter.test.null_q95}
			format={f.pct}
			names={{
				chance: m.eda_null_chance(),
				q95: m.eda_null_q95(),
				observed: m.eda_null_observed()
			}}
		/>
	</Figure>
	<Verdict check={chapter.checks.group_choice} hypothesis={m.eda_sauce_hyp2()}>
		{#snippet evidence()}{m.eda_sauce_check2({
				observed: f.pct(chapter.test.observed),
				null_mean: f.pct(chapter.test.null_mean),
				q95: f.pct(chapter.test.null_q95),
				p: f.pIs(chapter.test.p),
				groups: f.n(chapter.test.groups),
				gpacks: f.n(chapter.test.packs)
			})}{/snippet}
	</Verdict>
	<Figure
		caption={m.eda_sauce_groups_fig({ year: String(chapter.year) })}
		head={[m.eda_prefix(), m.eda_with_sauce(), m.eda_packs()]}
		rows={chapter.groups.map((g) => [g.prefix, f.n(g.with), f.n(g.packs)])}
	>
		<Bars
			label={m.eda_sauce_groups_fig({ year: String(chapter.year) })}
			format={f.pct}
			marked={['acdu', 'ice']}
			points={chapter.groups.map((g) => ({ x: g.prefix, y: g.with / g.packs }))}
		/>
	</Figure>
	<p>{m.eda_sauce_groups_reading({ acdu: groupShare('acdu'), ice: groupShare('ice') })}</p>
	{#if map.groups.length}
		<Figure
			caption={m.eda_sauce_map_fig({
				first: String(map.years[0]),
				last: String(map.years.at(-1))
			})}
			head={[m.eda_prefix(), ...map.years.map(String)]}
			rows={map.groups.map((g, r) => [g, ...map.cells[r].map((c) => `${c.with}/${c.packs}`)])}
		>
			<Heatmap
				label={m.eda_sauce_map_fig({
					first: String(map.years[0]),
					last: String(map.years.at(-1))
				})}
				rows={map.groups}
				columns={map.years.map(String)}
				cells={map.cells}
				empty={m.eda_heat_empty()}
			/>
		</Figure>
		<p>{m.eda_sauce_map_reading()}</p>
	{/if}
	<So text={m.eda_sauce_so()} />
</section>
