# Spec 0001 — Foundation

## R-RPM-001 — repo scaffold
Repo at `e:/claude_code/random-apps/release-pillar-mapper`. MIT license.
README, AGENTS.md, LICENSE, .gitignore at the root.

## R-RPM-002 — release event schema
`schemas/release_event.schema.json` defines a typed release: `id`
(`YYYY-MM-DD-<slug>`), `kind` (model / eval / dataset / framework),
`source_url`, `vendor`, `headline`, `claims[]` (each with `text` and
`source_anchor`), `ingested_at`.

## R-RPM-003 — impact map schema
`schemas/impact_map.schema.json` defines the three-axis output:
`release_id`, `repo_impacts[]`, `brief_impacts[]`, `pillar_impacts[]`.
Each impact entry carries `target_id`, `direction`
(strengthens / weakens / invalidates / confirms / refutes / unchanged),
`confidence` (low / medium / high), `evidence_anchor`,
`recommended_action`.

## R-RPM-004 — significance threshold
`config/significance.yaml` defines rules for what counts as worth
mapping (vendor tier, parameter delta, eval delta, framework adoption
proxy). A release that fails the threshold is logged in
`releases/_rejected.jsonl` and does not get a Markdown file.

## R-RPM-005 — three config registries
- `config/repo_index.yaml` lists portfolio repos with `slug`,
  `current_thesis_one_liner`, `coupled_pillars[]`.
- `config/brief_corpus.yaml` lists published brief items by `id`,
  `url`, `topic_tags[]`.
- `config/thesis_pillars.yaml` lists active pillars from
  thesis-pillar-tracker by `id`, `headline`, `current_verdict`.

## R-RPM-006 — release file naming
Output lives at `releases/<release_id>.md`. The Markdown file embeds
its own structured front matter that round-trips through the
impact_map schema.

## R-RPM-007 — back-scoring schema
`schemas/backscore.schema.json` defines a back-scoring record: for
each prior impact entry, `realized_direction`, `lag_days`, `notes`.
v0 ships the schema only; the back-scorer ships in spec 0003.

## R-RPM-008 — example release file
`examples/2026-04-EXAMPLE-release.md` ships a worked example: one
release of `kind: model`, two repo impacts, one brief impact, two
pillar impacts. All target ids are placeholders.

## R-RPM-009 — voice lint stub
`scripts/voice_lint.py` (portfolio copy) runs over `releases/*.md`.

## R-RPM-010 — spec check
`scripts/spec_check.py` confirms every `R-RPM-NNN` referenced in
`design.md` and `tasks.md` is defined here.

## R-RPM-011 — out-of-scope guard
v0 does not fetch arbitrary URLs, does not run model evals, does not
auto-publish anywhere. Inputs are user-pasted release URLs plus the
three config registries.
