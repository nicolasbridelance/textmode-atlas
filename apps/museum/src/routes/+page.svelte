<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: Apache-2.0
-->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';
</script>

<!-- The entrance will be a work, full screen. Until the work screen lands, the dedication. -->
<main>
	<h1>{m.museum_name()}</h1>
	<p>{m.dedication()}</p>
</main>

<style>
	main {
		min-height: 100dvh;
		display: grid;
		place-content: center;
		text-align: center;
		padding-inline: 1rem;
	}
	h1 {
		font-weight: 400;
		font-size: 1.25rem;
		color: #fff;
	}
</style>
