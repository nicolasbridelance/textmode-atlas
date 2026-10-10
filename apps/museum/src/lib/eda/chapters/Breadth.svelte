<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- 8. How wide is the collection? Practices held, sources, and the basis for showing. -->
<script lang="ts">
	import { getLocale } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import Bars from '../Bars.svelte';
	import Figure from '../Figure.svelte';
	import Verdict from '../Verdict.svelte';
	import So from './So.svelte';
	import type { Chapters, Format } from '../eda';

	let { chapter, f }: { chapter: Chapters['breadth']; f: Format } = $props();

	const locale = getLocale();
	const labelOf = (label: Record<string, string>) => label[locale] ?? label.en;
	const BASES = ['permission', 'scene', 'license', 'excerpt', 'none'] as const;
	const basisName = (basis: string) =>
		BASES.includes(basis as (typeof BASES)[number])
			? m[`eda_breadth_basis_${basis as (typeof BASES)[number]}`]()
			: basis;
	const practices = $derived(chapter.checks.practices_held);
	const representatives = $derived(chapter.checks.representatives_held);
	const num = (value: unknown) => (typeof value === 'number' ? value : 0);
</script>

<section id="breadth">
	<h3>{m.eda_breadth_title()}</h3>
	<p>{m.eda_breadth_why()}</p>
	<Figure
		caption={m.eda_breadth_fig_families()}
		head={[m.eda_breadth_family(), m.eda_breadth_held(), m.eda_breadth_total()]}
		rows={chapter.families.map((x) => [labelOf(x.label), f.n(x.held), f.n(x.total)])}
	>
		<Bars
			label={m.eda_breadth_fig_families()}
			format={f.n}
			points={chapter.families.map((x) => ({ x: labelOf(x.label), y: x.held }))}
		/>
	</Figure>
	{#if practices}
		<p>
			{m.eda_breadth_reading({
				held: f.n(num(practices.held)),
				total: f.n(num(practices.total)),
				empty: f.n(num(practices.empty_families))
			})}
		</p>
	{/if}
	<Figure
		caption={m.eda_breadth_fig_sources()}
		head={[m.eda_breadth_source(), m.eda_works()]}
		rows={chapter.sources.map((x) => [x.source, f.n(x.works)])}
	>
		<Bars
			label={m.eda_breadth_fig_sources()}
			format={f.n}
			points={chapter.sources.map((x) => ({ x: x.source, y: x.works }))}
		/>
	</Figure>
	<Figure
		caption={m.eda_breadth_fig_bases()}
		head={[m.eda_breadth_basis(), m.eda_works()]}
		rows={chapter.bases.map((x) => [basisName(x.basis), f.n(x.works)])}
	>
		<Bars
			label={m.eda_breadth_fig_bases()}
			format={f.n}
			points={chapter.bases.map((x) => ({ x: basisName(x.basis), y: x.works }))}
		/>
	</Figure>
	<Verdict check={representatives} hypothesis={m.eda_breadth_hyp()}>
		{#snippet evidence()}
			{m.eda_breadth_check({ missing: f.n(num(representatives?.missing)) })}
		{/snippet}
	</Verdict>
	<So text={m.eda_breadth_so()} />
</section>
