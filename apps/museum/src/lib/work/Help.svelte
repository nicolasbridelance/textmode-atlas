<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	// The whole help, on one key (`?`): no tutorial, no modal at the door (foundation document).
	import { m } from '#lib/paraglide/messages.js';

	let { open = $bindable(false) }: { open?: boolean } = $props();
	let dialog: HTMLDialogElement | undefined = $state();

	$effect(() => {
		if (!dialog) return;
		if (open && !dialog.open) dialog.showModal();
		if (!open && dialog.open) dialog.close();
	});

	const keys = [
		'␣', // the space bar, drawn rather than named: the same in every language
		'← →',
		'a',
		'y',
		'r',
		'+ − 0',
		'?'
	];
	const what = $derived([
		m.help_space(),
		m.help_arrows(),
		m.help_signature(),
		m.help_year(),
		m.help_chance(),
		m.help_zoom(),
		m.help_help()
	]);
</script>

<dialog bind:this={dialog} onclose={() => (open = false)} aria-labelledby="help-title">
	<h2 id="help-title">{m.help_title()}</h2>
	<dl>
		{#each keys as key, i (key)}
			<dt><kbd>{key}</kbd></dt>
			<dd>{what[i]}</dd>
		{/each}
	</dl>
	<p>{m.help_swipe()}</p>
	<form method="dialog"><button>{m.help_close()}</button></form>
</dialog>

<style>
	dialog {
		background: var(--surface);
		color: var(--ink);
		border: 1px solid var(--line);
		padding: 1.25rem 1.5rem;
		max-width: min(28rem, calc(100vw - 2rem));
	}
	dialog::backdrop {
		background: rgb(0 0 0 / 0.7);
	}
	h2 {
		margin: 0 0 0.75rem;
		font-size: 1rem;
		font-weight: 500;
		color: var(--bright);
	}
	dl {
		display: grid;
		grid-template-columns: 5rem 1fr;
		gap: 0.4rem 1rem;
		margin: 0 0 1rem;
		font-size: 0.875rem;
	}
	dd {
		margin: 0;
	}
	kbd {
		font-family: var(--mono);
		color: var(--accent);
	}
	p {
		font-size: 0.8rem;
		color: var(--dim);
	}
	button {
		background: none;
		border: 1px solid var(--line);
		color: var(--ink);
		font: inherit;
		font-size: 0.8rem;
		padding: 0.3rem 0.8rem;
		cursor: pointer;
	}
	button:hover,
	button:focus-visible {
		color: var(--bright);
		border-color: var(--dim);
	}
</style>
