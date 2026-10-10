<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- The corpus, explored (ADR 0028): a path of questions through the live database. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { getLocale } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import Bars from '../../lib/eda/Bars.svelte';
	import Figure from '../../lib/eda/Figure.svelte';
	import Lines from '../../lib/eda/Lines.svelte';
	import NullPlot from '../../lib/eda/NullPlot.svelte';
	import Split from '../../lib/eda/Split.svelte';
	import Verdict from '../../lib/eda/Verdict.svelte';
	import { HALF } from '../../lib/eda/geometry';
	import { REFRESH_MS, everyYear, formatter, loadSnapshot, type Snapshot } from '../../lib/eda/eda';

	const WRITTEN = '2026-10-10'; // when the readings below were written
	const REVIVAL_FROM = 2000;
	const MIN_PACKS = 50; // as the host: a year with fewer packs says little of their size
	const UNREAD_SHOWN = 8;
	const LABEL_EVERY = { years: 5, sized: 2, sauce: 4, recent: 3 };
	const SHARE_BINS = ['0–20 %', '20–40 %', '40–60 %', '60–80 %', '80–100 %'];

	let snap = $state<Snapshot | null>(null);
	let failed = $state(false);
	const f = formatter(getLocale());
	const when = (iso: string) =>
		new Intl.DateTimeFormat(getLocale(), { dateStyle: 'medium', timeStyle: 'medium' }).format(
			new Date(iso)
		);

	onMount(() => {
		let gone = false;
		const tick = async () => {
			try {
				const found = await loadSnapshot();
				if (gone) return;
				if (found) snap = found;
				failed = !found && !snap;
			} catch {
				failed = !snap;
			}
		};
		void tick();
		const timer = setInterval(() => {
			if (document.visibilityState === 'visible') void tick();
		}, REFRESH_MS);
		return () => {
			gone = true;
			clearInterval(timer);
		};
	});

	const c = $derived(snap?.chapters);
	const funnel = $derived(c?.contents.funnel);
	const unread = $derived(c ? c.contents.unread.reduce((sum, u) => sum + u.works, 0) : 0);
	const unreadByFormat = $derived(
		Object.entries(
			(c?.contents.unread ?? []).reduce<Record<string, number>>((by, u) => {
				by[u.format] = (by[u.format] ?? 0) + u.works;
				return by;
			}, {})
		)
			.map(([x, y]) => ({ x, y }))
			.sort((a, b) => b.y - a.y)
			.slice(0, UNREAD_SHOWN)
	);
	const peakCheck = $derived(c?.peak.checks.peaks_differ);
	const lateCheck = $derived(c?.peak.checks.fewer_and_smaller);
	const years = $derived(c?.peak.years ?? []);
	const sized = $derived(years.filter((y) => y.packs >= MIN_PACKS));
	const sauceYears = $derived(everyYear((c?.sauce.by_year ?? []).map((y) => y.year)));
	const sauceShare = (format: 'ansi' | 'ascii') =>
		sauceYears.map(
			(year) => c?.sauce.by_year.find((y) => y.year === year && y.format === format)?.share ?? null
		);
	const adoption = $derived(
		c?.sauce.by_year.find((y) => y.year === c.sauce.year && y.format === 'ansi')?.share
	);
	const groupShare = (prefix: string) => {
		const g = c?.sauce.groups.find((x) => x.prefix === prefix);
		return g ? `${f.n(g.with)} / ${f.n(g.packs)}` : '–';
	};
	const eraOf = (era: string) => c?.composition.eras.find((e) => e.era === era);
	const before = $derived(c ? eraOf(c.composition.before) : undefined);
	const after = $derived(c ? eraOf(c.composition.after) : undefined);
	const shadeOf = (era: { kinds: Record<string, { shade: number }> }) =>
		era.kinds.coloured_blocks?.shade ?? null;
	const recent = $derived(years.filter((y) => y.year >= REVIVAL_FROM));
	const revivalRows = $derived(c?.revival.checks.taller);
	const revivalIce = $derived(c?.revival.checks.ice_later);
	const num = (value: unknown) => (typeof value === 'number' ? value : 0);
</script>

<svelte:head><title>{m.eda_title()} · {m.museum_name()}</title></svelte:head>

