# Spec 0002 - Design

## Scope

Spec 0002 turns the scaffold into a runnable local data-report repo.
It implements the package and gate surface described by R-RPM-013
through R-RPM-018.

## Implementation Choice

The v0.1 runtime uses only the Python standard library. Config files
retain their `.yaml` names but use a JSON-compatible YAML subset, so
they can be parsed locally without adding a YAML dependency.

## CLI

The CLI exposes four commands:

- `validate-event <path>` validates a release event.
- `significance --event <path>` prints a threshold decision.
- `map --event <path>` prints an impact map as JSON.
- `render --event <path> --output <path>` writes a Markdown report.

`render --id <release_id>` also works for events stored in
`examples/_events/` or `releases/_events/`.

## Report Shape

The report front matter is the impact map. The Markdown body carries
the release source metadata plus three axis sections. Each impact entry
has direction, confidence, evidence anchor, and recommended action.

## Gates

R-RPM-016 gate scripts are small and repo-local:

- `voice_lint.py` scans release reports for banned phrasing.
- `spec_check.py` checks spec references, status headings, and packaging blocks.
- `validate_release_event.py` validates checked-in events.
