// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
//
// The measurements every chart of the exploration shares, in SVG user units.

export const CHART = {
	width: 640, // until the chart has measured its container
	minWidth: 280,
	tickGap: 6, // between an axis and its labels
	tickBaseline: 4, // lowers a label onto the middle of its line
	axisLabel: 8, // x labels sit this far above the bottom edge
	endLabel: 10, // a line's name sits this far right of its last point
	noteRise: 12, // notes sit this far above the plot
	markerReach: 6, // reference lines rise this far above the plot
	corner: 2, // radius of a bar's rounded top
	gap: 2 // surface between two bars
};

export const PERCENT = 100;
export const HALF = 0.5;
