from __future__ import annotations

from pathlib import Path

from release_mapper.mapper import build_impact_map, load_registries
from release_mapper.render import parse_impact_front_matter, render_report
from release_mapper.schema import load_release_event


ROOT = Path(__file__).resolve().parents[1]
EVENT_PATH = ROOT / "examples" / "_events" / "2026-04-01-example-frontier-agent-model.json"


def test_rendered_front_matter_round_trips() -> None:
    event = load_release_event(EVENT_PATH)
    impact_map = build_impact_map(event, load_registries(ROOT))

    rendered = render_report(event, impact_map)
    parsed = parse_impact_front_matter(rendered)

    assert parsed == impact_map
    assert "## Repo impacts" in rendered
    assert "## Brief impacts" in rendered
    assert "## Pillar impacts" in rendered


def test_checked_in_report_matches_renderer() -> None:
    event = load_release_event(EVENT_PATH)
    impact_map = build_impact_map(event, load_registries(ROOT))

    rendered = render_report(event, impact_map)
    checked_in = (ROOT / "releases" / f"{event.id}.md").read_text(encoding="utf-8")

    assert checked_in == rendered
