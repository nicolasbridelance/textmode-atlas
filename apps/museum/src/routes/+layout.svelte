<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import type { Path } from '$app/types';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import { browser } from '$app/env';
	import { getLocale, locales, localizeHref } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import favicon from '#lib/assets/favicon.svg';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();
	const context = $derived(browser ? `${page.url.search}${page.url.hash}` : '');

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
	<nav class="rooms" aria-label={m.atlas_rooms()}>
		<a href={localizeHref('/explore')}>{m.atlas_collection()}</a>
		<a href={localizeHref('/constellation')}>{m.atlas_constellation()}</a>
		<a href={localizeHref('/research')}>{m.atlas_research()}</a>
	</nav>
	<!-- Also tells the prerenderer to crawl every localized version of the page. -->
	<nav class="locales" aria-label={m.language_switch()}>
		{#each locales as locale (locale)}
			<a
				href={`${resolve(localizeHref(page.url.pathname, { locale }) as Path)}${context}`}
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
	:global(html) {
		background: #000;
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
		justify-content: space-between;
		gap: 1rem;
		flex-wrap: wrap;
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
	.locales {
		display: flex;
		gap: 0.75rem;
	}
	.rooms {
		display: flex;
		gap: 1rem;
		flex-wrap: wrap;
	}
	.rooms a {
		text-decoration: none;
	}
	@media (max-width: 600px) {
		.rooms {
			order: 3;
			width: 100%;
		}
	}
	.locales a {
		color: var(--faint);
		text-decoration: none;
	}
	.locales a[aria-current='true'] {
		color: var(--ink);
	}
</style>
