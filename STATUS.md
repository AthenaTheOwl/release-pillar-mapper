# Release Pillar Mapper Status

## Current state
- v0.1 ships a local Python CLI for validating release events, checking significance, mapping configured targets, and rendering a Markdown report.
- The repo has schemas, JSON-compatible YAML registries, product docs, system docs, spec 0002, tests, gate scripts, and one checked-in sample report artifact.
- The renderer writes typed front matter that round-trips through the impact-map validator.

## Known limits
- Release events are local JSON inputs; the CLI does not fetch or summarize vendor pages.
- The mapper uses explicit registry keywords and default actions; it does not infer novel target relationships.
- Back-scoring is represented by a schema only. The scorer workflow remains queued for a later spec.

## Next feature queue
- Add an interactive ingest flow that prompts for release claims and source anchors.
- Add per-target action templates that can vary by release kind.
- Add a back-score command that compares prior recommendations with realized repo, brief, and pillar outcomes.

- Resolve factory defect: missing PRODUCT_BRIEF.md,SYSTEM_MAP.md
- Resolve factory defect: missing reports/*.jsonl
- Resolve factory defect: PRODUCT_BRIEF.md is required for active repos
- Resolve factory defect: SYSTEM_MAP.md is required for active repos
- Resolve factory defect: expected file 'PRODUCT_BRIEF.md' is missing
- Resolve factory defect: expected file 'SYSTEM_MAP.md' is missing
- Resolve factory defect: expected file 'release_pillar_mapper/cli.py' is missing
- Resolve factory defect: expected glob 'reports/*.jsonl' matched no files
- Resolve factory defect: module 'cli' declares source 'release_pillar_mapper/cli.py', but it is missing
- Resolve factory defect: module 'model' declares source 'release_pillar_mapper/model.py', but it is missing
- Resolve factory defect: module 'report' declares source 'release_pillar_mapper/scoring.py', but it is missing
- Resolve factory defect: claude_code review requested patch; inspect defect log
- Resolve factory defect: expected file 'release_pillar_mapper/cli.py' is missing
- Resolve factory defect: module 'cli' declares source 'release_pillar_mapper/cli.py', but it is missing
- Resolve factory defect: module 'model' declares source 'release_pillar_mapper/model.py', but it is missing
- Resolve factory defect: module 'report' declares source 'release_pillar_mapper/scoring.py', but it is missing
- Resolve factory defect: claude_code review requested patch; inspect defect log
