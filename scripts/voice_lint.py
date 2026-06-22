from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BANNED_PHRASES = [
    "breakthrough",
    "game changer",
    "paradigm shift",
    "revolutionary",
    "seismic",
    "transformative",
    "unlock",
]
ANTITHETICAL_RE = re.compile(r"\bnot\s+(?:only\s+)?.{0,90}\bbut\b", re.IGNORECASE)


def main(argv: list[str] | None = None) -> int:
    paths = [Path(arg) for arg in (argv if argv is not None else sys.argv[1:])]
    if not paths:
        paths = sorted((ROOT / "releases").glob("*.md"))
    failures: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for phrase in BANNED_PHRASES:
            if phrase in lowered:
                failures.append(f"{path}: banned phrase {phrase!r}")
        if ANTITHETICAL_RE.search(text):
            failures.append(f"{path}: antithetical reversal pattern")
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print(f"OK voice_lint {len(paths)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
