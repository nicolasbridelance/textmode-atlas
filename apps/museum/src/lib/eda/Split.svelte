<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- A change split into parts that add up to it: horizontal bars from a zero line. -->
<script lang="ts">
	import { CHART } from './geometry';

	interface Part {
		name: string;
		value: number;
		tone: 'total' | 's1' | 's2';
	}
	let {
		parts,
		format,
		label
	}: { parts: Part[]; format: (value: number) => string; label: string } = $props();

	let measured = $state(0);
	const W = $derived(Math.max(CHART.minWidth, measured || CHART.width));
	const ROW = 34; // height of one part
	const BAR = 20;
	const BASELINE = 22; // of a label inside its row
	const TOP = 8;
	const NAMES = 0.32; // share of the width given to the names on the left
	const NAMES_MAX = 190;
	const LABEL = $derived(Math.min(NAMES_MAX, W * NAMES));
	const PAD = 70; // room for a value beyond a bar
	const TINY = 1e-9;
	const H = $derived(parts.length * ROW + TOP);
	const extent = $derived(Math.max(TINY, ...parts.map((p) => Math.abs(p.value))));
	const mixed = $derived(parts.some((p) => p.value < 0) && parts.some((p) => p.value > 0));
	const negative = $derived(parts.every((p) => p.value <= 0));
	const zero = $derived(
		mixed ? LABEL + (W - LABEL) / 2 : negative ? W - PAD : LABEL + CHART.tickBaseline
	);
	const scale = $derived((W - LABEL - PAD - CHART.tickBaseline) / extent);
	/** A negative value is written beyond the zero line, where its bar leaves room. */
	const valueAt = (value: number, x: number, w: number) =>
		value < 0 ? zero + CHART.tickGap : x + w + CHART.tickGap;
</script>

<div bind:clientWidth={measured}>
	<svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
		{#each parts as p, i (p.name)}
			{@const w = Math.abs(p.value) * scale}
			{@const x = p.value < 0 ? zero - w : zero}
			<text class="name" x="0" y={i * ROW + BASELINE}>{p.name}</text>
			<rect
				class={p.tone}
				{x}
				y={i * ROW + TOP}
				width={Math.max(1, w)}
				height={BAR}
				rx={CHART.corner}
			/>
			<text class="value" x={valueAt(p.value, x, w)} y={i * ROW + BASELINE}>{format(p.value)}</text>
		{/each}
		<line class="zero" x1={zero} x2={zero} y1="2" y2={H} />
	</svg>
</div>

<style>
	svg {
		width: 100%;
		height: auto;
		display: block;
		overflow: visible;
	}
	.name,
	.value {
		fill: var(--ink);
		font-size: 12px;
	}
	.value {
		font-family: var(--mono);
		fill: var(--bright);
	}
	.total {
		fill: var(--dim);
	}
	.s1 {
		fill: var(--series-1);
	}
	.s2 {
		fill: var(--series-2);
	}
	.zero {
		stroke: var(--faint);
	}
</style>
