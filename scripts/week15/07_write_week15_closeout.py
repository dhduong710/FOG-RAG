from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]

IN_REPORT = ROOT / "results/week15/path_score_report_v1.json"
OUT_JSON = ROOT / "results/week15/week15_go_decision.json"
OUT_MD = ROOT / "reports/week15/day7_week15_closeout.md"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main() -> None:
    obj = load_json(IN_REPORT)

    day4 = obj["day4_compare_summary"]
    day5_counts = obj["day5_bucket_counts"]
    anchor = obj["anchor_diagnostics"]
    freeze_checks = obj["freeze_checks"]

    backbone = day4["backbone_raw"]
    support = day4["soft_support_raw"]
    fuzzy = day4["soft_support_fuzzy_retrieval_v1"]
    delta_soft = day4["delta_fuzzy_vs_soft_support"]
    delta_backbone = day4["delta_fuzzy_vs_backbone"]
    case_level = day4["case_level"]

    # Week-15 GO rule
    go_checks = {
        "valid_fuzzy_retrieval_v1_built_cleanly": obj["recommended_action"] == "freeze_v1",
        "shortcut_noise_reduced_vs_soft_support": fuzzy["direct_shortcut_path_rate"] < support["direct_shortcut_path_rate"],
        "ranking_like_proxy_not_collapsed": delta_soft["mrr_like"] >= -0.001 and case_level["worsened_vs_soft_support"] == 0,
        "case_review_supports_cleaner_subgraph": day5_counts["same_rank_cleaner_subgraph"] > 0,
    }

    if all(go_checks.values()):
        decision = "GO"
        next_week_theme = "retrieval_sweep_and_main_row_selection"
    elif go_checks["valid_fuzzy_retrieval_v1_built_cleanly"] and go_checks["shortcut_noise_reduced_vs_soft_support"]:
        decision = "CONDITIONAL_GO"
        next_week_theme = "retrieval_repair_then_selection"
    else:
        decision = "NO_GO"
        next_week_theme = "retrieval_repair"

    closeout = {
        "week": 15,
        "decision": decision,
        "main_input_row": "soft_support_raw",
        "main_output_row": "soft_support_fuzzy_retrieval_v1",
        "reference_row": "backbone_raw",
        "negative_control": "ontology_raw",
        "week15_main_findings": {
            "avg_subgraph_size_before": support["avg_subgraph_size"],
            "avg_subgraph_size_after": fuzzy["avg_subgraph_size"],
            "avg_triple_score_after": fuzzy["avg_triple_score"],
            "direct_shortcut_path_rate_before": support["direct_shortcut_path_rate"],
            "direct_shortcut_path_rate_after": fuzzy["direct_shortcut_path_rate"],
            "shortcut_gain_vs_soft_support": obj["shortcut_gain_vs_soft_support"],
            "candidate_coverage_preserved_rate": fuzzy["candidate_coverage_preserved_rate"],
            "mrr_like_soft_support": support["mrr_like"],
            "mrr_like_fuzzy_v1": fuzzy["mrr_like"],
            "hits1_like_soft_support": support["hits1_like"],
            "hits1_like_fuzzy_v1": fuzzy["hits1_like"],
            "avg_gold_rank_soft_support": support["avg_gold_rank"],
            "avg_gold_rank_fuzzy_v1": fuzzy["avg_gold_rank"],
        },
        "delta_vs_soft_support": delta_soft,
        "delta_vs_backbone": delta_backbone,
        "case_review_summary": {
            "preserved_improvement_vs_backbone": day5_counts["preserved_improvement_vs_backbone"],
            "same_rank_cleaner_subgraph": day5_counts["same_rank_cleaner_subgraph"],
            "unchanged_bad": day5_counts["unchanged_bad"],
            "raw_bottleneck_failure": day5_counts["raw_bottleneck_failure"],
            "improved_vs_soft_support": case_level["improved_vs_soft_support"],
            "worsened_vs_soft_support": case_level["worsened_vs_soft_support"],
        },
        "anchor_diagnostics": anchor,
        "week15_go_checks": go_checks,
        "main_takeaway": [
            "Retrieval v1 produces a substantially smaller and cleaner evidence bundle than the original evidence package.",
            "The main improvement of week 15 is evidence cleanliness, not additional candidate-stage rank movement.",
            "The dominant remaining failure mode is raw/candidate bottleneck rather than retrieval breakage.",
            "Query anchoring remains a cautionary factor for week 16 but does not block freeze of retrieval v1."
        ],
        "week16_recommendation": {
            "theme": next_week_theme,
            "main_goal": "select or refine the main retrieval-stage row on valid before any encoder-stage expansion",
            "do_not_do": [
                "do_not_change_raw_source",
                "do_not_reopen_candidate_stage",
                "do_not_jump_to_encoder_without_retrieval_selection",
                "do_not_run_test_yet"
            ]
        }
    }

    save_json(OUT_JSON, closeout)

    md_lines = [
        "# Week 15 Closeout",
        "",
        f"## Decision",
        f"- **{decision}**",
        "",
        "## Main rows",
        f"- Main input row: `soft_support_raw`",
        f"- Main output row: `soft_support_fuzzy_retrieval_v1`",
        f"- Reference row: `backbone_raw`",
        f"- Negative control: `ontology_raw`",
        "",
        "## Main findings",
        f"- avg_subgraph_size: {support['avg_subgraph_size']} -> {fuzzy['avg_subgraph_size']}",
        f"- avg_triple_score (fuzzy only): {fuzzy['avg_triple_score']}",
        f"- direct_shortcut_path_rate: {support['direct_shortcut_path_rate']} -> {fuzzy['direct_shortcut_path_rate']}",
        f"- shortcut_gain_vs_soft_support: {obj['shortcut_gain_vs_soft_support']}",
        f"- candidate_coverage_preserved_rate: {fuzzy['candidate_coverage_preserved_rate']}",
        f"- mrr_like: {support['mrr_like']} -> {fuzzy['mrr_like']}",
        f"- hits1_like: {support['hits1_like']} -> {fuzzy['hits1_like']}",
        f"- avg_gold_rank: {support['avg_gold_rank']} -> {fuzzy['avg_gold_rank']}",
        "",
        "## Interpretation",
        "- Retrieval v1 clearly improves evidence cleanliness.",
        "- Retrieval v1 does not add extra ranking gain over soft_support_raw yet, but it also does not collapse ranking-like proxy.",
        "- The dominant remaining failure mode is raw / candidate bottleneck rather than retrieval breakage.",
        "",
        "## Case review summary",
        json.dumps(closeout["case_review_summary"], ensure_ascii=False, indent=2),
        "",
        "## Anchor diagnostics",
        json.dumps(anchor, ensure_ascii=False, indent=2),
        "",
        "## GO checks",
        json.dumps(go_checks, ensure_ascii=False, indent=2),
        "",
        "## Week 16 recommendation",
        json.dumps(closeout["week16_recommendation"], ensure_ascii=False, indent=2),
    ]

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print("=" * 80)
    print("WEEK 15 CLOSEOUT WRITTEN")
    print("json  :", OUT_JSON)
    print("md    :", OUT_MD)
    print("=" * 80)
    print(json.dumps({
        "decision": closeout["decision"],
        "week15_go_checks": closeout["week15_go_checks"],
        "week15_main_findings": closeout["week15_main_findings"],
        "week16_recommendation": closeout["week16_recommendation"],
    }, ensure_ascii=False, indent=2))
    print("=" * 80)


if __name__ == "__main__":
    main()