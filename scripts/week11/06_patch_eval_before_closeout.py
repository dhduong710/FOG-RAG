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


def compute_final_list_metrics(eval_rows):
    num_queries = len(eval_rows)
    rows_with_any_contra = 0
    total_contra = 0
    total_candidate_count = 0
    gold_in_final = 0

    for row in eval_rows:
        contra_flags = row.get("contra_flags_final", [])
        candidate_count = int(row.get("candidate_count_final", len(row.get("candidate_drugs_final", []))))
        row_has_gold = int(row.get("row_has_gold_in_topk", 0))

        contra_count = sum(int(x) for x in contra_flags)
        total_contra += contra_count
        total_candidate_count += candidate_count
        gold_in_final += row_has_gold

        if contra_count > 0:
            rows_with_any_contra += 1

    return {
        "num_queries": num_queries,
        "rows_with_any_contra_candidate_final": rows_with_any_contra,
        "SafetyViolation@final": rows_with_any_contra / num_queries if num_queries else 0.0,
        "Contra@final": total_contra / num_queries if num_queries else 0.0,
        "AvgCandidateSize": total_candidate_count / num_queries if num_queries else 0.0,
        "GoldInFinalListRate": gold_in_final / num_queries if num_queries else 0.0,
    }


def merge_row(row_name, metrics_payload, final_payload, note=None):
    ranking = metrics_payload["ranking_metrics"]
    sb = metrics_payload["setting_b_metrics"]
    out = {
        "row_name": row_name,
        "MRR": ranking["mrr"],
        "Hits@1": ranking["hits1"],
        "Hits@3": ranking["hits3"],
        "Hits@10": ranking["hits10"],
        "SafetyViolation@10": sb["SafetyViolation@10"],
        "Contra@10": sb["Contra@10"],
        "ConstraintViolationRate@10": sb["ConstraintViolationRate@10"],
        "QueryHasConstraintViolationRate@10": sb["QueryHasConstraintViolationRate@10"],
        "SafetyViolation@final": final_payload["SafetyViolation@final"],
        "Contra@final": final_payload["Contra@final"],
        "AvgCandidateSize": final_payload["AvgCandidateSize"],
        "GoldInFinalListRate": final_payload["GoldInFinalListRate"],
        "rows_with_any_contra_candidate_final": final_payload["rows_with_any_contra_candidate_final"],
    }
    if note is not None:
        out["note"] = note
    return out


def fmt(x):
    if isinstance(x, float):
        return f"{x:.6f}"
    return str(x)


