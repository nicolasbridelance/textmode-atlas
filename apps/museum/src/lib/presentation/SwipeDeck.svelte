<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import { previewUrl } from './catalogue';
	import type { Entry } from '../work/visit';
	import ArtworkPreview from './ArtworkPreview.svelte';
	let {
		entries,
		saved,
		setSaved,
		href,
		active = true,
		total,
		hasMore,
		loadingMore,
		more
	}: {
		entries: Entry[];
		saved: string[];
		setSaved: (id: string, value: boolean) => void;
		href: (id: string) => string;
		active?: boolean;
		total: number;
		hasMore: boolean;
		loadingMore: boolean;
		more: () => Promise<void>;
	} = $props();
	const SWIPE_THRESHOLD = 70;
	const ROTATION_DIVISOR = 24;
	let index = $state(0);
	let history: { id: string; wasSaved: boolean }[] = $state([]);
	let offset = $state(0);
	let pointer: number | null = null;
	let start = 0;
	let consumed = false;
	const current = $derived(entries[index]);
	const next = $derived(entries[index + 1]);
	function decide(keep: boolean): void {
		if (!current) return;
		history = [...history, { id: current.sha256, wasSaved: saved.includes(current.sha256) }];
		if (keep) setSaved(current.sha256, true);
		index += 1;
		offset = 0;
	}
	function undo(): void {
		const previous = history.at(-1);
		if (!previous) return;
		setSaved(previous.id, previous.wasSaved);
		history = history.slice(0, -1);
		index -= 1;
	}
	function reset(): void {
		index = 0;
		history = [];
		offset = 0;
	}
	function keyboard(event: KeyboardEvent): void {
		if (!active) return;
		if (
			event.target instanceof HTMLElement &&
			event.target.closest('input, select, textarea, [contenteditable="true"]')
		)
			return;
		if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
			event.preventDefault();
			decide(event.key === 'ArrowRight');
		}
	}
	function begin(event: PointerEvent): void {
		if (event.button !== 0) return;
		pointer = event.pointerId;
		start = event.clientX;
		consumed = false;
		(event.currentTarget as HTMLElement).setPointerCapture(event.pointerId);
	}
	function move(event: PointerEvent): void {
		if (event.pointerId === pointer) offset = event.clientX - start;
	}
	function end(event: PointerEvent): void {
		if (event.pointerId !== pointer) return;
		pointer = null;
		consumed = Math.abs(offset) > SWIPE_THRESHOLD;
		if (consumed) decide(offset > 0);
		offset = 0;
	}
	function cancel(): void {
		pointer = null;
		offset = 0;
	}
	function open(event: MouseEvent): void {
		if (consumed) {
			event.preventDefault();
			consumed = false;
		}
	}
</script>

<svelte:window onkeydown={keyboard} />

