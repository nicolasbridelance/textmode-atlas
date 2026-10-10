<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Parts of a whole per category: stacked columns, as counts or as shares of 100 %. -->
<script lang="ts">
	import { CHAR_PX, labelEvery, ticks } from './eda';
	import { CHART, HALF, PERCENT } from './geometry';

	interface Part {
		name: string;
		values: number[];
		colour: string; // a CSS colour; text never wears it
	}
	let {
		x,
		parts,
		format,
		label,
		share = false,
		legend = true,
		height = CHART.height
	}: {
		x: string[];
		parts: Part[];
		format: (value: number) => string;
		label: string;
		share?: boolean; // each column scaled to 100 %
		legend?: boolean;
		height?: number;
	} = $props();

	let measured = $state(0);
	const W = $derived(Math.max(CHART.minWidth, measured || CHART.width));
	const H = $derived(height);
	const PAD = { left: 46, right: 8, top: 10, bottom: 24 };
	const totals = $derived(x.map((_, i) => parts.reduce((sum, p) => sum + (p.values[i] ?? 0), 0)));
	const grid = $derived(share ? [0, HALF, 1] : ticks(Math.max(0, ...totals)));
	const top = $derived(grid.at(-1) || 1);
	const band = $derived((W - PAD.left - PAD.right) / Math.max(1, x.length));
	const spacing = $derived(labelEvery(band, Math.max(0, ...x.map((n) => n.length)) * CHAR_PX));
	const y = (value: number) => PAD.top + (H - PAD.top - PAD.bottom) * (1 - value / top);
	/** The segments of one column, bottom up, as [start, end] in the axis' unit. */
	function segments(i: number): [number, number][] {
		const scale = share && totals[i] ? 1 / totals[i] : 1;
		let at = 0;
		return parts.map((p) => {
			const start = at;
			at += (p.values[i] ?? 0) * scale;
			return [start, at];
		});
	}
	let hover = $state<number | null>(null);
</script>

<div class="chart" bind:clientWidth={measured}>
	{#if legend}
		<ul class="legend">
			{#each parts as p (p.name)}<li>
					<span class="key" style:background={p.colour}></span>{p.name}
				</li>{/each}
		</ul>
	{/if}
	<svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
		{#each grid as t (t)}
			<line class="grid" x1={PAD.left} x2={W - PAD.right} y1={y(t)} y2={y(t)} />
			<text
				class="tick"
				x={PAD.left - CHART.tickGap}
				y={y(t) + CHART.tickBaseline}
				text-anchor="end">{share ? `${t * PERCENT} %` : format(t)}</text
			>
		{/each}
		{#each x as name, i (name)}
			{@const left = PAD.left + i * band + CHART.gap / 2}
			<g class:dim={hover !== null && hover !== i}>
				{#each segments(i) as [start, end], k (k)}
					{#if end > start}
						<rect
							x={left}
							y={y(end)}
							width={Math.max(1, band - CHART.gap)}
							height={Math.max(0, y(start) - y(end) - (k ? 1 : 0))}
							style:fill={parts[k].colour}
						/>
					{/if}
				{/each}
			</g>
			{#if i % spacing === 0}
				<text class="tick" x={left + band / 2} y={H - CHART.axisLabel} text-anchor="middle"
					>{name}</text
				>
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
		<div class="tip" style:left={`${((PAD.left + (hover + HALF) * band) / W) * PERCENT}%`}>
			<strong>{x[hover]}</strong>
			{#each [...parts].reverse() as p (p.name)}
				{@const v = p.values[hover] ?? 0}
				{#if v}
					<span
						><span class="key" style:background={p.colour}></span>{p.name}: {share
							? format(v / (totals[hover] || 1))
							: format(v)}</span
					>
				{/if}
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
	.tick {
		fill: var(--dim);
		font-size: 11px;
		font-family: var(--mono);
	}
	g {
		transition: opacity 0.12s;
	}
	g rect {
		stroke: var(--line); /* black ink stays visible on a black page */
		stroke-width: 0.5;
	}
	g.dim {
		opacity: 0.45;
	}
	.hit {
		fill: transparent;
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 0.3rem 1rem;
		list-style: none;
		padding: 0;
		margin: 0 0 0.4rem;
		font-size: 0.75rem;
	}
	.key {
		display: inline-block;
		width: 0.7rem;
		height: 0.7rem;
		border-radius: 2px;
		margin-right: 0.35rem;
		vertical-align: -0.05rem;
		outline: 1px solid var(--line);
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
