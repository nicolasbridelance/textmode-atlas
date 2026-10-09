// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
declare global {
	interface Window {
		mountMuseumGraph: (
			root: HTMLElement,
			locale: string,
			workHref: (sha: string) => string
		) => () => void;
	}
}

let runtime: Promise<void> | null = null;

function script(src: string): Promise<void> {
	return new Promise((resolve, reject) => {
		const element = document.createElement('script');
		element.src = src;
		element.onload = () => resolve();
		element.onerror = () => reject(new Error('Graph runtime unavailable'));
		document.head.append(element);
	});
}

export function graphRuntime(): Promise<void> {
	runtime ??= script('https://unpkg.com/deck.gl@9.1.14/dist.min.js').then(() =>
		script('/atlas-graph.js')
	);
	return runtime;
}
