<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { fileUrl } from '../files';
	import type { Entry } from '../work/visit';
	let { name, entries, href }: { name: string; entries: Entry[]; href: (id: string) => string } =
		$props();
	const PER_RING = 12;
	const RING_GAP = 100;
	const MARGIN = 60;
	const NODE = 24;
	const LABEL_LENGTH = 18;
	const MIN_WIDTH = 600;
	const radius = $derived(Math.ceil(entries.length / PER_RING) * RING_GAP);
	const center = $derived(radius + MARGIN);
	const size = $derived(center * 2);
	const nodes = $derived(
		entries.map((entry, i) => {
			const ring = Math.floor(i / PER_RING);
			const count = Math.min(PER_RING, entries.length - ring * PER_RING);
			const angle = ((i % PER_RING) / count) * Math.PI * 2 - Math.PI / 2;
			return {
				entry,
				x: center + Math.cos(angle) * (ring + 1) * RING_GAP,
				y: center + Math.sin(angle) * (ring + 1) * RING_GAP
			};
		})
	);
</script>

<div class="map">
	<svg
		viewBox="0 0 {size} {size}"
		style:width="{size}px"
		style:min-width="{Math.min(size, MIN_WIDTH)}px"
		aria-label={name}
	>
		{#each nodes as node (node.entry.sha256)}<line
				x1={center}
				y1={center}
				x2={node.x}
				y2={node.y}
			/>{/each}
		<circle cx={center} cy={center} r="6" class="hub" />
		{#each nodes as { entry, x, y } (entry.sha256)}
			<a href={href(entry.sha256)} aria-label={entry.title || entry.file}>
				<title>{entry.title || entry.file} · {name}</title>
				<circle cx={x} cy={y} r={NODE + 2} />
				<image
					href={fileUrl(`works/${entry.sha256}/conservation.png`)}
					x={x - NODE}
					y={y - NODE}
					width={NODE * 2}
					height={NODE * 2}
					preserveAspectRatio="xMidYMid meet"
				/>
				<text {x} y={y + NODE * 2} text-anchor="middle"
					>{(entry.title || entry.file).slice(0, LABEL_LENGTH)}</text
				>
			</a>
		{/each}
	</svg>
</div>

<style>
	.map {
		overflow-x: auto;
	}
	svg {
		display: block;
		max-width: 55rem;
		width: 100%;
		margin: auto;
	}
	line {
		stroke: var(--line);
		stroke-width: 1;
	}
	circle {
		fill: #000;
		stroke: var(--dim);
	}
	.hub {
		fill: var(--accent);
		stroke: var(--accent);
	}
	text {
		fill: var(--ink);
		font: 11px var(--mono);
	}
	a:hover circle,
	a:focus-visible circle {
		stroke: var(--accent);
		stroke-width: 2;
	}
</style>
