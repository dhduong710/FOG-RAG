#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 21 Day 7
Write Week 21 closeout and freeze baseline comparison.

Inputs:
- results/week21/baseline_protocol_freeze.json
- results/week21/baseline_inventory.json
- results/week21/baseline_rerun_summary.json
- results/week21/day4_reviewer_safe_metrics_all.json
- results/week21/baseline_main_table.json
- results/week21/baseline_positioning_decision.json
- results/week21/baseline_interpretation_assets.json
- results/week21/baseline_main_table.tex

Outputs:
- results/week21/week21_closeout.json
- results/week21/week21_go_decision.json
- reports/week21/day7_week21_closeout.md
- reports/week21/week21_closeout.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(".")
RESULTS_DIR = ROOT / "results" / "week21"
REPORTS_DIR = ROOT / "reports" / "week21"

IN_PROTOCOL = RESULTS_DIR / "baseline_protocol_freeze.json"
IN_INVENTORY = RESULTS_DIR / "baseline_inventory.json"
IN_RERUN = RESULTS_DIR / "baseline_rerun_summary.json"
IN_DAY4 = RESULTS_DIR / "day4_reviewer_safe_metrics_all.json"
IN_TABLE = RESULTS_DIR / "baseline_main_table.json"
IN_DECISION = RESULTS_DIR / "baseline_positioning_decision.json"
IN_ASSETS = RESULTS_DIR / "baseline_interpretation_assets.json"
IN_TABLE_TEX = RESULTS_DIR / "baseline_main_table.tex"

OUT_CLOSEOUT_JSON = RESULTS_DIR / "week21_closeout.json"
OUT_GO_DECISION = RESULTS_DIR / "week21_go_decision.json"
OUT_DAY7_MD = REPORTS_DIR / "day7_week21_closeout.md"
OUT_WEEK_CLOSEOUT_MD = REPORTS_DIR / "week21_closeout.md"


def load_json(path: Path, required: bool = True) -> Any:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Missing required file: {path}")
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_text(path: Path, required: bool = True) -> str:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Missing required file: {path}")
        return ""
    return path.read_text(encoding="utf-8")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def get_row(rows: list[dict[str, Any]], name: str) -> dict[str, Any]:
    for row in rows:
        if row["row_name"] == name:
            return row
    raise KeyError(f"Missing row: {name}")


def fmt(x: float, n: int = 6) -> str:
    return f"{x:.{n}f}"


