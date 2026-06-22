from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_KINDS = {"model", "eval", "dataset", "framework"}
VALID_DIRECTIONS = {"strengthens", "weakens", "invalidates", "confirms", "refutes", "unchanged"}
VALID_CONFIDENCE = {"low", "medium", "high"}


class ValidationError(ValueError):
    """Raised when a release event or impact map fails local validation."""


def _require_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{key} must be a non-empty string")
    return value


def _validate_release_id(value: str, field: str = "id") -> None:
    if not ID_RE.match(value):
        raise ValidationError(f"{field} must match YYYY-MM-DD-<slug>")


def _validate_datetime(value: str) -> None:
    normalized = value.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValidationError("ingested_at must be an ISO 8601 datetime") from exc


@dataclass(frozen=True)
class Claim:
    text: str
    source_anchor: str

    @classmethod
    def from_dict(cls, data: Any) -> "Claim":
        if not isinstance(data, dict):
            raise ValidationError("claim must be an object")
        return cls(
            text=_require_string(data, "text"),
            source_anchor=_require_string(data, "source_anchor"),
        )

    def to_dict(self) -> dict[str, str]:
        return {"text": self.text, "source_anchor": self.source_anchor}


@dataclass(frozen=True)
class ReleaseEvent:
    id: str
    kind: str
    source_url: str
    vendor: str
    headline: str
    claims: tuple[Claim, ...]
    ingested_at: str

    @classmethod
    def from_dict(cls, data: Any) -> "ReleaseEvent":
        if not isinstance(data, dict):
            raise ValidationError("release event must be an object")
        release_id = _require_string(data, "id")
        _validate_release_id(release_id)
        kind = _require_string(data, "kind")
        if kind not in VALID_KINDS:
            raise ValidationError(f"kind must be one of {sorted(VALID_KINDS)}")
        source_url = _require_string(data, "source_url")
        if not source_url.startswith(("http://", "https://")):
            raise ValidationError("source_url must be an http or https URL")
        claims_raw = data.get("claims")
        if not isinstance(claims_raw, list) or not claims_raw:
            raise ValidationError("claims must contain at least one claim")
        ingested_at = _require_string(data, "ingested_at")
        _validate_datetime(ingested_at)
        return cls(
            id=release_id,
            kind=kind,
            source_url=source_url,
            vendor=_require_string(data, "vendor"),
            headline=_require_string(data, "headline"),
            claims=tuple(Claim.from_dict(claim) for claim in claims_raw),
            ingested_at=ingested_at,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "source_url": self.source_url,
            "vendor": self.vendor,
            "headline": self.headline,
            "claims": [claim.to_dict() for claim in self.claims],
            "ingested_at": self.ingested_at,
        }

    @property
    def searchable_text(self) -> str:
        claim_text = " ".join(claim.text for claim in self.claims)
        return f"{self.vendor} {self.headline} {claim_text}".lower()

    @property
    def first_evidence_anchor(self) -> str:
        return self.claims[0].source_anchor


@dataclass(frozen=True)
class Impact:
    target_id: str
    direction: str
    confidence: str
    evidence_anchor: str
    recommended_action: str

    @classmethod
    def from_dict(cls, data: Any) -> "Impact":
        if not isinstance(data, dict):
            raise ValidationError("impact must be an object")
        direction = _require_string(data, "direction")
        if direction not in VALID_DIRECTIONS:
            raise ValidationError(f"direction must be one of {sorted(VALID_DIRECTIONS)}")
        confidence = _require_string(data, "confidence")
        if confidence not in VALID_CONFIDENCE:
            raise ValidationError(f"confidence must be one of {sorted(VALID_CONFIDENCE)}")
        return cls(
            target_id=_require_string(data, "target_id"),
            direction=direction,
            confidence=confidence,
            evidence_anchor=_require_string(data, "evidence_anchor"),
            recommended_action=_require_string(data, "recommended_action"),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "target_id": self.target_id,
            "direction": self.direction,
            "confidence": self.confidence,
            "evidence_anchor": self.evidence_anchor,
            "recommended_action": self.recommended_action,
        }


@dataclass(frozen=True)
class ImpactMap:
    release_id: str
    repo_impacts: tuple[Impact, ...]
    brief_impacts: tuple[Impact, ...]
    pillar_impacts: tuple[Impact, ...]

    @classmethod
    def from_dict(cls, data: Any) -> "ImpactMap":
        if not isinstance(data, dict):
            raise ValidationError("impact map must be an object")
        release_id = _require_string(data, "release_id")
        _validate_release_id(release_id, "release_id")
        repo_impacts = _impact_tuple(data.get("repo_impacts"), "repo_impacts")
        brief_impacts = _impact_tuple(data.get("brief_impacts"), "brief_impacts")
        pillar_impacts = _impact_tuple(data.get("pillar_impacts"), "pillar_impacts")
        if not (repo_impacts or brief_impacts or pillar_impacts):
            raise ValidationError("impact map must contain at least one impact")
        return cls(
            release_id=release_id,
            repo_impacts=repo_impacts,
            brief_impacts=brief_impacts,
            pillar_impacts=pillar_impacts,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "release_id": self.release_id,
            "repo_impacts": [impact.to_dict() for impact in self.repo_impacts],
            "brief_impacts": [impact.to_dict() for impact in self.brief_impacts],
            "pillar_impacts": [impact.to_dict() for impact in self.pillar_impacts],
        }


def _impact_tuple(value: Any, field: str) -> tuple[Impact, ...]:
    if not isinstance(value, list):
        raise ValidationError(f"{field} must be an array")
    return tuple(Impact.from_dict(item) for item in value)


def load_release_event(path: Path) -> ReleaseEvent:
    return ReleaseEvent.from_dict(json.loads(path.read_text(encoding="utf-8")))


def load_impact_map(path: Path) -> ImpactMap:
    return ImpactMap.from_dict(json.loads(path.read_text(encoding="utf-8")))
