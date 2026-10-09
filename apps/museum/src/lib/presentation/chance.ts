// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
// Chance in the museum: shuffles and draws that a seed makes reproducible and shareable.

const FNV_OFFSET = 0x811c9dc5;
const FNV_PRIME = 0x01000193;
const SEED_LENGTH = 6;
const SEED_ALPHABET = 'abcdefghijkmnpqrstuvwxyz23456789'; // no look-alikes, readable aloud

/** FNV-1a over the text: the same work and seed always land at the same place. */
function rank(sha256: string, seed: string): number {
	let hash = FNV_OFFSET;
	for (const char of `${sha256}:${seed}`) {
		hash ^= char.charCodeAt(0);
		hash = Math.imul(hash, FNV_PRIME) >>> 0;
	}
	return hash;
}

export function shuffled<T extends { sha256: string }>(entries: T[], seed: string): T[] {
	return entries
		.map((entry) => ({ entry, key: rank(entry.sha256, seed) }))
		.sort((a, b) => a.key - b.key || a.entry.sha256.localeCompare(b.entry.sha256))
		.map(({ entry }) => entry);
}

export function draw<T extends { sha256: string }>(entries: T[], seed: string): T | null {
	return shuffled(entries, seed)[0] ?? null;
}

/** A short new seed; `random` is injectable so that tests stay deterministic. */
export function newSeed(random: () => number = Math.random): string {
	return Array.from(
		{ length: SEED_LENGTH },
		() => SEED_ALPHABET[Math.floor(random() * SEED_ALPHABET.length)]
	).join('');
}
