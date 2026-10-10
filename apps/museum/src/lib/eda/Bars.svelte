<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- One series as vertical bars, one per category, with a tooltip on each. -->
<script lang="ts">
	import { CHAR_PX, labelEvery, ticks } from './eda';
	import { CHART, HALF, PERCENT } from './geometry';

	interface Point {
		x: string;
		y: number;
	}
	let {
		points,
		format,
		label,
		marked = [],
		every = 1
	}: {
		points: Point[];
		format: (value: number) => string;
		label: string;
		marked?: string[];
		every?: number; // label every nth category
	} = $props();

	let measured = $state(0);
	const W = $derived(Math.max(CHART.minWidth, measured || CHART.width));
	const H = 200;
	const PAD = { left: 46, right: 8, top: 10, bottom: 24 };
	const R = CHART.corner;
	const max = $derived(Math.max(0, ...points.map((p) => p.y)));
	const grid = $derived(ticks(max));
	const top = $derived(grid.at(-1) || 1);
	const band = $derived((W - PAD.left - PAD.right) / Math.max(1, points.length));
	const y = (value: number) => PAD.top + (H - PAD.top - PAD.bottom) * (1 - value / top);
	/** A bar standing on the baseline, its top corners rounded. */
	function bar(x: number, h: number): string {
		const side = Math.max(0, h - R);
		const across = Math.max(0, band - CHART.gap - 2 * R);
		return `M${x + CHART.gap / 2},${y(0)} v${-side} q0,${-R} ${R},${-R} h${across} q${R},0 ${R},${R} v${side} z`;
	}
	const widest = $derived(Math.max(0, ...points.map((p) => p.x.length)) * CHAR_PX);
	const spacing = $derived(labelEvery(band, widest, every));
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
		{#each points as p, i (p.x)}
			{@const x = PAD.left + i * band}
			<path
				class="bar"
				class:marked={marked.includes(p.x)}
				class:dim={hover !== null && hover !== i}
				d={bar(x, Math.max(0, y(0) - y(p.y)))}
			/>
			{#if i % spacing === 0}
				<text class="tick" x={x + band / 2} y={H - CHART.axisLabel} text-anchor="middle">{p.x}</text
				>
			{/if}
			<rect
				role="presentation"
				class="hit"
				{x}
				y={PAD.top}
				width={band}
				height={H - PAD.top - PAD.bottom}
				onpointerenter={() => (hover = i)}
				onpointerleave={() => (hover = null)}
			/>
		{/each}
	</svg>
	{#if hover !== null}
		{@const p = points[hover]}
		<div class="tip" style:left={`${((PAD.left + (hover + HALF) * band) / W) * PERCENT}%`}>
			<span>{p.x}</span> <strong>{format(p.y)}</strong>
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
		stroke-width: 1;
	}
	.tick {
		fill: var(--dim);
		font-size: 11px;
		font-family: var(--mono);
	}
	.bar {
		fill: var(--series-1);
		transition: opacity 0.12s;
	}
	.bar.marked {
		fill: var(--series-2);
	}
	.bar.dim {
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
		padding: 0.2rem 0.45rem;
		font-size: 0.75rem;
		white-space: nowrap;
		color: var(--ink);
	}
	.tip strong {
		color: var(--bright);
		font-weight: 600;
	}
</style>
