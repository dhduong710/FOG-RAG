from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(".").resolve()

INPUTS = {
    "row_lock_report": ROOT / "results/week18/retrieval_main_lock_report.json",
    "valid_main_table": ROOT / "results/week18/novelty2_valid_main_table.json",
    "valid_ablation": ROOT / "results/week18/novelty2_valid_ablation.json",
    "case_shortlist": ROOT / "results/week18/novelty2_case_shortlist.json",
    "test_readiness": ROOT / "results/week18/test_readiness_manifest.json",
    "appendix_note": ROOT / "results/week18/encoder_probe_appendix_note.json",
    "week17_go_decision": ROOT / "results/week17/week17_go_decision.json",
}

OUT_JSON = ROOT / "results/week18/week18_go_decision.json"
OUT_MD = ROOT / "reports/week18/day7_week18_closeout.md"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_row(main_table: dict, canonical_row_name: str) -> dict:
    for row in main_table["rows"]:
        if row["canonical_row_name"] == canonical_row_name:
            return row
    raise KeyError(f"Cannot find row: {canonical_row_name}")


def main():
    row_lock = load_json(INPUTS["row_lock_report"])
    main_table = load_json(INPUTS["valid_main_table"])
    ablation = load_json(INPUTS["valid_ablation"])
    case_shortlist = load_json(INPUTS["case_shortlist"])
    test_readiness = load_json(INPUTS["test_readiness"])
    appendix_note = load_json(INPUTS["appendix_note"])
    week17 = load_json(INPUTS["week17_go_decision"])

    backbone = find_row(main_table, "backbone_raw")
    ontology = find_row(main_table, "ontology_raw")
    soft = find_row(main_table, "soft_support_raw")
    retrieval = find_row(main_table, "soft_support_fuzzy_retrieval_main")

    appendix_probe = ablation["appendix_probe_summary"]

    readiness_status = test_readiness["decision"]
    if readiness_status == "READY_FOR_LOCKED_TEST":
        final_decision = "GO_TO_LOCKED_TEST"
        week19_recommendation = "run official locked test"
        official_locked_test_now = True
    elif readiness_status == "PARTIAL_READY":
        final_decision = "GO_TO_BUILD_TEST_ARTIFACTS"
        week19_recommendation = (
            "build missing soft_support_raw_test and retrieval_main_test artifacts, "
            "then run official locked test"
        )
        official_locked_test_now = False
    else:
        final_decision = "NO_GO_FOR_LOCKED_TEST_PREP"
        week19_recommendation = "repair missing critical test-side sources first"
        official_locked_test_now = False

    result = {
        "week": 18,
        "theme": "lock_retrieval_main_and_prepare_clean_evaluation_package",
        "final_decision": final_decision,
        "official_locked_test_now": official_locked_test_now,
        "week19_recommendation": week19_recommendation,
        "main_row_after_week18": "soft_support_fuzzy_retrieval_main",
        "appendix_row": "soft_support_fuzzy_encoder_probe_v0",
        "week18_status": {
            "row_lock_completed": True,
            "reviewer_safe_valid_main_table_completed": True,
            "reviewer_safe_valid_ablation_completed": True,
            "case_shortlist_completed": True,
            "test_readiness_checked": True,
            "appendix_positioning_completed": True,
        },
        "core_findings": {
            "backbone_raw_mrr_at20": backbone["ranking_metrics"]["mrr_at20"],
            "ontology_raw_mrr_at20": ontology["ranking_metrics"]["mrr_at20"],
            "soft_support_raw_mrr_at20": soft["ranking_metrics"]["mrr_at20"],
            "retrieval_main_mrr_at20": retrieval["ranking_metrics"]["mrr_at20"],
            "retrieval_main_hits1_at20": retrieval["ranking_metrics"]["hits1_at20"],
            "retrieval_main_avg_gold_rank": retrieval["ranking_metrics"]["avg_gold_rank"],
            "retrieval_main_avg_subgraph_size": retrieval["row_specific_diagnostics"]["avg_subgraph_size"],
            "retrieval_main_avg_direct_shortcut_path_rate": retrieval["row_specific_diagnostics"]["avg_direct_shortcut_path_rate"],
            "retrieval_main_avg_contradiction_path_rate": retrieval["row_specific_diagnostics"]["avg_contradiction_path_rate"],
            "retrieval_main_candidate_coverage_preserved_rate": retrieval["row_specific_diagnostics"]["candidate_coverage_preserved_rate"],
            "encoder_probe_mrr_at20": appendix_probe["mrr_at20"],
            "encoder_probe_avg_bridge_norm": appendix_probe["avg_bridge_norm"],
        },
        "row_lock_summary": {
            "reference_row": "backbone_raw",
            "negative_control_row": "ontology_raw",
            "candidate_stage_main_intermediate": "soft_support_raw",
            "main_row_after_week18": "soft_support_fuzzy_retrieval_main",
            "appendix_row": "soft_support_fuzzy_encoder_probe_v0",
        },
        "case_shortlist_summary": case_shortlist["bucket_counts"],
        "test_readiness_summary": {
            "decision": test_readiness["decision"],
            "decision_notes": test_readiness["decision_notes"],
            "missing_required_sources": [
                k for k, v in test_readiness["required_test_sources"].items() if not v["exists"]
            ],
        },
        "paper_narrative_lock": [
            "Use reviewer-safe metrics with RR@20 = 1/rank if rank <= 20 else 0.",
            "Treat gold_rank = 21 only as a descriptive sentinel for out-of-top20 cases.",
            "Present backbone_raw as the reference row.",
            "Present ontology_raw as a brittle negative control.",
            "Present soft_support_raw as the candidate-stage main intermediate row.",
            "Present soft_support_fuzzy_retrieval_main as the strongest current frozen row.",
            "Present soft_support_fuzzy_encoder_probe_v0 as a supporting deferred appendix direction.",
        ],
        "successes_of_week18": [
            "The retrieval main row was locked as the main row after week 17.",
            "A reviewer-safe valid main table was built.",
            "A reviewer-safe ablation export was built.",
            "Ontology was correctly repositioned as a negative control under the reviewer-safe metric policy.",
            "A case-study shortlist was built for main-paper interpretation and appendix positioning.",
        ],
        "remaining_limits": [
            "Official locked test should not be run yet because the main test artifacts for soft_support_raw and retrieval_main are still missing.",
            "Encoder remains deferred and should not be reopened as the default main path.",
        ],
        "paper_ready_paragraph": (
            "By the end of week 18, we locked soft_support_fuzzy_retrieval_main as the "
            "strongest current frozen row of Novelty 2 under a reviewer-safe valid protocol. "
            "The valid main table now clearly separates backbone_raw as the reference row, "
            "ontology_raw as a brittle negative control, soft_support_raw as the candidate-stage "
            "main intermediate row, and retrieval_main as the final main row at the current stage. "
            "The encoder probe remains a supporting deferred direction rather than a promoted stage. "
            "However, official locked test is deferred until the missing main test-side artifacts are built."
        ),
        "dependencies_checked": {
            "week17_final_decision": week17["final_decision"],
            "week17_main_row_after_week17": week17["main_row_after_week17"],
            "week18_row_lock_status": row_lock["status"],
            "week18_test_readiness_status": test_readiness["decision"],
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    lines = []
    lines.append("# Week 18 Closeout\n")
    lines.append("## Final decision")
    lines.append(f"- **{result['final_decision']}**")
    lines.append(f"- official_locked_test_now: `{result['official_locked_test_now']}`")
    lines.append(f"- week19_recommendation: `{result['week19_recommendation']}`")
    lines.append("")
    lines.append("## Row lock summary")
    for k, v in result["row_lock_summary"].items():
        lines.append(f"- **{k}**: `{v}`")
    lines.append("")
    lines.append("## Week-18 status")
    for k, v in result["week18_status"].items():
        lines.append(f"- **{k}**: `{v}`")
    lines.append("")
    lines.append("## Core findings")
    for k, v in result["core_findings"].items():
        lines.append(f"- **{k}**: `{v}`")
    lines.append("")
    lines.append("## Test readiness summary")
    lines.append(f"- decision: `{result['test_readiness_summary']['decision']}`")
    for x in result["test_readiness_summary"]["decision_notes"]:
        lines.append(f"- note: {x}")
    lines.append(f"- missing_required_sources: `{result['test_readiness_summary']['missing_required_sources']}`")
    lines.append("")
    lines.append("## Paper narrative lock")
    for item in result["paper_narrative_lock"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Successes of week 18")
    for item in result["successes_of_week18"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Remaining limits")
    for item in result["remaining_limits"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Paper-ready paragraph")
    lines.append(result["paper_ready_paragraph"])
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote {OUT_JSON}")
    print(f"[OK] wrote {OUT_MD}")
    print(json.dumps({
        "final_decision": result["final_decision"],
        "official_locked_test_now": result["official_locked_test_now"],
        "week19_recommendation": result["week19_recommendation"],
        "main_row_after_week18": result["main_row_after_week18"],
        "appendix_row": result["appendix_row"],
        "test_readiness_status": result["test_readiness_summary"]["decision"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()