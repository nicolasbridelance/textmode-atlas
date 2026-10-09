<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<script lang="ts">
	let { text }: { text: string } = $props();
	const blocks = $derived(
		text
			.replace(/<!--[\s\S]*?-->/g, '')
			.trim()
			.split(/\n\s*\n/)
	);
	function cells(row: string): string[] {
		return row
			.trim()
			.replace(/^\||\|$/g, '')
			.split('|')
			.map((cell) => cell.trim());
	}
	function rows(block: string): string[] {
		return block.split('\n').filter((line) => !/^\|?\s*:?-{3,}/.test(line));
	}
</script>

<div class="prose">
	{#each blocks as block, index (index)}
		{#if block.startsWith('#')}
			<h2>{block.replace(/^#+\s*/, '')}</h2>
		{:else if block.startsWith('|')}
			<div class="table">
				<table>
					<tbody
						>{#each rows(block) as row, rowIndex (rowIndex)}<tr
								>{#each cells(row) as cell, cellIndex (cellIndex)}{#if rowIndex === 0}<th
											scope="col">{cell}</th
										>{:else}<td>{cell}</td>{/if}{/each}</tr
							>{/each}</tbody
					>
				</table>
			</div>
		{:else if block.startsWith('- ') || block.startsWith('* ')}
			<ul>
				{#each block.split('\n') as line, lineIndex (lineIndex)}<li>
						{line.replace(/^[-*]\s*/, '')}
					</li>{/each}
			</ul>
		{:else if block.startsWith('```')}
			<pre>{block.replace(/^```[^\n]*\n?/, '').replace(/\n?```$/, '')}</pre>
		{:else}
			<p>{block}</p>
		{/if}
	{/each}
</div>

<style>
	.prose {
		max-width: 85ch;
		line-height: 1.75;
		overflow-wrap: anywhere;
	}
	h2 {
		font-size: 1.15rem;
		font-weight: 500;
		color: var(--bright);
		margin-top: 2rem;
	}
	p {
		white-space: pre-line;
	}
	.table {
		overflow: auto;
	}
	table {
		border-collapse: collapse;
		font-size: 0.8rem;
		line-height: 1.5;
	}
	th,
	td {
		padding: 0.6rem;
		border-bottom: 1px solid var(--line);
		text-align: left;
		vertical-align: top;
	}
	th {
		color: var(--bright);
		font-weight: 400;
	}
	pre {
		white-space: pre-wrap;
		background: var(--panel);
		padding: 1rem;
		font: 0.8rem/1.6 var(--mono);
	}
</style>
