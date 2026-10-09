<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { onDestroy } from 'svelte';
	import { CELL_HEIGHT, CELL_WIDTH, paintCell } from './draw';
	import { BBS_BAUD } from './time';
	import { arrivalOrder, type TmgGrid } from './tmg';

	// A modem sends about baud / 10 characters a second (8 data bits, start and stop bits); `t`
	// is the offset of the byte that wrote the cell, so a cell appears at t / (baud / 10).
	const BITS_PER_BYTE = 10;
	const MS_PER_S = 1000;
	const RGBA = 4;
	const OPAQUE = 255;
	const MAX_FIT = 2;

	let {
		grid,
		font,
		label,
		showAll = false,
		replay = 0,
		baud = BBS_BAUD,
		zoom = 0,
		scale = $bindable(1),
		cell = $bindable(null)
	}: {
		grid: TmgGrid;
		font: Uint8Array;
		label: string;
		showAll?: boolean;
		replay?: number;
		baud?: number;
		/** 0 fits the work to the width it is given; otherwise a whole scale (1×, 2×…). */
		zoom?: number;
		/** The scale the work is drawn at, read by the controls. */
		scale?: number;
		/** The cell under the pointer, by index, or null. */
		cell?: number | null;
	} = $props();

	let canvas: HTMLCanvasElement | undefined = $state();
	let room = $state(0);
	let frame = 0;

	const width = $derived(grid.cols * CELL_WIDTH);
	const height = $derived(grid.rows * CELL_HEIGHT);
	// Fitting keeps whole scales while the work fits, so pixels stay square, up to 2× (larger is the
	// visitor's choice); below one it shrinks.
	const fit = $derived(
		room >= width ? Math.min(MAX_FIT, Math.floor(room / width)) : room / width || 1
	);
	$effect(() => {
		scale = zoom > 0 ? zoom : fit;
	});

	function start(target: HTMLCanvasElement, atOnce: boolean): void {
		cancelAnimationFrame(frame);
		const context = target.getContext('2d');
		if (!context) return;
		const image = context.createImageData(width, height);
		for (let i = RGBA - 1; i < image.data.length; i += RGBA) image.data[i] = OPAQUE;
		const order = arrivalOrder(grid);
		const bytesPerMs = baud / BITS_PER_BYTE / MS_PER_S;
		let drawn = 0;
		const began = performance.now();
		const step = (now: number): void => {
			const reached = atOnce ? Infinity : (now - began) * bytesPerMs;
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

	function point(event: PointerEvent): void {
		const col = Math.floor(event.offsetX / (CELL_WIDTH * scale));
		const row = Math.floor(event.offsetY / (CELL_HEIGHT * scale));
		const inside = col >= 0 && col < grid.cols && row >= 0 && row < grid.rows;
		cell = inside ? row * grid.cols + col : null;
	}

	const outline = $derived(
		cell === null
			? null
			: {
					left: (cell % grid.cols) * CELL_WIDTH * scale,
					top: Math.floor(cell / grid.cols) * CELL_HEIGHT * scale,
					width: CELL_WIDTH * scale,
					height: CELL_HEIGHT * scale
				}
	);
</script>

<div class="room" bind:clientWidth={room}>
	<figure role="img" aria-label={label} style:width="{width * scale}px">
		<canvas
			bind:this={canvas}
			{width}
			{height}
			aria-hidden="true"
			class:smooth={scale < 1}
			style:width="{width * scale}px"
			style:height="{height * scale}px"
			onpointermove={point}
			onpointerdown={point}
			onpointerleave={() => (cell = null)}
		></canvas>
		{#if outline && scale >= 2}
			<span
				class="cell"
				style:left="{outline.left}px"
				style:top="{outline.top}px"
				style:width="{outline.width}px"
				style:height="{outline.height}px"
			></span>
		{/if}
	</figure>
</div>

<style>
	.room {
		overflow-x: auto;
		overscroll-behavior-x: contain;
	}
	figure {
		position: relative;
		margin: 0 auto;
	}
	canvas {
		display: block;
		image-rendering: pixelated;
		touch-action: pan-x pan-y pinch-zoom;
	}
	/* Below one pixel per pixel, averaging keeps the drawing legible; whole scales stay sharp. */
	canvas.smooth {
		image-rendering: auto;
	}
	.cell {
		position: absolute;
		pointer-events: none;
		outline: 1px solid var(--accent);
		box-shadow: 0 0 0 1px #000;
	}
</style>
