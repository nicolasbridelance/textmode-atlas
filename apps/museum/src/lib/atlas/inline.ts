// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// Inline Markdown of the research notes: code, bold, italics and links, as segments for the
// template (never HTML). A link leaves the site only for an absolute web address; a path into
// the repository means nothing to a visitor, so its text stays plain.
export type Segment =
	| { kind: 'text' | 'code' | 'strong' | 'em'; text: string }
	| { kind: 'link'; text: string; href: string };

const TOKEN = /`([^`]+)`|\*\*([^*]+)\*\*|\*([^*\s][^*]*)\*|\[([^\]]+)\]\(([^)\s]+)\)/g;
const WEB = /^https?:\/\//;

/** The segment one match of TOKEN stands for. */
function segment([, code, strong, em, label = '', href = '']: RegExpMatchArray): Segment {
	if (code !== undefined) return { kind: 'code', text: code };
	if (strong !== undefined) return { kind: 'strong', text: strong };
	if (em !== undefined) return { kind: 'em', text: em };
	return WEB.test(href) ? { kind: 'link', text: label, href } : { kind: 'text', text: label };
}

export function inline(source: string): Segment[] {
	const out: Segment[] = [];
	let last = 0;
	for (const match of source.matchAll(TOKEN)) {
		if (match.index > last) out.push({ kind: 'text', text: source.slice(last, match.index) });
		out.push(segment(match));
		last = match.index + match[0].length;
	}
	if (last < source.length) out.push({ kind: 'text', text: source.slice(last) });
	return out;
}
