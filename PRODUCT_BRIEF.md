# Product Brief

## Job

Release Pillar Mapper turns one significant frontier release into a
typed report for three downstream systems the user already runs:
portfolio repos, published brief items, and investing thesis pillars.

## User

The user reviews frontier AI releases and needs to decide whether a
release changes build priorities, published claims, or active thesis
exposure. The useful output is a small decision queue, not a feed.

## Inputs

- A release event JSON file with vendor, kind, source URL, headline,
  claims, and source anchors.
- `config/repo_index.yaml` with repo theses and tags.
- `config/brief_corpus.yaml` with brief IDs, URLs, and tags.
- `config/thesis_pillars.yaml` with active pillar IDs, verdicts, and tags.
- `config/significance.yaml` with threshold rules.

## Outputs

- A Markdown report under `releases/<release_id>.md`.
- A JSONL report row under `reports/<release_id>.jsonl`.
- Typed front matter that validates as an impact map.
- Plain action recommendations per repo, brief item, and pillar.

## v0.1 Success Criteria

- A release event can be validated from the command line.
- A release can be accepted or rejected by local significance rules.
- A report can be rendered deterministically from the event and registries.
- Tests and gate scripts run without network access.