def validate_day_outputs(
    protocol: dict[str, Any],
    rerun: list[dict[str, Any]],
    day4: dict[str, Any],
    decision: dict[str, Any],
    assets: dict[str, Any],
) -> dict[str, Any]:
    checks: dict[str, Any] = {}

    # Protocol checks
    checks["protocol_top_k_is_20"] = protocol["task_protocol"]["top_k"] == 20
    checks["protocol_gold_injection_forbidden"] = (
        protocol["task_protocol"]["gold_injection"] == "forbidden"
    )
    checks["protocol_rr_absent_is_zero"] = (
        protocol["metric_protocol"]["rr_absent_policy"] == 0
    )
    checks["protocol_absent_rank_is_21"] = (
        protocol["metric_protocol"]["absent_rank_sentinel"] == 21
    )

    # Rerun checks
    expected_models = {"transe", "distmult", "complex", "rotate", "rgcn", "hrgat"}
    rerun_models = {x["model_name"] for x in rerun}
    checks["all_6_baselines_rerun"] = expected_models == rerun_models

    rerun_detail = {}
    for item in rerun:
        m = item["model_name"]
        vs = item["valid_summary"]
        ts = item["test_summary"]
        rerun_detail[m] = {
            "valid_rows_500": vs["num_rows"] == 500,
            "test_rows_500": ts["num_rows"] == 500,
            "valid_candidate_size_20": (
                vs["candidate_size_min"] == 20 and vs["candidate_size_max"] == 20
            ),
            "test_candidate_size_20": (
                ts["candidate_size_min"] == 20 and ts["candidate_size_max"] == 20
            ),
        }
    checks["rerun_detail"] = rerun_detail
    checks["all_rerun_rows_and_candidate_sizes_pass"] = all(
        all(v.values()) for v in rerun_detail.values()
    )

    # Day 4 checks
    day4_rows = day4["test"]["all_rows"]
    checks["all_day4_query_sets_match"] = all(
        bool(r["same_query_set_as_raw_source"]) for r in day4_rows
    )
    checks["all_day4_absent_rr_pass"] = all(
        bool(r["absent_rr_check_pass"]) for r in day4_rows
    )

    baseline_rows = day4["test"]["baseline_rows"]
    checks["baseline_no_gold_injection"] = all(
        r.get("gold_injection_values") == ["False"] for r in baseline_rows
    )

    # Main result checks
    test_table_rows = load_json(IN_TABLE)["test_rows"]
    fog = get_row(test_table_rows, "soft_support_fuzzy_retrieval_main")
    complex_row = get_row(test_table_rows, "complex")
    soft = get_row(test_table_rows, "soft_support_raw")
    backbone = get_row(test_table_rows, "backbone_raw")

    checks["fograg_main_mrr_above_complex"] = (
        fog["reviewer_safe_mrr_at20"] > complex_row["reviewer_safe_mrr_at20"]
    )
    checks["complex_gold_above_fograg_main"] = (
        complex_row["gold_present_at20"] > fog["gold_present_at20"]
    )
    checks["soft_and_retrieval_same_ranking_metrics"] = (
        abs(fog["reviewer_safe_mrr_at20"] - soft["reviewer_safe_mrr_at20"]) < 1e-12
        and abs(fog["hits1_at20"] - soft["hits1_at20"]) < 1e-12
        and abs(fog["hits3_at20"] - soft["hits3_at20"]) < 1e-12
        and abs(fog["hits10_at20"] - soft["hits10_at20"]) < 1e-12
    )
    checks["fograg_main_improves_backbone_mrr"] = (
        fog["reviewer_safe_mrr_at20"] > backbone["reviewer_safe_mrr_at20"]
    )

    checks["decision_headline_ok"] = (
        decision["headline_decision"]
        == "FOG_RAG_MAIN_BEST_TEST_MRR_OR_TIED_WITH_STRUCTURE_BASELINE"
    )
    checks["assets_ready"] = (
        assets["day6_decision"] == "INTERPRETATION_ASSETS_READY_FOR_WEEK21_CLOSEOUT"
    )

    pass_keys = [
        "protocol_top_k_is_20",
        "protocol_gold_injection_forbidden",
        "protocol_rr_absent_is_zero",
        "protocol_absent_rank_is_21",
        "all_6_baselines_rerun",
        "all_rerun_rows_and_candidate_sizes_pass",
        "all_day4_query_sets_match",
        "all_day4_absent_rr_pass",
        "baseline_no_gold_injection",
        "fograg_main_mrr_above_complex",
        "complex_gold_above_fograg_main",
        "soft_and_retrieval_same_ranking_metrics",
        "fograg_main_improves_backbone_mrr",
        "decision_headline_ok",
        "assets_ready",
    ]

    checks["overall_pass"] = all(bool(checks[k]) for k in pass_keys)
    checks["pass_keys"] = pass_keys
    checks["failed_keys"] = [k for k in pass_keys if not bool(checks[k])]

    return checks


