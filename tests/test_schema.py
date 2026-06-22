from __future__ import annotations

import pytest

from release_mapper.schema import ImpactMap, ReleaseEvent, ValidationError


VALID_EVENT = {
    "id": "2026-04-01-example-frontier-agent-model",
    "kind": "model",
    "source_url": "https://example.com/releases/frontier-agent-model",
    "vendor": "OpenAI",
    "headline": "Example frontier agent model improves coding reliability",
    "claims": [
        {
            "text": "The model improves coding workflow reliability.",
            "source_anchor": "example-release#claim-1",
        }
    ],
    "ingested_at": "2026-04-01T12:00:00Z",
}


def test_release_event_validates() -> None:
    event = ReleaseEvent.from_dict(VALID_EVENT)

    assert event.id == "2026-04-01-example-frontier-agent-model"
    assert event.claims[0].source_anchor == "example-release#claim-1"


def test_release_event_rejects_bad_id() -> None:
    data = dict(VALID_EVENT)
    data["id"] = "2026-04-example"

    with pytest.raises(ValidationError, match="YYYY-MM-DD"):
        ReleaseEvent.from_dict(data)


def test_release_event_requires_claims() -> None:
    data = dict(VALID_EVENT)
    data["claims"] = []

    with pytest.raises(ValidationError, match="at least one"):
        ReleaseEvent.from_dict(data)


def test_impact_map_requires_one_impact() -> None:
    with pytest.raises(ValidationError, match="at least one impact"):
        ImpactMap.from_dict(
            {
                "release_id": "2026-04-01-example-frontier-agent-model",
                "repo_impacts": [],
                "brief_impacts": [],
                "pillar_impacts": [],
            }
        )
