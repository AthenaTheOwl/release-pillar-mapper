from __future__ import annotations

import json

from release_pillar_mapper.schema import Impact, ImpactMap, ReleaseEvent


def render_report(event: ReleaseEvent, impact_map: ImpactMap) -> str:
    if event.id != impact_map.release_id:
        raise ValueError("release event id and impact map release_id differ")

    lines = [
        "---",
        json.dumps(impact_map.to_dict(), indent=2, sort_keys=True),
        "---",
        "",
        f"# {event.headline}",
        "",
        f"- Release id: `{event.id}`",
        f"- Vendor: {event.vendor}",
        f"- Kind: {event.kind}",
        f"- Source: {event.source_url}",
        f"- Ingested at: {event.ingested_at}",
        "",
        "## Source claims",
        "",
    ]
    for claim in event.claims:
        lines.append(f"- {claim.source_anchor}: {claim.text}")
    lines.extend(
        [
            "",
            "## Repo impacts",
            "",
            *_impact_lines(impact_map.repo_impacts),
            "## Brief impacts",
            "",
            *_impact_lines(impact_map.brief_impacts),
            "## Pillar impacts",
            "",
            *_impact_lines(impact_map.pillar_impacts),
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def parse_impact_front_matter(markdown: str) -> ImpactMap:
    lines = markdown.splitlines()
    if len(lines) < 3 or lines[0] != "---":
        raise ValueError("report is missing front matter")
    try:
        end_index = lines[1:].index("---") + 1
    except ValueError as exc:
        raise ValueError("report front matter is not closed") from exc
    payload = "\n".join(lines[1:end_index])
    return ImpactMap.from_dict(json.loads(payload))


def _impact_lines(impacts: tuple[Impact, ...]) -> list[str]:
    lines: list[str] = []
    for impact in impacts:
        lines.extend(
            [
                f"### {impact.target_id}",
                "",
                f"- Direction: `{impact.direction}`",
                f"- Confidence: `{impact.confidence}`",
                f"- Evidence: {impact.evidence_anchor}",
                f"- Recommended action: {impact.recommended_action}",
                "",
            ]
        )
    if not lines:
        return ["No mapped impacts.", ""]
    return lines
