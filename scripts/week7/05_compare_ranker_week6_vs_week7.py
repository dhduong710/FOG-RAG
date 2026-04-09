#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 7 - Day 4
Compare week6 vs week7 candidate retrieval quality directly on the same valid queries.

Inputs:
- dataset/setting_a/09_real_coarse_ranker/valid_top20_raw.json
- dataset/setting_a/09_real_coarse_ranker/valid_top20_drkgc_ready.json
- dataset/setting_a/09_real_coarse_ranker/candidate_recall_report.json
- dataset/setting_a/11_ranker_v2/valid_top20_raw.json
- dataset/setting_a/11_ranker_v2/valid_top20_drkgc_ready.json
- dataset/setting_a/11_ranker_v2/candidate_report.json

Outputs:
- reports/week7/day4_compare_summary.json
- reports/week7/day4_improved_cases.tsv
- reports/week7/day4_worsened_cases.tsv
- reports/week7/day4_rank_distribution_comparison.json
- reports/week7/day4_compare_week6_vs_week7.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections import Counter
from statistics import mean, median
from typing import Any, Dict, List, Tuple


# ============================================================
# Utilities
# ============================================================

def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def safe_div(a: float, b: float) -> float:
    return float(a) / float(b) if b else 0.0


def row_key(ex: Dict[str, Any]) -> Tuple[int, int]:
    return (int(ex["query_entity_id"]), int(ex["gold_entity_id"]))


