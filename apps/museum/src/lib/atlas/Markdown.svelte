<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<script lang="ts">
	import { inline } from './inline';

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

{#snippet rich(source: string)}{#each inline(source) as seg, i (i)}{#if seg.kind === 'code'}<code
				>{seg.text}</code
			>{:else if seg.kind === 'strong'}<strong>{seg.text}</strong>{:else if seg.kind === 'em'}<em
				>{seg.text}</em
			>{:else if seg.kind === 'link'}<a href={seg.href} rel="external noopener">{seg.text}</a
			>{:else}{seg.text}{/if}{/each}{/snippet}

<div class="prose">
	{#each blocks as block, index (index)}
		{#if block.startsWith('#')}
			<h2>{@render rich(block.replace(/^#+\s*/, ''))}</h2>
		{:else if block.startsWith('|')}
			<div class="table">
				<table>
					<tbody
						>{#each rows(block) as row, rowIndex (rowIndex)}<tr
								>{#each cells(row) as cell, cellIndex (cellIndex)}{#if rowIndex === 0}<th
											scope="col">{@render rich(cell)}</th
										>{:else}<td>{@render rich(cell)}</td>{/if}{/each}</tr
							>{/each}</tbody
					>
				</table>
			</div>
		{:else if block.startsWith('- ') || block.startsWith('* ')}
			<ul>
				<!-- An item may wrap over several lines: only a new marker starts a new item. -->
				{#each block.split(/\n(?=\s*[-*]\s)/) as line, lineIndex (lineIndex)}<li>
						{@render rich(line.replace(/^\s*[-*]\s*/, '').replace(/\s*\n\s*/g, ' '))}
					</li>{/each}
			</ul>
		{:else if block.startsWith('```')}
			<pre>{block.replace(/^```[^\n]*\n?/, '').replace(/\n?```$/, '')}</pre>
		{:else}
			<p>{@render rich(block)}</p>
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
		/* Words stay whole in a cell; a wide table scrolls instead. */
		overflow-wrap: normal;
		min-width: 5ch;
		padding: 0.6rem;
		border-bottom: 1px solid var(--line);
		text-align: left;
		vertical-align: top;
	}
	th {
		color: var(--bright);
		font-weight: 400;
	}
	code {
		font: 0.85em var(--mono);
	}
	pre {
		white-space: pre-wrap;
		background: var(--panel);
		padding: 1rem;
		font: 0.8rem/1.6 var(--mono);
	}
</style>
