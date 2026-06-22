# Spec 0002 Design Ledger

## Decisions

- Use dataclasses and explicit validators for v0.1 so the CLI works
  without runtime third-party dependencies.
- Store `.yaml` config files as JSON-compatible YAML until the repo has
  enough config complexity to justify a parser dependency.
- Keep report front matter limited to the impact map so schema
  round-tripping stays direct.
- Include unchanged impacts for configured targets. This keeps the
  report complete and makes a no-action recommendation explicit.

## Deferred

- URL fetching and source extraction.
- Back-scoring commands.
- Per-target action templating beyond the registry defaults.
