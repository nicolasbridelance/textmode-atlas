// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { defineConfig } from '@playwright/test';

export default defineConfig({
	webServer: { command: 'pnpm run build && pnpm run preview', port: 4173 },
	testMatch: '**/*.e2e.{ts,js}'
});
