from __future__ import annotations

from pathlib import Path
from typing import Any

from release_pillar_mapper.io import load_json_compatible
from release_pillar_mapper.schema import Impact, ImpactMap, ReleaseEvent


def load_registries(root: Path) -> dict[str, list[dict[str, Any]]]:
    repo_index = load_json_compatible(root / "config" / "repo_index.yaml")
    brief_corpus = load_json_compatible(root / "config" / "brief_corpus.yaml")
    thesis_pillars = load_json_compatible(root / "config" / "thesis_pillars.yaml")
    return {
        "repos": _object_list(repo_index.get("repos"), "repos"),
        "briefs": _object_list(brief_corpus.get("briefs"), "briefs"),
        "pillars": _object_list(thesis_pillars.get("pillars"), "pillars"),
    }


def build_impact_map(event: ReleaseEvent, registries: dict[str, list[dict[str, Any]]]) -> ImpactMap:
    return ImpactMap(
        release_id=event.id,
        repo_impacts=tuple(
            _impact_for_target(event, target, id_key="slug", default_direction="strengthens")
            for target in registries["repos"]
        ),
        brief_impacts=tuple(
            _impact_for_target(event, target, id_key="id", default_direction="confirms")
            for target in registries["briefs"]
        ),
        pillar_impacts=tuple(
            _impact_for_target(event, target, id_key="id", default_direction="strengthens")
            for target in registries["pillars"]
        ),
    )


def _impact_for_target(
    event: ReleaseEvent,
    target: dict[str, Any],
    *,
    id_key: str,
    default_direction: str,
) -> Impact:
    target_id = _required_string(target, id_key)
    tags = _string_list(target.get("topic_tags"), f"{target_id}.topic_tags")
    matched = _matches_any(event.searchable_text, tags)
    if matched:
        direction = _optional_string(target.get("impact_direction")) or default_direction
        confidence = "medium"
        action = _required_string(target, "recommended_action")
        evidence_anchor = event.first_evidence_anchor
    else:
        direction = "unchanged"
        confidence = "low"
        action = f"Leave {target_id} unchanged; review only if follow-on evidence mentions this target directly."
        evidence_anchor = "release.headline"
    return Impact(
        target_id=target_id,
        direction=direction,
        confidence=confidence,
        evidence_anchor=evidence_anchor,
        recommended_action=action,
    )


def _matches_any(text: str, tags: list[str]) -> bool:
    return any(tag.lower() in text for tag in tags)


def _object_list(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{field} must be a list of objects")
    return value


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be a list of strings")
    return value


def _required_string(target: dict[str, Any], field: str) -> str:
    value = target.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value
    return None
