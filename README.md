# release-pillar-mapper

A frontier model ships on a Tuesday. By Wednesday the news has been absorbed as
mood. This repo refuses the mood: it turns one release into nine ranked rows that
each say which thing you own it touches, which direction, and what to do about it.

## What it does

You run three coupled systems at once — a build portfolio, a brief corpus you've
already published, and an investing book with named thesis pillars. Every release
nudges some subset of all three, and the nudges arrive as ambient news that's gone
by Friday. Nothing gets written down. Nothing gets revisited when the claim turns
out wrong.

This takes one typed release event and scores it against three local registries:
which repos it strengthens, invalidates, or leaves alone; which already-published
briefs it confirms or refutes; which pillars it touches. Each row carries a
direction, a confidence, and a recommended action — add a scenario, append a
sentence, keep the hedge. Actionable rows sort above the ones that change nothing,
because the unchanged rows are the ones you want to skip. Releases below the
significance threshold in `config/significance.yaml` never get mapped; without that
gate, release-noise floods the queue and every Tuesday looks urgent.

It does not fetch the web. Release claims are treated as user-supplied evidence
with source anchors — the tool maps what you checked in, it doesn't go quote vendor
copy and pretend it's fact.

## Try it

No arguments, read-only, offline. It reads the committed report and ranks it:

```bash
python -m release_pillar_mapper show
```

```
release: 2026-04-01-example-frontier-agent-model
source : 2026-04-01-example-frontier-agent-model.jsonl
targets: 9 mapped  |  8 actionable  |  1 left unchanged

 #  axis    target                    direction     conf    action
------------------------------------------------------------------
 1  repo    agent-runtime-bench       strengthens   medium  Add one scenario that measures plan repair cost under long-ho...
 2  repo    portfolio-signal-board    strengthens   medium  Create a follow-up card for agent-infrastructure exposure and...
 3  brief   brief-agent-cost-curves   confirms      medium  Add a dated note on lower-cost computer-use traces.
 4  brief   brief-eval-bottlenecks    confirms      medium  Append one sentence distinguishing benchmark gains from produ...
 5  brief   brief-infra-margin        confirms      medium  Leave the current margin framing in place and review after th...
 6  pillar  agent-economics           strengthens   medium  Hold the pillar and add one monitoring item for successful mu...
 7  pillar  eval-infrastructure       strengthens   medium  Add one due-diligence question about release-specific benchma...
 8  pillar  infra-consolidation       strengthens   medium  Keep the hedge and recheck exposure after pricing and context...
 9  repo    brief-claim-ledger        unchanged     low     Leave brief-claim-ledger unchanged; review only if follow-on ...
```

Ranked with the actionable impacts first (`invalidates`/`refutes` above
`strengthens`/`confirms` above `unchanged`, ties broken by confidence), then a
one-line top finding. The bottom row is the work you get to not do.

## Live demo

The same impact map as a page you can poke. Pick which axes to show
(repo / brief / pillar), watch the ranked table, the actionable-vs-unchanged
counts, and the top finding. It reads the committed `reports/*.jsonl` directly —
no network, no secrets.

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Deploy on Streamlit Community Cloud: New app -> repo
`AthenaTheOwl/release-pillar-mapper`, branch `main`, main file
`streamlit_app.py`.

<!-- live-url: https://<your-app>.streamlit.app -->

## How it connects

The three registries it scores against aren't hypothetical — they're the other
repos in the portfolio. This is the thing that watches all of them at once:

- [thesis-pillar-tracker](https://github.com/AthenaTheOwl/thesis-pillar-tracker) —
  the investing pillars this mapper reads from `config/thesis_pillars.yaml` and
  recommends trims and hedges against.
- [ai-field-brief](https://github.com/AthenaTheOwl/ai-field-brief) — the published
  brief corpus a release can confirm or refute, with a correction hook per item.
- [portfolio-manifest](https://github.com/AthenaTheOwl/portfolio-manifest) — the
  build portfolio whose repos get the strengthens / invalidates / unchanged verdict.

## Run it in full

Validate the bundled v0.1 artifact first:

```bash
python -m release_pillar_mapper validate
```

Then walk the canonical example release from event to rendered Markdown:

```bash
python -m release_pillar_mapper validate-event examples/_events/2026-04-01-example-frontier-agent-model.json
python -m release_pillar_mapper significance --id 2026-04-01-example-frontier-agent-model
python -m release_pillar_mapper render --id 2026-04-01-example-frontier-agent-model --output releases/2026-04-01-example-frontier-agent-model.md
```

The v0.1 artifact is `reports/2026-04-01-example-frontier-agent-model.jsonl`.

## Layout

```
release_pillar_mapper/   schema, scoring, significance, model, mapper, render, cli
config/                  repo_index, brief_corpus, thesis_pillars, significance.yaml
schemas/                 release_event, impact_map, backscore JSON schemas
examples/_events/        the canonical release event JSON
reports/                 the committed impact-map artifact (jsonl)
releases/                one rendered Markdown file per significant release
scripts/  specs/  docs/  tests/
```

## License

MIT. See `LICENSE`.
