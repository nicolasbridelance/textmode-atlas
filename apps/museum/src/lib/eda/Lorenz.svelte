<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Lorenz curves: the smallest share x of the groups holds the share y of the works. The
     diagonal is perfect equality; the further below it, the more a few groups hold. -->
<script lang="ts">
	import { CHART, HALF, PERCENT } from './geometry';

	interface Curve {
		name: string;
		points: [number, number][];
		colour: string;
	}
	let {
		curves,
		label,
		names
	}: {
		curves: Curve[];
		label: string;
		names: { x: string; y: string; equality: string };
	} = $props();

	let measured = $state(0);
	const MAX_SIDE = 420;
	const SIDE = $derived(Math.min(MAX_SIDE, Math.max(CHART.minWidth, measured || MAX_SIDE)));
	const PAD = { left: 46, right: 12, top: 12, bottom: 40 };
	const plot = $derived(SIDE - PAD.left - PAD.right);
	const px = (v: number) => PAD.left + v * plot;
	const py = (v: number) => PAD.top + (1 - v) * plot;
	const marks = [0, HALF, 1];
	const path = (points: [number, number][]) =>
		points.map(([x, y], i) => `${i ? 'L' : 'M'}${px(x)},${py(y)}`).join('');
</script>

<div class="chart" bind:clientWidth={measured}>
	<ul class="legend">
		{#each curves as c (c.name)}<li>
				<span class="key" style:background={c.colour}></span>{c.name}
			</li>{/each}
		<li><span class="key equal"></span>{names.equality}</li>
	</ul>
	<svg
		viewBox={`0 0 ${SIDE} ${PAD.top + plot + PAD.bottom}`}
		style:max-width={`${MAX_SIDE}px`}
		role="img"
		aria-label={label}
	>
		{#each marks as m (m)}
			<line class="grid" x1={px(0)} x2={px(1)} y1={py(m)} y2={py(m)} />
			<line class="grid" x1={px(m)} x2={px(m)} y1={py(0)} y2={py(1)} />
			<text
				class="tick"
				x={PAD.left - CHART.tickGap}
				y={py(m) + CHART.tickBaseline}
				text-anchor="end">{m * PERCENT} %</text
			>
			<text class="tick" x={px(m)} y={py(0) + CHART.axisLabel * 2} text-anchor="middle"
				>{m * PERCENT} %</text
			>
		{/each}
		<line class="equality" x1={px(0)} y1={py(0)} x2={px(1)} y2={py(1)} />
		{#each curves as c (c.name)}
			<path class="curve" d={path(c.points)} style:stroke={c.colour} />
		{/each}
		<text class="axis" x={px(HALF)} y={py(0) + CHART.axisTitle} text-anchor="middle">{names.x}</text
		>
	</svg>
	<p class="axis-note">{names.y}</p>
</div>

<style>
	svg {
		width: 100%;
		height: auto;
		display: block;
		overflow: visible;
	}
	.grid {
		stroke: var(--line);
	}
	.tick,
	.axis {
		fill: var(--dim);
		font-size: 11px;
		font-family: var(--mono);
	}
	.equality {
		stroke: var(--faint);
		stroke-dasharray: 4 4;
	}
	.curve {
		fill: none;
		stroke-width: 2;
		stroke-linejoin: round;
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
		width: 0.9rem;
		height: 0.18rem;
		margin-right: 0.35rem;
		vertical-align: 0.2rem;
	}
	.key.equal {
		border-top: 2px dashed var(--faint);
		height: 0;
	}
	.axis-note {
		font-size: 0.72rem;
		color: var(--dim);
		margin: 0.2rem 0 0;
	}
</style>
