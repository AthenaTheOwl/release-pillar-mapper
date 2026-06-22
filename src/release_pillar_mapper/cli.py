from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from release_pillar_mapper.io import find_event_path, write_json
from release_pillar_mapper.model import build_impact_map, load_registries
from release_pillar_mapper.render import render_report
from release_pillar_mapper.schema import Claim, ReleaseEvent, load_release_event
from release_pillar_mapper.scoring import evaluate_significance, load_significance_config


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
