// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import catalogue from '../../../../../research/exploration/catalogue.md?raw';
import works from '../../../../../research/exploration/works.md?raw';
import neighbours from '../../../../../research/exploration/neighbours.md?raw';
import programme from '../../../../../docs/research-program.md?raw';

export const reports = [
	{ id: 'programme', title: 'Research programme', text: programme },
	{ id: 'catalogue', title: 'Catalogue exploration', text: catalogue },
	{ id: 'works', title: 'Reading the corpus', text: works },
	{ id: 'neighbours', title: 'Nearest works and attribution', text: neighbours }
];
