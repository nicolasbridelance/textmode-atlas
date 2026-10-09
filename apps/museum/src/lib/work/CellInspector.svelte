<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	// How one cell is made: its glyph, its two colours, and the byte that wrote it.
	import { m } from '#lib/paraglide/messages.js';
	import { COLOUR_NAMES, glyph, hex } from './cp437';
	import { shownBackground, VGA_PALETTE } from './draw';
	import { duration, secondsAt } from './time';
	import { NEVER, type TmgGrid } from './tmg';

	const COLOUR = 0x0f;

	let {
		grid,
		cell,
		baud,
		locale
	}: { grid: TmgGrid; cell: number | null; baud: number; locale: string } = $props();

	const names = $derived(COLOUR_NAMES[locale] ?? COLOUR_NAMES.en);
	const rgb = (i: number): string => `rgb(${VGA_PALETTE[i & COLOUR].join(' ')})`;
	const numbers = $derived(new Intl.NumberFormat(locale));
	const shown = $derived(
		cell === null
			? null
			: {
					row: Math.floor(cell / grid.cols) + 1,
					col: (cell % grid.cols) + 1,
					code: grid.codepoint[cell],
					fg: grid.fg[cell] & COLOUR,
					bg: shownBackground(grid, cell) & COLOUR,
					blink: !grid.ice && grid.blink[cell] === 1,
					t: grid.t[cell]
				}
	);
</script>

<div class="inspector" aria-live="off">
	{#if shown}
		<span class="glyph" style:color={rgb(shown.fg)} style:background={rgb(shown.bg)}
			>{glyph(shown.code)}</span
		>
		<span class="facts">
			<span>{m.cell_position({ row: shown.row, col: shown.col })}</span>
			<span>{m.cell_glyph({ glyph: glyph(shown.code), code: hex(shown.code) })}</span>
			<span>
				<i class="swatch" style:background={rgb(shown.fg)}></i>
				{m.cell_colours({ fg: names[shown.fg], bg: names[shown.bg] })}
				<i class="swatch" style:background={rgb(shown.bg)}></i>
				{#if shown.blink}· {m.cell_blink()}{/if}
			</span>
			<span>
				{shown.t === NEVER
					? m.cell_never()
					: m.cell_byte({
							byte: numbers.format(shown.t),
							time: duration(secondsAt(shown.t, baud))
						})}
			</span>
		</span>
	{:else}
		<span class="hint">{m.cell_hint()}</span>
	{/if}
</div>

<style>
	.inspector {
		display: flex;
		gap: 0.75rem;
		align-items: center;
		min-height: 4.2rem;
		font-size: 0.75rem;
		color: var(--ink);
	}
	.glyph {
		font-family: var(--mono);
		font-size: 2rem;
		line-height: 1;
		width: 2.6rem;
		height: 3.6rem;
		display: grid;
		place-items: center;
		flex: none;
		outline: 1px solid var(--line);
	}
	.facts {
		display: grid;
		gap: 0.1rem;
	}
	.swatch {
		display: inline-block;
		width: 0.7rem;
		height: 0.7rem;
		vertical-align: -0.1rem;
		outline: 1px solid var(--line);
	}
	.hint {
		color: var(--dim);
	}
</style>
