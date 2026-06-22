from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from release_pillar_mapper.io import load_json_compatible
from release_pillar_mapper.schema import ReleaseEvent


@dataclass(frozen=True)
class SignificanceResult:
    accepted: bool
    reason: str

    def to_cli_line(self) -> str:
        decision = "yes" if self.accepted else "no"
        return f"{decision}: {self.reason}"


def load_significance_config(path: Path) -> dict[str, object]:
    return load_json_compatible(path)


def evaluate_significance(
    event: ReleaseEvent,
    config: dict[str, object],
    *,
    force: bool = False,
) -> SignificanceResult:
    if force:
        return SignificanceResult(True, "forced by operator")

    vendors = set(_string_list(config.get("vendor_allowlist"), "vendor_allowlist"))
    if event.vendor not in vendors:
        return SignificanceResult(False, f"vendor {event.vendor} is outside the allowlist")

    text = event.searchable_text
    if event.kind == "model":
        keyword = _first_match(text, _string_list(config.get("headline_keywords"), "headline_keywords"))
        if keyword:
            return SignificanceResult(True, f"model release matched keyword {keyword!r}")
        return SignificanceResult(False, "model release did not match a frontier keyword")

    if event.kind == "eval":
        keyword = _first_match(text, _string_list(config.get("curated_eval_ids"), "curated_eval_ids"))
        if keyword:
            return SignificanceResult(True, f"eval release matched curated eval {keyword!r}")
        return SignificanceResult(False, "eval release did not match the curated eval list")

    if event.kind == "dataset":
        keyword = _first_match(text, _string_list(config.get("dataset_keywords"), "dataset_keywords"))
        if keyword:
            return SignificanceResult(True, f"dataset release matched keyword {keyword!r}")
        return SignificanceResult(False, "dataset release did not match a mapped dataset keyword")

    keyword = _first_match(text, _string_list(config.get("framework_keywords"), "framework_keywords"))
    if keyword:
        return SignificanceResult(True, f"framework release matched keyword {keyword!r}")
    return SignificanceResult(False, "framework release did not match a mapped framework keyword")


def _first_match(text: str, keywords: list[str]) -> str | None:
    for keyword in keywords:
        if keyword.lower() in text:
            return keyword
    return None


def _string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be a list of strings")
    return value
