# Spec 0002 - Runnable v0.1

## R-RPM-012 - product and status docs
The repo ships `docs/product-brief.md`, `docs/system-map.md`, and
`STATUS.md`. `STATUS.md` uses the exact H2 headings required by the
factory contract.

## R-RPM-013 - package metadata
`pyproject.toml` declares the `release-pillar-mapper` project, the
`release-mapper` console script, `[dependency-groups]`, and `[tool.uv]`
with `package = true`.

## R-RPM-014 - local validation
The package validates release events and impact maps without network
access or runtime third-party dependencies.

## R-RPM-015 - deterministic report rendering
The renderer emits `releases/<release_id>.md` with typed front matter
that round-trips through the impact-map validator.

## R-RPM-016 - gate scripts
The repo ships `scripts/voice_lint.py`, `scripts/spec_check.py`, and
`scripts/validate_release_event.py`.

## R-RPM-017 - checked-in report artifact
At least one report exists under `releases/` and is generated from a
checked-in example event.

## R-RPM-018 - tests
Tests cover schema validation, significance, rendering, CLI entry
points, and the `STATUS.md` section contract.
