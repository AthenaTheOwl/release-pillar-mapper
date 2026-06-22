from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from release_mapper.schema import ValidationError, load_release_event


def main(argv: list[str] | None = None) -> int:
    raw_args = argv if argv is not None else sys.argv[1:]
    paths = [Path(arg) for arg in raw_args]
    if not paths:
        paths = sorted((ROOT / "examples" / "_events").glob("*.json"))
        paths.extend(sorted((ROOT / "releases" / "_events").glob("*.json")))
    if not paths:
        print("ERROR: no release event files found")
        return 1

    failed = False
    for path in paths:
        try:
            event = load_release_event(path)
        except (OSError, ValueError, ValidationError) as exc:
            failed = True
            print(f"ERROR {path}: {exc}")
        else:
            print(f"OK {event.id}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
