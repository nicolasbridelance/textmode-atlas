// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { defineEnvVars } from '@sveltejs/kit/env';

export const variables = defineEnvVars({
	FILES_BASE: {
		public: true,
		static: true,
		description:
			'Base URL of public files exported by `tm export`: `/files` (dev proxy to the local public bucket) or the CDN.',
		schema: (value) => (value || '/files').replace(/\/$/, '')
	}
});
