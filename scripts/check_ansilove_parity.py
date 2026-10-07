# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
"""Check that the pinned ansilove draws every golden artifact with the pixels we expect (ADR 0010).

`tests/golden/renderings.json` records the pixels of our conservation rendering; the test suite
checks that tm_render reproduces them, this script that ansilove agrees. It needs `ansilove` on
the PATH: run it in the development image (`just parity`).
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image
from tm_render.conservation import pixels_sha256

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden"


def main() -> int:
    if shutil.which("ansilove") is None:
        print("ansilove is not on the PATH: run `just parity` (development image)")
        return 2
    expected = json.loads((GOLDEN / "renderings.json").read_text())
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, entry in expected.items():
            out = Path(tmp) / "out.png"
            arguments = ["ansilove", "-q", *entry["ansilove_arguments"], "-o", str(out)]
            subprocess.run([*arguments, str(GOLDEN / name)], check=True, capture_output=True)
            got = pixels_sha256(Image.open(out))
            same = got == entry["pixels_sha256"]
            failures += not same
            print(f"{'same' if same else 'DIFFERENT'}  {name}  {got}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
