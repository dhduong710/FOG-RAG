from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]

MAIN_DECISION_PATH = ROOT / "results/week16/retrieval_main_decision.json"
MAIN_MANIFEST_PATH = ROOT / "dataset/setting_a/27_n2_fuzzy_retrieval/retrieval_main_manifest.json"
MAIN_ROW_PATH = ROOT / "dataset/setting_a/27_n2_fuzzy_retrieval/valid_fuzzy_retrieval_main.json"
COMPARE_PATH = ROOT / "results/week16/retrieval_valid_compare.json"
CASE_PATH = ROOT / "results/week16/retrieval_case_samples_main.json"
WEEK15_GO_PATH = ROOT / "results/week15/week15_go_decision.json"

OUT_JSON = ROOT / "results/week16/retrieval_stage_freeze_report.json"
OUT_MD = ROOT / "reports/week16/day6_freeze_and_bridge.md"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main() -> None:
    decision = load_json(MAIN_DECISION_PATH)
    manifest = load_json(MAIN_MANIFEST_PATH)
    main_rows = load_json(MAIN_ROW_PATH)
    compare = load_json(COMPARE_PATH)
    case_obj = load_json(CASE_PATH)
    week15 = load_json(WEEK15_GO_PATH)

    if decision.get("selected_source_variant") != "soft_support_fuzzy_retrieval_tight":
        raise RuntimeError("Unexpected selected main variant. Review day-5 decision first.")

    if not isinstance(main_rows, list) or len(main_rows) != 500:
        raise RuntimeError("valid_fuzzy_retrieval_main.json must contain 500 rows.")

    rows = compare["rows"]
    soft = rows["soft_support_raw"]
    v1 = rows["soft_support_fuzzy_retrieval_v1"]
    main = decision["selected_metrics"]

    freeze_checks = {
        "selected_main_row_exists": True,
        "main_row_has_500_rows": len(main_rows) == 500,
        "ranking_like_proxy_not_collapsed_vs_soft_support": (
            main["mrr_like"] >= soft["mrr_like"] - 0.001
            and main["worsened_vs_soft_support"] == 0
        ),
        "candidate_coverage_preserved": main["candidate_coverage_preserved_rate"] >= 0.999,
        "main_beats_v1_on_tradeoff": (
            main["direct_shortcut_path_rate"] < v1["direct_shortcut_path_rate"]
            and main["avg_subgraph_size"] < v1["avg_subgraph_size"]
        ),
    }

    if all(freeze_checks.values()):
        recommended_action = "freeze_retrieval_main"
        bridge_mode = "encoder_readiness_check_but_not_commit_yet"
        rationale = (
            "The selected main retrieval row preserves ranking-like proxy, reduces shortcut-heavy evidence more than v1, "
            "and keeps full candidate coverage."
        )
    else:
        recommended_action = "needs_retrieval_repair"
        bridge_mode = "retrieval_repair"
        rationale = (
            "At least one freeze check failed, so retrieval-stage should not yet be treated as fully locked."
        )

    shortcut_gain_vs_soft = round(
        soft["direct_shortcut_path_rate"] - main["direct_shortcut_path_rate"], 6
    )
    shortcut_gain_vs_v1 = round(
        v1["direct_shortcut_path_rate"] - main["direct_shortcut_path_rate"], 6
    )
    size_gain_vs_soft = round(
        soft["avg_subgraph_size"] - main["avg_subgraph_size"], 6
    )
    size_gain_vs_v1 = round(
        v1["avg_subgraph_size"] - main["avg_subgraph_size"], 6
    )

    report = {
        "week": 16,
        "day": 6,
        "canonical_row_name": manifest["canonical_row_name"],
        "selected_source_variant": manifest["selected_source_variant"],
        "week15_bridge": {
            "week15_main_output_row": week15["main_output_row"],
            "week15_decision": week15["decision"],
            "week15_shortcut_gain_vs_soft_support": week15["week15_main_findings"]["shortcut_gain_vs_soft_support"],
        },
        "main_row_metrics": main,
        "comparison_summary": {
            "vs_soft_support_raw": {
                "mrr_like_delta": round(main["mrr_like"] - soft["mrr_like"], 6),
                "avg_gold_rank_delta": round(main["avg_gold_rank"] - soft["avg_gold_rank"], 6),
                "shortcut_gain": shortcut_gain_vs_soft,
                "subgraph_size_gain": size_gain_vs_soft,
                "avg_query_touch_count_delta": round(main["avg_query_touch_count"] - soft["avg_query_touch_count"], 6),
                "avg_non_direct_query_touch_count_delta": round(main["avg_non_direct_query_touch_count"] - soft["avg_non_direct_query_touch_count"], 6),
            },
            "vs_v1": {
                "mrr_like_delta": round(main["mrr_like"] - v1["mrr_like"], 6),
                "avg_gold_rank_delta": round(main["avg_gold_rank"] - v1["avg_gold_rank"], 6),
                "shortcut_gain": shortcut_gain_vs_v1,
                "subgraph_size_gain": size_gain_vs_v1,
                "avg_query_touch_count_delta": round(main["avg_query_touch_count"] - v1["avg_query_touch_count"], 6),
                "avg_non_direct_query_touch_count_delta": round(main["avg_non_direct_query_touch_count"] - v1["avg_non_direct_query_touch_count"], 6),
            },
        },
        "case_review_support": decision["case_review_support"],
        "freeze_checks": freeze_checks,
        "recommended_action": recommended_action,
        "rationale": rationale,
        "remaining_failure_modes": [
            "raw_candidate_bottleneck",
            "weak_evidence_cases",
            "small_anchor_caution_bucket",
        ],
        "week17_bridge_recommendation": {
            "mode": bridge_mode,
            "main_goal": "decide whether retrieval is stable enough to support an encoder-stage entry",
            "do_not_do": [
                "do_not_change_raw_source",
                "do_not_reopen_candidate_stage",
                "do_not_run_test_yet",
                "do_not_commit_to_encoder_without_week16_closeout"
            ],
        },
    }

    save_json(OUT_JSON, report)

    md_lines = [
        "# Week 16 - Day 6 Freeze and Bridge",
        "",
        "## Selected main retrieval row",
        f"- canonical_row_name: `{report['canonical_row_name']}`",
        f"- selected_source_variant: `{report['selected_source_variant']}`",
        "",
        "## Freeze checks",
        json.dumps(report["freeze_checks"], ensure_ascii=False, indent=2),
        "",
        "## Comparison summary",
        json.dumps(report["comparison_summary"], ensure_ascii=False, indent=2),
        "",
        "## Case review support",
        json.dumps(report["case_review_support"], ensure_ascii=False, indent=2),
        "",
        "## Recommended action",
        f"- `{report['recommended_action']}`",
        f"- {report['rationale']}",
        "",
        "## Remaining failure modes",
        "\n".join([f"- {x}" for x in report["remaining_failure_modes"]]),
        "",
        "## Week 17 bridge recommendation",
        json.dumps(report["week17_bridge_recommendation"], ensure_ascii=False, indent=2),
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print("=" * 80)
    print("DAY 6 RETRIEVAL MAIN FREEZE REPORT WRITTEN")
    print("json  :", OUT_JSON)
    print("md    :", OUT_MD)
    print("=" * 80)
    print(json.dumps({
        "canonical_row_name": report["canonical_row_name"],
        "selected_source_variant": report["selected_source_variant"],
        "freeze_checks": report["freeze_checks"],
        "recommended_action": report["recommended_action"],
        "week17_bridge_recommendation": report["week17_bridge_recommendation"],
    }, ensure_ascii=False, indent=2))
    print("=" * 80)


if __name__ == "__main__":
    main()