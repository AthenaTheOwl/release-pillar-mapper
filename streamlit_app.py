"""release-pillar-mapper — live demo (Streamlit Community Cloud).

Reads the committed impact map under reports/*.jsonl and shows where one
frontier release lands across three downstream systems the user runs: the
repo portfolio, the published brief corpus, and the investing thesis pillars.
Each target gets a direction, a confidence, and a recommended action. No
network, no secrets — runs entirely off the committed report.

Deploy: Streamlit Community Cloud -> New app -> repo
AthenaTheOwl/release-pillar-mapper, branch main, main file streamlit_app.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

REPO = Path(__file__).resolve().parent
REPORTS = REPO / "reports"

_DIRECTION_RANK = {
    "invalidates": 5,
    "refutes": 5,
    "weakens": 4,
    "strengthens": 3,
    "confirms": 3,
    "unchanged": 0,
}
_CONFIDENCE_RANK = {"high": 3, "medium": 2, "low": 1}


def load_impact_map() -> tuple[dict, str]:
    files = sorted(REPORTS.glob("*.jsonl"))
    if not files:
        return {}, ""
    latest = files[-1]
    records = [
        json.loads(line)
        for line in latest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    impact = next(
        (r for r in records if r.get("artifact_type") == "impact_map"),
        records[0] if records else {},
    )
    return impact, latest.stem


def rows_for(impact: dict, axes: list[str]) -> list[dict]:
    out: list[dict] = []
    axis_key = {"repo": "repo_impacts", "brief": "brief_impacts", "pillar": "pillar_impacts"}
    for axis in axes:
        for item in impact.get(axis_key[axis], []):
            out.append({"axis": axis, **item})
    out.sort(
        key=lambda r: (
            _DIRECTION_RANK.get(r.get("direction"), 1),
            _CONFIDENCE_RANK.get(r.get("confidence"), 0),
        ),
        reverse=True,
    )
    return out


st.set_page_config(page_title="release-pillar-mapper", layout="wide")
st.title("release-pillar-mapper")
st.caption(
    "one frontier release, mapped against three downstream systems — the repo "
    "portfolio, the brief corpus, and the investing thesis pillars. each target "
    "gets a direction, a confidence, and a recommended action."
)

impact, release_id = load_impact_map()
if not impact:
    st.warning("no impact map found under reports/*.jsonl")
    st.stop()

all_rows = rows_for(impact, ["repo", "brief", "pillar"])
actionable = [r for r in all_rows if r.get("direction") != "unchanged"]
unchanged = [r for r in all_rows if r.get("direction") == "unchanged"]

st.subheader(f"release: {release_id}")

c1, c2, c3 = st.columns(3)
c1.metric("targets mapped", len(all_rows))
c2.metric("actionable", len(actionable), help="direction is not 'unchanged'")
c3.metric("left unchanged", len(unchanged))

axes = st.multiselect(
    "axes to show",
    options=["repo", "brief", "pillar"],
    default=["repo", "brief", "pillar"],
)
shown = rows_for(impact, axes) if axes else []

st.dataframe(
    [
        {
            "axis": r.get("axis"),
            "target": r.get("target_id"),
            "direction": r.get("direction"),
            "confidence": r.get("confidence"),
            "evidence": r.get("evidence_anchor"),
            "recommended action": r.get("recommended_action"),
        }
        for r in shown
    ],
    use_container_width=True,
    hide_index=True,
)

ranked_actionable = [r for r in shown if r.get("direction") != "unchanged"]
if ranked_actionable:
    top = ranked_actionable[0]
    st.info(
        f"**top finding:** {top.get('target_id')} ({top.get('axis')}) "
        f"{top.get('direction')} [{top.get('confidence')}] -> "
        f"{top.get('recommended_action')}"
    )
else:
    st.info("no actionable impacts in the selected axes; every target was left unchanged.")

st.caption(
    "v0.1 ships one example release. the schema + mapper live in "
    "`src/release_pillar_mapper/`; this page reads the committed `reports/*.jsonl`. "
    "the same summary prints from the CLI: `python -m release_pillar_mapper show`. "
    "repo: github.com/AthenaTheOwl/release-pillar-mapper"
)