<main>
	<header class="intro">
		<h1>{m.eda_title()}</h1>
		<p class="lede">{m.eda_lede()}</p>
		<p>{m.eda_live({ date: WRITTEN })}</p>
		<p class="rules">{m.eda_rules()}</p>
		{#if snap}
			<p class="status" aria-live="polite">
				<span class="pulse" aria-hidden="true"></span>
				{m.eda_status({
					when: when(snap.computed_at),
					seconds: f.d(snap.seconds),
					hidden: f.n(snap.hidden)
				})}
			</p>
		{:else if failed}
			<p class="status">{m.eda_unavailable()}</p>
		{:else}
			<p class="status">{m.eda_loading()}</p>
		{/if}
	</header>

	{#if c && funnel}
		<section id="contents">
			<h2>{m.eda_contents_title()}</h2>
			<p>{m.eda_contents_why()}</p>
			<Figure
				caption={m.eda_contents_fig()}
				head={['', m.eda_works()]}
				rows={[
					[m.eda_step_art(), f.n(funnel.art)],
					[m.eda_step_decoding(), f.n(funnel.decoding)],
					[m.eda_step_grids(), f.n(funnel.grids)],
					[m.eda_step_rendered(), f.n(funnel.rendered)],
					[m.eda_step_measured(), f.n(funnel.measured)]
				]}
			>
				<Split
					label={m.eda_contents_fig()}
					format={f.n}
					parts={[
						{ name: m.eda_step_art(), value: funnel.art, tone: 's1' },
						{ name: m.eda_step_decoding(), value: funnel.decoding, tone: 's1' },
						{ name: m.eda_step_grids(), value: funnel.grids, tone: 's1' },
						{ name: m.eda_step_rendered(), value: funnel.rendered, tone: 's1' },
						{ name: m.eda_step_measured(), value: funnel.measured, tone: 's1' }
					]}
				/>
			</Figure>
			<p>
				{m.eda_contents_reading({
					files: f.n(c.contents.sources.reduce((s, x) => s + x.files, 0)),
					sources: f.n(c.contents.sources.length),
					art: f.n(funnel.art),
					packs: f.n(funnel.packs),
					grids: f.n(funnel.grids),
					share: f.pct(funnel.grids / Math.max(1, funnel.art))
				})}
			</p>
			<Figure
				caption={m.eda_contents_unread_fig()}
				head={[m.eda_format(), m.eda_reason(), m.eda_works()]}
				rows={c.contents.unread.map((u) => [u.format, u.error_class, f.n(u.works)])}
			>
				<Bars label={m.eda_contents_unread_fig()} format={f.n} points={unreadByFormat} />
			</Figure>
			<Verdict check={c.contents.checks.every_work_decoded} hypothesis={m.eda_contents_hyp()}>
				{#snippet evidence()}{m.eda_contents_check({
						missing: f.n(num(c.contents.checks.every_work_decoded?.missing))
					})}{/snippet}
			</Verdict>
			<p class="so">
				<span class="tag">{m.eda_so()}</span>
				{m.eda_contents_so({ unread: f.n(unread) })}
			</p>
		</section>

		<section id="peak">
			<h2>{m.eda_peak_title()}</h2>
			<p>{m.eda_peak_why()}</p>
			<div>
				<Figure
					caption={m.eda_peak_fig_works()}
					head={[m.eda_year(), m.eda_works(), m.eda_packs()]}
					rows={years.map((y) => [y.year, f.n(y.works), f.n(y.packs)])}
				>
					<Bars
						label={m.eda_peak_fig_works()}
						format={f.n}
						every={LABEL_EVERY.years}
						marked={peakCheck ? [String(peakCheck.works_year)] : []}
						points={years.map((y) => ({ x: String(y.year), y: y.works }))}
					/>
				</Figure>
				<Figure
					caption={m.eda_peak_fig_packs()}
					head={[m.eda_year(), m.eda_packs()]}
					rows={years.map((y) => [y.year, f.n(y.packs)])}
				>
					<Bars
						label={m.eda_peak_fig_packs()}
						format={f.n}
						every={LABEL_EVERY.years}
						marked={peakCheck ? [String(peakCheck.packs_year)] : []}
						points={years.map((y) => ({ x: String(y.year), y: y.packs }))}
					/>
				</Figure>
			</div>
			<Figure
				caption={m.eda_peak_fig_size()}
				head={[m.eda_year(), m.eda_packs(), m.eda_works()]}
				rows={sized.map((y) => [y.year, f.n(y.packs), f.d(y.median_art)])}
			>
				<Bars
					label={m.eda_peak_fig_size()}
					format={f.d}
					every={LABEL_EVERY.sized}
					marked={peakCheck ? [String(peakCheck.size_year)] : []}
					points={sized.map((y) => ({ x: String(y.year), y: y.median_art }))}
				/>
			</Figure>
			{#if peakCheck}
				<p>
					{m.eda_peak_reading({
						works_year: String(peakCheck.works_year),
						works: f.n(num(peakCheck.works)),
						packs_year: String(peakCheck.packs_year),
						packs: f.n(num(peakCheck.packs)),
						size_year: String(peakCheck.size_year),
						size: f.d(num(peakCheck.size))
					})}
				</p>
			{/if}
			<p class="caution">{m.eda_peak_caution()}</p>
			<Verdict check={lateCheck} hypothesis={m.eda_peak_hyp()}>
				{#snippet evidence()}{m.eda_peak_check({
						year: String(lateCheck?.year ?? ''),
						late_packs: f.n(num(lateCheck?.packs)),
						packs: f.n(num(peakCheck?.packs)),
						late_size: f.d(num(lateCheck?.size)),
						size: f.d(num(peakCheck?.size))
					})}{/snippet}
			</Verdict>
			<p class="so"><span class="tag">{m.eda_so()}</span> {m.eda_peak_so()}</p>
		</section>

		<section id="sauce">
			<h2>{m.eda_sauce_title()}</h2>
			<p>{m.eda_sauce_why()}</p>
			<Figure
				caption={m.eda_sauce_fig_years()}
				head={[m.eda_year(), 'ANSI', 'ASCII']}
				rows={sauceYears.map((y, i) => [
					y,
					f.pct(sauceShare('ansi')[i]),
					f.pct(sauceShare('ascii')[i])
				])}
			>
				<Lines
					label={m.eda_sauce_fig_years()}
					format={f.pct}
					max={1}
					every={LABEL_EVERY.sauce}
					x={sauceYears.map(String)}
					series={[
						{ name: 'ANSI', values: sauceShare('ansi') },
						{ name: 'ASCII', values: sauceShare('ascii') }
					]}
				/>
			</Figure>
			<p>{m.eda_sauce_reading_years({ year: String(c.sauce.year), share: f.pct(adoption) })}</p>
			<Figure
				caption={m.eda_sauce_fig_packs({ year: String(c.sauce.year) })}
				head={[m.eda_share(), m.eda_packs()]}
				rows={c.sauce.shares.map((n, i) => [SHARE_BINS[i], f.n(n)])}
			>
				<Bars
					label={m.eda_sauce_fig_packs({ year: String(c.sauce.year) })}
					format={f.n}
					points={c.sauce.shares.map((n, i) => ({ x: SHARE_BINS[i], y: n }))}
				/>
			</Figure>
			<p>
				{m.eda_sauce_reading_packs({
					year: String(c.sauce.year),
					none: f.n(c.sauce.none),
					packs: f.n(c.sauce.packs),
					all: f.n(c.sauce.all)
				})}
			</p>
			<Verdict check={c.sauce.checks.not_packager} hypothesis={m.eda_sauce_hyp1()} refutes>
				{#snippet evidence()}{m.eda_sauce_check1({
						dates: f.d(c.sauce.full_mean_dates),
						files: f.d(c.sauce.full_mean_files),
						one_date: f.pct(num(c.sauce.checks.not_packager?.one_date))
					})}{/snippet}
			</Verdict>
			<p>{m.eda_sauce_hyp2()}</p>
			<p class="method">{m.eda_sauce_method()}</p>
			<Figure
				caption={m.eda_sauce_fig_null()}
				head={[m.eda_null_observed(), m.eda_null_chance(), m.eda_null_q95(), 'p']}
				rows={[
					[
						f.pct(c.sauce.test.observed),
						f.pct(c.sauce.test.null_mean),
						f.pct(c.sauce.test.null_q95),
						f.p(c.sauce.test.p)
					]
				]}
			>
				<NullPlot
					label={m.eda_sauce_fig_null()}
					counts={c.sauce.test.null}
					low={HALF}
					high={1}
					observed={c.sauce.test.observed}
					q95={c.sauce.test.null_q95}
					format={f.pct}
					names={{
						chance: m.eda_null_chance(),
						q95: m.eda_null_q95(),
						observed: m.eda_null_observed()
					}}
				/>
			</Figure>
			<Verdict check={c.sauce.checks.group_choice} hypothesis={m.eda_sauce_hyp2()}>
				{#snippet evidence()}{m.eda_sauce_check2({
						observed: f.pct(c.sauce.test.observed),
						null_mean: f.pct(c.sauce.test.null_mean),
						q95: f.pct(c.sauce.test.null_q95),
						p: f.pIs(c.sauce.test.p),
						groups: f.n(c.sauce.test.groups),
						gpacks: f.n(c.sauce.test.packs)
					})}{/snippet}
			</Verdict>
			<Figure
				caption={m.eda_sauce_groups_fig({ year: String(c.sauce.year) })}
				head={[m.eda_prefix(), m.eda_with_sauce(), m.eda_packs()]}
				rows={c.sauce.groups.map((g) => [g.prefix, f.n(g.with), f.n(g.packs)])}
			>
				<Bars
					label={m.eda_sauce_groups_fig({ year: String(c.sauce.year) })}
					format={f.pct}
					marked={['acdu', 'ice']}
					points={c.sauce.groups.map((g) => ({ x: g.prefix, y: g.with / g.packs }))}
				/>
			</Figure>
			<p>{m.eda_sauce_groups_reading({ acdu: groupShare('acdu'), ice: groupShare('ice') })}</p>
			<p class="so"><span class="tag">{m.eda_so()}</span> {m.eda_sauce_so()}</p>
		</section>

		{#if before && after}
			<section id="composition">
				<h2>{m.eda_comp_title()}</h2>
				<p>{m.eda_comp_why()}</p>
				<Figure
					caption={m.eda_comp_fig()}
					head={[m.eda_era(), m.eda_comp_all(), m.eda_comp_blocks()]}
					rows={c.composition.eras.map((e) => [e.era, f.pct(e.all), f.pct(shadeOf(e))])}
				>
					<Lines
						label={m.eda_comp_fig()}
						format={f.pct}
						x={c.composition.eras.map((e) => e.era)}
						series={[
							{ name: m.eda_comp_all(), values: c.composition.eras.map((e) => e.all) },
							{ name: m.eda_comp_blocks(), values: c.composition.eras.map(shadeOf) }
						]}
					/>
				</Figure>
				<p>
					{m.eda_comp_reading({
						before: c.composition.before,
						after: c.composition.after,
						before_all: f.pct(before.all),
						after_all: f.pct(after.all),
						before_cb: f.pct(shadeOf(before)),
						after_cb: f.pct(shadeOf(after)),
						before_share: f.pct(before.kinds.coloured_blocks?.share),
						after_share: f.pct(after.kinds.coloured_blocks?.share)
					})}
				</p>
				<p class="method">{m.eda_comp_method()}</p>
				<Figure
					caption={m.eda_comp_fig_split({
						before: c.composition.before,
						after: c.composition.after
					})}
					head={['', 'pts']}
					rows={[
						[m.eda_comp_total(), f.pts(c.composition.split.total)],
						[m.eda_comp_within(), f.pts(c.composition.split.within)],
						[m.eda_comp_mix(), f.pts(c.composition.split.composition)]
					]}
				>
					<Split
						label={m.eda_comp_fig_split({
							before: c.composition.before,
							after: c.composition.after
						})}
						format={f.pts}
						parts={[
							{ name: m.eda_comp_total(), value: c.composition.split.total, tone: 'total' },
							{ name: m.eda_comp_within(), value: c.composition.split.within, tone: 's2' },
							{ name: m.eda_comp_mix(), value: c.composition.split.composition, tone: 's1' }
						]}
					/>
				</Figure>
				<Verdict check={c.composition.checks.composition_dominates} hypothesis={m.eda_comp_hyp()}>
					{#snippet evidence()}{m.eda_comp_check({
							total: f.pts(c.composition.split.total),
							composition: f.pts(c.composition.split.composition),
							within: f.pts(c.composition.split.within)
						})}{/snippet}
				</Verdict>
				<p class="so"><span class="tag">{m.eda_so()}</span> {m.eda_comp_so()}</p>
			</section>
		{/if}

		<section id="revival">
			<h2>{m.eda_rev_title()}</h2>
			<p>{m.eda_rev_why()}</p>
			<Figure
				caption={m.eda_rev_fig_years()}
				head={[m.eda_year(), m.eda_works()]}
				rows={recent.map((y) => [y.year, f.n(y.works)])}
			>
				<Bars
					label={m.eda_rev_fig_years()}
					format={f.n}
					every={LABEL_EVERY.recent}
					points={recent.map((y) => ({ x: String(y.year), y: y.works }))}
				/>
			</Figure>
			<div>
				<Figure
					caption={m.eda_rev_fig_rows()}
					head={[m.eda_era(), m.eda_works(), m.eda_rows()]}
					rows={c.revival.eras.map((e) => [e.era, f.n(e.works), f.d(e.median_rows)])}
				>
					<Bars
						label={m.eda_rev_fig_rows()}
						format={f.n}
						marked={['2013-26']}
						points={c.revival.eras.map((e) => ({ x: e.era, y: e.median_rows }))}
					/>
				</Figure>
				<Figure
					caption={m.eda_rev_fig_ice()}
					head={[m.eda_era(), m.eda_ice()]}
					rows={c.revival.eras.map((e) => [e.era, f.pct(e.ice)])}
				>
					<Bars
						label={m.eda_rev_fig_ice()}
						format={f.pct}
						marked={['2013-26']}
						points={c.revival.eras.map((e) => ({ x: e.era, y: e.ice }))}
					/>
				</Figure>
			</div>
			<Verdict check={revivalRows} hypothesis={m.eda_rev_hyp1()}>
				{#snippet evidence()}{m.eda_rev_check1({
						recent: f.d(num(revivalRows?.recent)),
						nineties: f.d(num(revivalRows?.nineties))
					})}{/snippet}
			</Verdict>
			<Verdict check={revivalIce} hypothesis={m.eda_rev_hyp2()}>
				{#snippet evidence()}{m.eda_rev_check2({
						recent: f.pct(num(revivalIce?.recent)),
						nineties: f.pct(num(revivalIce?.nineties))
					})}{/snippet}
			</Verdict>
			<p class="so"><span class="tag">{m.eda_so()}</span> {m.eda_rev_so()}</p>
		</section>

		<section id="next">
			<h2>{m.eda_next_title()}</h2>
			<ul>
				<li>{m.eda_next_q21()}</li>
				<li>{m.eda_next_sauce()}</li>
				<li>{m.eda_next_tools()}</li>
				<li>{m.eda_next_test()}</li>
			</ul>
		</section>
	{/if}
