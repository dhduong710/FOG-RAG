#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


def compute_final_metrics(eval_rows):
    num_queries = len(eval_rows)
    rows_with_any_contra = 0
    total_contra = 0
    total_candidate_size = 0
    gold_in_final = 0

    for row in eval_rows:
        flags = row.get("contra_flags_final", [])
        contra_count = sum(int(x) for x in flags)
        total_contra += contra_count
        if contra_count > 0:
            rows_with_any_contra += 1
        total_candidate_size += int(row.get("candidate_count_final", len(row.get("candidate_drugs_final", []))))
        gold_in_final += int(row.get("row_has_gold_in_topk", 0))

    return {
        "SafetyViolation@final": rows_with_any_contra / num_queries if num_queries else 0.0,
        "Contra@final": total_contra / num_queries if num_queries else 0.0,
        "AvgCandidateSize": total_candidate_size / num_queries if num_queries else 0.0,
        "GoldInFinalListRate": gold_in_final / num_queries if num_queries else 0.0,
        "RowsWithContraFinal": rows_with_any_contra,
    }


def flatten_row(name, metrics_payload, eval_rows):
    ranking = metrics_payload["ranking_metrics"]
    sb = metrics_payload["setting_b_metrics"]
    final_m = compute_final_metrics(eval_rows)
    return {
        "row_name": name,
        "mrr": ranking["mrr"],
        "hits1": ranking["hits1"],
        "hits3": ranking["hits3"],
        "hits10": ranking["hits10"],
        "SafetyViolation@10": sb["SafetyViolation@10"],
        "Contra@10": sb["Contra@10"],
        "ConstraintViolationRate@10": sb["ConstraintViolationRate@10"],
        "QueryHasConstraintViolationRate@10": sb["QueryHasConstraintViolationRate@10"],
        "GoldInTopKRate": sb["GoldInTopKRate"],
        "SafetyViolation@final": final_m["SafetyViolation@final"],
        "Contra@final": final_m["Contra@final"],
        "AvgCandidateSize": final_m["AvgCandidateSize"],
        "GoldInFinalListRate": final_m["GoldInFinalListRate"],
        "RowsWithContraFinal": final_m["RowsWithContraFinal"],
    }


def decide_between_hard_and_soft(hard, soft):
    # Ưu tiên final-list safety -> ranking -> GoldInFinalListRate
    hard_key = (
        -hard["SafetyViolation@final"],
        -hard["Contra@final"],
        hard["mrr"],
        hard["hits10"],
        hard["GoldInFinalListRate"],
    )
    soft_key = (
        -soft["SafetyViolation@final"],
        -soft["Contra@final"],
        soft["mrr"],
        soft["hits10"],
        soft["GoldInFinalListRate"],
    )

    if hard_key >= soft_key:
        return {
            "main_row": "hard_main",
            "supporting_row": "soft_best",
            "reason": "hard_main is at least as safe as soft_best on final-list test metrics and is not worse on ranking.",
        }
    return {
        "main_row": "soft_best",
        "supporting_row": "hard_main",
        "reason": "soft_best provides the better final test trade-off under the fixed rule.",
    }


def main():
    rows = [
        flatten_row(
            "backbone",
            load_json("results/week11_test/backbone_test/metrics.json"),
            load_json("dataset/setting_b/06_eval_week11_test/test_backbone_eval.json"),
        ),
        flatten_row(
            "ontology",
            load_json("results/week11_test/ontology_test/metrics.json"),
            load_json("dataset/setting_b/06_eval_week11_test/test_ontology_eval.json"),
        ),
        flatten_row(
            "hard_main",
            load_json("results/week11_test/hard_main_test/metrics.json"),
            load_json("dataset/setting_b/06_eval_week11_test/test_hard_main_eval.json"),
        ),
        flatten_row(
            "soft_best",
            load_json("results/week11_test/soft_best_test/metrics.json"),
            load_json("dataset/setting_b/06_eval_week11_test/test_soft_best_eval.json"),
        ),
    ]

    by_name = {r["row_name"]: r for r in rows}
    decision = decide_between_hard_and_soft(by_name["hard_main"], by_name["soft_best"])

    payload = {
        "rows": rows,
        "decision": decision,
    }
    save_json(payload, "results/week11_test/variant_comparison_test.json")

    md = []
    md.append("# Novelty 1 Test Comparison")
    md.append("")
    md.append("| Row | MRR | Hits@1 | Hits@3 | Hits@10 | SafetyViolation@10 | Contra@10 | SafetyViolation@final | Contra@final | GoldInFinalListRate |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        md.append(
            f"| {r['row_name']} | {r['mrr']:.6f} | {r['hits1']:.6f} | {r['hits3']:.6f} | {r['hits10']:.6f} | "
            f"{r['SafetyViolation@10']:.6f} | {r['Contra@10']:.6f} | {r['SafetyViolation@final']:.6f} | "
            f"{r['Contra@final']:.6f} | {r['GoldInFinalListRate']:.6f} |"
        )
    md.append("")
    md.append("## Decision")
    md.append(f"- main_row: `{decision['main_row']}`")
    md.append(f"- supporting_row: `{decision['supporting_row']}`")
    md.append(f"- reason: {decision['reason']}")
    md.append("")

    Path("reports/week11").mkdir(parents=True, exist_ok=True)
    with open("reports/week11/dayX_test_check_before_closeout.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("Saved: results/week11_test/variant_comparison_test.json")
    print("Saved: reports/week11/dayX_test_check_before_closeout.md")
    print("Decision:", decision)


if __name__ == "__main__":
    main()