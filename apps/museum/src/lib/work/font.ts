// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// The same bitmap font as the pipeline's renderer (corpus/fonts, libansilove's VGA 8×16), fetched
// once for the whole visit.
import fontUrl from '../../../../../corpus/fonts/ibm-vga-8x16.f16?url';
import { checkFont } from './draw';

let font: Promise<Uint8Array> | null = null;

export function loadFont(): Promise<Uint8Array> {
	font ??= fetch(fontUrl)
		.then((response) => response.arrayBuffer())
		.then((bytes) => checkFont(new Uint8Array(bytes)));
	return font;
}
