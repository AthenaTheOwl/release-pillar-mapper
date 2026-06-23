from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from release_pillar_mapper.io import find_event_path, write_json
from release_pillar_mapper.model import build_impact_map, load_registries
from release_pillar_mapper.render import render_report
from release_pillar_mapper.schema import (
    Claim,
    Impact,
    ImpactMap,
    ReleaseEvent,
    load_release_event,
)
from release_pillar_mapper.scoring import evaluate_significance, load_significance_config


# project root: src/release_pillar_mapper/cli.py -> parents[2]
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

# rank weights: active impacts above "unchanged", high confidence above low
_DIRECTION_RANK = {
    "invalidates": 5,
    "refutes": 5,
    "weakens": 4,
    "strengthens": 3,
    "confirms": 3,
    "unchanged": 0,
}
_CONFIDENCE_RANK = {"high": 3, "medium": 2, "low": 1}


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    return args.func(args)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="release-mapper")
    subcommands = parser.add_subparsers(dest="command")

    ingest = subcommands.add_parser("ingest", help="write a local release event JSON file")
    ingest.add_argument("--id", required=True)
    ingest.add_argument("--kind", choices=["model", "eval", "dataset", "framework"], required=True)
    ingest.add_argument("--source-url", required=True)
    ingest.add_argument("--vendor", required=True)
    ingest.add_argument("--headline", required=True)
    ingest.add_argument("--ingested-at", required=True)
    ingest.add_argument(
        "--claim",
        action="append",
        required=True,
        help="claim text and source anchor separated by ||",
    )
    ingest.add_argument("--output")
    ingest.set_defaults(func=_ingest)

    validate = subcommands.add_parser("validate-event", help="validate release event JSON")
    validate.add_argument("paths", nargs="+")
    validate.set_defaults(func=_validate_event)

    validate_default = subcommands.add_parser("validate", help="validate bundled v0.1 artifact")
    validate_default.set_defaults(func=_validate_default)

    significance = subcommands.add_parser("significance", help="evaluate significance rules")
    _event_args(significance)
    significance.add_argument("--config", default="config/significance.yaml")
    significance.add_argument("--force", action="store_true")
    significance.set_defaults(func=_significance)

    map_command = subcommands.add_parser("map", help="build impact map JSON")
    _event_args(map_command)
    map_command.add_argument("--output")
    map_command.set_defaults(func=_map)

    render = subcommands.add_parser("render", help="render Markdown report")
    _event_args(render)
    render.add_argument("--output")
    render.set_defaults(func=_render)

    show = subcommands.add_parser(
        "show",
        help="print a ranked, readable summary of the committed impact map (no args, read-only)",
    )
    show.set_defaults(func=_show)

    return parser


def _event_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--event")
    group.add_argument("--id")


def _ingest(args: argparse.Namespace) -> int:
    claims = tuple(_parse_claim(raw) for raw in args.claim)
    event = ReleaseEvent(
        id=args.id,
        kind=args.kind,
        source_url=args.source_url,
        vendor=args.vendor,
        headline=args.headline,
        claims=claims,
        ingested_at=args.ingested_at,
    )
    ReleaseEvent.from_dict(event.to_dict())
    output = Path(args.output) if args.output else Path("releases") / "_events" / f"{event.id}.json"
    write_json(output, event.to_dict())
    print(f"wrote {output}")
    return 0


def _validate_event(args: argparse.Namespace) -> int:
    for raw_path in args.paths:
        event = load_release_event(Path(raw_path))
        print(f"OK {event.id}")
    return 0


def _validate_default(_args: argparse.Namespace) -> int:
    events = sorted(Path("examples/_events").glob("*.json"))
    reports = sorted(Path("reports").glob("*.jsonl"))
    if not events:
        raise SystemExit("missing examples/_events/*.json")
    if not reports:
        raise SystemExit("missing reports/*.jsonl")
    for event_path in events:
        load_release_event(event_path)
    for report_path in reports:
        if not report_path.read_text(encoding="utf-8").strip():
            raise SystemExit(f"empty report: {report_path}")
    print(f"OK {len(events)} release event(s), {len(reports)} report artifact(s)")
    return 0


