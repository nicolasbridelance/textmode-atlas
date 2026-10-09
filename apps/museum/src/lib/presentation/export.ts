// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { CELL_HEIGHT, CELL_WIDTH } from '../work/draw';
import type { Work } from '../work/record';
import { renderPixels } from './render';
import { FRAME_PADDING, FRAME_COLOUR, type preferences } from './settings.svelte';

const MAX_PIXELS = 24_000_000;
const HEX = 16;

function download(blob: Blob, name: string): void {
	const url = URL.createObjectURL(blob);
	const link = document.createElement('a');
	link.href = url;
	link.download = name;
	link.click();
	setTimeout(() => URL.revokeObjectURL(url), 1000); // eslint-disable-line @typescript-eslint/no-magic-numbers
}

function presentationCanvas(
	work: Work,
	font: Uint8Array,
	settings: typeof preferences,
	scale: number
): HTMLCanvasElement {
	if (!work.grid) throw new Error('grid');
	const padding = FRAME_PADDING[settings.frame];
	const width = work.grid.cols * CELL_WIDTH;
	const height = work.grid.rows * CELL_HEIGHT;
	const target = document.createElement('canvas');
	target.width = (width + padding * 2) * scale;
	target.height = (height + padding * 2) * scale;
	if (target.width * target.height > MAX_PIXELS) throw new Error('size');
	const source = document.createElement('canvas');
	source.width = width;
	source.height = height;
	const context = source.getContext('2d');
	const output = target.getContext('2d');
	if (!context || !output) throw new Error('canvas');
	const pixels = context.createImageData(width, height);
	pixels.data.set(renderPixels(work.grid, font, settings.style, settings.sampling, settings));
	context.putImageData(pixels, 0, 0);
	output.fillStyle = FRAME_COLOUR[settings.frame];
	output.fillRect(0, 0, target.width, target.height);
	output.imageSmoothingEnabled = settings.sampling !== 'pixels';
	output.imageSmoothingQuality = 'high';
	output.drawImage(source, padding * scale, padding * scale, width * scale, height * scale);
	return target;
}

/** Export the whole work, independently of the arrival animation and viewport. */
export async function exportPresentation(
	work: Work,
	font: Uint8Array,
	settings: typeof preferences,
	scale: number
): Promise<void> {
	if (!work.grid) return;
	const target = presentationCanvas(work, font, settings, scale);
	const blob = await new Promise<Blob | null>((done) => target.toBlob(done, 'image/png'));
	if (!blob) throw new Error('png');
	const fontHash = Array.from(
		new Uint8Array(await crypto.subtle.digest('SHA-256', new Uint8Array(font))),
		(byte) => byte.toString(HEX).padStart(2, '0')
	).join('');
	const recipe = {
		schema: 1,
		level:
			settings.style === 'original' && settings.sampling === 'pixels'
				? 'conservation'
				: 'interpretation',
		asserted_by: 'algo:museum-presentation-v2',
		source_sha256: work.record.sha256,
		grid_sha256: work.record.files['grid.tmg'],
		font_sha256: fontHash,
		settings: { ...settings, scale },
		width: target.width,
		height: target.height,
		resampling: settings.sampling === 'pixels' ? 'nearest-neighbour' : 'browser-high-quality',
		user_agent: navigator.userAgent
	};
	const name = `${work.record.sha256}-${settings.style}-${scale}x`;
	download(
		new Blob([JSON.stringify(recipe, null, 2)], { type: 'application/json' }),
		`${name}.json`
	);
	download(blob, `${name}.png`);
}
