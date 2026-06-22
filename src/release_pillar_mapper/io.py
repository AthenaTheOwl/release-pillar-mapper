from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json_compatible(path: Path) -> dict[str, Any]:
    """Load JSON-compatible YAML files without a YAML dependency."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON-compatible YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def find_event_path(release_id: str, root: Path) -> Path:
    candidates = [
        root / "examples" / "_events" / f"{release_id}.json",
        root / "releases" / "_events" / f"{release_id}.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    searched = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"release event {release_id!r} not found; searched {searched}")
