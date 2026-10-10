<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- 5. Did artists stop shading? -->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import Figure from '../Figure.svelte';
	import Lines from '../Lines.svelte';
	import Split from '../Split.svelte';
	import Stacked from '../Stacked.svelte';
	import Verdict from '../Verdict.svelte';
	import So from './So.svelte';
	import type { Chapters, Format } from '../eda';

	let { chapter, f }: { chapter: Chapters['composition']; f: Format } = $props();

	/** The kinds of the works, from the most to the least drawn, each with its colour. */
	const KINDS = [
		{ key: 'coloured_blocks', name: m.eda_kind_coloured_blocks, colour: 'var(--cat-1)' },
		{ key: 'blocks', name: m.eda_kind_blocks, colour: 'var(--cat-2)' },
		{ key: 'coloured_text', name: m.eda_kind_coloured_text, colour: 'var(--cat-3)' },
		{ key: 'text', name: m.eda_kind_text, colour: 'var(--cat-4)' },
		{ key: 'empty', name: m.eda_kind_empty, colour: 'var(--faint)' }
	];
	const eras = $derived(chapter.eras);
	const before = $derived(eras.find((e) => e.era === chapter.before));
	const after = $derived(eras.find((e) => e.era === chapter.after));
	const split = $derived(chapter.split);
	const shadeOf = (era: (typeof eras)[number], kind = 'coloured_blocks') =>
		era.kinds[kind]?.shade ?? null;
	const shareOf = (era: (typeof eras)[number], kind: string) => era.kinds[kind]?.share ?? 0;
	const caption = $derived(m.eda_comp_fig_split({ before: chapter.before, after: chapter.after }));
</script>

{#if before && after && split}
	<section id="composition">
		<h3>{m.eda_comp_title()}</h3>
		<p>{m.eda_comp_why()}</p>
		<Figure
			caption={m.eda_comp_fig()}
			head={[m.eda_era(), m.eda_comp_all(), m.eda_comp_blocks()]}
			rows={eras.map((e) => [e.era, f.pct(e.all), f.pct(shadeOf(e))])}
		>
			<Lines
				label={m.eda_comp_fig()}
				format={f.pct}
				x={eras.map((e) => e.era)}
				series={[
					{ name: m.eda_comp_all(), values: eras.map((e) => e.all) },
					{ name: m.eda_comp_blocks(), values: eras.map((e) => shadeOf(e)) }
				]}
			/>
		</Figure>
		<p>
			{m.eda_comp_reading({
				before: chapter.before,
				after: chapter.after,
				before_all: f.pct(before.all),
				after_all: f.pct(after.all),
				before_cb: f.pct(shadeOf(before)),
				after_cb: f.pct(shadeOf(after)),
				before_share: f.pct(before.kinds.coloured_blocks?.share),
				after_share: f.pct(after.kinds.coloured_blocks?.share)
			})}
		</p>
		<Figure
			caption={m.eda_comp_fig_mix()}
			head={[m.eda_era(), ...KINDS.map((k) => k.name())]}
			rows={eras.map((e) => [e.era, ...KINDS.map((k) => f.pct(shareOf(e, k.key)))])}
		>
			<Stacked
				label={m.eda_comp_fig_mix()}
				format={f.pct}
				share
				x={eras.map((e) => e.era)}
				parts={KINDS.map((k) => ({
					name: k.name(),
					values: eras.map((e) => shareOf(e, k.key)),
					colour: k.colour
				}))}
			/>
		</Figure>
		<Figure
			caption={m.eda_comp_fig_kinds()}
			head={[m.eda_era(), ...KINDS.slice(0, -1).map((k) => k.name())]}
			rows={eras.map((e) => [e.era, ...KINDS.slice(0, -1).map((k) => f.pct(shadeOf(e, k.key)))])}
		>
			<Lines
				label={m.eda_comp_fig_kinds()}
				format={f.pct}
				x={eras.map((e) => e.era)}
				series={KINDS.slice(0, -1).map((k) => ({
					name: k.name(),
					values: eras.map((e) => shadeOf(e, k.key)),
					colour: k.colour
				}))}
			/>
		</Figure>
		<p>{m.eda_comp_kinds_reading()}</p>
		<p class="method">{m.eda_comp_method()}</p>
		<Figure
			{caption}
			head={['', 'pts']}
			rows={[
				[m.eda_comp_total(), f.pts(split.total)],
				[m.eda_comp_within(), f.pts(split.within)],
				[m.eda_comp_mix(), f.pts(split.composition)]
			]}
		>
			<Split
				label={caption}
				format={f.pts}
				parts={[
					{ name: m.eda_comp_total(), value: split.total, tone: 'total' },
					{ name: m.eda_comp_within(), value: split.within, tone: 's2' },
					{ name: m.eda_comp_mix(), value: split.composition, tone: 's1' }
				]}
			/>
		</Figure>
		<Verdict check={chapter.checks.composition_dominates} hypothesis={m.eda_comp_hyp()}>
			{#snippet evidence()}{m.eda_comp_check({
					total: f.pts(split.total),
					composition: f.pts(split.composition),
					within: f.pts(split.within)
				})}{/snippet}
		</Verdict>
		<So text={m.eda_comp_so()} />
	</section>
{/if}
