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


def build_row(row_name, payload, role_in_story, paper_position):
    ranking = payload["ranking_metrics"]
    sb = payload["setting_b_metrics"]
    return {
        "row_name": row_name,
        "role_in_story": role_in_story,
        "paper_position": paper_position,
        "MRR": ranking["mrr"],
        "Hits@1": ranking["hits1"],
        "Hits@3": ranking["hits3"],
        "Hits@10": ranking["hits10"],
        "SafetyViolation@10": sb["SafetyViolation@10"],
        "Contra@10": sb["Contra@10"],
        "ConstraintViolationRate@10": sb["ConstraintViolationRate@10"],
        "QueryHasConstraintViolationRate@10": sb["QueryHasConstraintViolationRate@10"],
        "GoldInTopKRate": sb["GoldInTopKRate"],
    }


def fmt(x):
    if isinstance(x, float):
        return f"{x:.6f}"
    return str(x)


def main():
    backbone = load_json("results/week11/backbone_valid/metrics.json")
    ontology = load_json("results/week11/ontology_valid/metrics.json")
    hard_main = load_json("results/week11/hard_main_valid/metrics.json")
    soft_best = load_json("results/week11/soft_best_valid/metrics.json")
    variant_decision = load_json("results/week11/variant_comparison.json")

    rows = [
        build_row("backbone", backbone, "reference", "main_table_reference"),
        build_row("ontology", ontology, "intermediate_ablation", "main_table_ablation"),
        build_row("hard_main", hard_main, "main_variant", "main_table_main_row"),
        build_row("soft_best", soft_best, "supporting_ablation", "main_table_supporting_row"),
    ]

    payload = {
        "title": "Novelty 1 ablation v1",
        "rows": rows,
        "decision": variant_decision["decision"],
        "main_takeaways": [
            "The ontology-only row is more conservative than backbone and loses substantial ranking coverage.",
            "The hard_main row recovers ranking relative to ontology while remaining fully clean on Setting B @10.",
            "The soft_best row does not outperform hard_main and is therefore kept as a supporting ablation.",
        ],
    }

    save_json(payload, "results/week11/ablation_novelty1_v1.json")

    md = []
    md.append("# Ablation v1 - Novelty 1")
    md.append("")
    md.append("| Row | Story Role | MRR | Hits@1 | Hits@3 | Hits@10 | SafetyViolation@10 | Contra@10 | ConstraintViolationRate@10 | QueryHasConstraintViolationRate@10 | GoldInTopKRate |")
    md.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        md.append(
            f"| {r['row_name']} | {r['role_in_story']} | "
            f"{fmt(r['MRR'])} | {fmt(r['Hits@1'])} | {fmt(r['Hits@3'])} | {fmt(r['Hits@10'])} | "
            f"{fmt(r['SafetyViolation@10'])} | {fmt(r['Contra@10'])} | "
            f"{fmt(r['ConstraintViolationRate@10'])} | {fmt(r['QueryHasConstraintViolationRate@10'])} | "
            f"{fmt(r['GoldInTopKRate'])} |"
        )
    md.append("")
    md.append("## Main decision")
    md.append(f"- main_row: `{variant_decision['decision']['main_row']}`")
    md.append(f"- supporting_row: `{variant_decision['decision']['supporting_row']}`")
    md.append(f"- reason: {variant_decision['decision']['reason']}")
    md.append("")
    md.append("## Main takeaways")
    for x in payload["main_takeaways"]:
        md.append(f"- {x}")
    md.append("")

    Path("results/week11").mkdir(parents=True, exist_ok=True)
    with open("results/week11/ablation_novelty1_v1.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    rpt = []
    rpt.append("# Week 11 - Day 6 Ablation")
    rpt.append("")
    rpt.append("## Goal")
    rpt.append("Build the first clean ablation table for Novelty 1 and prepare the week11 closeout.")
    rpt.append("")
    rpt.append("## Rows included")
    for r in rows:
        rpt.append(f"- {r['row_name']}: {r['role_in_story']}")
    rpt.append("")
    rpt.append("## Decision reused from Day 5")
    rpt.append(f"- main_row: `{variant_decision['decision']['main_row']}`")
    rpt.append(f"- supporting_row: `{variant_decision['decision']['supporting_row']}`")
    rpt.append(f"- reason: {variant_decision['decision']['reason']}")
    rpt.append("")
    rpt.append("## Interpretation")
    rpt.append("- backbone is the high-coverage reference row.")
    rpt.append("- ontology is the conservative intermediate row that demonstrates the cost of ontology-only filtering.")
    rpt.append("- hard_main is the main safety-aware row because it stays clean on Setting B while recovering ranking relative to ontology.")
    rpt.append("- soft_best remains useful as a supporting ablation but does not beat hard_main.")
    rpt.append("")
    rpt.append("## Output files")
    rpt.append("- results/week11/ablation_novelty1_v1.json")
    rpt.append("- results/week11/ablation_novelty1_v1.md")
    rpt.append("")

    Path("reports/week11").mkdir(parents=True, exist_ok=True)
    with open("reports/week11/day6_ablation.md", "w", encoding="utf-8") as f:
        f.write("\n".join(rpt))

    print("Saved: results/week11/ablation_novelty1_v1.json")
    print("Saved: results/week11/ablation_novelty1_v1.md")
    print("Saved: reports/week11/day6_ablation.md")
    print("Decision:", variant_decision["decision"])


if __name__ == "__main__":
    main()