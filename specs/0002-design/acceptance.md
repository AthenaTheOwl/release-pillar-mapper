# Spec 0002 - Acceptance

The v0.1 implementation is accepted when these commands exit zero:

```bash
uv run pytest
python scripts/voice_lint.py
python scripts/spec_check.py
python scripts/validate_release_event.py
```

Additional acceptance checks:

- `STATUS.md` has exactly these H2 headings: `Current state`,
  `Known limits`, and `Next feature queue`.
- `python -m release_mapper significance --event examples/_events/2026-04-01-example-frontier-agent-model.json` prints `yes`.
- `python -m release_mapper render --event examples/_events/2026-04-01-example-frontier-agent-model.json --output releases/2026-04-01-example-frontier-agent-model.md` can regenerate the checked-in report.
