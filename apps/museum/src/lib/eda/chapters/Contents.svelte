<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- 1. Before counting: what is in the database? -->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import Bars from '../Bars.svelte';
	import Figure from '../Figure.svelte';
	import Split from '../Split.svelte';
	import Stacked from '../Stacked.svelte';
	import Verdict from '../Verdict.svelte';
	import So from './So.svelte';
	import { everyYear, type Chapters, type Format } from '../eda';

	let { chapter, f }: { chapter: Chapters['contents']; f: Format } = $props();

	const UNREAD_SHOWN = 8;
	const funnel = $derived(chapter.funnel);
	const unread = $derived(chapter.unread.reduce((sum, u) => sum + u.works, 0));
	const unreadByFormat = $derived(
		Object.entries(
			chapter.unread.reduce<Record<string, number>>((by, u) => {
				by[u.format] = (by[u.format] ?? 0) + u.works;
				return by;
			}, {})
		)
			.map(([x, y]) => ({ x, y }))
			.sort((a, b) => b.y - a.y)
			.slice(0, UNREAD_SHOWN)
	);
	const years = $derived(everyYear(chapter.years.map((y) => y.year)));
	const of = (key: 'ansi' | 'ascii' | 'other') =>
		years.map((year) => chapter.years.find((y) => y.year === year)?.[key] ?? 0);
	const wave = $derived(chapter.checks.ascii_wave);
	const num = (value: unknown) => (typeof value === 'number' ? value : 0);
</script>

<section id="contents">
	<h3>{m.eda_contents_title()}</h3>
	<p>{m.eda_contents_why()}</p>
	<Figure
		caption={m.eda_contents_fig()}
		head={['', m.eda_works()]}
		rows={[
			[m.eda_step_art(), f.n(funnel.art)],
			[m.eda_step_decoding(), f.n(funnel.decoding)],
			[m.eda_step_grids(), f.n(funnel.grids)],
			[m.eda_step_rendered(), f.n(funnel.rendered)],
			[m.eda_step_measured(), f.n(funnel.measured)]
		]}
	>
		<Split
			label={m.eda_contents_fig()}
			format={f.n}
			parts={[
				{ name: m.eda_step_art(), value: funnel.art, tone: 's1' },
				{ name: m.eda_step_decoding(), value: funnel.decoding, tone: 's1' },
				{ name: m.eda_step_grids(), value: funnel.grids, tone: 's1' },
				{ name: m.eda_step_rendered(), value: funnel.rendered, tone: 's1' },
				{ name: m.eda_step_measured(), value: funnel.measured, tone: 's1' }
			]}
		/>
	</Figure>
	<p>
		{m.eda_contents_reading({
			files: f.n(chapter.sources.reduce((s, x) => s + x.files, 0)),
			sources: f.n(chapter.sources.length),
			art: f.n(funnel.art),
			packs: f.n(funnel.packs),
			grids: f.n(funnel.grids),
			share: f.pct(funnel.grids / Math.max(1, funnel.art))
		})}
	</p>
	<Figure
		caption={m.eda_contents_fig_years()}
		head={[m.eda_year(), 'ANSI', 'ASCII', m.eda_format_other()]}
		rows={years.map((y, i) => [y, f.n(of('ansi')[i]), f.n(of('ascii')[i]), f.n(of('other')[i])])}
	>
		<Stacked
			label={m.eda_contents_fig_years()}
			format={f.n}
			x={years.map(String)}
			parts={[
				{ name: 'ANSI', values: of('ansi'), colour: 'var(--cat-1)' },
				{ name: 'ASCII', values: of('ascii'), colour: 'var(--cat-2)' },
				{ name: m.eda_format_other(), values: of('other'), colour: 'var(--cat-3)' }
			]}
		/>
	</Figure>
	{#if wave?.holds}
		<p>
			{m.eda_contents_years_reading({ first: String(wave.first), last: String(wave.last) })}
		</p>
	{/if}
	<Figure
		caption={m.eda_contents_unread_fig()}
		head={[m.eda_format(), m.eda_reason(), m.eda_works()]}
		rows={chapter.unread.map((u) => [u.format, u.error_class, f.n(u.works)])}
	>
		<Bars label={m.eda_contents_unread_fig()} format={f.n} points={unreadByFormat} />
	</Figure>
	<Verdict check={chapter.checks.every_work_decoded} hypothesis={m.eda_contents_hyp()}>
		{#snippet evidence()}{m.eda_contents_check({
				missing: f.n(num(chapter.checks.every_work_decoded?.missing))
			})}{/snippet}
	</Verdict>
	<So text={m.eda_contents_so({ unread: f.n(unread) })} />
</section>
