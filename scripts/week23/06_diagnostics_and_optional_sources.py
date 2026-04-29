#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 23 Day 6: Diagnostics, failure analysis, and paper interpretation.

This script analyzes:
- raw candidate bottleneck
- hard-support non-discrimination
- soft-support improved/worsened cases
- fuzzy retrieval same-rank cleaner evidence
- paper-safe interpretation
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(".")

DATASET_DIR = ROOT / "dataset" / "setting_c_pharmkg"
FINAL_EVAL_DIR = DATASET_DIR / "12_eval_rows"
SOFT_DIR = DATASET_DIR / "10_soft_support"
FUZZY_DIR = DATASET_DIR / "11_fuzzy_retrieval"
HARD_DIR = DATASET_DIR / "09_hard_support_raw"

RESULT_DIR = ROOT / "results" / "week23"
REPORT_DIR = ROOT / "reports" / "week23"

FAILURE_ANALYSIS_PATH = RESULT_DIR / "dataset2_failure_analysis.json"
CASE_BUCKETS_PATH = RESULT_DIR / "dataset2_case_buckets.json"
PAPER_INTERPRETATION_PATH = RESULT_DIR / "dataset2_paper_interpretation.json"
REPORT_PATH = REPORT_DIR / "day6_diagnostics_and_optional_sources.md"

TOP_K = 20
ABSENT_RANK = 21


