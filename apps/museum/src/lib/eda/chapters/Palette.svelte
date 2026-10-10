<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- 6. An art of colour? The ink drawn in each VGA colour, and what the characters are. -->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import Figure from '../Figure.svelte';
	import Stacked from '../Stacked.svelte';
	import Verdict from '../Verdict.svelte';
	import So from './So.svelte';
	import { VGA, type Chapters, type Format } from '../eda';

	let { chapter, f }: { chapter: Chapters['palette']; f: Format } = $props();

	const NAMES = [
		m.eda_vga_0,
		m.eda_vga_1,
		m.eda_vga_2,
		m.eda_vga_3,
		m.eda_vga_4,
		m.eda_vga_5,
		m.eda_vga_6,
		m.eda_vga_7,
		m.eda_vga_8,
		m.eda_vga_9,
		m.eda_vga_10,
		m.eda_vga_11,
		m.eda_vga_12,
		m.eda_vga_13,
		m.eda_vga_14,
		m.eda_vga_15
	];
	/** Greys first, at the bottom of each column, so that their weight reads at a glance. */
	const ORDER = Object.values({
		darkGrey: 8,
		lightGrey: 7,
		white: 15,
		black: 0,
		blue: 1,
		brightBlue: 9,
		cyan: 3,
		brightCyan: 11,
		green: 2,
		brightGreen: 10,
		brown: 6,
		yellow: 14,
		red: 4,
		brightRed: 12,
		magenta: 5,
		brightMagenta: 13
	});
	const GLYPHS = [
		{ key: 'block', name: m.eda_glyph_block, colour: 'var(--cat-1)' },
		{ key: 'half_block', name: m.eda_glyph_half_block, colour: 'var(--cat-2)' },
		{ key: 'shade', name: m.eda_glyph_shade, colour: 'var(--cat-3)' },
		{ key: 'alphanumeric', name: m.eda_glyph_alphanumeric, colour: 'var(--cat-4)' },
		{ key: 'punctuation', name: m.eda_glyph_punctuation, colour: 'var(--cat-5)' },
		{ key: 'other', name: m.eda_glyph_other, colour: 'var(--faint)' }
	];
	const eras = $derived(chapter.eras);
	const grey = $derived(chapter.checks.mostly_grey);
	const meanGreys = $derived(
		eras.reduce((sum, e) => sum + e.greys * e.works, 0) /
			Math.max(
				1,
				eras.reduce((sum, e) => sum + e.works, 0)
			)
	);
</script>

{#if eras.length}
	<section id="palette">
		<h2>{m.eda_pal_title()}</h2>
		<p>{m.eda_pal_why()}</p>
		<Figure
			caption={m.eda_pal_fig_ink()}
			head={[m.eda_colour(), ...eras.map((e) => e.era)]}
			rows={ORDER.map((c) => [NAMES[c](), ...eras.map((e) => f.pct(e.ink[c]))])}
		>
			<Stacked
				label={m.eda_pal_fig_ink()}
				format={f.pct}
				share
				legend={false}
				x={eras.map((e) => e.era)}
				parts={ORDER.map((c) => ({
					name: NAMES[c](),
					values: eras.map((e) => e.ink[c]),
					colour: VGA[c]
				}))}
			/>
			<ul class="swatches">
				{#each ORDER as c (c)}<li><span style:background={VGA[c]}></span>{NAMES[c]()}</li>{/each}
			</ul>
		</Figure>
		<p>
			{m.eda_pal_reading({
				greys: f.pct(meanGreys),
				lowest: f.pct(typeof grey?.lowest === 'number' ? grey.lowest : null)
			})}
		</p>
		<Verdict check={grey} hypothesis={m.eda_pal_hyp()}>
			{#snippet evidence()}{m.eda_pal_check({
					lowest: f.pct(typeof grey?.lowest === 'number' ? grey.lowest : null)
				})}{/snippet}
		</Verdict>
		<Figure
			caption={m.eda_pal_fig_glyphs()}
			head={[m.eda_era(), ...GLYPHS.map((g) => g.name())]}
			rows={eras.map((e) => [e.era, ...GLYPHS.map((g) => f.pct(e.glyphs[g.key]))])}
		>
			<Stacked
				label={m.eda_pal_fig_glyphs()}
				format={f.pct}
				share
				x={eras.map((e) => e.era)}
				parts={GLYPHS.map((g) => ({
					name: g.name(),
					values: eras.map((e) => e.glyphs[g.key] ?? 0),
					colour: g.colour
				}))}
			/>
		</Figure>
		<p>{m.eda_pal_glyphs_reading()}</p>
		<So text={m.eda_pal_so()} />
	</section>
{/if}

<style>
	.swatches {
		display: flex;
		flex-wrap: wrap;
		gap: 0.25rem 0.8rem;
		list-style: none;
		padding: 0;
		margin: 0.5rem 0 0;
		font-size: 0.72rem;
	}
	.swatches span {
		display: inline-block;
		width: 0.7rem;
		height: 0.7rem;
		margin-right: 0.3rem;
		vertical-align: -0.05rem;
		outline: 1px solid var(--line);
	}
</style>