def build_closeout() -> dict[str, Any]:
    protocol = load_json(IN_PROTOCOL)
    inventory = load_json(IN_INVENTORY)
    rerun = load_json(IN_RERUN)
    day4 = load_json(IN_DAY4)
    table = load_json(IN_TABLE)
    decision = load_json(IN_DECISION)
    assets = load_json(IN_ASSETS)
    table_tex = load_text(IN_TABLE_TEX)

    test_rows = table["test_rows"]
    valid_rows = table["valid_rows"]

    test_fog = get_row(test_rows, "soft_support_fuzzy_retrieval_main")
    test_soft = get_row(test_rows, "soft_support_raw")
    test_backbone = get_row(test_rows, "backbone_raw")
    test_complex = get_row(test_rows, "complex")
    valid_complex = get_row(valid_rows, "complex")
    valid_fog = get_row(valid_rows, "soft_support_fuzzy_retrieval_main")

    checks = validate_day_outputs(protocol, rerun, day4, decision, assets)

    graph_efficiency = assets["key_numbers"]["graph_efficiency"]

    closeout = {
        "week": 21,
        "theme": "Structure baseline rerun and reviewer-safe comparison",
        "final_decision": "WEEK21_BASELINE_FREEZE_GO_DATASET2"
        if checks["overall_pass"]
        else "WEEK21_NEEDS_FIX_BEFORE_DATASET2",
        "overall_pass": checks["overall_pass"],
        "checks": checks,
        "protocol": {
            "task": "(?, indication, disease)",
            "missing_entity": "drug",
            "candidate_universe": "drug_only",
            "top_k": 20,
            "gold_injection": "forbidden",
            "main_metric": "reviewer_safe_mrr_at20",
            "rr_rule": "RR = 1/rank if rank <= 20 else 0",
            "absent_rank_sentinel": 21,
            "rr_absent_policy": 0,
        },
        "baseline_rerun_summary": {
            item["model_name"]: {
                "valid_gold_at20": item["valid_summary"]["gold_present_at20_raw"],
                "test_gold_at20": item["test_summary"]["gold_present_at20_raw"],
                "valid_rows": item["valid_summary"]["num_rows"],
                "test_rows": item["test_summary"]["num_rows"],
                "valid_rank21": item["valid_summary"]["gold_rank_21_count"],
                "test_rank21": item["test_summary"]["gold_rank_21_count"],
            }
            for item in rerun
        },
        "locked_test_main_numbers": {
            "backbone_raw": {
                "gold_at20": test_backbone["gold_present_at20"],
                "mrr_at20": test_backbone["reviewer_safe_mrr_at20"],
                "hits1": test_backbone["hits1_at20"],
                "hits3": test_backbone["hits3_at20"],
                "hits10": test_backbone["hits10_at20"],
            },
            "complex": {
                "gold_at20": test_complex["gold_present_at20"],
                "mrr_at20": test_complex["reviewer_safe_mrr_at20"],
                "hits1": test_complex["hits1_at20"],
                "hits3": test_complex["hits3_at20"],
                "hits10": test_complex["hits10_at20"],
            },
            "soft_support_raw": {
                "gold_at20": test_soft["gold_present_at20"],
                "mrr_at20": test_soft["reviewer_safe_mrr_at20"],
                "hits1": test_soft["hits1_at20"],
                "hits3": test_soft["hits3_at20"],
                "hits10": test_soft["hits10_at20"],
            },
            "fograg_main": {
                "gold_at20": test_fog["gold_present_at20"],
                "mrr_at20": test_fog["reviewer_safe_mrr_at20"],
                "hits1": test_fog["hits1_at20"],
                "hits3": test_fog["hits3_at20"],
                "hits10": test_fog["hits10_at20"],
            },
        },
        "valid_caveat": {
            "valid_best_row": "complex",
            "complex_valid_mrr_at20": valid_complex["reviewer_safe_mrr_at20"],
            "fograg_main_valid_mrr_at20": valid_fog["reviewer_safe_mrr_at20"],
            "interpretation": (
                "ComplEx is higher than FOG-RAG main on validation, so the paper should avoid "
                "claiming universal superiority."
            ),
        },
        "test_deltas": decision["deltas"],
        "graph_efficiency": graph_efficiency,
        "paper_positioning": {
            "headline": assets["headline"],
            "recommended_claims": assets["recommended_claims"],
            "forbidden_claims": assets["forbidden_claims"],
            "recommended_results_paragraph": assets["paper_snippets"]["results_paragraph"],
            "recommended_discussion_paragraph": assets["paper_snippets"]["discussion_paragraph"],
            "reviewer_defense": assets["paper_snippets"]["reviewer_defense"],
            "table_caption": assets["paper_snippets"]["table_caption"],
        },
        "important_artifacts": {
            "protocol": str(IN_PROTOCOL),
            "inventory": str(IN_INVENTORY),
            "rerun_summary": str(IN_RERUN),
            "day4_metrics": str(IN_DAY4),
            "main_table_json": str(IN_TABLE),
            "main_table_tex": str(IN_TABLE_TEX),
            "positioning_decision": str(IN_DECISION),
            "interpretation_assets": str(IN_ASSETS),
            "closeout_json": str(OUT_CLOSEOUT_JSON),
            "go_decision": str(OUT_GO_DECISION),
            "week21_closeout_md": str(OUT_WEEK_CLOSEOUT_MD),
        },
        "latex_table": table_tex,
        "next_week": {
            "week": 22,
            "theme": "Dataset 2 setup and raw baseline transfer",
            "recommended_first_step": (
                "Inventory and select Dataset 2, likely PharmKG, then define the same "
                "reviewer-safe top-20 candidate-generator protocol before running FOG-RAG stages."
            ),
            "do_not_do_yet": [
                "Do not change FOG-RAG main row based only on ComplEx coverage.",
                "Do not promote ComplEx-source FOG-RAG before a separate controlled experiment.",
                "Do not open extra LLM ablations before Dataset 2 setup unless Dataset 2 is blocked.",
            ],
        },
    }

    return closeout


