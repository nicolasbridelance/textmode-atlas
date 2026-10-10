<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- A hypothesis, the number that tests it, and whether that number still supports the reading. -->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { m } from '#lib/paraglide/messages.js';
	import { checkState, type Check } from './eda';

	let {
		check,
		hypothesis,
		evidence,
		refutes = false
	}: {
		check: Check | undefined;
		hypothesis: string;
		evidence: Snippet;
		refutes?: boolean; // the check holding means the hypothesis is rejected
	} = $props();

	const state = $derived(checkState(check));
	const verdict = $derived(
		state === 'unknown'
			? m.eda_check_unknown()
			: state === 'broken'
				? m.eda_check_broken()
				: refutes
					? m.eda_check_refuted()
					: m.eda_check_holds()
	);
</script>

<aside class={`verdict ${state}`} class:refutes>
	<p class="hypothesis"><span class="tag">{m.eda_hypothesis()}</span> {hypothesis}</p>
	<p class="evidence"><span class="tag">{m.eda_check()}</span> {@render evidence()}</p>
	<p class="state">
		<span aria-hidden="true"
			>{state === 'holds' ? (refutes ? '✗' : '✓') : state === 'broken' ? '!' : '?'}</span
		>
		{verdict}
	</p>
</aside>

<style>
	.verdict {
		border-left: 3px solid var(--series-1);
		background: var(--panel);
		padding: 0.6rem 1rem;
		margin: 1.2rem 0;
		max-width: 70ch;
	}
	.verdict.refutes {
		border-left-color: var(--series-2);
	}
	.verdict.broken,
	.verdict.unknown {
		border-left-color: var(--dim);
		border-left-style: dashed;
	}
	p {
		margin: 0.3rem 0;
		line-height: 1.55;
	}
	.tag {
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--dim);
		margin-right: 0.3rem;
	}
	.state {
		color: var(--bright);
		font-size: 0.85rem;
	}
	.broken .state {
		color: var(--ink);
		font-style: italic;
	}
</style>
