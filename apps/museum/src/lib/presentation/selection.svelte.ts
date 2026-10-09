// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
// The visitor's selection: works kept in this browser only, with one undo for clearing it.
import { isWorkId } from '../work/record';

const KEY = 'textmode-discovery-selection-v1';

class Selection {
	ids: string[] = $state([]);
	cleared: string[] | null = $state(null);
	#restored = false;

	/** Read the browser's copy once; the selection still works when storage is unavailable. */
	restore(): void {
		if (this.#restored) return;
		this.#restored = true;
		try {
			const value: unknown = JSON.parse(localStorage.getItem(KEY) ?? '[]');
			if (Array.isArray(value))
				this.ids = [...new Set(value.filter((id): id is string => typeof id === 'string'))].filter(
					isWorkId
				);
		} catch {
			/* Start empty. */
		}
	}
	#store(): void {
		try {
			localStorage.setItem(KEY, JSON.stringify(this.ids));
		} catch {
			/* Keep the selection for this visit. */
		}
	}
	has(id: string): boolean {
		return this.ids.includes(id);
	}
	set(id: string, value: boolean): void {
		this.ids = value ? [...new Set([...this.ids, id])] : this.ids.filter((other) => other !== id);
		this.#store();
	}
	toggle(id: string): void {
		this.set(id, !this.has(id));
	}
	clear(): void {
		this.cleared = [...this.ids];
		this.ids = [];
		this.#store();
	}
	undoClear(): void {
		if (this.cleared) this.ids = [...new Set([...this.ids, ...this.cleared])];
		this.cleared = null;
		this.#store();
	}
}

export const selection = new Selection();
