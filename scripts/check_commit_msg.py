# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Check a commit message against the project's commit rules (CONTRIBUTING.md).

Usage: python scripts/check_commit_msg.py <message-file>   (git commit-msg hook)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TYPES = ("feat", "fix", "refactor", "perf", "test", "docs", "build", "ci", "chore", "revert")
SUBJECT_MAX = 72
HEADER = re.compile(rf"^(?:{'|'.join(TYPES)})(?:\([a-z0-9-]+\))?!?: \S.*$")
EXEMPT = re.compile(r"^(?:Merge |Revert \"|fixup! |squash! )")


def problems(message: str) -> list[str]:
    lines = [line for line in message.splitlines() if not line.startswith("#")]
    if not lines or not lines[0].strip():
        return ["empty commit message"]
    subject = lines[0]
    if EXEMPT.match(subject):
        return []
    found: list[str] = []
    if not HEADER.match(subject):
        allowed = ", ".join(TYPES)
        found.append(f"subject must be `<type>(<scope>)?: <summary>`, type in {allowed}")
    if len(subject) > SUBJECT_MAX:
        found.append(f"subject is {len(subject)} characters, max {SUBJECT_MAX}")
    if subject.endswith("."):
        found.append("subject must not end with a period")
    if len(lines) > 1 and lines[1].strip():
        found.append("second line must be blank")
    return found


def main() -> int:
    found = problems(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for problem in found:
        print(f"✗ commit message: {problem}", file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
