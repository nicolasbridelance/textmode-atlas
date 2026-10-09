<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { onDestroy } from 'svelte';
	import { CELL_HEIGHT, CELL_WIDTH, paintCell } from './draw';
	import { arrivalOrder, type TmgGrid } from './tmg';

	// A modem sends about baud / 10 characters a second (8 data bits, start and stop bits); `t`
	// is the offset of the byte that wrote the cell, so a cell appears at t / (baud / 10).
	const BAUD = 2400;
	const BITS_PER_BYTE = 10;
	const MS_PER_S = 1000;
	const BYTES_PER_MS = BAUD / BITS_PER_BYTE / MS_PER_S;
	const RGBA = 4;
	const OPAQUE = 255;

	let {
		grid,
		font,
		label,
		showAll = false,
		replay = 0
	}: {
		grid: TmgGrid;
		font: Uint8Array;
		label: string;
		showAll?: boolean;
		replay?: number;
	} = $props();

	let canvas: HTMLCanvasElement | undefined = $state();
	let frame = 0;

	const width = $derived(grid.cols * CELL_WIDTH);
	const height = $derived(grid.rows * CELL_HEIGHT);

	function start(target: HTMLCanvasElement, atOnce: boolean): void {
		cancelAnimationFrame(frame);
		const context = target.getContext('2d');
		if (!context) return;
		const image = context.createImageData(width, height);
		image.data.fill(0);
		for (let i = RGBA - 1; i < image.data.length; i += RGBA) image.data[i] = OPAQUE;
		const order = arrivalOrder(grid);
		let drawn = 0;
		const began = performance.now();
		const step = (now: number): void => {
			const reached = atOnce ? Infinity : (now - began) * BYTES_PER_MS;
			let top = Infinity;
			let bottom = -1;
			while (drawn < order.length && grid.t[order[drawn]] <= reached) {
				const row = Math.floor(order[drawn] / grid.cols);
				top = Math.min(top, row);
				bottom = Math.max(bottom, row);
				paintCell(image.data, width, grid, font, order[drawn++]);
			}
			if (bottom >= 0) {
				const y = top * CELL_HEIGHT;
				context.putImageData(image, 0, 0, 0, y, width, (bottom - top + 1) * CELL_HEIGHT);
			}
			if (drawn < order.length) frame = requestAnimationFrame(step);
		};
		context.putImageData(image, 0, 0);
		frame = requestAnimationFrame(step);
	}

	$effect(() => {
		void replay; // a new value draws the arrival again
		if (!canvas) return;
		const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
		start(canvas, showAll || reduced);
	});

	onDestroy(() => cancelAnimationFrame(frame));
</script>

<figure role="img" aria-label={label}>
	<canvas bind:this={canvas} {width} {height} aria-hidden="true" style:--cols={grid.cols}></canvas>
</figure>

<style>
	figure {
		margin: 0;
	}
	canvas {
		display: block;
		width: min(100%, calc(var(--cols) * 16px));
		height: auto;
		image-rendering: pixelated;
		margin-inline: auto;
	}
</style>