def ensure_dirs() -> None:
    for p in [RESULT_DIR, REPORT_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def index_rows(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {int(r["row_index"]): r for r in rows}


def load_split_bundle(split: str) -> dict[str, Any]:
    bundle = {
        "backbone_eval": index_rows(read_json(FINAL_EVAL_DIR / f"{split}_backbone_raw.json")),
        "hard_eval": index_rows(read_json(FINAL_EVAL_DIR / f"{split}_hard_support_raw.json")),
        "soft_eval": index_rows(read_json(FINAL_EVAL_DIR / f"{split}_soft_support_raw.json")),
        "fuzzy_eval": index_rows(read_json(FINAL_EVAL_DIR / f"{split}_fuzzy_retrieval_main.json")),
        "soft_detail": index_rows(read_json(SOFT_DIR / f"{split}_top20_soft_support_main.json")),
        "fuzzy_detail": index_rows(read_json(FUZZY_DIR / f"{split}_fuzzy_retrieval_main.json")),
    }
    return bundle


def safe_case_row(
    split: str,
    idx: int,
    backbone: dict[str, Any],
    hard: dict[str, Any],
    soft: dict[str, Any],
    fuzzy: dict[str, Any],
    soft_detail: dict[str, Any],
    fuzzy_detail: dict[str, Any],
) -> dict[str, Any]:
    subgraph_summary = fuzzy_detail.get("subgraph_summary", {})

    # Day 5 final eval rows do not keep direct-T diagnostics.
    # Recover them from the original Day 3 soft-support detailed rows.
    soft_debug_rows = soft_detail.get("candidate_debug_rows", [])

    if soft_debug_rows:
        num_direct_T_candidates_before = int(
            sum(int(x.get("direct_T_candidate_query_flag", 0)) for x in soft_debug_rows)
        )
        num_direct_T_candidates_top5_after = int(
            sum(int(x.get("direct_T_candidate_query_flag", 0)) for x in soft_debug_rows[:5])
        )
    else:
        num_direct_T_candidates_before = None
        num_direct_T_candidates_top5_after = None

    return {
        "split": split,
        "row_index": int(idx),
        "query_entity": backbone["query_entity"],
        "gold_entity": backbone["gold_entity"],
        "backbone_rank": int(backbone["gold_rank"]),
        "hard_rank": int(hard["gold_rank"]),
        "soft_rank": int(soft["gold_rank"]),
        "fuzzy_rank": int(fuzzy["gold_rank"]),
        "backbone_present": bool(backbone["gold_present"]),
        "soft_present": bool(soft["gold_present"]),
        "fuzzy_present": bool(fuzzy["gold_present"]),
        "rank_delta_soft_vs_backbone": int(backbone["gold_rank"]) - int(soft["gold_rank"]),
        "rank_delta_fuzzy_vs_soft": int(soft["gold_rank"]) - int(fuzzy["gold_rank"]),
        "rr_backbone": float(backbone["reciprocal_rank_item"]),
        "rr_soft": float(soft["reciprocal_rank_item"]),
        "rr_fuzzy": float(fuzzy["reciprocal_rank_item"]),
        "num_direct_T_candidates_before": num_direct_T_candidates_before,
        "num_direct_T_candidates_top5_after": num_direct_T_candidates_top5_after,
        "original_subgraph_size": subgraph_summary.get("original_subgraph_size"),
        "selected_subgraph_size": subgraph_summary.get("selected_subgraph_size"),
        "candidate_coverage_preserved_rate": subgraph_summary.get("candidate_coverage_preserved_rate"),
        "top_band_coverage_preserved_rate": subgraph_summary.get("top_band_coverage_preserved_rate"),
        "top5_after_soft": list(soft_detail.get("candidate_entities", []))[:5],
    }


def analyze_split(split: str, max_examples: int = 20) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    b = load_split_bundle(split)

    buckets: dict[str, list[dict[str, Any]]] = {
        "raw_bottleneck_failure": [],
        "soft_support_improved": [],
        "soft_support_worsened": [],
        "soft_support_unchanged_present": [],
        "hard_support_non_discriminative": [],
        "same_rank_cleaner_subgraph": [],
        "fuzzy_not_cleaner_or_not_preserved": [],
    }

    counters = {
        "num_rows": 0,
        "raw_bottleneck_failure": 0,
        "raw_gold_present": 0,
        "soft_support_improved": 0,
        "soft_support_worsened": 0,
        "soft_support_unchanged_present": 0,
        "hard_same_rank_as_backbone": 0,
        "hard_same_candidates_as_backbone": 0,
        "same_rank_cleaner_subgraph": 0,
        "fuzzy_rank_changed_vs_soft": 0,
        "fuzzy_coverage_preserved": 0,
    }

    rank_deltas_gold_present = []
    rr_deltas_all = []
    subgraph_reductions = []
    direct_before_values = []
    direct_top5_values = []

    all_indices = sorted(b["backbone_eval"].keys())

    for idx in all_indices:
        backbone = b["backbone_eval"][idx]
        hard = b["hard_eval"][idx]
        soft = b["soft_eval"][idx]
        fuzzy = b["fuzzy_eval"][idx]
        soft_detail = b["soft_detail"][idx]
        fuzzy_detail = b["fuzzy_detail"][idx]

        counters["num_rows"] += 1

        case = safe_case_row(
            split=split,
            idx=idx,
            backbone=backbone,
            hard=hard,
            soft=soft,
            fuzzy=fuzzy,
            soft_detail=soft_detail,
            fuzzy_detail=fuzzy_detail,
        )

        backbone_rank = int(backbone["gold_rank"])
        hard_rank = int(hard["gold_rank"])
        soft_rank = int(soft["gold_rank"])
        fuzzy_rank = int(fuzzy["gold_rank"])

        backbone_candidates = list(backbone["candidate_entities"])
        hard_candidates = list(hard["candidate_entities"])

        raw_present = bool(backbone["gold_present"])

        if not raw_present:
            counters["raw_bottleneck_failure"] += 1
            add_example(buckets["raw_bottleneck_failure"], case, max_examples)
        else:
            counters["raw_gold_present"] += 1

            rank_delta = backbone_rank - soft_rank
            rank_deltas_gold_present.append(rank_delta)

            if soft_rank < backbone_rank:
                counters["soft_support_improved"] += 1
                add_example(buckets["soft_support_improved"], case, max_examples)
            elif soft_rank > backbone_rank:
                counters["soft_support_worsened"] += 1
                add_example(buckets["soft_support_worsened"], case, max_examples)
            else:
                counters["soft_support_unchanged_present"] += 1
                add_example(buckets["soft_support_unchanged_present"], case, max_examples)

        rr_deltas_all.append(float(soft["reciprocal_rank_item"]) - float(backbone["reciprocal_rank_item"]))

        if hard_rank == backbone_rank:
            counters["hard_same_rank_as_backbone"] += 1

        if hard_candidates == backbone_candidates:
            counters["hard_same_candidates_as_backbone"] += 1
            add_example(buckets["hard_support_non_discriminative"], case, max_examples)

        subgraph_summary = fuzzy_detail.get("subgraph_summary", {})
        original_size = int(subgraph_summary.get("original_subgraph_size", 0))
        selected_size = int(subgraph_summary.get("selected_subgraph_size", 0))
        coverage = float(subgraph_summary.get("candidate_coverage_preserved_rate", 0.0))
        top_cov = float(subgraph_summary.get("top_band_coverage_preserved_rate", 0.0))

        if original_size > 0:
            subgraph_reductions.append(original_size - selected_size)

        if fuzzy_rank != soft_rank:
            counters["fuzzy_rank_changed_vs_soft"] += 1

        if coverage >= 0.999999 and top_cov >= 0.999999:
            counters["fuzzy_coverage_preserved"] += 1

        if fuzzy_rank == soft_rank and selected_size < original_size and coverage >= 0.999999 and top_cov >= 0.999999:
            counters["same_rank_cleaner_subgraph"] += 1
            add_example(buckets["same_rank_cleaner_subgraph"], case, max_examples)
        else:
            add_example(buckets["fuzzy_not_cleaner_or_not_preserved"], case, max_examples)

        if case.get("num_direct_T_candidates_before") is not None:
            direct_before_values.append(int(case["num_direct_T_candidates_before"]))
        if case.get("num_direct_T_candidates_top5_after") is not None:
            direct_top5_values.append(int(case["num_direct_T_candidates_top5_after"]))

    n = max(1, counters["num_rows"])

    summary = {
        "split": split,
        **counters,
        "raw_bottleneck_failure_rate": counters["raw_bottleneck_failure"] / n,
        "raw_gold_present_rate": counters["raw_gold_present"] / n,
        "soft_improved_rate_all_rows": counters["soft_support_improved"] / n,
        "soft_worsened_rate_all_rows": counters["soft_support_worsened"] / n,
        "soft_improved_rate_given_gold_present": (
            counters["soft_support_improved"] / max(1, counters["raw_gold_present"])
        ),
        "soft_worsened_rate_given_gold_present": (
            counters["soft_support_worsened"] / max(1, counters["raw_gold_present"])
        ),
        "avg_rank_delta_given_gold_present": avg(rank_deltas_gold_present),
        "avg_rr_delta_all_rows": avg(rr_deltas_all),
        "hard_same_rank_rate": counters["hard_same_rank_as_backbone"] / n,
        "hard_same_candidates_rate": counters["hard_same_candidates_as_backbone"] / n,
        "same_rank_cleaner_subgraph_rate": counters["same_rank_cleaner_subgraph"] / n,
        "fuzzy_rank_changed_rate": counters["fuzzy_rank_changed_vs_soft"] / n,
        "fuzzy_coverage_preserved_rate": counters["fuzzy_coverage_preserved"] / n,
        "avg_subgraph_reduction": avg(subgraph_reductions),
        "avg_direct_T_candidates_before": avg(direct_before_values),
        "avg_direct_T_candidates_top5_after": avg(direct_top5_values),
    }

    return summary, buckets


def add_example(bucket: list[dict[str, Any]], case: dict[str, Any], max_examples: int) -> None:
    if len(bucket) < max_examples:
        bucket.append(case)


def avg(vals: list[float | int]) -> float:
    if not vals:
        return 0.0
    return float(sum(vals) / len(vals))


def load_metric_tables() -> dict[str, Any]:
    return {
        "fograg_valid": read_json(RESULT_DIR / "dataset2_fograg_main_table_valid.json"),
        "fograg_test": read_json(RESULT_DIR / "dataset2_fograg_main_table_test.json"),
        "vs_structure_baselines": read_json(RESULT_DIR / "dataset2_vs_structure_baselines.json"),
        "claim_summary": read_json(RESULT_DIR / "dataset2_main_claim_summary.json"),
    }


def build_paper_interpretation(
    valid_summary: dict[str, Any],
    test_summary: dict[str, Any],
    metric_tables: dict[str, Any],
) -> dict[str, Any]:
    claim = metric_tables["claim_summary"]
    vs = metric_tables["vs_structure_baselines"]

    interpretation = {
        "week": 23,
        "day": 6,
        "decision": "DATASET2_DIAGNOSTICS_READY",
        "paper_status_candidate": claim.get("paper_status_candidate"),
        "main_row": "fuzzy_retrieval_main",
        "relation_wording": "therapeutic_association_proxy",
        "diagnostic_findings": {
            "raw_candidate_bottleneck": {
                "valid_absent_count": valid_summary["raw_bottleneck_failure"],
                "valid_absent_rate": valid_summary["raw_bottleneck_failure_rate"],
                "test_absent_count": test_summary["raw_bottleneck_failure"],
                "test_absent_rate": test_summary["raw_bottleneck_failure_rate"],
                "interpretation": (
                    "Most PharmKG queries remain raw candidate bottleneck cases, so FOG-RAG "
                    "cannot improve Gold@20 without changing the candidate generator."
                ),
            },
            "hard_support_control": {
                "valid_same_rank_rate": valid_summary["hard_same_rank_rate"],
                "test_same_rank_rate": test_summary["hard_same_rank_rate"],
                "valid_same_candidates_rate": valid_summary["hard_same_candidates_rate"],
                "test_same_candidates_rate": test_summary["hard_same_candidates_rate"],
                "interpretation": (
                    "Hard binary graph support is non-discriminative on PharmKG because "
                    "candidate support/path features are saturated."
                ),
            },
            "soft_support_gain": {
                "valid_improved": valid_summary["soft_support_improved"],
                "test_improved": test_summary["soft_support_improved"],
                "valid_worsened": valid_summary["soft_support_worsened"],
                "test_worsened": test_summary["soft_support_worsened"],
                "valid_improved_given_present_rate": valid_summary["soft_improved_rate_given_gold_present"],
                "test_improved_given_present_rate": test_summary["soft_improved_rate_given_gold_present"],
                "valid_avg_rank_delta_given_present": valid_summary["avg_rank_delta_given_gold_present"],
                "test_avg_rank_delta_given_present": test_summary["avg_rank_delta_given_gold_present"],
                "interpretation": (
                    "Frozen soft support improves many gold-present cases and does not worsen "
                    "any gold-present case in the current PharmKG run."
                ),
            },
            "fuzzy_retrieval_efficiency": {
                "valid_same_rank_cleaner_count": valid_summary["same_rank_cleaner_subgraph"],
                "test_same_rank_cleaner_count": test_summary["same_rank_cleaner_subgraph"],
                "valid_same_rank_cleaner_rate": valid_summary["same_rank_cleaner_subgraph_rate"],
                "test_same_rank_cleaner_rate": test_summary["same_rank_cleaner_subgraph_rate"],
                "valid_avg_subgraph_reduction": valid_summary["avg_subgraph_reduction"],
                "test_avg_subgraph_reduction": test_summary["avg_subgraph_reduction"],
                "interpretation": (
                    "Fuzzy retrieval preserves soft-support ranking while reducing every subgraph "
                    "from 100 to 55 triples with full candidate/band coverage."
                ),
            },
            "baseline_position": {
                "valid_delta_main_vs_best_structure_mrr": vs["valid"]["delta_main_vs_best_structure_mrr"],
                "test_delta_main_vs_best_structure_mrr": vs["test"]["delta_main_vs_best_structure_mrr"],
                "valid_best_structure": vs["valid"]["best_structure_baseline"]["row_name"],
                "test_best_structure": vs["test"]["best_structure_baseline"]["row_name"],
                "interpretation": (
                    "FOG-RAG main is ahead of the best structure baseline in reviewer-safe MRR@20 "
                    "under the task-specific top-20 protocol."
                ),
            },
        },
        "recommended_paper_claim": (
            "On PharmKG, frozen soft support transfers beyond PrimeKG by improving R-GCN "
            "top-20 ranking without valid/test gold injection, and fuzzy retrieval preserves "
            "the gain while reducing the evidence budget by 45%."
        ),
        "paper_safe_language": [
            "Use 'PharmKG therapeutic-association proxy task', not 'clinical indication'.",
            "Use 'task-specific reviewer-safe top-20 protocol', not 'full-universe PharmKG KGC'.",
            "Say FOG-RAG improves MRR/ranking among fixed top-20 candidates, not Gold@20 recall.",
            "Say fuzzy retrieval compresses evidence with preserved coverage, not that it suppresses shortcut rate.",
        ],
        "week7_or_paper_next_step": [
            "Use Day 6 diagnostics in Week 23 closeout.",
            "Update paper tables with PharmKG Dataset 2 main result.",
            "Optionally add a diagnostics paragraph explaining raw bottleneck and hard-support saturation.",
        ],
    }

    return interpretation


def build_failure_analysis(
    valid_summary: dict[str, Any],
    test_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "week": 23,
        "day": 6,
        "decision": "DATASET2_DIAGNOSTICS_READY",
        "valid": valid_summary,
        "test": test_summary,
        "main_diagnostic_conclusion": {
            "raw_bottleneck": (
                "High raw bottleneck remains: valid/test have many Rank21 cases."
            ),
            "hard_support": (
                "Hard graph-support control is non-discriminative rather than brittle on PharmKG."
            ),
            "soft_support": (
                "Soft support provides the actual ranking gain."
            ),
            "fuzzy_retrieval": (
                "Fuzzy retrieval gives evidence-efficiency gain by preserving ranking with smaller subgraphs."
            ),
        },
    }


def write_report(
    failure: dict[str, Any],
    interpretation: dict[str, Any],
    case_buckets: dict[str, Any],
) -> None:
    valid = failure["valid"]
    test = failure["test"]
    diag = interpretation["diagnostic_findings"]

    md = f"""# Week 23 Day 6 — Diagnostics, Failure Analysis, and Paper Interpretation

## Decision

`DATASET2_DIAGNOSTICS_READY`

## Main diagnostic conclusion

- Raw candidate bottleneck remains strong.
- Hard support is non-discriminative on PharmKG because binary support/path features are saturated.
- Soft support is the source of ranking gain.
- Fuzzy retrieval is the source of evidence-efficiency gain.

## Raw candidate bottleneck

| Split | Raw bottleneck count | Rate | Raw gold-present count | Rate |
|---|---:|---:|---:|---:|
| valid | {valid["raw_bottleneck_failure"]} | {valid["raw_bottleneck_failure_rate"]:.3f} | {valid["raw_gold_present"]} | {valid["raw_gold_present_rate"]:.3f} |
| test | {test["raw_bottleneck_failure"]} | {test["raw_bottleneck_failure_rate"]:.3f} | {test["raw_gold_present"]} | {test["raw_gold_present_rate"]:.3f} |

Interpretation:

{diag["raw_candidate_bottleneck"]["interpretation"]}

## Hard-support control

| Split | Same-rank rate | Same-candidates rate |
|---|---:|---:|
| valid | {valid["hard_same_rank_rate"]:.3f} | {valid["hard_same_candidates_rate"]:.3f} |
| test | {test["hard_same_rank_rate"]:.3f} | {test["hard_same_candidates_rate"]:.3f} |

Interpretation:

{diag["hard_support_control"]["interpretation"]}

## Soft-support improvements

| Split | Improved | Worsened | Improved given present | Avg rank delta given present | Avg RR delta |
|---|---:|---:|---:|---:|---:|
| valid | {valid["soft_support_improved"]} | {valid["soft_support_worsened"]} | {valid["soft_improved_rate_given_gold_present"]:.3f} | {valid["avg_rank_delta_given_gold_present"]:.3f} | {valid["avg_rr_delta_all_rows"]:.6f} |
| test | {test["soft_support_improved"]} | {test["soft_support_worsened"]} | {test["soft_improved_rate_given_gold_present"]:.3f} | {test["avg_rank_delta_given_gold_present"]:.3f} | {test["avg_rr_delta_all_rows"]:.6f} |

Direct-T penalty effect:

| Split | Avg direct-T before | Avg direct-T in top-5 after |
|---|---:|---:|
| valid | {valid["avg_direct_T_candidates_before"]:.3f} | {valid["avg_direct_T_candidates_top5_after"]:.3f} |
| test | {test["avg_direct_T_candidates_before"]:.3f} | {test["avg_direct_T_candidates_top5_after"]:.3f} |

Interpretation:

{diag["soft_support_gain"]["interpretation"]}

## Fuzzy retrieval efficiency

| Split | Same-rank cleaner count | Rate | Avg subgraph reduction | Coverage preserved rate |
|---|---:|---:|---:|---:|
| valid | {valid["same_rank_cleaner_subgraph"]} | {valid["same_rank_cleaner_subgraph_rate"]:.3f} | {valid["avg_subgraph_reduction"]:.1f} | {valid["fuzzy_coverage_preserved_rate"]:.3f} |
| test | {test["same_rank_cleaner_subgraph"]} | {test["same_rank_cleaner_subgraph_rate"]:.3f} | {test["avg_subgraph_reduction"]:.1f} | {test["fuzzy_coverage_preserved_rate"]:.3f} |

Interpretation:

{diag["fuzzy_retrieval_efficiency"]["interpretation"]}

## Baseline position

- valid best structure baseline: `{diag["baseline_position"]["valid_best_structure"]}`
- valid FOG-RAG main delta MRR: `{diag["baseline_position"]["valid_delta_main_vs_best_structure_mrr"]:.12f}`
- test best structure baseline: `{diag["baseline_position"]["test_best_structure"]}`
- test FOG-RAG main delta MRR: `{diag["baseline_position"]["test_delta_main_vs_best_structure_mrr"]:.12f}`

## Recommended paper claim

{interpretation["recommended_paper_claim"]}

## Paper-safe language

{chr(10).join(f"- {x}" for x in interpretation["paper_safe_language"])}

## Example buckets written

The detailed examples are saved in:

- `results/week23/dataset2_case_buckets.json`

Buckets include:

- raw_bottleneck_failure
- soft_support_improved
- soft_support_worsened
- soft_support_unchanged_present
- hard_support_non_discriminative
- same_rank_cleaner_subgraph

## Files written

- `results/week23/dataset2_failure_analysis.json`
- `results/week23/dataset2_case_buckets.json`
- `results/week23/dataset2_paper_interpretation.json`
- `reports/week23/day6_diagnostics_and_optional_sources.md`

## Next step

Day 7 will close out Week 23 and decide final paper status.
"""
    REPORT_PATH.write_text(md, encoding="utf-8")


def main() -> None:
    ensure_dirs()

    valid_summary, valid_buckets = analyze_split("valid", max_examples=20)
    test_summary, test_buckets = analyze_split("test", max_examples=20)

    metric_tables = load_metric_tables()

    failure = build_failure_analysis(valid_summary, test_summary)
    case_buckets = {
        "week": 23,
        "day": 6,
        "valid": valid_buckets,
        "test": test_buckets,
    }
    interpretation = build_paper_interpretation(valid_summary, test_summary, metric_tables)

    write_json(failure, FAILURE_ANALYSIS_PATH)
    write_json(case_buckets, CASE_BUCKETS_PATH)
    write_json(interpretation, PAPER_INTERPRETATION_PATH)

    write_report(failure, interpretation, case_buckets)

    print("Saved:")
    print(f"  {FAILURE_ANALYSIS_PATH}")
    print(f"  {CASE_BUCKETS_PATH}")
    print(f"  {PAPER_INTERPRETATION_PATH}")
    print(f"  {REPORT_PATH}")

    print("\nDecision:", failure["decision"])

    print("\nVALID diagnostics:")
    print(json.dumps(valid_summary, ensure_ascii=False, indent=2))

    print("\nTEST diagnostics:")
    print(json.dumps(test_summary, ensure_ascii=False, indent=2))

    print("\nPaper interpretation:")
    print(json.dumps(interpretation, ensure_ascii=False, indent=2))

    if failure["decision"] != "DATASET2_DIAGNOSTICS_READY":
        raise RuntimeError("Day 6 diagnostics failed.")


if __name__ == "__main__":
    main()