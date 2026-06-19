# Frontier Release Pillar Mapper

Each frontier model release (or eval / dataset / framework release) is mapped
against three downstream artifacts the user already maintains: the repo
portfolio, the published brief corpus, and the investing thesis pillars.
One typed release event, three impact maps, one decision queue.

## What this is

A frontier release lands. Within hours, this repo emits a single
`releases/<release_id>.md` containing:

1. Which portfolio repos the release strengthens, invalidates, or leaves
   unchanged — with a recommended action per repo.
2. Which already-published brief items the release confirms or refutes —
   with a recommended follow-up (correction, note, leave alone).
3. Which investing thesis pillars the release touches — with a
   recommended action (trim, hedge, add, hold).

The mapper's confidence per axis is tuned by back-scoring each release's
predictions against subsequent reality. Releases below a configurable
significance threshold do not get mapped; release-noise floods the
system otherwise.

## Status

v0 scaffold. No mapping engine, no ingestion, no back-scoring. Spec 0001
names the event schema, the three downstream impact schemas, the
significance threshold, and the gates that land in spec 0002.

## How to run

Placeholder. Spec 0002 will ship the CLI:

```bash
uv run release-mapper ingest --url https://openai.com/blog/...
uv run release-mapper map --release-id 2026-07-15-gpt-X
uv run release-mapper backscore --release-id 2026-04-01-claude-Y
```

For now read `specs/0001-foundation/` and `docs/first-pr.md`.

## Layout

```
.
├── AGENTS.md
├── LICENSE
├── README.md
├── docs/
│   └── first-pr.md
└── specs/
    └── 0001-foundation/
        ├── acceptance.md
        ├── design.md
        ├── requirements.md
        └── tasks.md
```

Planned directories named in the spec:

- `releases/` — one Markdown file per significant release.
- `src/release_mapper/` — schema, ingest, mapper, back-scoring.
- `config/`
  - `repo_index.yaml` — portfolio repos + their current theses.
  - `brief_corpus.yaml` — refs into the brief publication repo.
  - `thesis_pillars.yaml` — refs into thesis-pillar-tracker.
  - `significance.yaml` — threshold rules for what counts as a release.
- `eval/` — back-scoring scripts.

## Why this exists

The user runs three coupled systems: a build portfolio, a brief
publication pipeline, and an investing book with explicit theses. Every
frontier release touches some subset of all three. Today those impacts
are absorbed as ambient news. This repo converts each release into a
typed event with three explicit downstream maps.

## License

MIT. See `LICENSE`.
