<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Where a study stands: status, strand, data, date and the leads it answers. -->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
	import type { Study } from './studies';

	let {
		study,
		locale,
		leads = false
	}: { study: Study; locale: string; leads?: boolean } = $props();
	const date = $derived(
		new Intl.DateTimeFormat(locale, { dateStyle: 'long', timeZone: 'UTC' }).format(
			new Date(study.date)
		)
	);
</script>

<dl>
	<div class="status {study.status}">
		<dt class="hidden">{m.research_status()}</dt>
		<dd>{m[`research_status_${study.status}`]()}</dd>
	</div>
	<div>
		<dt class="hidden">{m.research_strand()}</dt>
		<dd>
			{study.strand.startsWith('W') ? `${study.strand} · ` : ''}{m[
				`research_strand_${study.strand}`
			]()}
		</dd>
	</div>
	{#if study.dataset}
		<div>
			<dt>{m.research_data()}</dt>
			<dd>{study.dataset === 'live' ? m.research_data_live() : study.dataset}</dd>
		</div>
	{/if}
	<div>
		<dt>{m.research_date()}</dt>
		<dd><time datetime={study.date}>{date}</time></dd>
	</div>
	{#if leads && study.leads.length}
		<div>
			<dt>{m.research_leads()}</dt>
			<dd>{study.leads.join(', ')}</dd>
		</div>
	{/if}
</dl>

<style>
	dl {
		display: flex;
		flex-wrap: wrap;
		gap: 0.25rem 1rem;
		margin: 0;
		font-size: 0.8rem;
		color: var(--dim);
	}
	div {
		display: flex;
		gap: 0.35rem;
	}
	dd {
		margin: 0;
	}
	.hidden {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip-path: inset(50%);
	}
	.status dd {
		color: var(--bright);
	}
	.status.confirmed dd,
	.status.refuted dd,
	.status.preregistered dd {
		font-weight: 600;
	}
</style>
