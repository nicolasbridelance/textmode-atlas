// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
// The works the collection shows: the whole corpus page by page from the host, or a
// published list (days, pack, signature, year) when only the static site is there.
import type { Entry } from '../work/visit';
import { loadList } from '../work/visit';
import { researchPage } from './catalogue';

export class CollectionLoader {
	works: Entry[] = $state([]);
	total = $state(0);
	loading = $state(true);
	failed = $state(false);
	loadingMore = $state(false);
	#serial = 0;
	#corpus = false;
	#key = '';
	#controller: AbortController | null = null;
	readonly base: string;

	constructor(base = '') {
		this.base = base;
	}

	get hasMore(): boolean {
		return this.#corpus && this.works.length < this.total;
	}

	/** Start again from the first page; an older request that answers late is ignored. */
	async load(key: string, corpus: boolean): Promise<void> {
		const { serial, signal } = this.#restart(key, corpus);
		try {
			const list = corpus
				? await researchPage(this.base, key, 0, signal)
				: await loadList(key || null);
			if (serial === this.#serial) this.#show(list);
		} catch {
			if (serial === this.#serial && !signal.aborted) this.failed = true;
		} finally {
			if (serial === this.#serial) this.loading = false;
		}
	}

	#restart(key: string, corpus: boolean): { serial: number; signal: AbortSignal } {
		this.#controller?.abort();
		this.#controller = new AbortController();
		this.#corpus = corpus;
		this.#key = key;
		this.works = [];
		this.total = 0;
		this.loading = true;
		this.failed = false;
		this.loadingMore = false;
		return { serial: ++this.#serial, signal: this.#controller.signal };
	}

	#show(list: { works: Entry[]; total?: number } | null): void {
		this.works = list?.works ?? [];
		this.total = list?.total ?? this.works.length;
		this.failed = list === null;
	}

	/** The next corpus page, appended. */
	async more(): Promise<void> {
		if (this.loadingMore || !this.hasMore) return;
		const serial = this.#serial;
		this.loadingMore = true;
		try {
			const page = await researchPage(this.base, this.#key, this.works.length);
			if (serial !== this.#serial) return;
			this.works = [...this.works, ...page.works];
			this.total = page.total;
		} catch {
			if (serial === this.#serial) this.failed = true;
		} finally {
			if (serial === this.#serial) this.loadingMore = false;
		}
	}

	stop(): void {
		this.#controller?.abort();
		this.#serial += 1;
	}
}
