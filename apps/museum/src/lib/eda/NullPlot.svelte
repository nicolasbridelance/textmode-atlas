<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- What chance gives (a histogram of shuffles) against what was observed (a line). -->
<script lang="ts">
	import { CHART } from './geometry';

	let {
		counts,
		low,
		high,
		observed,
		q95,
		format,
		label,
		names
	}: {
		counts: number[];
		low: number;
		high: number;
		observed: number;
		q95: number;
		format: (value: number) => string;
		label: string;
		names: { chance: string; q95: string; observed: string };
	} = $props();

	let measured = $state(0);
	const W = $derived(Math.max(CHART.minWidth, measured || CHART.width));
	const H = 170;
	const PAD = { left: 12, right: 12, top: 30, bottom: 24 };
	const GAP = 1;
	const max = $derived(Math.max(1, ...counts));
	const band = $derived((W - PAD.left - PAD.right) / counts.length);
	const px = (v: number) => PAD.left + ((v - low) / (high - low)) * (W - PAD.left - PAD.right);
	const base = H - PAD.bottom;
	const STEP = 0.1;
	const marks = $derived(
		Array.from({ length: Math.round((high - low) / STEP) + 1 }, (_, i) => low + i * STEP)
	);
</script>

<div bind:clientWidth={measured}>
	<svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
		{#each counts as c, i (i)}
			{@const h = (c / max) * (base - PAD.top)}
			<rect
				class="chance"
				x={PAD.left + i * band + GAP / 2}
				y={base - h}
				width={band - GAP}
				height={h}
			/>
		{/each}
		<line class="axis" x1={PAD.left} x2={W - PAD.right} y1={base} y2={base} />
		{#each marks as m (m)}
			<text class="tick" x={px(m)} y={H - CHART.axisLabel} text-anchor="middle">{format(m)}</text>
		{/each}
		<line class="q95" x1={px(q95)} x2={px(q95)} y1={PAD.top - CHART.markerReach} y2={base} />
		<text class="note" x={px(q95) - CHART.tickGap} y={PAD.top - CHART.noteRise} text-anchor="end"
			>{names.q95}</text
		>
		<line
			class="observed"
			x1={px(observed)}
			x2={px(observed)}
			y1={PAD.top - CHART.markerReach}
			y2={base}
		/>
		<text class="note strong" x={px(observed) + CHART.tickGap} y={PAD.top - CHART.noteRise}
			>{names.observed} {format(observed)}</text
		>
		<text class="note" x={PAD.left} y={PAD.top + CHART.endLabel}>{names.chance}</text>
	</svg>
</div>

<style>
	svg {
		width: 100%;
		height: auto;
		display: block;
		overflow: visible;
	}
	.chance {
		fill: var(--faint);
		opacity: 0.7;
	}
	.axis {
		stroke: var(--line);
	}
	.tick,
	.note {
		fill: var(--dim);
		font-size: 11px;
		font-family: var(--mono);
	}
	.strong {
		fill: var(--bright);
	}
	.q95 {
		stroke: var(--dim);
		stroke-dasharray: 3 3;
	}
	.observed {
		stroke: var(--series-1);
		stroke-width: 2;
	}
</style>
