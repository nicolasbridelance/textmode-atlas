// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// Where public files (grids, renderings, JSON exported by `tm export`) are read from. Only the
// base URL changes between environments (see `src/env.ts`).
import { FILES_BASE } from '$app/env/public';

export function fileUrl(key: string, base: string = FILES_BASE): string {
	return `${base}/${key.replace(/^\//, '')}`;
}
