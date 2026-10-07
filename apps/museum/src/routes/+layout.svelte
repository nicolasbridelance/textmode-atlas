<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import type { Path } from '$app/types';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import { getLocale, locales, localizeHref } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import favicon from '#lib/assets/favicon.svg';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();

	const localeNames: Record<string, () => string> = {
		en: m.locale_name_en,
		fr: m.locale_name_fr
	};
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>{m.museum_name()}</title>
</svelte:head>

{@render children()}

<!-- Also tells the prerenderer to crawl every localized version of the page. -->
<nav class="locales" aria-label={m.language_switch()}>
	{#each locales as locale (locale)}
		<a
			href={resolve(localizeHref(page.url.pathname, { locale }) as Path)}
			hreflang={locale}
			data-sveltekit-reload
			lang={locale}
			aria-current={locale === getLocale() ? 'true' : undefined}>{localeNames[locale]()}</a
		>
	{/each}
</nav>

<style>
	:global(html) {
		background: #000;
		color: #aaa;
		color-scheme: dark;
	}
	:global(body) {
		margin: 0;
		font-family: system-ui, sans-serif;
	}
	.locales {
		position: fixed;
		inset-block-end: max(0.75rem, env(safe-area-inset-bottom));
		inset-inline-end: 1rem;
		display: flex;
		gap: 0.75rem;
		font-size: 0.8rem;
	}
	.locales a {
		color: #555;
		text-decoration: none;
	}
	.locales a[aria-current='true'] {
		color: #aaa;
	}
</style>
