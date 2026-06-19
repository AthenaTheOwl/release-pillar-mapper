# Spec 0001 — Tasks

Ordered for the first 2-3 PRs.

## PR 1 — schemas and config registries

- [ ] Write `schemas/release_event.schema.json` (R-RPM-002).
- [ ] Write `schemas/impact_map.schema.json` (R-RPM-003).
- [ ] Write `schemas/backscore.schema.json` (R-RPM-007).
- [ ] Write `src/release_mapper/schema.py` Pydantic mirrors.
- [ ] Write `config/significance.yaml` with rules (R-RPM-004).
- [ ] Write `config/repo_index.yaml` with placeholder entries
      (R-RPM-005).
- [ ] Write `config/brief_corpus.yaml` with placeholder entries.
- [ ] Write `config/thesis_pillars.yaml` with placeholder entries.
- [ ] Write `examples/2026-04-EXAMPLE-release.md` (R-RPM-008).
- [ ] Write `tests/test_release_event_schema.py` and
      `tests/test_impact_map_schema.py`.

## PR 2 — significance + render

- [ ] Write `src/release_mapper/significance.py`.
- [ ] Write `src/release_mapper/render.py` (impact_map -> Markdown
      with round-trippable front matter, R-RPM-006).
- [ ] Write `tests/test_significance.py` and
      `tests/test_render_roundtrip.py`.
- [ ] CLI wires `release-mapper significance --id` and
      `release-mapper render --id`.

## PR 3 — gates and one real worked example

- [ ] Copy `scripts/voice_lint.py` from portfolio (R-RPM-009).
- [ ] Write `scripts/spec_check.py` (R-RPM-010).
- [ ] Write `pyproject.toml`.
- [ ] Add one real release id (still placeholder claims) end-to-end
      through ingest -> significance -> map -> render.
- [ ] Confirm all gates exit zero.
