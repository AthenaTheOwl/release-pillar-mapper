from __future__ import annotations

from release_mapper.schema import ReleaseEvent
from release_mapper.significance import evaluate_significance


CONFIG = {
    "vendor_allowlist": ["OpenAI"],
    "headline_keywords": ["agent", "coding"],
    "curated_eval_ids": ["swe-bench"],
    "dataset_keywords": ["agent traces"],
    "framework_keywords": ["tool calling"],
}


def _event(**overrides: object) -> ReleaseEvent:
    data = {
        "id": "2026-04-01-example-frontier-agent-model",
        "kind": "model",
        "source_url": "https://example.com/releases/frontier-agent-model",
        "vendor": "OpenAI",
        "headline": "Example frontier agent model improves coding reliability",
        "claims": [{"text": "The release improves agent traces.", "source_anchor": "claim-1"}],
        "ingested_at": "2026-04-01T12:00:00Z",
    }
    data.update(overrides)
    return ReleaseEvent.from_dict(data)


def test_model_release_accepts_allowlisted_keyword() -> None:
    result = evaluate_significance(_event(), CONFIG)

    assert result.accepted is True
    assert result.to_cli_line().startswith("yes:")


def test_vendor_outside_allowlist_rejects() -> None:
    result = evaluate_significance(_event(vendor="Small Lab"), CONFIG)

    assert result.accepted is False
    assert "outside the allowlist" in result.reason


def test_force_accepts_borderline_release() -> None:
    result = evaluate_significance(_event(vendor="Small Lab"), CONFIG, force=True)

    assert result.accepted is True
    assert result.reason == "forced by operator"
