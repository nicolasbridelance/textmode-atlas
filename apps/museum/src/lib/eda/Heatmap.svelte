<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- A share per row and column, darker where higher; each cell says its count, so that a full
     cell of two packs is not read like a full cell of twenty. -->
<script lang="ts">
	import { PERCENT } from './geometry';

	interface Cell {
		with: number;
		packs: number;
	}
	let {
		rows,
		columns,
		cells,
		label,
		empty
	}: {
		rows: string[];
		columns: string[];
		cells: Cell[][];
		label: string;
		empty: string; // what a cell without packs says
	} = $props();
	const tone = (cell: Cell) =>
		`color-mix(in oklab, var(--series-1) ${Math.round((cell.with / cell.packs) * PERCENT)}%, var(--panel))`;
	const DARK_TEXT = 0.55; // above this share the text turns to the surface colour
</script>

<div class="scroll">
	<table class="heat" aria-label={label}>
		<thead>
			<tr>
				<th></th>
				{#each columns as c (c)}<th scope="col">{c}</th>{/each}
			</tr>
		</thead>
		<tbody>
			{#each rows as row, r (row)}
				<tr>
					<th scope="row">{row}</th>
					{#each cells[r] as cell, k (k)}
						{#if cell.packs}
							<td
								style:background={tone(cell)}
								class:strong={cell.with / cell.packs > DARK_TEXT}
								title={`${row} ${columns[k]}: ${cell.with} / ${cell.packs}`}
								>{cell.with}/{cell.packs}</td
							>
						{:else}
							<td class="none" title={`${row} ${columns[k]}: ${empty}`}>·</td>
						{/if}
					{/each}
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	.scroll {
		overflow-x: auto;
	}
	.heat {
		border-collapse: separate;
		border-spacing: 2px;
		font-family: var(--mono);
		font-size: 0.72rem;
	}
	th {
		color: var(--dim);
		font-weight: 400;
		padding: 0.15rem 0.5rem;
		text-align: right;
	}
	td {
		min-width: 3.2rem;
		text-align: center;
		padding: 0.35rem 0.3rem;
		color: var(--ink);
		border-radius: 3px;
	}
	td.strong {
		color: var(--surface);
		font-weight: 600;
	}
	td.none {
		color: var(--faint);
	}
</style>
