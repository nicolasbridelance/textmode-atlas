<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- A numbered figure: its caption, the chart, and the same numbers as a table. -->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { m } from '#lib/paraglide/messages.js';

	let {
		caption,
		head,
		rows,
		children
	}: { caption: string; head: string[]; rows: (string | number)[][]; children: Snippet } = $props();
</script>

<figure>
	<figcaption>{caption}</figcaption>
	{@render children()}
	<details>
		<summary>{m.eda_table()}</summary>
		<div class="scroll">
			<table>
				<thead
					><tr
						>{#each head as h (h)}<th scope="col">{h}</th>{/each}</tr
					></thead
				>
				<tbody>
					{#each rows as row, i (i)}
						<tr
							>{#each row as cell, j (j)}<td>{cell}</td>{/each}</tr
						>
					{/each}
				</tbody>
			</table>
		</div>
	</details>
</figure>

<style>
	figure {
		margin: 1.5rem 0;
		max-width: 46rem;
	}
	figcaption {
		color: var(--bright);
		font-size: 0.85rem;
		margin-bottom: 0.5rem;
	}
	details {
		margin-top: 0.4rem;
		font-size: 0.75rem;
	}
	summary {
		cursor: pointer;
		color: var(--dim);
	}
	.scroll {
		overflow-x: auto;
		max-height: 18rem;
	}
	table {
		border-collapse: collapse;
		font-family: var(--mono);
		margin-top: 0.4rem;
	}
	th,
	td {
		text-align: right;
		padding: 0.15rem 0.6rem;
		border-bottom: 1px solid var(--line);
	}
	th {
		color: var(--dim);
		font-weight: 400;
	}
</style>
