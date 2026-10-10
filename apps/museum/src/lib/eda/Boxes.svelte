<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- A distribution per category: the middle half as a box, the median as a line, and the
     whiskers from the 10th to the 90th percentile. -->
<script lang="ts">
	import { CHAR_PX, labelEvery, ticks } from './eda';
	import { CHART, HALF, PERCENT } from './geometry';

	interface Spread {
		x: string;
		q: number[]; // 10th, 25th, 50th, 75th, 90th percentiles
		marked?: boolean;
	}
	let {
		spreads,
		format,
		label,
		names
	}: {
		spreads: Spread[];
		format: (value: number) => string;
		label: string;
		names: { p10: string; p25: string; median: string; p75: string; p90: string };
	} = $props();

	let measured = $state(0);
	const W = $derived(Math.max(CHART.minWidth, measured || CHART.width));
	const H = 220;
	const PAD = { left: 46, right: 8, top: 10, bottom: 24 };
	const BOX = 0.6; // share of a band the box takes
	const { P10, P25, P50, P75, P90 } = { P10: 0, P25: 1, P50: 2, P75: 3, P90: 4 };
	const grid = $derived(ticks(Math.max(0, ...spreads.map((s) => s.q[P90]))));
	const top = $derived(grid.at(-1) || 1);
	const band = $derived((W - PAD.left - PAD.right) / Math.max(1, spreads.length));
	const spacing = $derived(
		labelEvery(band, Math.max(0, ...spreads.map((s) => s.x.length)) * CHAR_PX)
	);
	const y = (value: number) => PAD.top + (H - PAD.top - PAD.bottom) * (1 - value / top);
	let hover = $state<number | null>(null);
</script>

<div class="chart" bind:clientWidth={measured}>
	<svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
		{#each grid as t (t)}
			<line class="grid" x1={PAD.left} x2={W - PAD.right} y1={y(t)} y2={y(t)} />
			<text
				class="tick"
				x={PAD.left - CHART.tickGap}
				y={y(t) + CHART.tickBaseline}
				text-anchor="end">{format(t)}</text
			>
		{/each}
		{#each spreads as s, i (s.x)}
			{@const mid = PAD.left + (i + HALF) * band}
			{@const half = (band * BOX) / 2}
			<g class:marked={s.marked} class:dim={hover !== null && hover !== i}>
				<line class="whisker" x1={mid} x2={mid} y1={y(s.q[P90])} y2={y(s.q[P10])} />
				<rect
					class="box"
					x={mid - half}
					y={y(s.q[P75])}
					width={half * 2}
					height={Math.max(1, y(s.q[P25]) - y(s.q[P75]))}
					rx={CHART.corner}
				/>
				<line class="median" x1={mid - half} x2={mid + half} y1={y(s.q[P50])} y2={y(s.q[P50])} />
			</g>
			{#if i % spacing === 0}
				<text class="tick" x={mid} y={H - CHART.axisLabel} text-anchor="middle">{s.x}</text>
			{/if}
			<rect
				role="presentation"
				class="hit"
				x={PAD.left + i * band}
				y={PAD.top}
				width={band}
				height={H - PAD.top - PAD.bottom}
				onpointerenter={() => (hover = i)}
				onpointerleave={() => (hover = null)}
			/>
		{/each}
	</svg>
	{#if hover !== null}
		{@const s = spreads[hover]}
		<div class="tip" style:left={`${((PAD.left + (hover + HALF) * band) / W) * PERCENT}%`}>
			<strong>{s.x}</strong>
			<span>{names.p90}: {format(s.q[P90])}</span>
			<span>{names.p75}: {format(s.q[P75])}</span>
			<span>{names.median}: <strong>{format(s.q[P50])}</strong></span>
			<span>{names.p25}: {format(s.q[P25])}</span>
			<span>{names.p10}: {format(s.q[P10])}</span>
		</div>
	{/if}
</div>

<style>
	.chart {
		position: relative;
	}
	svg {
		width: 100%;
		height: auto;
		display: block;
		overflow: visible;
	}
	.grid {
		stroke: var(--line);
	}
	.tick {
		fill: var(--dim);
		font-size: 11px;
		font-family: var(--mono);
	}
	.whisker {
		stroke: var(--dim);
		stroke-width: 1.5;
	}
	.box {
		fill: color-mix(in oklab, var(--series-1) 45%, var(--surface));
		stroke: var(--series-1);
		stroke-width: 1.5;
	}
	.marked .box {
		fill: color-mix(in oklab, var(--series-2) 45%, var(--surface));
		stroke: var(--series-2);
	}
	.median {
		stroke: var(--bright);
		stroke-width: 2;
	}
	g {
		transition: opacity 0.12s;
	}
	g.dim {
		opacity: 0.45;
	}
	.hit {
		fill: transparent;
	}
	.tip {
		position: absolute;
		top: 0;
		transform: translateX(-50%);
		pointer-events: none;
		background: var(--panel);
		border: 1px solid var(--line);
		padding: 0.25rem 0.5rem;
		font-size: 0.75rem;
		display: grid;
		gap: 0.1rem;
		white-space: nowrap;
		z-index: 1;
	}
	.tip strong {
		color: var(--bright);
	}
</style>
