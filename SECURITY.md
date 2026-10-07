<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Security

Please do not open a public issue for a vulnerability. Use
[GitHub's private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
on this repository.

Especially sensitive:

- any path that would let a work refused by `can_display()` reach the public bucket;
- any exposure of the `person` table or of a handle → civil identity link;
- decoders and archive extraction, which read files from outside.

We answer within seven days.
