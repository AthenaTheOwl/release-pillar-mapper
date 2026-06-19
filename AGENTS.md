# AGENTS.md — release-pillar-mapper

Operating contract for AI agents in this repo. Same conventions as the
rest of the portfolio.

## What this repo is

An event-driven mapper. Input: one frontier release (model, eval,
dataset, framework). Output: a single typed Markdown file with three
impact axes — repos, brief items, investing pillars — plus a per-axis
recommended action.

This is not a news aggregator and not a generic "AI tracker". It is the
three-way mapping function that only makes sense because the user runs
all three downstream systems.

## Voice constraints

- No marketing words. The release-mapping write-ups are evidence-led,
  not breathless. The portfolio voice spec banlist applies.
- No antithetical reversals as a structural device.
- Plain assertions per axis. "This release strengthens repo X because Y
  is now cheaper" rather than "this release is a paradigm shift".
- Recommended actions are concrete enough to act on or reject. Vague
  recommendations are a gate failure.

## Roles in tasks

| Role | What they do |
|---|---|
| `release-curator` | Decides which releases pass the significance threshold |
| `repo-axis` | Maps the release across `config/repo_index.yaml` |
| `brief-axis` | Maps the release across `config/brief_corpus.yaml` |
| `pillar-axis` | Maps the release across `config/thesis_pillars.yaml` |
| `back-scorer` | Reopens past mappings; scores predictions vs reality |

Roles are vocabulary, not running services in v0.

## Gates (will land in spec 0002)

```bash
uv run pytest
python scripts/voice_lint.py
python scripts/spec_check.py
python scripts/validate_release_event.py
```

## Out of scope

- Reading every model release. The significance threshold filters
  ruthlessly. Tiny version bumps do not earn a mapping.
- Live alerting. The repo emits Markdown; the user reads it in their
  normal review cadence.
- Cross-user portfolios. The three downstream systems are the user's.
- Generic impact-analysis frameworks. The schema names specific repos,
  brief items, and pillars.