def write_tsv(path: Path, rows: List[Dict[str, Any]], columns: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("\t".join(columns) + "\n")
        for r in rows:
            vals = []
            for c in columns:
                v = r.get(c, "")
                if isinstance(v, list):
                    v = " | ".join(str(x) for x in v)
                vals.append(str(v))
            f.write("\t".join(vals) + "\n")


# ============================================================
# Core comparison
# ============================================================

def align_rows(
    w6_raw: List[Dict[str, Any]],
    w6_ready: List[Dict[str, Any]],
    w7_raw: List[Dict[str, Any]],
    w7_ready: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    w6_raw_map = {row_key(x): x for x in w6_raw}
    w6_ready_map = {row_key(x): x for x in w6_ready}
    w7_raw_map = {row_key(x): x for x in w7_raw}
    w7_ready_map = {row_key(x): x for x in w7_ready}

    keys = sorted(set(w6_raw_map.keys()) & set(w6_ready_map.keys()) & set(w7_raw_map.keys()) & set(w7_ready_map.keys()))
    aligned = []

    for k in keys:
        a = w6_raw_map[k]
        b = w6_ready_map[k]
        c = w7_raw_map[k]
        d = w7_ready_map[k]

        aligned.append(
            {
                "query_entity": a["query_entity"],
                "query_entity_id": a["query_entity_id"],
                "gold_entity": a["gold_entity"],
                "gold_entity_id": a["gold_entity_id"],

                "w6_gold_rank_in_full_universe": a["gold_rank_in_full_universe"],
                "w7_gold_rank_in_full_universe": c["gold_rank_in_full_universe"],

                "w6_gold_in_top20_raw": bool(a["gold_in_topk_raw"]),
                "w7_gold_in_top20_raw": bool(c["gold_in_topk_raw"]),

                "w6_gold_in_top20_ready": bool(b["gold_in_topk_ready"]),
                "w7_gold_in_top20_ready": bool(d["gold_in_topk_ready"]),

                "w6_gold_injected": bool(b["gold_injected"]),
                "w7_gold_injected": bool(d["gold_injected"]),

                "w6_raw_top5": a["candidate_entities"][:5],
                "w7_raw_top5": c["candidate_entities"][:5],

                "w6_raw_top20": a["candidate_entities"],
                "w7_raw_top20": c["candidate_entities"],
            }
        )
    return aligned


def classify_case(row: Dict[str, Any]) -> str:
    w6_hit = row["w6_gold_in_top20_raw"]
    w7_hit = row["w7_gold_in_top20_raw"]

    if (not w6_hit) and w7_hit:
        return "improved_to_top20"
    if w6_hit and (not w7_hit):
        return "worsened_out_of_top20"
    if (not w6_hit) and (not w7_hit):
        return "still_missing"
    return "still_hit"


def compare_rows(aligned_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    category_counter = Counter()
    inject_transition_counter = Counter()

    rank_deltas = []
    improved_cases = []
    worsened_cases = []
    still_missing_cases = []
    inject_removed_cases = []
    inject_still_needed_cases = []

    for row in aligned_rows:
        category = classify_case(row)
        category_counter[category] += 1

        if row["w6_gold_injected"] and not row["w7_gold_injected"]:
            inject_transition_counter["inject_removed"] += 1
            inject_removed_cases.append(row)
        elif row["w6_gold_injected"] and row["w7_gold_injected"]:
            inject_transition_counter["inject_still_needed"] += 1
            inject_still_needed_cases.append(row)
        elif (not row["w6_gold_injected"]) and row["w7_gold_injected"]:
            inject_transition_counter["inject_newly_needed"] += 1
        else:
            inject_transition_counter["never_injected"] += 1

        delta_rank = row["w6_gold_rank_in_full_universe"] - row["w7_gold_rank_in_full_universe"]
        row["delta_rank"] = delta_rank
        rank_deltas.append(delta_rank)

        if category == "improved_to_top20" or delta_rank >= 20:
            improved_cases.append(row)
        elif category == "worsened_out_of_top20" or delta_rank <= -20:
            worsened_cases.append(row)
        elif category == "still_missing":
            still_missing_cases.append(row)

    improved_cases = sorted(improved_cases, key=lambda x: (-x["delta_rank"], x["w7_gold_rank_in_full_universe"]))
    worsened_cases = sorted(worsened_cases, key=lambda x: (x["delta_rank"], -x["w7_gold_rank_in_full_universe"]))
    still_missing_cases = sorted(still_missing_cases, key=lambda x: x["w7_gold_rank_in_full_universe"])
    inject_removed_cases = sorted(inject_removed_cases, key=lambda x: (-x["delta_rank"], x["w7_gold_rank_in_full_universe"]))
    inject_still_needed_cases = sorted(inject_still_needed_cases, key=lambda x: x["w7_gold_rank_in_full_universe"])

    return {
        "category_counts": dict(category_counter),
        "inject_transition_counts": dict(inject_transition_counter),
        "rank_delta_summary": {
            "mean_delta_rank": mean(rank_deltas) if rank_deltas else 0.0,
            "median_delta_rank": median(rank_deltas) if rank_deltas else 0.0,
            "num_positive_delta": sum(1 for x in rank_deltas if x > 0),
            "num_zero_delta": sum(1 for x in rank_deltas if x == 0),
            "num_negative_delta": sum(1 for x in rank_deltas if x < 0),
        },
        "improved_cases": improved_cases[:50],
        "worsened_cases": worsened_cases[:50],
        "still_missing_cases": still_missing_cases[:50],
        "inject_removed_cases": inject_removed_cases[:50],
        "inject_still_needed_cases": inject_still_needed_cases[:50],
    }


def build_summary(
    week6_report: Dict[str, Any],
    week7_report: Dict[str, Any],
    compare_stats: Dict[str, Any],
) -> Dict[str, Any]:
    w6 = week6_report["splits"]["valid"]
    w7 = week7_report["splits"]["valid"]

    summary = {
        "week6_valid": {
            "recall_at_20_raw": w6["recall_at_k_raw"],
            "top1_hit_ratio_raw": w6["top1_hit_ratio_raw"],
            "inject_ratio_ready": w6["inject_ratio_ready"],
            "unique_top1_count_raw": w6.get("unique_top1_count_raw", None),
            "top1_dominance_ratio_raw": w6.get("top1_dominance_ratio_raw", None),
        },
        "week7_valid": {
            "recall_at_20_raw": w7["recall_at_k_raw"],
            "top1_hit_ratio_raw": w7["top1_hit_ratio_raw"],
            "inject_ratio_ready": w7["inject_ratio_ready"],
            "unique_top1_count_raw": w7.get("unique_top1_count_raw", None),
            "top1_dominance_ratio_raw": w7.get("top1_dominance_ratio_raw", None),
        },
        "delta_valid": {
            "delta_recall_at_20_raw": round(w7["recall_at_k_raw"] - w6["recall_at_k_raw"], 6),
            "delta_top1_hit_ratio_raw": round(w7["top1_hit_ratio_raw"] - w6["top1_hit_ratio_raw"], 6),
            "delta_inject_ratio_ready": round(w7["inject_ratio_ready"] - w6["inject_ratio_ready"], 6),
            "delta_unique_top1_count_raw": (
                (w7.get("unique_top1_count_raw") or 0) - (w6.get("unique_top1_count_raw") or 0)
            ),
            "delta_top1_dominance_ratio_raw": round(
                (w7.get("top1_dominance_ratio_raw") or 0.0) - (w6.get("top1_dominance_ratio_raw") or 0.0),
                6
            ),
        },
        "per_query_comparison": {
            "category_counts": compare_stats["category_counts"],
            "inject_transition_counts": compare_stats["inject_transition_counts"],
            "rank_delta_summary": compare_stats["rank_delta_summary"],
        },
    }
    return summary


def write_markdown_report(
    md_path: Path,
    summary: Dict[str, Any],
    compare_stats: Dict[str, Any],
) -> None:
    w6 = summary["week6_valid"]
    w7 = summary["week7_valid"]
    d = summary["delta_valid"]
    cats = compare_stats["category_counts"]
    injects = compare_stats["inject_transition_counts"]
    rank_delta = compare_stats["rank_delta_summary"]

    lines = []
    lines.append("# Day 4 — Direct comparison: week6 vs week7 candidate retrieval on valid")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Compare week6 and week7 candidate retrieval artifacts directly on the same valid queries.")
    lines.append("- Quantify retrieval improvement, inject reduction, and remaining collapse.")
    lines.append("")

    lines.append("## Aggregate comparison")
    lines.append("")
    lines.append(f"- week6_valid_recall@20_raw = `{w6['recall_at_20_raw']}`")
    lines.append(f"- week7_valid_recall@20_raw = `{w7['recall_at_20_raw']}`")
    lines.append(f"- delta_recall@20_raw = `{d['delta_recall_at_20_raw']}`")
    lines.append("")
    lines.append(f"- week6_valid_top1_hit_ratio_raw = `{w6['top1_hit_ratio_raw']}`")
    lines.append(f"- week7_valid_top1_hit_ratio_raw = `{w7['top1_hit_ratio_raw']}`")
    lines.append(f"- delta_top1_hit_ratio_raw = `{d['delta_top1_hit_ratio_raw']}`")
    lines.append("")
    lines.append(f"- week6_valid_inject_ratio_ready = `{w6['inject_ratio_ready']}`")
    lines.append(f"- week7_valid_inject_ratio_ready = `{w7['inject_ratio_ready']}`")
    lines.append(f"- delta_inject_ratio_ready = `{d['delta_inject_ratio_ready']}`")
    lines.append("")
    lines.append(f"- week6_valid_unique_top1_count_raw = `{w6['unique_top1_count_raw']}`")
    lines.append(f"- week7_valid_unique_top1_count_raw = `{w7['unique_top1_count_raw']}`")
    lines.append(f"- delta_unique_top1_count_raw = `{d['delta_unique_top1_count_raw']}`")
    lines.append("")
    lines.append(f"- week6_valid_top1_dominance_ratio_raw = `{w6['top1_dominance_ratio_raw']}`")
    lines.append(f"- week7_valid_top1_dominance_ratio_raw = `{w7['top1_dominance_ratio_raw']}`")
    lines.append(f"- delta_top1_dominance_ratio_raw = `{d['delta_top1_dominance_ratio_raw']}`")
    lines.append("")

    lines.append("## Per-query transitions")
    lines.append("")
    lines.append(f"- improved_to_top20 = `{cats.get('improved_to_top20', 0)}`")
    lines.append(f"- worsened_out_of_top20 = `{cats.get('worsened_out_of_top20', 0)}`")
    lines.append(f"- still_missing = `{cats.get('still_missing', 0)}`")
    lines.append(f"- still_hit = `{cats.get('still_hit', 0)}`")
    lines.append("")
    lines.append(f"- inject_removed = `{injects.get('inject_removed', 0)}`")
    lines.append(f"- inject_still_needed = `{injects.get('inject_still_needed', 0)}`")
    lines.append(f"- inject_newly_needed = `{injects.get('inject_newly_needed', 0)}`")
    lines.append(f"- never_injected = `{injects.get('never_injected', 0)}`")
    lines.append("")

    lines.append("## Rank delta summary")
    lines.append("")
    lines.append(f"- mean_delta_rank = `{rank_delta['mean_delta_rank']}`")
    lines.append(f"- median_delta_rank = `{rank_delta['median_delta_rank']}`")
    lines.append(f"- num_positive_delta = `{rank_delta['num_positive_delta']}`")
    lines.append(f"- num_zero_delta = `{rank_delta['num_zero_delta']}`")
    lines.append(f"- num_negative_delta = `{rank_delta['num_negative_delta']}`")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("- Week 7 is clearly better than week 6 on valid if recall@20_raw rises and inject_ratio_ready drops.")
    lines.append("- If improved_to_top20 is much larger than worsened_out_of_top20, retrieval quality genuinely improved.")
    lines.append("- If top1_dominance_ratio_raw remains high, score collapse is still a concern even after improvement.")
    lines.append("- Day 5 should package backbone-ready v2 only after accepting that week7 retrieval is truly better but not fully solved.")
    lines.append("")

    md_path.parent.mkdir(parents=True, exist_ok=True)
    with md_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--week6-dir",
        default="dataset/setting_a/09_real_coarse_ranker",
        help="Directory for week6 candidate artifacts",
    )
    parser.add_argument(
        "--week7-dir",
        default="dataset/setting_a/11_ranker_v2",
        help="Directory for week7 candidate artifacts",
    )
    parser.add_argument(
        "--report-dir",
        default="reports/week7",
        help="Output report dir",
    )
    args = parser.parse_args()

    week6_dir = Path(args.week6_dir)
    week7_dir = Path(args.week7_dir)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    w6_raw = load_json(week6_dir / "valid_top20_raw.json")
    w6_ready = load_json(week6_dir / "valid_top20_drkgc_ready.json")
    w6_report = load_json(week6_dir / "candidate_recall_report.json")

    w7_raw = load_json(week7_dir / "valid_top20_raw.json")
    w7_ready = load_json(week7_dir / "valid_top20_drkgc_ready.json")
    w7_report = load_json(week7_dir / "candidate_report.json")

    aligned = align_rows(w6_raw, w6_ready, w7_raw, w7_ready)
    compare_stats = compare_rows(aligned)
    summary = build_summary(w6_report, w7_report, compare_stats)

    save_json(report_dir / "day4_compare_summary.json", summary)
    save_json(report_dir / "day4_rank_distribution_comparison.json", {
        "week6_valid_rank_distribution_raw_top50": w6_report["splits"]["valid"]["rank_distribution_raw_top50"],
        "week7_valid_rank_distribution_raw_top50": w7_report["splits"]["valid"]["rank_distribution_raw_top50"],
    })

    improved_cols = [
        "query_entity", "gold_entity",
        "w6_gold_rank_in_full_universe", "w7_gold_rank_in_full_universe", "delta_rank",
        "w6_gold_in_top20_raw", "w7_gold_in_top20_raw",
        "w6_gold_injected", "w7_gold_injected",
        "w6_raw_top5", "w7_raw_top5",
    ]
    write_tsv(report_dir / "day4_improved_cases.tsv", compare_stats["improved_cases"], improved_cols)
    write_tsv(report_dir / "day4_worsened_cases.tsv", compare_stats["worsened_cases"], improved_cols)

    write_markdown_report(
        md_path=report_dir / "day4_compare_week6_vs_week7.md",
        summary=summary,
        compare_stats=compare_stats,
    )

    print("Saved:")
    print(f"- {report_dir / 'day4_compare_summary.json'}")
    print(f"- {report_dir / 'day4_rank_distribution_comparison.json'}")
    print(f"- {report_dir / 'day4_improved_cases.tsv'}")
    print(f"- {report_dir / 'day4_worsened_cases.tsv'}")
    print(f"- {report_dir / 'day4_compare_week6_vs_week7.md'}")


if __name__ == "__main__":
    main()