def _significance(args: argparse.Namespace) -> int:
    event = _load_event_from_args(args)
    config = load_significance_config(Path(args.config))
    result = evaluate_significance(event, config, force=args.force)
    print(result.to_cli_line())
    return 0 if result.accepted else 1


def _map(args: argparse.Namespace) -> int:
    event = _load_event_from_args(args)
    impact_map = build_impact_map(event, load_registries(Path.cwd()))
    payload = json.dumps(impact_map.to_dict(), indent=2, sort_keys=True)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n", encoding="utf-8")
        print(f"wrote {output}")
    else:
        print(payload)
    return 0


def _render(args: argparse.Namespace) -> int:
    event = _load_event_from_args(args)
    impact_map = build_impact_map(event, load_registries(Path.cwd()))
    rendered = render_report(event, impact_map)
    output = Path(args.output) if args.output else Path("releases") / f"{event.id}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"wrote {output}")
    return 0


def _load_event_from_args(args: argparse.Namespace) -> ReleaseEvent:
    if args.event:
        return load_release_event(Path(args.event))
    return load_release_event(find_event_path(args.id, Path.cwd()))


def _parse_claim(raw: str) -> Claim:
    if "||" not in raw:
        raise ValueError("--claim must use 'claim text||source_anchor'")
    text, source_anchor = raw.split("||", 1)
    return Claim(text=text.strip(), source_anchor=source_anchor.strip())


def _impact_rank(impact: Impact) -> tuple[int, int]:
    return (
        _DIRECTION_RANK.get(impact.direction, 1),
        _CONFIDENCE_RANK.get(impact.confidence, 0),
    )


def _ranked_rows(impact_map: ImpactMap) -> list[tuple[str, Impact]]:
    rows: list[tuple[str, Impact]] = []
    for axis, impacts in (
        ("repo", impact_map.repo_impacts),
        ("brief", impact_map.brief_impacts),
        ("pillar", impact_map.pillar_impacts),
    ):
        for impact in impacts:
            rows.append((axis, impact))
    rows.sort(key=lambda row: _impact_rank(row[1]), reverse=True)
    return rows


def load_committed_impact_map(root: Path) -> tuple[ImpactMap, Path]:
    reports = sorted(root.glob("reports/*.jsonl"))
    if not reports:
        raise FileNotFoundError(f"no committed report found under {root / 'reports'}")
    report_path = reports[0]
    records = [
        json.loads(line)
        for line in report_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    impact_record = next(
        (rec for rec in records if rec.get("artifact_type") == "impact_map"),
        records[0] if records else None,
    )
    if impact_record is None:
        raise ValueError(f"{report_path} contains no impact_map record")
    return ImpactMap.from_dict(impact_record), report_path


def render_show(impact_map: ImpactMap, report_path: Path) -> str:
    rows = _ranked_rows(impact_map)
    active = [row for row in rows if row[1].direction != "unchanged"]
    quiet = [row for row in rows if row[1].direction == "unchanged"]

    lines: list[str] = []
    lines.append(f"release: {impact_map.release_id}")
    lines.append(f"source : {report_path.name}")
    lines.append(
        f"targets: {len(rows)} mapped  |  {len(active)} actionable  |  {len(quiet)} left unchanged"
    )
    lines.append("")

    header = f"{'#':>2}  {'axis':<6}  {'target':<24}  {'direction':<12}  {'conf':<6}  action"
    lines.append(header)
    lines.append("-" * len(header))
    for index, (axis, impact) in enumerate(rows, start=1):
        action = impact.recommended_action
        if len(action) > 64:
            action = action[:61] + "..."
        lines.append(
            f"{index:>2}  {axis:<6}  {impact.target_id:<24}  "
            f"{impact.direction:<12}  {impact.confidence:<6}  {action}"
        )
    lines.append("")

    if active:
        axis, top = active[0]
        lines.append(
            f"top finding: {top.target_id} ({axis}) {top.direction} "
            f"[{top.confidence}] -> {top.recommended_action}"
        )
    else:
        lines.append("top finding: no actionable impacts; every target was left unchanged.")
    return "\n".join(lines)


def _show(_args: argparse.Namespace) -> int:
    impact_map, report_path = load_committed_impact_map(_PROJECT_ROOT)
    print(render_show(impact_map, report_path))
    return 0
