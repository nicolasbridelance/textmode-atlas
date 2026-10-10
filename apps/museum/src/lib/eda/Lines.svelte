<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- One or two series over ordered categories, labelled at their end, with a crosshair. -->
<script lang="ts">
	import { CHAR_PX, labelEvery, ticks } from './eda';
	import { CHART, PERCENT } from './geometry';

	interface Series {
		name: string;
		values: (number | null)[];
	}
	let {
		x,
		series,
		format,
		label,
		every = 1,
		max: fixedMax
	}: {
		x: string[];
		series: Series[];
		format: (value: number) => string;
		label: string;
		every?: number;
		max?: number;
	} = $props();

	let measured = $state(0);
	const W = $derived(Math.max(CHART.minWidth, measured || CHART.width));
	const H = 220;
	const ROOMY = 480; // below this width the legend names the lines, not their ends
	const END_ROOM = 150;
	const EDGE = 12;
	const ends = $derived(W >= ROOMY);
	const PAD = $derived({ left: 46, right: ends ? END_ROOM : EDGE, top: EDGE, bottom: 24 });
	const values = $derived(series.flatMap((s) => s.values.filter((v): v is number => v != null)));
	const grid = $derived(ticks(fixedMax ?? Math.max(0, ...values)));
	const top = $derived(grid.at(-1) || 1);
	const step = $derived((W - PAD.left - PAD.right) / Math.max(1, x.length - 1));
	const px = (i: number) => PAD.left + i * step;
	const py = (v: number) => PAD.top + (H - PAD.top - PAD.bottom) * (1 - v / top);
	function path(values: (number | null)[]): string {
		let d = '';
		let pen = false;
		values.forEach((v, i) => {
			if (v == null) {
				pen = false;
				return;
			}
			d += `${pen ? 'L' : 'M'}${px(i)},${py(v)}`;
			pen = true;
		});
		return d;
	}
	function last(values: (number | null)[]): number {
		for (let i = values.length - 1; i >= 0; i--) if (values[i] != null) return i;
		return -1;
	}
	const widest = $derived(Math.max(0, ...x.map((name) => name.length)) * CHAR_PX);
	const spacing = $derived(labelEvery(step, widest, every));
	let hover = $state<number | null>(null);
</script>

<div class="chart" bind:clientWidth={measured}>
	{#if series.length > 1}
		<ul class="legend">
			{#each series as s, k (s.name)}<li><span class={`key s${k + 1}`}></span>{s.name}</li>{/each}
		</ul>
	{/if}
	<svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
		{#each grid as t (t)}
			<line class="grid" x1={PAD.left} x2={W - PAD.right} y1={py(t)} y2={py(t)} />
			<text
				class="tick"
				x={PAD.left - CHART.tickGap}
				y={py(t) + CHART.tickBaseline}
				text-anchor="end">{format(t)}</text
			>
		{/each}
		{#each x as name, i (name)}
			{#if i % spacing === 0}
				<text class="tick" x={px(i)} y={H - CHART.axisLabel} text-anchor="middle">{name}</text>
			{/if}
		{/each}
		{#if hover !== null}
			<line class="cross" x1={px(hover)} x2={px(hover)} y1={PAD.top} y2={H - PAD.bottom} />
		{/if}
		{#each series as s, k (s.name)}
			{@const end = last(s.values)}
			<path class={`line s${k + 1}`} d={path(s.values)} />
			{#each s.values as v, i (i)}
				{#if v != null}<circle class={`dot s${k + 1}`} cx={px(i)} cy={py(v)} r="4" />{/if}
			{/each}
			{#if ends && end >= 0}
				<text
					class="end"
					x={px(end) + CHART.endLabel}
					y={py(s.values[end] ?? 0) + CHART.tickBaseline}>{s.name}</text
				>
			{/if}
		{/each}
		{#each x as name, i (name)}
			<rect
				role="presentation"
				class="hit"
				x={px(i) - step / 2}
				y={PAD.top}
				width={step}
				height={H - PAD.top - PAD.bottom}
				onpointerenter={() => (hover = i)}
				onpointerleave={() => (hover = null)}
			/>
		{/each}
	</svg>
	{#if hover !== null}
		<div class="tip" style:left={`${(px(hover) / W) * PERCENT}%`}>
			<span>{x[hover]}</span>
			{#each series as s, k (s.name)}
				{@const v = s.values[hover]}
				<span
					><span class={`key s${k + 1}`}></span>{s.name}:
					<strong>{v == null ? '–' : format(v)}</strong></span
				>
			{/each}
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
	.cross {
		stroke: var(--faint);
		stroke-dasharray: 2 3;
	}
	.tick,
	.end {
		fill: var(--dim);
		font-size: 11px;
		font-family: var(--mono);
	}
	.end {
		fill: var(--ink);
	}
	.line {
		fill: none;
		stroke-width: 2;
		stroke-linejoin: round;
	}
	.line.s1 {
		stroke: var(--series-1);
	}
	.line.s2 {
		stroke: var(--series-2);
	}
	.dot {
		stroke: var(--surface);
		stroke-width: 2;
	}
	.dot.s1,
	.key.s1 {
		fill: var(--series-1);
		background: var(--series-1);
	}
	.dot.s2,
	.key.s2 {
		fill: var(--series-2);
		background: var(--series-2);
	}
	.hit {
		fill: transparent;
	}
	.legend {
		display: flex;
		gap: 1rem;
		list-style: none;
		padding: 0;
		margin: 0 0 0.3rem;
		font-size: 0.75rem;
	}
	.key {
		display: inline-block;
		width: 0.7rem;
		height: 0.7rem;
		border-radius: 50%;
		margin-right: 0.35rem;
		vertical-align: -0.05rem;
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
	}
	.tip strong {
		color: var(--bright);
	}
</style>
