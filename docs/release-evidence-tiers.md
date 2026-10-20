# A release claim becomes a work order through a measured gap

Method update: October 18, 2026. Proposed experiments below are not reported as executed results.

The mapper already treats release events as checked-in evidence rather than fetching promotional copy. Preserve three evidence states when preparing those events: vendor claim, independently reproduced observation and local product result. Keep that record outside the release-event JSON: `schemas/release_event.schema.json` rejects undeclared keys on the event and on each claim, so an evidence-state field fails schema validation. A benchmark gain in the first state should not become a high-confidence repo improvement in the third.

A useful proposed mapping names the affected requirement and a bounded test. For example, a claim of better long-horizon repair can map to running one recovery scenario at a fixed tool and token budget. Record completion, failure type, cost per accepted result and configuration. Compare against the current model on the same cases.

If the release changes price, policy or tool permissions, map those assumptions separately from capability. Reuse unaffected brief and pillar mappings only when the premises behind them still hold. The registries do not record those premises yet, and an event cannot be marked withdrawn: `schemas/impact_map.schema.json` and `schemas/release_event.schema.json` reject undeclared keys, so premises and withdrawal status must be recorded outside those records until the schemas declare fields for them. A withdrawn vendor claim should then queue the dependent mappings for review while leaving the old event record readable. The output remains a proposal for a specific change, not permission to adopt a model or execute a financial action.
