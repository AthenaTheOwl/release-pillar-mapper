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
import sys
from pathlib import Path

import streamlit as st

REPO = Path(__file__).resolve().parent
REPORTS = REPO / "reports"
CONFIG = REPO / "config"

# the real engine lives in src/release_pillar_mapper. make it importable whether
# or not the package was pip-installed (requirements.txt carries `.` for cloud).
_SRC = REPO / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

try:
    from release_pillar_mapper.model import build_impact_map, load_registries
    from release_pillar_mapper.schema import Claim, ReleaseEvent, ValidationError
    from release_pillar_mapper.scoring import (
        evaluate_significance,
        load_significance_config,
    )

    _ENGINE_OK = True
    _ENGINE_ERR = ""
except Exception as exc:  # pragma: no cover - import guard for cloud
    _ENGINE_OK = False
    _ENGINE_ERR = f"{type(exc).__name__}: {exc}"

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

# ---------------------------------------------------------------------------
# interactive: map YOUR OWN release through the real engine
# ---------------------------------------------------------------------------
_DIRECTION_RANK_LIVE = _DIRECTION_RANK
_CONFIDENCE_RANK_LIVE = _CONFIDENCE_RANK

st.divider()
st.subheader("map your own release")
st.caption(
    "the table above is the committed example. below you edit a release event and "
    "drive the real engine live: `scoring.evaluate_significance` gates it against "
    "`config/significance.yaml`, then `model.build_impact_map` matches your event "
    "text against the repo / brief / pillar registries. no lookup — same functions "
    "the CLI runs."
)

if not _ENGINE_OK:
    st.error(
        "could not import the engine from `src/release_pillar_mapper`. add `.` to "
        f"requirements.txt so the package installs on cloud. ({_ENGINE_ERR})"
    )
    st.stop()


def _registry_targets() -> dict[str, list[str]]:
    regs = load_registries(REPO)
    return {
        "repos": [t.get("slug", "") for t in regs["repos"]],
        "briefs": [t.get("id", "") for t in regs["briefs"]],
        "pillars": [t.get("id", "") for t in regs["pillars"]],
    }


_VENDORS = ["OpenAI", "Anthropic", "Google", "Meta", "xAI", "DeepSeek", "Mistral", "Other"]

col_a, col_b = st.columns(2)
with col_a:
    vendor_pick = st.selectbox("vendor", _VENDORS, index=1)
    vendor = (
        st.text_input("vendor name", value="", placeholder="type the vendor")
        if vendor_pick == "Other"
        else vendor_pick
    )
    kind = st.selectbox("kind", ["model", "eval", "dataset", "framework"], index=0)
with col_b:
    rid = st.text_input("release id", value="2026-06-22-your-frontier-release")
    headline = st.text_input(
        "headline",
        value="New frontier agent model improves coding and reasoning",
    )

claim_text = st.text_area(
    "claim text (what the release actually says — this is what the engine matches on)",
    value=(
        "The model improves multi-step computer use and SWE-bench style coding "
        "reliability, with longer context handling for agent traces."
    ),
    height=90,
)
source_anchor = st.text_input("evidence anchor", value="your-release#claim-1")
force = st.checkbox(
    "force significance (operator override)",
    value=False,
    help="bypass the vendor/keyword gate — drives evaluate_significance(force=True)",
)

run = st.button("run the engine", type="primary")

if run:
    try:
        event = ReleaseEvent.from_dict(
            {
                "id": rid.strip(),
                "kind": kind,
                "source_url": "https://example.com/your-release",
                "vendor": vendor.strip(),
                "headline": headline.strip(),
                "claims": [
                    {"text": claim_text.strip(), "source_anchor": source_anchor.strip()}
                ],
                "ingested_at": "2026-06-22T00:00:00Z",
            }
        )
    except ValidationError as exc:
        st.error(f"event rejected by the validator: {exc}")
        st.stop()

    # 1) real significance gate
    sig_cfg = load_significance_config(CONFIG / "significance.yaml")
    sig = evaluate_significance(event, sig_cfg, force=force)
    if sig.accepted:
        st.success(f"significance: yes — {sig.reason}")
    else:
        st.warning(
            f"significance: no — {sig.reason}. "
            "the gate would stop here; tick 'force' to map it anyway."
        )

    # 2) real mapper (always shown so you can see the impact axes either way)
    impact_map = build_impact_map(event, load_registries(REPO))
    live_rows: list[dict] = []
    for axis, impacts in (
        ("repo", impact_map.repo_impacts),
        ("brief", impact_map.brief_impacts),
        ("pillar", impact_map.pillar_impacts),
    ):
        for imp in impacts:
            live_rows.append(
                {
                    "axis": axis,
                    "target": imp.target_id,
                    "direction": imp.direction,
                    "confidence": imp.confidence,
                    "evidence": imp.evidence_anchor,
                    "recommended action": imp.recommended_action,
                }
            )
    live_rows.sort(
        key=lambda r: (
            _DIRECTION_RANK_LIVE.get(r["direction"], 1),
            _CONFIDENCE_RANK_LIVE.get(r["confidence"], 0),
        ),
        reverse=True,
    )

    live_actionable = [r for r in live_rows if r["direction"] != "unchanged"]
    m1, m2, m3 = st.columns(3)
    m1.metric("targets mapped", len(live_rows))
    m2.metric("actionable", len(live_actionable))
    m3.metric("left unchanged", len(live_rows) - len(live_actionable))

    st.dataframe(live_rows, use_container_width=True, hide_index=True)

    if live_actionable:
        top = live_actionable[0]
        st.info(
            f"**top finding:** {top['target']} ({top['axis']}) {top['direction']} "
            f"[{top['confidence']}] -> {top['recommended action']}"
        )
    else:
        st.info(
            "no actionable impacts: your event text matched no registry topic tags. "
            "try mentioning agent / coding / eval / infrastructure."
        )

    st.caption(
        "engine: `release_pillar_mapper.scoring.evaluate_significance` + "
        "`release_pillar_mapper.model.build_impact_map`, run live on the event above."
    )
