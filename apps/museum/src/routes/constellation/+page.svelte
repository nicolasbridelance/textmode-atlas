<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { getLocale, localizeHref } from '#lib/paraglide/runtime.js';
	import { m } from '#lib/paraglide/messages.js';
	import { graphRuntime } from '../../lib/atlas/graph';
	import '../../lib/atlas/graph.css';
	let root: HTMLElement;
	onMount(() => {
		let dispose: (() => void) | undefined;
		let gone = false;
		void graphRuntime()
			.then(() => {
				if (!gone)
					dispose = window.mountMuseumGraph(
						root,
						getLocale(),
						(sha) => `${localizeHref('/work')}?w=${sha}`
					);
			})
			.catch(() => {
				const loading = root.querySelector('#loading');
				if (loading) loading.textContent = m.atlas_graph_missing();
			});
		return () => {
			gone = true;
			dispose?.();
		};
	});
</script>

<svelte:head><title>{m.atlas_constellation()} · {m.museum_name()}</title></svelte:head>
<main class="atlas-graph" bind:this={root} aria-label={m.atlas_constellation()}>
	<div id="map"></div>
	<div id="loading">{m.atlas_graph_loading()}</div>
	<section id="brand" class="glass">
		<h1>{m.atlas_constellation()}</h1>
		<p id="stats">{m.atlas_similarity_note()}</p>
		<span class="small" id="colour-label">{m.atlas_colour()}</span>
		<div class="row seg" id="modes" role="group" aria-labelledby="colour-label"></div>
		<label class="small" for="find">{m.atlas_graph_find()}</label><input id="find" type="search" />
		<div id="time">
			<button class="btn" id="play" aria-label={m.atlas_play()}>▶</button><input
				id="slider"
				aria-label={m.atlas_year()}
				type="range"
				min="1990"
				max="2026"
				value="2026"
			/><span id="year">{m.atlas_all()}</span>
		</div>
		<div class="row">
			<button class="btn" id="openComms">{m.atlas_communities()}</button><button
				class="btn"
				id="reset">{m.atlas_reset()}</button
			><a class="btn" href={localizeHref('/explore')}>{m.atlas_collection()}</a>
		</div>
	</section>
	<section id="legend" class="glass" aria-label={m.atlas_method()}></section>
	<div id="tip" class="glass"></div>
	<aside id="side" class="glass"></aside>
	<aside id="comms" class="glass"></aside>
</main>
