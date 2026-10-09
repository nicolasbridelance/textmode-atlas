<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	// The label: five lines, then levels that open (context, words, bytes), as the foundation
	// document asks. Credit as signed, never a civil name; withdrawal on every record (ADR 0009).
	import { m } from '#lib/paraglide/messages.js';
	import { fileUrl } from '../files';
	import { descriptorBadge, GRID_PAGE, levelBadge } from './audience';
	import type { WorkRecord } from './record';
	import { duration } from './time';

	let {
		record,
		locale,
		seconds,
		baud,
		eyebrow = null
	}: {
		record: WorkRecord;
		locale: string;
		/** Arrival time at `baud`, or null when the work is not shown. */
		seconds: number | null;
		baud: number;
		eyebrow?: string | null;
	} = $props();

	const credit = $derived(record.credit);
	const signed = $derived(
		[credit.author, credit.group].filter(Boolean).join(' / ') || m.work_unsigned()
	);
	const title = $derived(record.title || record.file);
	const level = $derived(levelBadge(record.audience.level, locale));
	const marks = $derived(
		[...record.audience.descriptors, ...record.audience.notices].map((code) =>
			descriptorBadge(code, locale)
		)
	);
	const dates = $derived(new Intl.DateTimeFormat(locale, { dateStyle: 'long' }));
	const numbers = $derived(new Intl.NumberFormat(locale));
	const text = $derived(record.text ?? []);
</script>

<section class="cartel" aria-labelledby="work-title">
	{#if eyebrow}<p class="eyebrow">{eyebrow}</p>{/if}
	<h1 id="work-title">{title}</h1>
	<p class="signed">{signed}</p>
	<p>
		{#if credit.pack}{m.work_in_pack({ pack: credit.pack, year: record.year ?? '?' })}{/if}
	</p>
	<p class="data">
		{#if seconds !== null}
			{m.work_arrival({
				cols: record.grid.cols,
				rows: record.grid.rows,
				time: duration(seconds),
				baud: numbers.format(baud)
			})}
		{:else}
			{m.work_size({ cols: record.grid.cols, rows: record.grid.rows })}
		{/if}
	</p>
	<div class="audience" aria-label={m.work_audience()}>
		<img src={level.src} alt={level.label} title={level.label} height="24" />
		{#each marks as mark (mark.src)}
			<img src={mark.src} alt={mark.label} title={mark.label} height="18" />
		{/each}
		{#if !record.audience.reviewed}<span class="note">{m.work_unreviewed()}</span>{/if}
	</div>

	<details>
		<summary>{m.work_context()}</summary>
		<ul class="plain">
			{#if credit.url && credit.archive}
				<li>
					<a href={credit.url} rel="external">{m.work_source({ archive: credit.archive })}</a>
				</li>
			{/if}
			{#each record.provenance as fetched, i (i)}
				<li>
					{m.work_fetched({
						source: fetched.source,
						date: fetched.retrieved_at ? dates.format(new Date(fetched.retrieved_at)) : '?'
					})}{#if fetched.via_archive}, {m.work_fetched_via()}{/if}
				</li>
			{/each}
			<li><a href={GRID_PAGE[locale] ?? GRID_PAGE.en} rel="external">{m.work_grid_link()}</a></li>
		</ul>
	</details>

	{#if record.shown === 'files'}
		<details>
			<summary>{m.work_words()}</summary>
			{#if text.length}
				<ol class="words">
					{#each text as line (line.row)}<li value={line.row + 1}>{line.text}</li>{/each}
				</ol>
				<p class="note">{m.work_words_note()}</p>
			{:else}
				<p class="note">{m.work_words_none()}</p>
			{/if}
		</details>
	{/if}

	<details>
		<summary>{m.work_bytes()}</summary>
		<dl>
			<dt>{m.work_file()}</dt>
			<dd>{record.file}</dd>
			<dt>{m.work_format()}</dt>
			<dd>{record.format}</dd>
			<dt>{m.work_canvas()}</dt>
			<dd>
				{m.work_size({ cols: record.grid.cols, rows: record.grid.rows })},
				{record.grid.ice ? m.work_colours_ice() : m.work_colours_blink()}
			</dd>
			<dt>SHA-256</dt>
			<dd class="hash">{record.sha256}</dd>
			<dt>{m.work_published()}</dt>
			<dd class="files">
				{#each Object.keys(record.files) as name (name)}
					<a href={fileUrl(`works/${record.sha256}/${name}`)}>{name}</a>
				{/each}
				<a href={fileUrl(`works/${record.sha256}/record.json`)}>record.json</a>
			</dd>
		</dl>
	</details>

	<p class="withdraw"><a href={record.withdraw} rel="external">{m.work_withdraw()}</a></p>
</section>

<style>
	.cartel {
		font-size: 0.875rem;
		line-height: 1.45;
	}
	.eyebrow {
		color: var(--accent);
		font-size: 0.75rem;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		margin: 0 0 0.5rem;
	}
	h1 {
		color: var(--bright);
		font-size: 1.15rem;
		font-weight: 500;
		line-height: 1.25;
		margin: 0 0 0.15rem;
		overflow-wrap: anywhere;
	}
	p {
		margin: 0;
	}
	.signed {
		color: var(--bright);
		opacity: 0.85;
	}
	.data {
		font-family: var(--mono);
		font-size: 0.78rem;
		color: var(--dim);
		margin-block: 0.15rem;
	}
	.audience {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.4rem;
		margin-block: 0.5rem 0.75rem;
	}
	.audience img {
		image-rendering: pixelated;
	}
	.note {
		color: var(--dim);
		font-size: 0.78rem;
	}
	details {
		border-top: 1px solid var(--line);
		padding-block: 0.45rem;
	}
	summary {
		cursor: pointer;
		color: var(--ink);
		font-size: 0.8rem;
		letter-spacing: 0.04em;
	}
	summary:hover {
		color: var(--bright);
	}
	details[open] summary {
		color: var(--bright);
		margin-bottom: 0.4rem;
	}
	.plain {
		overflow-wrap: anywhere;
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 0.3rem;
	}
	.words {
		font-family: var(--mono);
		font-size: 0.75rem;
		max-height: 16rem;
		overflow: auto;
		margin: 0 0 0.4rem;
		padding-inline-start: 2.6rem;
		color: var(--ink);
	}
	.words li::marker {
		color: var(--faint);
	}
	dl {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: 0.2rem 0.75rem;
		margin: 0;
		font-size: 0.8rem;
	}
	dt {
		color: var(--dim);
	}
	dd {
		margin: 0;
		overflow-wrap: anywhere;
	}
	.files {
		display: flex;
		flex-wrap: wrap;
		gap: 0 0.75rem;
	}
	.hash {
		font-family: var(--mono);
		font-size: 0.7rem;
	}
	.withdraw {
		border-top: 1px solid var(--line);
		padding-top: 0.5rem;
		font-size: 0.8rem;
	}
</style>