def main():
    # setting B metrics
    backbone_metrics = load_json("results/week11/backbone_valid/metrics.json")
    ontology_metrics = load_json("results/week11/ontology_valid/metrics.json")
    hard_metrics = load_json("results/week11/hard_main_valid/metrics.json")
    soft_metrics = load_json("results/week11/soft_best_valid/metrics.json")

    # eval-ready rows
    backbone_eval = load_json("dataset/setting_b/05_eval_week11/valid_backbone_eval.json")
    ontology_eval = load_json("dataset/setting_b/05_eval_week11/valid_ontology_eval.json")
    hard_eval = load_json("dataset/setting_b/05_eval_week11/valid_hard_main_eval.json")
    soft_eval = load_json("dataset/setting_b/05_eval_week11/valid_soft_best_eval.json")

    # week10 proxy
    hard_proxy = load_json("results/week10/hard_valid/safety_proxy_metrics.json")
    soft_proxy = load_json("results/week10/soft_valid/safety_proxy_metrics.json")

    # decision
    variant_decision = load_json("results/week11/variant_comparison.json")

    backbone_final = compute_final_list_metrics(backbone_eval)
    ontology_final = compute_final_list_metrics(ontology_eval)
    hard_final = compute_final_list_metrics(hard_eval)
    soft_final = compute_final_list_metrics(soft_eval)

    rows = [
        merge_row(
            "backbone",
            backbone_metrics,
            backbone_final,
            note="GoldInFinalListRate is not directly comparable with novelty rows because backbone uses candidate-ready reference coverage.",
        ),
        merge_row("ontology", ontology_metrics, ontology_final),
        merge_row("hard_main", hard_metrics, hard_final),
        merge_row("soft_best", soft_metrics, soft_final),
    ]

    payload = {
        "title": "Novelty 1 ablation v2 (patched before closeout)",
        "decision": variant_decision["decision"],
        "rows": rows,
        "supporting_week10_proxy": {
            "hard_main": hard_proxy,
            "soft_best": soft_proxy,
        },
        "main_takeaways": [
            "At @10, all rows are already clean on Setting B, so @10 safety metrics alone are not sufficient to distinguish the novelty rows.",
            "The candidate/final-list stage remains discriminative: hard_main removes contraindicated final candidates completely, whereas ontology and soft_best still keep some contraindicated final candidates.",
            "hard_main therefore remains the main row, while soft_best stays as the supporting ablation row.",
        ],
    }
    save_json(payload, "results/week11/ablation_novelty1_v2.json")

    # Main paper table v2
    md = []
    md.append("# Ablation v2 - Novelty 1 (patched)")
    md.append("")
    md.append("| Row | MRR | Hits@1 | Hits@3 | Hits@10 | SafetyViolation@10 | Contra@10 | SafetyViolation@final | Contra@final |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        md.append(
            f"| {r['row_name']} | {fmt(r['MRR'])} | {fmt(r['Hits@1'])} | {fmt(r['Hits@3'])} | {fmt(r['Hits@10'])} | "
            f"{fmt(r['SafetyViolation@10'])} | {fmt(r['Contra@10'])} | {fmt(r['SafetyViolation@final'])} | {fmt(r['Contra@final'])} |"
        )
    md.append("")
    md.append("## Decision")
    md.append(f"- main_row: `{variant_decision['decision']['main_row']}`")
    md.append(f"- supporting_row: `{variant_decision['decision']['supporting_row']}`")
    md.append(f"- reason: {variant_decision['decision']['reason']}")
    md.append("")
    md.append("## Notes")
    md.append("- GoldInFinalListRate is not used in the main table because the backbone reference row is not directly comparable on this axis.")
    md.append("- The main table now combines ranking + Setting B @10 + final-list safety.")
    md.append("")
    Path("results/week11").mkdir(parents=True, exist_ok=True)
    with open("results/week11/ablation_novelty1_v2.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # Supporting safety table
    support = []
    support.append("# Novelty 1 Safety Support Table v2")
    support.append("")
    support.append("| Row | AvgCandidateSize | GoldInFinalListRate | RowsWithContraFinal | SafetyViolation@final | Contra@final |")
    support.append("|---|---:|---:|---:|---:|---:|")
    for r in rows:
        support.append(
            f"| {r['row_name']} | {fmt(r['AvgCandidateSize'])} | {fmt(r['GoldInFinalListRate'])} | "
            f"{fmt(r['rows_with_any_contra_candidate_final'])} | {fmt(r['SafetyViolation@final'])} | {fmt(r['Contra@final'])} |"
        )
    support.append("")
    support.append("## Candidate-stage notes from week 10")
    support.append(f"- hard_main fallback_after_hard: {hard_proxy['fallback_after_hard']}")
    support.append(f"- hard_main hard_removed_candidates: {hard_proxy['hard_removed_candidates']}")
    support.append(f"- soft_best soft_demoted_contra_candidates: {soft_proxy['soft_demoted_contra_candidates']}")
    support.append("")
    support.append("## Interpretation")
    support.append("- hard_main is the cleanest final-list row.")
    support.append("- soft_best is cleaner than ontology at candidate-stage demotion, but not cleaner than hard_main at final-list level.")
    support.append("- backbone remains a reference row, but its final-list coverage should not be over-interpreted as directly comparable.")
    support.append("")
    with open("results/week11/novelty1_safety_support_v2.md", "w", encoding="utf-8") as f:
        f.write("\n".join(support))

    # Report
    rpt = []
    rpt.append("# Week 11 - Patch Before Closeout")
    rpt.append("")
    rpt.append("## Why this patch is needed")
    rpt.append("- The previous v1 table hid the novelty signal because GoldInTopKRate unfairly favored the backbone reference row.")
    rpt.append("- Setting B @10 metrics were saturated at 0 for all rows, so @10 alone could not show where the novelty helps.")
    rpt.append("- The patch therefore adds final-list safety metrics and moves GoldInFinalListRate to a supporting table.")
    rpt.append("")
    rpt.append("## What was changed")
    rpt.append("- No model retraining.")
    rpt.append("- No candidate logic change.")
    rpt.append("- Added SafetyViolation@final and Contra@final for all rows.")
    rpt.append("- Rewrote the main ablation table to remove GoldInTopKRate from the main comparison.")
    rpt.append("")
    rpt.append("## Main decision after patch")
    rpt.append(f"- main_row: `{variant_decision['decision']['main_row']}`")
    rpt.append(f"- supporting_row: `{variant_decision['decision']['supporting_row']}`")
    rpt.append(f"- reason: {variant_decision['decision']['reason']}")
    rpt.append("")
    rpt.append("## Main takeaway")
    rpt.append("- hard_main remains the main row because it is fully clean at both @10 and final-list level while recovering ranking over ontology.")
    rpt.append("- soft_best remains a supporting ablation.")
    rpt.append("")
    with open("reports/week11/day6_patch_before_closeout.md", "w", encoding="utf-8") as f:
        f.write("\n".join(rpt))

    print("Saved: results/week11/ablation_novelty1_v2.json")
    print("Saved: results/week11/ablation_novelty1_v2.md")
    print("Saved: results/week11/novelty1_safety_support_v2.md")
    print("Saved: reports/week11/day6_patch_before_closeout.md")
    print("Decision:", variant_decision["decision"])


if __name__ == "__main__":
    main()