</main>

<style>
	main {
		/* The two series of every chart: validated for colour vision deficiency on each surface. */
		--series-1: #11a3ad;
		--series-2: #cc7a12;
		max-width: 52rem;
		margin: auto;
		padding: 1.5rem 1rem 5rem;
		line-height: 1.65;
	}
	:global(:root[data-theme='light']) main {
		--series-1: #007f9a;
		--series-2: #b35900;
	}
	@media (prefers-color-scheme: light) {
		:global(:root[data-theme='system']) main {
			--series-1: #007f9a;
			--series-2: #b35900;
		}
	}
	h1,
	h2 {
		font-weight: 400;
		color: var(--bright);
	}
	h2 {
		margin-top: 3.5rem;
		padding-top: 1rem;
		border-top: 1px solid var(--line);
		font-size: 1.35rem;
	}
	section {
		scroll-margin-top: 1rem;
	}
	p {
		max-width: 68ch;
	}
	.lede {
		font-size: 1.1rem;
		color: var(--bright);
	}
	.rules,
	.caution,
	.method {
		font-size: 0.9rem;
		color: var(--dim);
	}
	.method {
		border-left: 1px solid var(--line);
		padding-left: 0.8rem;
	}
	.status {
		font-family: var(--mono);
		font-size: 0.75rem;
		color: var(--dim);
	}
	.pulse {
		display: inline-block;
		width: 0.5rem;
		height: 0.5rem;
		border-radius: 50%;
		background: var(--series-1);
		margin-right: 0.4rem;
		animation: pulse 2.4s ease-in-out infinite;
	}
	@media (prefers-reduced-motion: reduce) {
		.pulse {
			animation: none;
		}
	}
	@keyframes pulse {
		50% {
			opacity: 0.25;
		}
	}
	.tag {
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--dim);
		margin-right: 0.3rem;
	}
	.so {
		color: var(--bright);
	}
	@media (min-width: 900px) {
		main {
			max-width: 64rem;
			padding-inline: 2rem;
		}
	}
	ul {
		padding-left: 1.2rem;
	}
</style>
