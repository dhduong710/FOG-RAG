from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

FREEZE_REPORT_PATH = ROOT / "results/week16/retrieval_stage_freeze_report.json"
MAIN_DECISION_PATH = ROOT / "results/week16/retrieval_main_decision.json"
MAIN_MANIFEST_PATH = ROOT / "dataset/setting_a/27_n2_fuzzy_retrieval/retrieval_main_manifest.json"

OUT_JSON = ROOT / "results/week16/week16_go_decision.json"
OUT_MD = ROOT / "reports/week16/day7_week16_closeout.md"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main() -> None:
    freeze = load_json(FREEZE_REPORT_PATH)
    decision = load_json(MAIN_DECISION_PATH)
    manifest = load_json(MAIN_MANIFEST_PATH)

    main_metrics = freeze["main_row_metrics"]
    comp = freeze["comparison_summary"]
    freeze_checks = freeze["freeze_checks"]
    case_support = freeze["case_review_support"]

    week16_go_checks = {
        "retrieval_main_row_selected": decision["selected_main_row"] == "soft_support_fuzzy_retrieval_main",
        "retrieval_main_row_frozen_cleanly": freeze["recommended_action"] == "freeze_retrieval_main",
        "ranking_like_proxy_not_collapsed_vs_soft_support": freeze_checks["ranking_like_proxy_not_collapsed_vs_soft_support"],
        "main_row_beats_v1_on_retrieval_tradeoff": freeze_checks["main_beats_v1_on_tradeoff"],
    }

    if all(week16_go_checks.values()):
        final_decision = "GO"
        week17_mode = "encoder_readiness_check"
        week17_goal = "evaluate whether retrieval is stable enough to justify a careful encoder-stage entry"
    elif week16_go_checks["retrieval_main_row_selected"] and week16_go_checks["retrieval_main_row_frozen_cleanly"]:
        final_decision = "CONDITIONAL_GO"
        week17_mode = "retrieval_repair_then_encoder_readiness_check"
        week17_goal = "repair the remaining retrieval caution points before considering encoder entry"
    else:
        final_decision = "NO_GO"
        week17_mode = "retrieval_repair"
        week17_goal = "continue retrieval-stage repair and do not open encoder-stage yet"

    closeout = {
        "week": 16,
        "decision": final_decision,
        "main_input_row": "soft_support_raw",
        "main_output_row": "soft_support_fuzzy_retrieval_main",
        "selected_source_variant": decision["selected_source_variant"],
        "reference_retrieval_row": "soft_support_fuzzy_retrieval_v1",
        "week16_main_findings": {
            "mrr_like_main": main_metrics["mrr_like"],
            "hits1_like_main": main_metrics["hits1_like"],
            "hits3_like_main": main_metrics["hits3_like"],
            "hits10_like_main": main_metrics["hits10_like"],
            "avg_gold_rank_main": main_metrics["avg_gold_rank"],
            "avg_subgraph_size_main": main_metrics["avg_subgraph_size"],
            "avg_triple_score_main": main_metrics["avg_triple_score"],
            "direct_shortcut_path_rate_main": main_metrics["direct_shortcut_path_rate"],
            "candidate_coverage_preserved_rate_main": main_metrics["candidate_coverage_preserved_rate"],
        },
        "comparison_summary": comp,
        "case_review_support": case_support,
        "week16_go_checks": week16_go_checks,
        "main_takeaway": [
            "Week 16 selected and froze a single retrieval main row on valid.",
            "The selected row preserves ranking-like proxy relative to soft_support_raw.",
            "The selected row improves retrieval-side trade-off over week-15 v1 by reducing shortcut-heavy evidence and shrinking the subgraph.",
            "Remaining failure is still dominated by raw bottleneck and weak-evidence cases, with only a small anchoring caution bucket."
        ],
        "week17_recommendation": {
            "mode": week17_mode,
            "main_goal": week17_goal,
            "do_not_do": [
                "do_not_change_raw_source",
                "do_not_reopen_candidate_stage",
                "do_not_run_test_yet",
                "do_not_commit_to_encoder_without_a_day1_readiness_check"
            ],
        },
    }

    save_json(OUT_JSON, closeout)

    md_lines = [
        "# Week 16 Closeout",
        "",
        "## Decision",
        f"- **{final_decision}**",
        "",
        "## Main rows",
        "- Main input row: `soft_support_raw`",
        "- Main output row: `soft_support_fuzzy_retrieval_main`",
        f"- Selected source variant: `{decision['selected_source_variant']}`",
        "- Reference retrieval row: `soft_support_fuzzy_retrieval_v1`",
        "",
        "## Main findings",
        f"- mrr_like: {main_metrics['mrr_like']}",
        f"- hits1_like: {main_metrics['hits1_like']}",
        f"- hits3_like: {main_metrics['hits3_like']}",
        f"- hits10_like: {main_metrics['hits10_like']}",
        f"- avg_gold_rank: {main_metrics['avg_gold_rank']}",
        f"- avg_subgraph_size: {main_metrics['avg_subgraph_size']}",
        f"- avg_triple_score: {main_metrics['avg_triple_score']}",
        f"- direct_shortcut_path_rate: {main_metrics['direct_shortcut_path_rate']}",
        f"- candidate_coverage_preserved_rate: {main_metrics['candidate_coverage_preserved_rate']}",
        "",
        "## Comparison summary",
        json.dumps(comp, ensure_ascii=False, indent=2),
        "",
        "## Case review support",
        json.dumps(case_support, ensure_ascii=False, indent=2),
        "",
        "## GO checks",
        json.dumps(week16_go_checks, ensure_ascii=False, indent=2),
        "",
        "## Week 17 recommendation",
        json.dumps(closeout["week17_recommendation"], ensure_ascii=False, indent=2),
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print("=" * 80)
    print("WEEK 16 CLOSEOUT WRITTEN")
    print("json  :", OUT_JSON)
    print("md    :", OUT_MD)
    print("=" * 80)
    print(json.dumps({
        "decision": closeout["decision"],
        "main_output_row": closeout["main_output_row"],
        "selected_source_variant": closeout["selected_source_variant"],
        "week16_go_checks": closeout["week16_go_checks"],
        "week17_recommendation": closeout["week17_recommendation"],
    }, ensure_ascii=False, indent=2))
    print("=" * 80)


if __name__ == "__main__":
    main()