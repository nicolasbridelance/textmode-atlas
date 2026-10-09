// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// What a cell holds, said in words: the CP437 glyph as Unicode, and the VGA colour names.
// For the cell inspector; the drawing itself always comes from the bitmap font.

// CP437 as Unicode: the control glyphs, ASCII, then the upper half.
const LOW = ' ☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼';
const ASCII_FIRST = 32;
const ASCII_COUNT = 95;
const ASCII = Array.from({ length: ASCII_COUNT }, (_, i) =>
	String.fromCharCode(ASCII_FIRST + i)
).join('');
const HIGH =
	'⌂ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜ¢£¥₧ƒáíóúñÑªº¿⌐¬½¼¡«»░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀αßΓπΣσµτΦΘΩδ∞φε∩≡±≥≤⌠⌡÷≈°∙·√ⁿ²■ ';
const CP437 = [...(LOW + ASCII + HIGH)];
const BYTE = 0xff;
const HEX = 16;
const HEX_DIGITS = 2;

export function glyph(codepoint: number): string {
	return CP437[codepoint & BYTE] ?? '?';
}

export function hex(codepoint: number): string {
	return '0x' + (codepoint & BYTE).toString(HEX).toUpperCase().padStart(HEX_DIGITS, '0');
}

export const COLOUR_NAMES: Record<string, readonly string[]> = {
	en: [
		'black', 'blue', 'green', 'cyan', 'red', 'magenta', 'brown', 'light grey',
		'dark grey', 'bright blue', 'bright green', 'bright cyan', 'bright red', 'bright magenta',
		'yellow', 'white'
	],
	fr: [
		'noir', 'bleu', 'vert', 'cyan', 'rouge', 'magenta', 'marron', 'gris clair',
		'gris foncé', 'bleu vif', 'vert vif', 'cyan vif', 'rouge vif', 'magenta vif',
		'jaune', 'blanc'
	]
}; // prettier-ignore
