# First PR after the scaffold

Title: `feat: release-event + impact-map schemas, three config registries`

## Scope

This PR lands all three schemas, all three config registries (with
placeholder rows), the Pydantic mirrors, the worked example release
file, and the schema round-trip tests. No CLI logic yet; no
significance evaluator yet; no renderer yet.

## Files added

- `schemas/release_event.schema.json` — R-RPM-002. Required fields:
  `id`, `kind`, `source_url`, `vendor`, `headline`, `claims[]` (min
  1), `ingested_at`. `kind` enum: `model`, `eval`, `dataset`,
  `framework`.
- `schemas/impact_map.schema.json` — R-RPM-003. Required:
  `release_id`, plus the three impact arrays (each may be empty
  individually but at least one must be non-empty in total).
  Each impact entry: `target_id`, `direction`, `confidence`,
  `evidence_anchor`, `recommended_action`.
- `schemas/backscore.schema.json` — R-RPM-007. Schema only; no
  consumer in this PR.
- `src/release_mapper/__init__.py`
- `src/release_mapper/schema.py` — Pydantic mirrors.
- `config/significance.yaml` — initial rules per R-RPM-004
  (vendor whitelist, kind+headline regex set, eval-id whitelist,
  `--force` flag mention).
- `config/repo_index.yaml` — 3-5 placeholder repo entries with
  `slug`, `current_thesis_one_liner`, `coupled_pillars`.
- `config/brief_corpus.yaml` — 3-5 placeholder brief entries.
- `config/thesis_pillars.yaml` — 3-5 placeholder pillars.
- `examples/_events/2026-04-EXAMPLE.json` — one example release
  event JSON.
- `examples/2026-04-EXAMPLE-release.md` — R-RPM-008. One model
  release, two repo impacts, one brief impact, two pillar impacts.
  All `target_id` values are placeholders.
- `tests/test_release_event_schema.py` — required-fields,
  enum-validation, and id-format tests.
- `tests/test_impact_map_schema.py` — round-trip + the at-least-
  one-impact-total rule.
- `pyproject.toml` — `pydantic`, `pyyaml`, `jsonschema`, `pytest`,
  `ruff`.

## Files changed

None — this is the first PR after the scaffold.

## Verification

```bash
uv sync
uv run pytest -v
uv run python -c "import json, jsonschema; \
  [jsonschema.Draft202012Validator.check_schema(json.load(open(f))) \
   for f in ['schemas/release_event.schema.json', \
             'schemas/impact_map.schema.json', \
             'schemas/backscore.schema.json']]"
```

All commands exit zero. `pytest -v` shows at least 8 passing tests.

## What this PR does not do

- No CLI subcommands wired (PR 2).
- No significance evaluator (PR 2).
- No renderer (PR 2).
- No voice_lint copy (PR 3).
- No real vendor URL ingestion (later spec).

## Review checklist

- [ ] All three JSON Schemas validate against Draft 2020-12.
- [ ] Pydantic mirrors do not drift from the schemas (round-trip
      tests pin this).
- [ ] Significance config uses rules, not weights (per design.md).
- [ ] Example release uses placeholder `target_id` values that match
      ids actually present in the three placeholder config
      registries.
- [ ] No real vendor headline is paraphrased in a way that could be
      confused for a quote.
