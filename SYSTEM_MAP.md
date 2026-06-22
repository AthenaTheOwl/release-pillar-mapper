# System Map

## Components

- `release_pillar_mapper.schema` validates release events and impact maps.
- `release_pillar_mapper.scoring` applies local significance threshold rules.
- `release_pillar_mapper.model` builds three impact axes from config registries.
- `release_pillar_mapper.render` writes deterministic Markdown with typed front matter.
- `release_pillar_mapper.cli` exposes the local workflow.
- `release_mapper` remains as a compatibility import path for existing callers.

## Data Flow

1. The user creates or checks in a release event JSON file.
2. The validator checks the event shape and source-anchored claims.
3. The significance scorer reads `config/significance.yaml` and returns a yes/no decision with a reason.
4. The mapper compares event text with registry tags and builds repo, brief, and pillar impacts.
5. The renderer writes `releases/<release_id>.md`.
6. The checked-in JSONL artifact records the same impact-map payload for downstream data review.

## Trust Boundary

The CLI treats release-event claims as user-supplied evidence. It does
not fetch web pages, quote vendor copy, or rewrite claims from remote
sources. The checked-in report is a structured decision artifact.

## Local Gate Surface

- `uv run pytest`
- `python scripts/voice_lint.py`
- `python scripts/spec_check.py`
- `python scripts/validate_release_event.py`
