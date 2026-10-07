// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// Screenshots of the built site, desktop and mobile, for every locale.
// Usage: pnpm run screenshots [path…]   (needs `pnpm run build` first)
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { mkdir } from 'node:fs/promises';
import { setTimeout as sleep } from 'node:timers/promises';

const PORT = 4174;
const OUT = 'test-results/screenshots';
const SERVER_START_MS = 2000;
const VIEWPORTS = {
	desktop: { width: 1280, height: 800 },
	mobile: { width: 390, height: 844 }
} as const;
const LOCALE_PREFIXES = { en: '', fr: '/fr' } as const;

const paths = process.argv.slice(2);
const shots = (paths.length ? paths : ['/']).flatMap((path) =>
	Object.entries(LOCALE_PREFIXES).flatMap(([locale, prefix]) =>
		Object.entries(VIEWPORTS).map(([device, viewport]) => ({
			path,
			locale,
			prefix,
			device,
			viewport
		}))
	)
);

const server = spawn('pnpm', ['exec', 'vite', 'preview', '--port', String(PORT), '--strictPort'], {
	stdio: 'ignore'
});
try {
	await sleep(SERVER_START_MS);
	await mkdir(OUT, { recursive: true });
	const browser = await chromium.launch();
	for (const { path, locale, prefix, device, viewport } of shots) {
		const page = await browser.newPage({ viewport });
		await page.goto(`http://localhost:${PORT}${prefix}${path}`, { waitUntil: 'networkidle' });
		const slug = path.replace(/\W+/g, '-').replace(/^-|-$/g, '') || 'home';
		const file = `${OUT}/${slug}.${locale}.${device}.png`;
		await page.screenshot({ path: file });
		process.stdout.write(`${file}\n`);
		await page.close();
	}
	await browser.close();
} finally {
	server.kill();
}
