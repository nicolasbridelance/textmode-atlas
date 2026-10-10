<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/env';
	import { SvelteURLSearchParams } from 'svelte/reactivity';
	import {
		preferences,
		museumContext,
		restorePreferences,
		savePreferences
	} from '../lib/presentation/settings.svelte';
	import type { Path } from '$app/types';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import { getLocale, locales, localizeHref } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import favicon from '#lib/assets/favicon.svg';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();

	let restored = $state(false);
	onMount(() => {
		restorePreferences();
		restored = true;
	});
	$effect(() => {
		if (!browser || !restored) return;
		document.documentElement.dataset.theme = preferences.theme;
		savePreferences({ ...preferences });
	});
	const workId = $derived(
		browser ? (page.url.searchParams.get('w') ?? museumContext.workId) : null
	);
	/** The collection, keeping the current display and filters, and the work it came from. */
	function exploreHref(): string {
		const query = new SvelteURLSearchParams(
			browser && page.url.pathname.endsWith('/explore') ? page.url.search : ''
		);
		if (workId && !query.has('w')) query.set('w', workId);
		const search = query.toString();
		return `${resolve(localizeHref('/explore') as Path)}${search ? `?${search}` : ''}`;
	}
	const localeNames: Record<string, () => string> = {
		en: m.locale_name_en,
		fr: m.locale_name_fr
	};
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>{m.museum_name()}</title>
</svelte:head>

<header class="top">
	<a class="name" href={resolve(localizeHref('/') as Path)}>{m.museum_name()}</a>
	<nav class="views" aria-label={m.nav_explore()}>
		<a
			href={resolve(localizeHref('/') as Path)}
			aria-current={page.url.pathname === localizeHref('/') ? 'page' : undefined}>{m.nav_today()}</a
		>
		<a
			href={exploreHref()}
			aria-current={page.url.pathname.endsWith('/explore') ? 'page' : undefined}
			>{m.atlas_collection()}</a
		>
		<a href={localizeHref('/constellation')}>{m.atlas_constellation()}</a>
		<a
			href={localizeHref('/corpus')}
			aria-current={page.url.pathname.endsWith('/corpus') ? 'page' : undefined}>{m.nav_corpus()}</a
		>
		<a href={localizeHref('/research')}>{m.atlas_research()}</a>
	</nav>
	<label class="theme"
		>{m.presentation_theme()}
		<select bind:value={preferences.theme}>
			<option value="dark">{m.theme_dark()}</option>
			<option value="light">{m.theme_light()}</option>
			<option value="system">{m.theme_system()}</option>
		</select>
	</label>
	<!-- Also tells the prerenderer to crawl every localized version of the page. -->
	<nav class="locales" aria-label={m.language_switch()}>
		{#each locales as locale (locale)}
			<a
				href={`${resolve(localizeHref(page.url.pathname, { locale }) as Path)}${browser ? page.url.search : ''}`}
				hreflang={locale}
				data-sveltekit-reload
				lang={locale}
				aria-current={locale === getLocale() ? 'true' : undefined}>{localeNames[locale]()}</a
			>
		{/each}
	</nav>
</header>

{@render children()}

<style>
	:global(:root) {
		/* VGA's own greys and cyan, on black: the works set the palette, the museum stays quiet. */
		--surface: #000;
		--bright: #fff;
		--ink: #aaa;
		--dim: #808080;
		--faint: #555;
		--line: #262626;
		--panel: #111;
		--accent: #55ffff;
		--mono: ui-monospace, 'SFMono-Regular', 'Cascadia Mono', 'DejaVu Sans Mono', monospace;
		color-scheme: dark;
	}
	:global(:root[data-theme='light']) {
		--surface: #f8f7f3;
		--bright: #181b20;
		--ink: #41464e;
		--dim: #606873;
		--faint: #737b85;
		--line: #d3d5d7;
		--panel: #eeede8;
		--accent: #006e78;
		color-scheme: light;
	}
	@media (prefers-color-scheme: light) {
		:global(:root[data-theme='system']) {
			--surface: #f8f7f3;
			--bright: #181b20;
			--ink: #41464e;
			--dim: #606873;
			--faint: #737b85;
			--line: #d3d5d7;
			--panel: #eeede8;
			--accent: #006e78;
			color-scheme: light;
		}
	}
	:global(html) {
		background: var(--surface);
		color: var(--ink);
	}
	:global(body) {
		margin: 0;
		font-family:
			system-ui,
			-apple-system,
			'Segoe UI',
			sans-serif;
		-webkit-font-smoothing: antialiased;
	}
	:global(a) {
		color: var(--ink);
		text-underline-offset: 0.2em;
		text-decoration-color: var(--faint);
	}
	:global(a:hover) {
		color: var(--bright);
		text-decoration-color: var(--dim);
	}
	:global(:focus-visible) {
		outline: 1px solid var(--accent);
		outline-offset: 2px;
	}
	.top {
		display: flex;
		align-items: baseline;
		flex-wrap: wrap;
		justify-content: space-between;
		gap: 1rem;
		padding: 0.9rem 1rem;
		font-size: 0.75rem;
		letter-spacing: 0.06em;
	}
	@media (min-width: 1100px) {
		.top {
			padding-inline: 1.5rem;
		}
	}
	.name {
		color: var(--dim);
		text-decoration: none;
		text-transform: uppercase;
	}
	.views {
		display: flex;
		flex-wrap: wrap;
		gap: 0.8rem;
	}
	.views a {
		text-decoration: none;
	}
	.views a[aria-current='page'] {
		color: var(--accent);
	}
	.theme {
		display: flex;
		gap: 0.4rem;
		align-items: center;
	}
	.theme select {
		background: var(--panel);
		color: var(--ink);
		border: 1px solid var(--line);
		font: inherit;
		padding: 0.25rem;
	}
	.locales {
		display: flex;
		gap: 0.75rem;
	}
	.locales a {
		color: var(--faint);
		text-decoration: none;
	}
	.locales a[aria-current='true'] {
		color: var(--ink);
	}
</style>
