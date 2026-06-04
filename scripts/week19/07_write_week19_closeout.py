from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(".").resolve()

IN_PROTOCOL = ROOT / "results/week19/test_protocol_freeze.json"
IN_SOFT = ROOT / "results/week19/soft_support_test_build_summary.json"
IN_RETR = ROOT / "results/week19/retrieval_test_build_summary.json"
IN_EVAL = ROOT / "results/week19/test_eval_ready_summary.json"
IN_MAIN = ROOT / "results/week19/test_main_table.json"
IN_ABL = ROOT / "results/week19/test_ablation.json"
IN_CASES = ROOT / "results/week19/test_case_shortlist.json"

OUT_JSON = ROOT / "results/week19/week19_go_decision.json"
OUT_MD = ROOT / "reports/week19/day7_week19_closeout.md"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def pick_case_subset(cases: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
    return cases[:n] if len(cases) > n else cases


def main():
    protocol = load_json(IN_PROTOCOL)
    soft = load_json(IN_SOFT)
    retr = load_json(IN_RETR)
    eval_sum = load_json(IN_EVAL)
    main_table = load_json(IN_MAIN)
    ablation = load_json(IN_ABL)
    case_shortlist = load_json(IN_CASES)

    # ---------- hard checks ----------
    q1_soft_clean = (
        soft.get("status") == "BUILT"
        and soft.get("summary", {}).get("num_rows") == 500
        and soft.get("policy_checks", {}).get("reorder_only") is True
        and soft.get("policy_checks", {}).get("no_pruning") is True
        and soft.get("policy_checks", {}).get("formula_changed") is False
        and soft.get("policy_checks", {}).get("row_naming_changed") is False
    )

    q2_retr_clean = (
        retr.get("status") == "BUILT"
        and retr.get("retrieval_main_summary", {}).get("num_rows") == 500
        and retr.get("schema_check", {}).get("num_rows_is_500") is True
        and retr.get("policy_checks", {}).get("retrieval_logic_changed") is False
        and retr.get("policy_checks", {}).get("selected_source_variant_changed") is False
        and retr.get("policy_checks", {}).get("candidate_stage_reopened") is False
        and retr.get("policy_checks", {}).get("encoder_promoted") is False
    )

    q3_eval_ready_clean = (
        eval_sum.get("status") == "BUILT"
        and eval_sum.get("global_checks", {}).get("all_rows_have_500_examples") is True
        and eval_sum.get("global_checks", {}).get("all_query_sets_match") is True
        and eval_sum.get("global_checks", {}).get("all_top_level_keys_match_across_test_rows") is True
        and eval_sum.get("global_checks", {}).get("all_gold_rank_use_21_sentinel_when_missing") is True
        and eval_sum.get("global_checks", {}).get("all_row_metrics_keys_match_valid_refs") is True
        and eval_sum.get("global_checks", {}).get("all_top_keys_match_valid_refs") is True
    )

    q4_locked_table_clean = (
        main_table.get("status") == "BUILT"
        and main_table.get("metric_policy", {}).get("main_metric") == "mrr_at20"
        and main_table.get("metric_policy", {}).get("gold_rank_out_of_top20") == 21
    )

    narrative = main_table.get("narrative_checks", {})
    q5_main_row_supported = (
        narrative.get("ontology_is_weaker_than_backbone") is True
        and narrative.get("soft_is_stronger_than_backbone") is True
        and narrative.get("retrieval_preserves_or_improves_vs_soft") is True
        and main_table.get("provisional_main_row") == "soft_support_fuzzy_retrieval_main"
    )

    encoder_appendix = (
        ablation.get("appendix_note", {}).get("encoder_probe_status") == "deferred_appendix_only"
        and ablation.get("appendix_note", {}).get("encoder_probe_not_in_main_table") is True
    )

    # ---------- recommended case packs ----------
    bucket1 = case_shortlist.get("shortlist", {}).get("backbone_to_retrieval_improved", [])
    bucket2 = case_shortlist.get("shortlist", {}).get("ontology_failure_retrieval_success", [])
    bucket3_all = case_shortlist.get("shortlist", {}).get("same_rank_cleaner_graph", [])

    # For main paper, prefer same-rank cleaner graph cases where retrieval still has gold present and rank <= 10
    bucket3_main = [
        x for x in bucket3_all
        if x.get("retrieval_gold_present") and int(x.get("retrieval_gold_rank", 21)) <= 10
    ]
    if not bucket3_main:
        bucket3_main = bucket3_all

    recommended_main_paper_cases = {
        "backbone_to_retrieval_improved": pick_case_subset(bucket1, 3),
        "ontology_failure_retrieval_success": pick_case_subset(bucket2, 3),
        "same_rank_cleaner_graph": pick_case_subset(bucket3_main, 3),
    }

    recommended_appendix_cases = {
        "same_rank_cleaner_graph_extra": pick_case_subset(bucket3_all[3:], 5) if len(bucket3_all) > 3 else [],
        "encoder_appendix_deferred": case_shortlist.get("shortlist", {}).get("encoder_appendix_deferred", []),
    }

    all_success = all([
        q1_soft_clean,
        q2_retr_clean,
        q3_eval_ready_clean,
        q4_locked_table_clean,
        q5_main_row_supported,
        encoder_appendix,
    ])

    if all_success:
        final_status = "GO_PAPER_ASSEMBLY"
        next_step = "paper_assembly_final_interpretation_figures_tables"
        paper_main_row = "soft_support_fuzzy_retrieval_main"
        short_decision = (
            "Locked test confirms the valid-side narrative under reviewer-safe protocol. "
            "Keep soft_support_fuzzy_retrieval_main as the paper-facing main row."
        )
    else:
        final_status = "CONDITIONAL_GO_NEEDS_SMALL_CLEANUP"
        next_step = "small_cleanup_then_paper_assembly"
        paper_main_row = main_table.get("provisional_main_row", "soft_support_fuzzy_retrieval_main")
        short_decision = (
            "Week 19 is mostly successful, but one or more closeout checks still require small cleanup."
        )

    decision = {
        "week": 19,
        "stage": "week19_closeout_and_go_decision",
        "status": final_status,
        "theme": "Build missing main test artifacts then run official locked test",
        "closeout_checks": {
            "soft_support_raw_test_built_clean": q1_soft_clean,
            "retrieval_main_test_built_clean": q2_retr_clean,
            "test_eval_ready_package_clean": q3_eval_ready_clean,
            "official_locked_test_main_table_clean": q4_locked_table_clean,
            "test_side_supports_retrieval_main_as_main_row": q5_main_row_supported,
            "encoder_remains_appendix_only": encoder_appendix,
        },
        "paper_facing_decision": {
            "paper_main_row": paper_main_row,
            "reference_row": "backbone_raw",
            "negative_control": "ontology_raw",
            "candidate_stage_intermediate": "soft_support_raw",
            "appendix_only": ["soft_support_fuzzy_encoder_probe_v0"],
            "selected_source_variant": retr.get("selected_source_variant"),
            "selected_source_variant_set_from_locked_test": ablation.get("main_row", {}).get("selected_source_variant_set", []),
        },
        "locked_test_summary": {
            "backbone_raw": ablation.get("reference_row"),
            "ontology_raw": ablation.get("negative_control"),
            "soft_support_raw": ablation.get("candidate_stage_intermediate"),
            "retrieval_main": ablation.get("main_row"),
            "candidate_gain_vs_backbone": ablation.get("candidate_gain_vs_backbone"),
            "retrieval_gain_vs_soft": ablation.get("retrieval_gain_vs_soft"),
            "ontology_vs_backbone": ablation.get("ontology_vs_backbone"),
        },
        "recommended_case_packs": {
            "main_paper": recommended_main_paper_cases,
            "appendix": recommended_appendix_cases,
        },
        "next_step": next_step,
        "decision_note": short_decision,
    }

    save_json(OUT_JSON, decision)

    md = []
    md.append("# Day 7 — Week 19 closeout")
    md.append("")
    md.append(f"- status: **{decision['status']}**")
    md.append(f"- paper_main_row: **`{decision['paper_facing_decision']['paper_main_row']}`**")
    md.append(f"- next_step: **`{decision['next_step']}`**")
    md.append("")
    md.append("## 1. Closeout checks")
    for k, v in decision["closeout_checks"].items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## 2. Paper-facing decision")
    for k, v in decision["paper_facing_decision"].items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## 3. Candidate-stage gain vs backbone")
    for k, v in decision["locked_test_summary"]["candidate_gain_vs_backbone"].items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## 4. Retrieval-stage gain vs soft")
    for k, v in decision["locked_test_summary"]["retrieval_gain_vs_soft"].items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## 5. Ontology vs backbone")
    for k, v in decision["locked_test_summary"]["ontology_vs_backbone"].items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## 6. Recommended main-paper cases")
    for bucket, cases in decision["recommended_case_packs"]["main_paper"].items():
        md.append(f"### {bucket}")
        for x in cases:
            md.append(
                f"- row={x['row_index']} | query=`{x['query_entity']}` | gold=`{x['gold_entity']}` | "
                f"backbone_rank={x['backbone_gold_rank']} | soft_rank={x['soft_gold_rank']} | "
                f"retrieval_rank={x['retrieval_gold_rank']}"
            )
        md.append("")
    md.append("## 7. Decision note")
    md.append(decision["decision_note"])
    md.append("")
    md.append("## 8. Day-7 conclusion")
    md.append(
        "Week 19 is now closed. Locked test artifacts, eval-ready package, main table, ablation, "
        "and shortlist are all assembled into one paper-facing decision package."
    )

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
