#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from pathlib import Path


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def evaluate_setting_b(rows, k=10):
    num_queries = len(rows)

    safety_violation_queries = 0
    contra_count_total = 0

    constraint_violation_queries = 0
    constraint_violation_slots = 0
    total_slots = 0

    gold_in_topk = 0

    safety_cases = []
    constraint_cases = []
    gold_missing_cases = []
    clean_cases = []

    for row in rows:
        cands = row.get("candidate_drugs_final", [])
        cand_types = row.get("candidate_types_final", [])
        contra_flags = row.get("contra_flags_final", [])
        conflict_flags = row.get("conflict_flags_final", [])

        topk = min(k, len(cands))
        top_cands = cands[:topk]
        top_types = cand_types[:topk]
        top_contra = contra_flags[:topk]
        top_conflict = conflict_flags[:topk] if isinstance(conflict_flags, list) else [0] * topk

        total_slots += topk

        # Safety
        query_contra_count = sum(int(x) for x in top_contra)
        contra_count_total += query_contra_count
        if query_contra_count > 0:
            safety_violation_queries += 1

        # Constraint: type-validity only
        query_constraint_count = 0
        for t in top_types:
            if t != "Drug":
                query_constraint_count += 1
        constraint_violation_slots += query_constraint_count
        if query_constraint_count > 0:
            constraint_violation_queries += 1

        # ranking side
        gold_in_topk += int(row.get("row_has_gold_in_topk", 0))

        # cases
        case = {
            "query_disease": row.get("query_disease"),
            "gold_drug": row.get("gold_drug"),
            "candidate_count_final": row.get("candidate_count_final"),
            "top10_candidates": top_cands,
            "top10_types": top_types,
            "top10_contra_flags": top_contra,
            "top10_conflict_flags": top_conflict,
            "row_has_gold_in_topk": row.get("row_has_gold_in_topk", 0),
        }

        if query_contra_count > 0 and len(safety_cases) < 20:
            safety_cases.append(case)

        if query_constraint_count > 0 and len(constraint_cases) < 20:
            constraint_cases.append(case)

        if row.get("row_has_gold_in_topk", 0) == 0 and len(gold_missing_cases) < 20:
            gold_missing_cases.append(case)

        if (
            query_contra_count == 0
            and query_constraint_count == 0
            and row.get("row_has_gold_in_topk", 0) == 1
            and len(clean_cases) < 20
        ):
            clean_cases.append(case)

    metrics = {
        "num_queries": num_queries,
        "K": k,
        "SafetyViolation@10": safety_violation_queries / num_queries if num_queries else 0.0,
        "Contra@10": contra_count_total / num_queries if num_queries else 0.0,
        "ConstraintViolationRate@10": constraint_violation_slots / total_slots if total_slots else 0.0,
        "QueryHasConstraintViolationRate@10": constraint_violation_queries / num_queries if num_queries else 0.0,
        "GoldInTopKRate": gold_in_topk / num_queries if num_queries else 0.0,
    }

    cases = {
        "safety_violation_cases": safety_cases,
        "constraint_violation_cases": constraint_cases,
        "gold_missing_cases": gold_missing_cases,
        "clean_cases": clean_cases,
    }
    return metrics, cases


def write_report(path, row_name, ranking_metrics, setting_b_metrics, cases):
    lines = []
    lines.append(f"# Week 11 - Day 3 Setting B Valid ({row_name})")
    lines.append("")
    lines.append("## Ranking metrics")
    for k, v in ranking_metrics.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Setting B metrics")
    for k, v in setting_b_metrics.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Case summary")
    lines.append(f"- safety_violation_cases: {len(cases['safety_violation_cases'])}")
    lines.append(f"- constraint_violation_cases: {len(cases['constraint_violation_cases'])}")
    lines.append(f"- gold_missing_cases: {len(cases['gold_missing_cases'])}")
    lines.append(f"- clean_cases: {len(cases['clean_cases'])}")
    lines.append("")
    lines.append("## Notes")
    lines.append("- Day 3 prioritizes the main candidate row under the frozen Setting B protocol.")
    lines.append("- Day 4 will run the same evaluation on soft_best for trade-off comparison.")
    lines.append("")

    write_path = Path(path)
    write_path.parent.mkdir(parents=True, exist_ok=True)
    with open(write_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval_json", required=True)
    parser.add_argument("--ranking_json", required=True)
    parser.add_argument("--out_dir", required=True)
    parser.add_argument("--row_name", required=True)
    parser.add_argument("--report_md", required=True)
    parser.add_argument("--k", type=int, default=10)
    args = parser.parse_args()

    rows = load_json(args.eval_json)
    ranking_metrics = load_json(args.ranking_json)

    setting_b_metrics, cases = evaluate_setting_b(rows, k=args.k)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "row_name": args.row_name,
        "ranking_metrics": ranking_metrics,
        "setting_b_metrics": setting_b_metrics,
    }

    save_json(payload, out_dir / "metrics.json")
    save_json(cases, out_dir / "case_samples.json")
    write_report(args.report_md, args.row_name, ranking_metrics, setting_b_metrics, cases)

    print(f"Saved: {out_dir / 'metrics.json'}")
    print(f"Saved: {out_dir / 'case_samples.json'}")
    print(f"Saved: {args.report_md}")
    print("ranking_metrics =", ranking_metrics)
    print("setting_b_metrics =", setting_b_metrics)


if __name__ == "__main__":
    main()