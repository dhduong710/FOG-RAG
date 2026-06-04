from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(".").resolve()

READINESS_PATH = ROOT / "results/week17/encoder_readiness_manifest.json"
INPUT_SUMMARY_PATH = ROOT / "results/week17/encoder_input_summary.json"
PROBE_MANIFEST_PATH = ROOT / "dataset/setting_a/28_n2_fuzzy_encoder/encoder_probe_manifest.json"
COMPARE_PATH = ROOT / "results/week17/encoder_probe_compare.json"
CASES_PATH = ROOT / "results/week17/encoder_case_samples.json"
FREEZE_PATH = ROOT / "results/week17/encoder_freeze_report.json"

OUT_JSON = ROOT / "results/week17/week17_go_decision.json"
OUT_MD = ROOT / "reports/week17/day7_week17_closeout.md"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    readiness = load_json(READINESS_PATH)
    input_summary = load_json(INPUT_SUMMARY_PATH)
    probe_manifest = load_json(PROBE_MANIFEST_PATH)
    compare = load_json(COMPARE_PATH)
    cases = load_json(CASES_PATH)
    freeze = load_json(FREEZE_PATH)

    m_ret = compare["metrics"]["soft_support_fuzzy_retrieval_main"]
    m_probe = compare["metrics"]["soft_support_fuzzy_encoder_probe_v0"]
    comp = compare["probe_vs_retrieval_main"]
    buckets = cases["bucket_counts"]
    freeze_result = freeze["result"]

    # Final week-17 decision
    if freeze_result["decision"] == "DEFER_ENCODER":
        week17_decision = "NO_GO_FOR_FULL_ENCODER_STAGE"
        week18_mode = "keep_retrieval_main_as_final_row_or_only_redesign_encoder_as_side_probe"
    else:
        week17_decision = "CONDITIONAL_GO"
        week18_mode = "encoder_redesign_only_if_explicitly_scoped"

    summary = {
        "week": 17,
        "theme": "encoder_readiness_check_on_top_of_frozen_retrieval_main",
        "final_decision": week17_decision,
        "week18_recommendation": week18_mode,
        "main_row_after_week17": "soft_support_fuzzy_retrieval_main",
        "promote_encoder_probe_to_main_row": False,
        "week17_status": {
            "readiness_check_completed": True,
            "encoder_input_package_built": True,
            "encoder_probe_built": True,
            "probe_compare_completed": True,
            "probe_case_review_completed": True,
        },
        "core_findings": {
            "retrieval_main_mrr_like": m_ret["mrr_like"],
            "retrieval_main_hits1_like": m_ret["hits1_like"],
            "retrieval_main_avg_gold_rank": m_ret["avg_gold_rank"],
            "encoder_probe_mrr_like": m_probe["mrr_like"],
            "encoder_probe_hits1_like": m_probe["hits1_like"],
            "encoder_probe_avg_gold_rank": m_probe["avg_gold_rank"],
            "encoder_probe_avg_bridge_norm": m_probe["avg_bridge_norm"],
            "improved_vs_retrieval_main": comp["improved_vs_retrieval_main"],
            "worsened_vs_retrieval_main": comp["worsened_vs_retrieval_main"],
            "avg_rank_delta_probe_minus_retrieval": comp["avg_rank_delta_probe_minus_retrieval"],
            "anchor_caution_cases": buckets["anchor_caution_cases"],
        },
        "successes_of_week17": [
            "Encoder readiness was checked in a controlled, valid-only setting.",
            "Encoder inputs were built cleanly from the frozen retrieval main row.",
            "A minimal fuzzy encoder probe v0 was successfully constructed and compared.",
            "The project avoided prematurely committing to a full encoder stage.",
        ],
        "failures_or_limits_of_probe": [
            "Probe v0 underperforms retrieval main on ranking-like proxy metrics.",
            "Bridge signal is too sparse to support promotion of encoder stage now.",
            "Probe changes ordering in many cases without reliable gains.",
            "Anchor caution cases are too frequent.",
        ],
        "paper_narrative_lock": [
            "Candidate-stage freeze: soft_support_raw.",
            "Retrieval-stage freeze: soft_support_fuzzy_retrieval_main.",
            "Week 17 checks encoder readiness instead of jumping directly to full encoder training.",
            "Encoder probe v0 is reported as a controlled but not-yet-successful probe.",
            "Retrieval main remains the strongest frozen row after week 17.",
        ],
        "next_step_options": [
            "Option A: keep retrieval main as the final N2 row and move toward locked evaluation / interpretation.",
            "Option B: revisit encoder only as an explicitly redesigned side experiment, not as the default week-18 main path.",
        ],
        "source_artifacts": {
            "readiness_manifest": str(READINESS_PATH.relative_to(ROOT)),
            "encoder_input_summary": str(INPUT_SUMMARY_PATH.relative_to(ROOT)),
            "encoder_probe_manifest": str(PROBE_MANIFEST_PATH.relative_to(ROOT)),
            "encoder_probe_compare": str(COMPARE_PATH.relative_to(ROOT)),
            "encoder_case_samples": str(CASES_PATH.relative_to(ROOT)),
            "encoder_freeze_report": str(FREEZE_PATH.relative_to(ROOT)),
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    lines = []
    lines.append("# Week 17 Closeout\n")
    lines.append("## Final decision")
    lines.append(f"- **{summary['final_decision']}**")
    lines.append(f"- Week-18 recommendation: `{summary['week18_recommendation']}`")
    lines.append(f"- Main row after week 17: `{summary['main_row_after_week17']}`")
    lines.append(f"- Promote encoder probe: `{summary['promote_encoder_probe_to_main_row']}`")
    lines.append("")
    lines.append("## Week-17 status")
    for k, v in summary["week17_status"].items():
        lines.append(f"- **{k}**: `{v}`")
    lines.append("")
    lines.append("## Core findings")
    for k, v in summary["core_findings"].items():
        lines.append(f"- **{k}**: `{v}`")
    lines.append("")
    lines.append("## Successes of week 17")
    for item in summary["successes_of_week17"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Failures / limits of encoder probe")
    for item in summary["failures_or_limits_of_probe"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Paper narrative lock")
    for item in summary["paper_narrative_lock"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Next-step options")
    for item in summary["next_step_options"]:
        lines.append(f"- {item}")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote {OUT_JSON}")
    print(f"[OK] wrote {OUT_MD}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()