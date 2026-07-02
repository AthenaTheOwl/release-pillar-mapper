from __future__ import annotations

from pathlib import Path

import pytest

from release_mapper.cli import main
from release_pillar_mapper.cli import _ranked_rows, render_show
from release_mapper.schema import Impact, ImpactMap


ROOT = Path(__file__).resolve().parents[1]
EVENT_PATH = ROOT / "examples" / "_events" / "2026-04-01-example-frontier-agent-model.json"


def test_cli_validate_event(capsys) -> None:
    assert main(["validate-event", str(EVENT_PATH)]) == 0

    out = capsys.readouterr().out
    assert "OK 2026-04-01-example-frontier-agent-model" in out


def test_cli_validate_default_artifact(capsys) -> None:
    assert main(["validate"]) == 0

    out = capsys.readouterr().out
    assert "release event(s)" in out
    assert "report artifact(s)" in out


def test_cli_significance_accepts(capsys) -> None:
    assert main(["significance", "--event", str(EVENT_PATH), "--config", str(ROOT / "config" / "significance.yaml")]) == 0

    out = capsys.readouterr().out
    assert out.startswith("yes:")


def test_cli_render_writes_report() -> None:
    output = ROOT / "tests" / "_tmp_report.md"

    try:
        assert main(["render", "--event", str(EVENT_PATH), "--output", str(output)]) == 0

        assert output.exists()
        assert "## Pillar impacts" in output.read_text(encoding="utf-8")
    finally:
        output.unlink(missing_ok=True)


# A fixed impact map whose ordering exercises every ranking weight:
#   - "invalidates" and "weakens" rows must outrank "strengthens" (direction
#     priority: invalidates/refutes > weakens > strengthens/confirms > unchanged)
#   - two "strengthens" rows with high vs medium confidence pin the tie-break
_RANKING_MAP = ImpactMap(
    release_id="2026-04-01-example-frontier-agent-model",
    repo_impacts=(
        Impact("repo-strengthens-med", "strengthens", "medium", "a#1", "review adapter"),
        Impact("repo-strengthens-high", "strengthens", "high", "b#1", "ship adapter"),
    ),
    brief_impacts=(
        Impact("brief-invalidated", "invalidates", "high", "x#1", "rewrite section"),
        Impact("brief-weakened", "weakens", "high", "w#1", "flag caveat"),
    ),
    pillar_impacts=(
        Impact("pillar-quiet", "unchanged", "low", "z#1", "no action"),
    ),
)


def test_ranked_rows_pins_direction_and_confidence_order() -> None:
    order = [(axis, impact.target_id) for axis, impact in _ranked_rows(_RANKING_MAP)]
    assert order == [
        ("brief", "brief-invalidated"),  # invalidates outranks weakens/strengthens
        ("brief", "brief-weakened"),  # weakens outranks strengthens
        ("repo", "repo-strengthens-high"),  # high confidence tie-break wins
        ("repo", "repo-strengthens-med"),
        ("pillar", "pillar-quiet"),  # unchanged ranked last
    ]


def test_render_show_golden_master() -> None:
    rendered = render_show(_RANKING_MAP, Path("reports/impact.jsonl"))
    assert rendered == (
        "release: 2026-04-01-example-frontier-agent-model\n"
        "source : impact.jsonl\n"
        "targets: 5 mapped  |  4 actionable  |  1 left unchanged\n"
        "\n"
        " #  axis    target                    direction     conf    action\n"
        "------------------------------------------------------------------\n"
        " 1  brief   brief-invalidated         invalidates   high    rewrite section\n"
        " 2  brief   brief-weakened            weakens       high    flag caveat\n"
        " 3  repo    repo-strengthens-high     strengthens   high    ship adapter\n"
        " 4  repo    repo-strengthens-med      strengthens   medium  review adapter\n"
        " 5  pillar  pillar-quiet              unchanged     low     no action\n"
        "\n"
        "top finding: brief-invalidated (brief) invalidates [high] -> rewrite section"
    )


def test_cli_validate_event_missing_file_exits_clean() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["validate-event", "does/not/exist.json"])
    message = str(excinfo.value)
    assert "exist.json" in message
    assert "Traceback" not in message


def test_cli_significance_unknown_id_exits_clean() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["significance", "--id", "no-such-event"])
    assert "no-such-event" in str(excinfo.value)


def test_cli_show_prints_ranked_summary(capsys) -> None:
    assert main(["show"]) == 0

    out = capsys.readouterr().out
    # headline + the committed release id
    assert "release: 2026-04-01-example-frontier-agent-model" in out
    assert "top finding:" in out
    # ranking puts an actionable impact (not "unchanged") at row 1
    first_row = next(line for line in out.splitlines() if line.lstrip().startswith("1  "))
    assert "unchanged" not in first_row
    # the "unchanged" target is ranked last, not first
    lines = out.splitlines()
    unchanged_line = next(line for line in lines if "unchanged" in line and "left unchanged" not in line)
    assert lines.index(unchanged_line) > lines.index(first_row)
