from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC_RE = re.compile(r"\bR-RPM-\d{3}\b")
REQUIRED_STATUS_HEADINGS = [
    "## Current state",
    "## Known limits",
    "## Next feature queue",
]


def main() -> int:
    failures: list[str] = []
    failures.extend(_check_status())
    failures.extend(_check_specs())
    failures.extend(_check_pyproject())
    failures.extend(_check_required_files())
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("OK spec_check")
    return 0


def _check_status() -> list[str]:
    path = ROOT / "STATUS.md"
    if not path.exists():
        return ["STATUS.md is missing"]
    headings = re.findall(r"^## .+$", path.read_text(encoding="utf-8"), flags=re.MULTILINE)
    if headings != REQUIRED_STATUS_HEADINGS:
        return [f"STATUS.md H2 headings must be exactly {REQUIRED_STATUS_HEADINGS}"]
    return []


def _check_specs() -> list[str]:
    failures: list[str] = []
    defined: set[str] = set()
    for requirements in sorted((ROOT / "specs").glob("*/requirements.md")):
        defined.update(SPEC_RE.findall(requirements.read_text(encoding="utf-8")))
    if not defined:
        failures.append("no spec requirement IDs found")
    for spec_file in sorted((ROOT / "specs").glob("*/*.md")):
        if spec_file.name == "requirements.md":
            continue
        refs = set(SPEC_RE.findall(spec_file.read_text(encoding="utf-8")))
        missing = sorted(refs - defined)
        if missing:
            failures.append(f"{spec_file.relative_to(ROOT)} references undefined IDs: {', '.join(missing)}")
    return failures


def _check_pyproject() -> list[str]:
    path = ROOT / "pyproject.toml"
    if not path.exists():
        return ["pyproject.toml is missing"]
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    failures: list[str] = []
    if "dependency-groups" not in data:
        failures.append("pyproject.toml must use [dependency-groups]")
    if data.get("project", {}).get("optional-dependencies"):
        failures.append("pyproject.toml must not use [project.optional-dependencies] for dev deps")
    if data.get("tool", {}).get("uv", {}).get("package") is not True:
        failures.append("pyproject.toml [tool.uv] package must be true")
    return failures


def _check_required_files() -> list[str]:
    required = [
        "docs/product-brief.md",
        "docs/system-map.md",
        "releases/2026-04-01-example-frontier-agent-model.md",
        "examples/_events/2026-04-01-example-frontier-agent-model.json",
    ]
    return [f"{path} is missing" for path in required if not (ROOT / path).exists()]


if __name__ == "__main__":
    raise SystemExit(main())
