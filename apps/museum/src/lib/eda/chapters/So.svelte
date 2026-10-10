<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- What a chapter changes for what comes next. -->
<script lang="ts">
	import { m } from '#lib/paraglide/messages.js';

	let { text }: { text: string } = $props();
</script>

<p class="so"><span class="tag">{m.eda_so()}</span> {text}</p>

<style>
	.so {
		color: var(--bright);
		max-width: 68ch;
	}
</style>
