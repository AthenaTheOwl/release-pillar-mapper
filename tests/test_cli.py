from __future__ import annotations

from pathlib import Path

from release_mapper.cli import main


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