<div class="swipe-layout" data-layout="tinder">
	<aside class="deck-intro">
		<span class="deck-label">{m.discovery_deck_label()}</span>
		<h2>{m.discovery_deck_title()}</h2>
		<p>{m.discovery_deck_note()}</p>
		<div class="key-guide">
			<span>←</span>
			{m.discovery_pass()} <span>→</span>
			{m.discovery_keep()}
		</div>
		<p class="local-note">{m.discovery_local_note()}</p>
	</aside>
	<div class="deck">
		<div class="progress" role="status">
			{m.discovery_progress({
				current: Math.min(index + 1, total),
				total
			})}
		</div>
		{#if current}
			<div class="card-stack">
				<div class="back-card" aria-hidden="true"></div>
				<article
					class="swipe-card"
					style:transform={`translateX(${offset}px) rotate(${offset / ROTATION_DIVISOR}deg)`}
				>
					<a
						class="swipe-image"
						href={href(current.sha256)}
						aria-label={m.discovery_open()}
						onpointerdown={begin}
						onpointermove={move}
						onpointerup={end}
						onpointercancel={cancel}
						onclick={open}
						ondragstart={(event) => event.preventDefault()}
					>
						<ArtworkPreview entry={current} eager />
						{#if Math.abs(offset) > SWIPE_THRESHOLD}<span class="decision" class:keep={offset > 0}
								>{offset > 0 ? m.discovery_keep() : m.discovery_pass()}</span
							>{/if}
					</a>
					<div class="card-caption">
						<div class="card-topline">
							<span>{current.year || m.explore_unknown()}</span><span
								>{current.pack || m.discovery_archive()}</span
							>
						</div>
						<h2><a href={href(current.sha256)}>{current.title || current.file}</a></h2>
						<p>
							{[current.author, current.group].filter(Boolean).join(' / ') || m.explore_unknown()}
						</p>
					</div>
				</article>
			</div>
			<div class="decisions">
				<button
					class="undo"
					type="button"
					onclick={undo}
					disabled={!history.length}
					aria-label={m.discovery_undo()}>↶</button
				>
				<button class="pass" type="button" onclick={() => decide(false)}
					><span aria-hidden="true">×</span>{m.discovery_pass()}</button
				>
				<button class="keep-button" type="button" onclick={() => decide(true)}
					><span aria-hidden="true">♡</span>{m.discovery_keep()}</button
				>
			</div>
			<p class="swipe-hint">{m.discovery_swipe_hint()}</p>
		{:else}
			<section class="finished">
				<span aria-hidden="true">✦</span>
				<h2>{hasMore ? m.browse_continue() : m.discovery_finished()}</h2>
				<p>{hasMore ? m.browse_more_cards() : m.discovery_finished_note()}</p>
				{#if hasMore}<button type="button" disabled={loadingMore} onclick={() => void more()}
						>{loadingMore ? m.explore_loading() : m.explore_more()}</button
					>
				{:else}<button type="button" onclick={reset}>{m.discovery_restart()}</button>{/if}
				<button type="button" onclick={undo} disabled={!history.length}>{m.discovery_undo()}</button
				>
			</section>
		{/if}
		{#if next && previewUrl(next)}<img src={previewUrl(next)!} alt="" hidden />{/if}
	</div>
</div>

<style>
	.swipe-layout {
		display: grid;
		grid-template-columns: 260px minmax(0, 460px);
		justify-content: center;
		gap: 6rem;
		align-items: center;
	}
	.deck-label {
		text-transform: uppercase;
		font: 0.65rem var(--mono);
		letter-spacing: 0.18em;
		color: #ac89a5;
	}
	.deck-intro h2 {
		font-size: clamp(2rem, 4vw, 3rem);
		font-weight: 600;
		letter-spacing: -0.055em;
		line-height: 1.1;
		margin: 1.2rem 0;
	}
	.deck-intro p {
		font-size: 0.9rem;
		line-height: 1.8;
		color: var(--discovery-dim);
	}
	.key-guide {
		font-size: 0.8rem;
		display: flex;
		align-items: center;
		gap: 0.6rem;
		margin-top: 2rem;
	}
	.key-guide span {
		border: 1px solid var(--discovery-line);
		border-radius: 0.4rem;
		padding: 0.4rem 0.6rem;
	}
	.deck-intro .local-note {
		font-size: 0.7rem;
		margin-top: 2rem;
	}
	.deck {
		min-width: 0;
		width: 100%;
	}
	.progress {
		text-align: center;
		font: 0.7rem var(--mono);
		color: var(--discovery-dim);
		margin: 0 0 1.3rem;
	}
	.card-stack {
		position: relative;
		margin: 0 0.6rem;
	}
	.back-card {
		position: absolute;
		inset: 0;
		border: 1px solid #5f354e;
		border-radius: 1.2rem;
		background: #241a28;
		transform: rotate(3deg);
	}
	.swipe-card {
		position: relative;
		border-radius: 1.2rem;
		overflow: hidden;
		background: #18121d;
		border: 1px solid #513343;
		box-shadow: 0 18px 60px #0005;
	}
	.swipe-image {
		display: flex;
		align-items: center;
		background: #000;
		height: clamp(15rem, 45dvh, 29rem);
		position: relative;
		touch-action: pan-y;
		cursor: grab;
		--art-height: 100%;
	}
	.swipe-image:active {
		cursor: grabbing;
	}
	.card-caption {
		padding: 1.2rem 1.5rem;
	}
	.card-topline {
		display: flex;
		justify-content: space-between;
		gap: 1rem;
		font: 0.65rem var(--mono);
		text-transform: uppercase;
		color: var(--discovery-dim);
		overflow-wrap: anywhere;
	}
	.card-caption h2 {
		font-size: 1.4rem;
		letter-spacing: -0.025em;
		margin: 0.7rem 0 0.4rem;
		overflow-wrap: anywhere;
	}
	.card-caption a {
		color: inherit;
		text-decoration: none;
	}
	.card-caption p {
		font-size: 0.8rem;
		color: #c6aabf;
		margin: 0;
		overflow-wrap: anywhere;
	}
	.decisions {
		display: flex;
		justify-content: center;
		align-items: center;
		gap: 1rem;
		margin-top: 1.8rem;
	}
	button {
		font: inherit;
		cursor: pointer;
		color: inherit;
		border: 1px solid var(--discovery-line);
		border-radius: 3rem;
		background: transparent;
		min-height: 44px;
		padding: 0.7rem 1.3rem;
	}
	button:disabled {
		opacity: 0.35;
		cursor: default;
	}
	.pass,
	.keep-button {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.6rem;
		font-size: 0.8rem;
	}
	.pass span,
	.keep-button span {
		font-size: 1.5rem;
	}
	.keep-button {
		background: #f75380;
		color: #160c13;
		font-weight: 650;
		border-color: #f75380;
	}
	.undo {
		padding: 0;
		width: 44px;
		height: 44px;
		font-size: 1.5rem;
	}
	.swipe-hint {
		text-align: center;
		color: var(--discovery-dim);
		font-size: 0.7rem;
		line-height: 1.5;
		margin-top: 1rem;
	}
	.decision {
		position: absolute;
		top: 2rem;
		right: 2rem;
		border: 3px solid #ffc9dd;
		color: #ffc9dd;
		padding: 0.7rem;
		font-weight: 700;
		text-transform: uppercase;
		transform: rotate(12deg);
		background: #000b;
	}
	.decision.keep {
		color: #b5f2c4;
		border-color: #b5f2c4;
		right: auto;
		left: 2rem;
		transform: rotate(-12deg);
	}
	.finished {
		text-align: center;
		min-height: 25rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 1rem;
	}
	.finished > span {
		font-size: 4rem;
		color: #f75380;
	}
	.finished h2,
	.finished p {
		margin: 0;
	}
	.finished p {
		color: var(--discovery-dim);
		font-size: 0.85rem;
		line-height: 1.7;
	}
	@media (max-width: 800px) {
		.swipe-layout {
			display: block;
			max-width: 460px;
			margin: auto;
		}
		.deck-intro {
			display: none;
		}
		.decisions {
			gap: 0.6rem;
		}
		.pass,
		.keep-button {
			padding-inline: 1rem;
		}
		.swipe-image {
			height: clamp(10rem, calc(100dvh - 38rem), 20rem);
		}
		.card-caption {
			padding: 1rem 1.2rem;
		}
	}
</style>
