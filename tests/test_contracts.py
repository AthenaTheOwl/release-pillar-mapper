from __future__ import annotations

import re
from pathlib import Path

from release_mapper.render import parse_impact_front_matter


ROOT = Path(__file__).resolve().parents[1]


def test_status_has_exact_required_h2_headings() -> None:
    text = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    headings = re.findall(r"^## .+$", text, flags=re.MULTILINE)

    assert headings == [
        "## Current state",
        "## Known limits",
        "## Next feature queue",
    ]


def test_checked_in_report_front_matter_is_impact_map() -> None:
    report = (ROOT / "releases" / "2026-04-01-example-frontier-agent-model.md").read_text(
        encoding="utf-8"
    )
    impact_map = parse_impact_front_matter(report)

    assert impact_map.release_id == "2026-04-01-example-frontier-agent-model"
    assert impact_map.repo_impacts
    assert impact_map.brief_impacts
    assert impact_map.pillar_impacts
