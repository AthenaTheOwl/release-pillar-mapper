# System Map

## Components

- `release_mapper.schema` validates release events and impact maps.
- `release_mapper.significance` applies local threshold rules.
- `release_mapper.mapper` builds three impact axes from config registries.
- `release_mapper.render` writes deterministic Markdown with typed front matter.
- `release_mapper.cli` exposes the local workflow.

## Data Flow

1. The user creates or checks in a release event JSON file.
2. The validator checks the event shape and source-anchored claims.
3. The significance evaluator reads `config/significance.yaml` and returns a yes/no decision with a reason.
4. The mapper compares event text with registry tags and builds repo, brief, and pillar impacts.
5. The renderer writes `releases/<release_id>.md`.

## Trust Boundary

The CLI treats release-event claims as user-supplied evidence. It does
not fetch web pages, quote vendor copy, or rewrite claims from remote
sources. The checked-in report is a structured decision artifact.

## Local Gate Surface

- `uv run pytest`
- `python scripts/voice_lint.py`
- `python scripts/spec_check.py`
- `python scripts/validate_release_event.py`
