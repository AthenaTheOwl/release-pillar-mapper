# Spec 0001 — Acceptance

v0 is done when the following hold.

## Repo shape

- README, LICENSE, AGENTS.md, .gitignore at the root.
- `specs/0001-foundation/` complete (requirements / design / tasks /
  acceptance).
- `docs/first-pr.md` describes the next PR concretely.

## Commands

After PR 1-3 land:

```bash
uv run pytest
python scripts/voice_lint.py
python scripts/spec_check.py
python scripts/validate_release_event.py examples/_events/2026-04-EXAMPLE.json
python -m release_mapper render --id 2026-04-EXAMPLE
```

All five exit zero.

## Functional gates

- `examples/2026-04-EXAMPLE-release.md` validates against the
  impact_map schema and contains at least one impact entry on each
  of the three axes.
- `release-mapper significance --id 2026-04-EXAMPLE` returns yes
  with a logged reason from `config/significance.yaml`.
- `release-mapper render --id 2026-04-EXAMPLE` regenerates the
  Markdown identically to a freshly committed canonical version
  (rendering is deterministic).
- The front matter in the rendered file round-trips through the
  impact_map schema without loss.
- `spec_check.py` confirms every `R-RPM-NNN` reference is defined.

## Out of scope for v0 acceptance

- Real auto-ingest of vendor blog posts.
- Back-scoring against realized reality.
- Publishing anywhere.

Those land in later specs.