def make_metric_table_md(rows: list[dict[str, Any]]) -> str:
    lines = []
    lines.append("| Method | Group | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | Avg. rank |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        lines.append(
            f"| {r['display_name']} | {r['group']} "
            f"| {r['gold_present_at20']:.4f} "
            f"| {r['reviewer_safe_mrr_at20']:.6f} "
            f"| {r['hits1_at20']:.4f} "
            f"| {r['hits3_at20']:.4f} "
            f"| {r['hits10_at20']:.4f} "
            f"| {r['avg_gold_rank_absent_as_21']:.3f} |"
        )
    return "\n".join(lines)


def build_closeout_md(closeout: dict[str, Any]) -> str:
    table = load_json(IN_TABLE)
    test_rows = table["test_rows"]
    valid_rows = table["valid_rows"]

    nums = closeout["locked_test_main_numbers"]
    deltas = closeout["test_deltas"]
    graph = closeout["graph_efficiency"]

    lines = []
    lines.append("# Week 21 Closeout — Baseline Rerun and Reviewer-safe Comparison")
    lines.append("")
    lines.append("## Final decision")
    lines.append("")
    lines.append(f"**{closeout['final_decision']}**")
    lines.append("")
    lines.append("## Overall status")
    lines.append("")
    lines.append(f"- Overall pass: `{closeout['overall_pass']}`")
    lines.append(f"- Failed checks: `{closeout['checks']['failed_keys']}`")
    lines.append("")
    lines.append("## Frozen protocol")
    lines.append("")
    for k, v in closeout["protocol"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## What was completed this week")
    lines.append("")
    lines.append("- Day 1: froze baseline-as-candidate-generator protocol.")
    lines.append("- Day 2: audited old baseline artifacts.")
    lines.append("- Day 3: reran all 6 structure baselines from scratch.")
    lines.append("- Day 4: recomputed reviewer-safe metrics for baselines and FOG-RAG rows.")
    lines.append("- Day 5: built paper-ready baseline table and positioning decision.")
    lines.append("- Day 6: generated Results, Discussion, and reviewer-defense snippets.")
    lines.append("- Day 7: froze Week 21 closeout and GO decision for Dataset 2.")
    lines.append("")
    lines.append("## Baselines rerun")
    lines.append("")
    lines.append("| Model | Valid Gold@20 | Test Gold@20 | Valid rows | Test rows |")
    lines.append("|---|---:|---:|---:|---:|")
    for model, s in closeout["baseline_rerun_summary"].items():
        lines.append(
            f"| `{model}` | {s['valid_gold_at20']:.4f} | {s['test_gold_at20']:.4f} "
            f"| {s['valid_rows']} | {s['test_rows']} |"
        )
    lines.append("")
    lines.append("## Locked-test headline numbers")
    lines.append("")
    lines.append("| Row | Gold@20 | MRR@20 | H@1 | H@3 | H@10 |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for row_name in ["backbone_raw", "complex", "soft_support_raw", "fograg_main"]:
        r = nums[row_name]
        lines.append(
            f"| `{row_name}` | {r['gold_at20']:.4f} | {r['mrr_at20']:.6f} "
            f"| {r['hits1']:.4f} | {r['hits3']:.4f} | {r['hits10']:.4f} |"
        )
    lines.append("")
    lines.append("## Full valid table")
    lines.append("")
    lines.append(make_metric_table_md(valid_rows))
    lines.append("")
    lines.append("## Full test table")
    lines.append("")
    lines.append(make_metric_table_md(test_rows))
    lines.append("")
    lines.append("## Main interpretation")
    lines.append("")
    lines.append(
        "FOG-RAG main achieves the highest locked-test reviewer-safe MRR@20, "
        "slightly above the strongest structure-only baseline, ComplEx. "
        "The margin is small, so the paper must not overclaim universal superiority. "
        "The strongest and safest claim is that FOG-RAG improves the DrKGC-compatible raw "
        "candidate source substantially and remains competitive with a strong structure-only "
        "candidate generator."
    )
    lines.append("")
    lines.append("## Key deltas on locked test")
    lines.append("")
    lines.append(
        f"- FOG-RAG main minus backbone raw MRR@20: "
        f"{deltas['fograg_main_minus_backbone_raw']['delta_mrr_at20']:+.6f}"
    )
    lines.append(
        f"- FOG-RAG main minus ComplEx MRR@20: "
        f"{deltas['fograg_main_minus_complex']['delta_mrr_at20']:+.6f}"
    )
    lines.append(
        f"- FOG-RAG main minus ComplEx Gold@20: "
        f"{deltas['fograg_main_minus_complex']['delta_gold_present_at20']:+.3f}"
    )
    lines.append(
        f"- ComplEx minus backbone raw MRR@20: "
        f"{deltas['complex_minus_backbone_raw']['delta_mrr_at20']:+.6f}"
    )
    lines.append("")
    lines.append("## Graph-efficiency reminder")
    lines.append("")
    lines.append(
        f"- Soft/backbone average subgraph size: "
        f"{graph['soft_support_avg_subgraph_size_test']:.2f}"
    )
    lines.append(
        f"- Retrieval-main average subgraph size: "
        f"{graph['retrieval_main_avg_subgraph_size_test']:.2f}"
    )
    lines.append(
        f"- Reduction: {graph['subgraph_size_reduction_vs_soft']:.2f} triples/query"
    )
    lines.append("- Ranking gain is driven by soft support.")
    lines.append("- Retrieval main preserves ranking and improves graph compactness/evidence quality.")
    lines.append("")
    lines.append("## Claims allowed in paper")
    lines.append("")
    for item in closeout["paper_positioning"]["recommended_claims"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Claims to avoid")
    lines.append("")
    for item in closeout["paper_positioning"]["forbidden_claims"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Recommended paper stance")
    lines.append("")
    lines.append(closeout["paper_positioning"]["recommended_results_paragraph"])
    lines.append("")
    lines.append("## Reviewer-defense note")
    lines.append("")
    lines.append(closeout["paper_positioning"]["reviewer_defense"])
    lines.append("")
    lines.append("## Important artifacts")
    lines.append("")
    for k, v in closeout["important_artifacts"].items():
        if k != "latex_table":
            lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## GO decision for next week")
    lines.append("")
    lines.append("Proceed to **Week 22 — Dataset 2 setup and transfer**.")
    lines.append("")
    lines.append("Recommended first step:")
    lines.append("")
    lines.append(f"> {closeout['next_week']['recommended_first_step']}")
    lines.append("")
    lines.append("Do not do yet:")
    lines.append("")
    for item in closeout["next_week"]["do_not_do_yet"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def build_day7_md(closeout: dict[str, Any]) -> str:
    lines = []
    lines.append("# Week 21 Day 7 — Closeout")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(f"**{closeout['final_decision']}**")
    lines.append("")
    lines.append("## Check summary")
    lines.append("")
    lines.append(f"- Overall pass: `{closeout['overall_pass']}`")
    lines.append(f"- Failed keys: `{closeout['checks']['failed_keys']}`")
    lines.append("")
    lines.append("## Passed checks")
    lines.append("")
    for key in closeout["checks"]["pass_keys"]:
        lines.append(f"- `{key}`: `{closeout['checks'][key]}`")
    lines.append("")
    lines.append("## Main numbers")
    lines.append("")
    nums = closeout["locked_test_main_numbers"]
    for k, v in nums.items():
        lines.append(
            f"- `{k}`: Gold@20={v['gold_at20']:.4f}, "
            f"MRR@20={v['mrr_at20']:.6f}, "
            f"H@1={v['hits1']:.4f}, H@3={v['hits3']:.4f}, H@10={v['hits10']:.4f}"
        )
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append("Week 22 should start Dataset 2 setup and protocol adaptation.")
    return "\n".join(lines)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    closeout = build_closeout()

    go_decision = {
        "week": 21,
        "decision": closeout["final_decision"],
        "overall_pass": closeout["overall_pass"],
        "ready_for_week22_dataset2": bool(closeout["overall_pass"]),
        "blocked": not bool(closeout["overall_pass"]),
        "failed_keys": closeout["checks"]["failed_keys"],
        "next_week": closeout["next_week"],
    }

    write_json(OUT_CLOSEOUT_JSON, closeout)
    write_json(OUT_GO_DECISION, go_decision)
    write_text(OUT_DAY7_MD, build_day7_md(closeout))
    write_text(OUT_WEEK_CLOSEOUT_MD, build_closeout_md(closeout))

    print("=" * 100)
    print("WEEK 21 DAY 7 — CLOSEOUT")
    print("=" * 100)
    print(f"Wrote: {OUT_CLOSEOUT_JSON}")
    print(f"Wrote: {OUT_GO_DECISION}")
    print(f"Wrote: {OUT_DAY7_MD}")
    print(f"Wrote: {OUT_WEEK_CLOSEOUT_MD}")
    print()
    print("Decision:", closeout["final_decision"])
    print("Overall pass:", closeout["overall_pass"])
    print("Failed keys:", closeout["checks"]["failed_keys"])
    print()
    print("Locked-test headline:")
    nums = closeout["locked_test_main_numbers"]
    print(
        "  FOG-RAG main: "
        f"Gold@20={nums['fograg_main']['gold_at20']:.4f}, "
        f"MRR@20={nums['fograg_main']['mrr_at20']:.6f}, "
        f"H@1={nums['fograg_main']['hits1']:.4f}, "
        f"H@3={nums['fograg_main']['hits3']:.4f}, "
        f"H@10={nums['fograg_main']['hits10']:.4f}"
    )
    print(
        "  ComplEx:      "
        f"Gold@20={nums['complex']['gold_at20']:.4f}, "
        f"MRR@20={nums['complex']['mrr_at20']:.6f}, "
        f"H@1={nums['complex']['hits1']:.4f}, "
        f"H@3={nums['complex']['hits3']:.4f}, "
        f"H@10={nums['complex']['hits10']:.4f}"
    )
    print()
    print("Next:", closeout["next_week"]["theme"])
    print("=" * 100)


if __name__ == "__main__":
    main()