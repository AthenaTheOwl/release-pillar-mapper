# Spec 0001 — Design

## Shape

Two schemas (release event, impact map) plus three config registries
plus a CLI that takes a release URL and emits a Markdown file.

```
schemas/
  release_event.schema.json   # R-RPM-002
  impact_map.schema.json      # R-RPM-003
  backscore.schema.json       # R-RPM-007
config/
  significance.yaml           # R-RPM-004
  repo_index.yaml             # R-RPM-005
  brief_corpus.yaml           # R-RPM-005
  thesis_pillars.yaml         # R-RPM-005
src/release_mapper/
  cli.py
  schema.py                   # Pydantic mirrors
  ingest.py                   # release URL -> release_event
  significance.py             # threshold filter
  mapper.py                   # three-axis impact map
  render.py                   # impact_map -> Markdown
releases/                     # one file per significant release (R-RPM-006)
  _rejected.jsonl             # filtered-out releases
examples/
  2026-04-EXAMPLE-release.md  # R-RPM-008
scripts/
  voice_lint.py
  spec_check.py
tests/
  test_release_event_schema.py
  test_impact_map_schema.py
  test_significance.py
  test_render_roundtrip.py
```

## Data flow

1. User runs `release-mapper ingest --url <url>`. The ingest step
   does not crawl; it captures `url`, `vendor` from a small whitelist,
   `headline`, and user-pasted `claims[]`. The output is a typed
   release event JSON in `releases/_events/<id>.json`.
2. `release-mapper significance --id <id>` evaluates the threshold
   rules. Failing events go to `releases/_rejected.jsonl`.
3. `release-mapper map --id <id>` reads the three config registries
   and emits one `releases/<id>.md` with three impact axes.
4. The user edits the rendered Markdown by hand to refine
   `recommended_action` per impact. The front matter round-trips
   through the impact_map schema so later edits stay typed.

## Why three axes and not one synthesis

The user already runs three coupled systems and the recurring
decision shape differs per axis: repo work uses a sprint cadence,
brief items use a publication cadence, investing pillars use a
position-management cadence. A single "impact score" would collapse
three distinct decision queues into one number that none of the
three downstream systems could act on.

## Significance threshold

`config/significance.yaml` is rules, not weights. Examples of rules
v0 supports:

- vendor in `{OpenAI, Anthropic, Google, Meta, xAI, DeepSeek}`.
- kind == `model` AND headline matches one of N regexes about
  frontier-class capability.
- kind == `eval` AND eval-id in a curated list (SWE-bench, GPQA,
  ARC-AGI, etc.).
- explicit `--force` flag for the rare borderline case.

The rules emit a yes/no plus a reason; the reason is logged.

## What is not in spec 0001

- The back-scorer itself (spec 0003).
- Auto-fetch from arxiv / vendor blogs (spec 0004).
- Cross-release temporal analysis (spec 0005).
- Publishing the mapping anywhere (this repo writes Markdown; the user
  consumes it).

Spec 0002 lands the actual `ingest / significance / map / render`
pipeline against one real release.
