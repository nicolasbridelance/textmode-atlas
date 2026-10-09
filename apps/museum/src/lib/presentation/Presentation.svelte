<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { localizeHref } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import type { Work } from '../work/record';
	import { exportPresentation } from './export';
	import { DEFAULT_EFFECT } from './effects';
	import { preferences, STYLES, SAMPLING, FRAMES } from './settings.svelte';
	let { work, font }: { work: Work; font: Uint8Array } = $props();
	let scale = $state(1);
	let busy = $state(false);
	let error = $state(false);
	const scales = [1, 2, 4]; // eslint-disable-line @typescript-eslint/no-magic-numbers
	const styles = $derived({
		original: m.style_original(),
		paper: m.style_paper(),
		density: m.style_density(),
		reconstruction: m.style_reconstruction(),
		halftone: m.style_halftone(),
		kuwahara: m.style_kuwahara(),
		pointillism: m.style_pointillism(),
		impressionism: m.style_impressionism(),
		graffiti: m.style_graffiti()
	});
	const rules = $derived({
		original: m.presentation_rule_original(),
		paper: m.presentation_rule_paper(),
		density: m.presentation_rule_density(),
		reconstruction: m.presentation_rule_reconstruction(),
		halftone: m.presentation_rule_halftone(),
		kuwahara: m.presentation_rule_kuwahara(),
		pointillism: m.presentation_rule_pointillism(),
		impressionism: m.presentation_rule_impressionism(),
		graffiti: m.presentation_rule_graffiti()
	});
	const frames = $derived({ none: m.frame_none(), line: m.frame_line(), mat: m.frame_mat() });
	const sampling = $derived({
		pixels: m.sampling_pixels(),
		smooth: m.sampling_smooth(),
		gaussian: m.sampling_gaussian()
	});
	async function download(): Promise<void> {
		busy = true;
		error = false;
		try {
			await exportPresentation(work, font, { ...preferences }, scale);
		} catch {
			error = true;
		} finally {
			busy = false;
		}
	}
</script>

<details class="workshop">
	<summary>{m.presentation_title()}</summary>
	<div class="fields">
		<label
			>{m.presentation_background()}
			<input type="color" bind:value={preferences.background} /></label
		>
		<label
			>{m.presentation_frame()}
			<select data-control="frame" bind:value={preferences.frame}
				>{#each FRAMES as frame (frame)}<option value={frame}>{frames[frame]}</option
					>{/each}</select
			></label
		>
		<label
			>{m.presentation_style()}
			<select data-control="style" bind:value={preferences.style}
				>{#each STYLES as style (style)}<option value={style}>{styles[style]}</option
					>{/each}</select
			></label
		>
		<label
			>{m.presentation_sampling()}
			<select data-control="sampling" bind:value={preferences.sampling}
				>{#each SAMPLING as mode (mode)}<option value={mode}>{sampling[mode]}</option
					>{/each}</select
			></label
		>
	</div>
	{#if !['original', 'paper', 'density', 'reconstruction'].includes(preferences.style)}
		<div class="fields effect-settings">
			<label
				>{m.presentation_size()} · {preferences.size}px
				<input type="range" min="3" max="12" step="1" bind:value={preferences.size} /></label
			>
			<label
				>{m.presentation_strength()} · {preferences.strength}%
				<input type="range" min="0" max="100" step="5" bind:value={preferences.strength} /></label
			>
			<label
				>{m.presentation_preparation()}
				<select bind:value={preferences.preparation}
					><option value="coverage">{m.presentation_input_coverage()}</option><option value="pixels"
						>{m.presentation_input_pixels()}</option
					></select
				></label
			>
			{#if preferences.style !== 'kuwahara'}<label
					>{m.presentation_paper()}
					<select bind:value={preferences.paper}
						><option value="dark">{m.presentation_dark_support()}</option><option value="light"
							>{m.presentation_light_support()}</option
						></select
					></label
				>{/if}
		</div>
	{/if}

	<p>{rules[preferences.style]}</p>
	{#if preferences.sampling === 'gaussian'}<p>{m.presentation_gaussian_note()}</p>{/if}
	{#if preferences.style !== 'original' || preferences.sampling !== 'pixels'}<p class="badge">
			{m.presentation_interpretation()}
		</p>{/if}
	<div class="fields">
		<label
			>{m.presentation_export_scale()}
			<select data-control="export-scale" bind:value={scale}
				>{#each scales as value (value)}<option {value}>{value}×</option>{/each}</select
			></label
		>
		<button type="button" disabled={busy} onclick={download}
			>{busy ? m.presentation_exporting() : m.presentation_export()}</button
		>
		<button
			type="button"
			onclick={() =>
				Object.assign(preferences, {
					background: '#000000',
					frame: 'none',
					style: 'original',
					sampling: 'pixels',
					...DEFAULT_EFFECT
				})}>{m.presentation_reset()}</button
		>
	</div>
	<p>
		<a href={localizeHref('/research')}>{m.presentation_review_link()}</a>
	</p>
	<p>{m.presentation_export_note()}</p>
	{#if error}<p role="alert">{m.presentation_export_error()}</p>{/if}
</details>

<style>
	.workshop {
		border-block: 1px solid var(--line);
		padding-block: 0.6rem;
		font-size: 0.8rem;
	}
	summary {
		cursor: pointer;
		color: var(--bright);
	}
	.fields {
		display: grid;
		gap: 0.65rem;
		margin-block: 0.8rem;
	}
	label {
		display: grid;
		grid-template-columns: 1fr;
		gap: 0.25rem;
	}
	select,
	button,
	input {
		font: inherit;
		color: var(--ink);
		background: var(--panel);
		border: 1px solid var(--line);
		border-radius: 3px;
		padding: 0.4rem;
		min-width: 0;
	}
	input {
		width: 100%;
		height: 2rem;
		box-sizing: border-box;
	}
	button {
		cursor: pointer;
	}
	p {
		color: var(--dim);
		line-height: 1.5;
	}
	.badge {
		color: var(--accent);
	}
</style>
