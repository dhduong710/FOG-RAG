#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def fmt(x):
    if isinstance(x, float):
        return f"{x:.6f}"
    return str(x)


def main():
    # references
    week7_backbone = load_json("results/week7/backbone_valid_v2_short/valid_eval_v2/eval_valid_v2_metrics.json")
    week9_ontology = load_json("results/week9/ontology_only_valid/ranking_metrics.json")
    week10_hard_rank = load_json("results/week10/hard_valid/ranking_metrics.json")
    week10_hard_safe = load_json("results/week10/hard_valid/safety_proxy_metrics.json")
    week10_soft_rank = load_json("results/week10/soft_valid/ranking_metrics.json")
    week10_soft_safe = load_json("results/week10/soft_valid/safety_proxy_metrics.json")
    week10_day6 = load_json("results/week10/safety_error_cases.json")

    decision = week10_day6["decision"]
    summary = week10_day6["summary"]

    # safety ablation table
    ablation_md = []
    ablation_md.append("# Week 10 Safety Ablation v0")
    ablation_md.append("")
    ablation_md.append("| Row | MRR | Hits@1 | Hits@3 | Hits@10 | ContraFinal | QueryHasContraRate | GoldInTopKRate | FallbackAfterHard | SoftDemotedContra |")
    ablation_md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    ablation_md.append(
        f"| Backbone (week7-v2) | {fmt(week7_backbone['mrr'])} | {fmt(week7_backbone['hits1'])} | {fmt(week7_backbone['hits3'])} | {fmt(week7_backbone['hits10'])} | - | - | - | - | - |"
    )
    ablation_md.append(
        f"| + Ontology (week9) | {fmt(week9_ontology['mrr'])} | {fmt(week9_ontology['hits1'])} | {fmt(week9_ontology['hits3'])} | {fmt(week9_ontology['hits10'])} | 73 | 0.076000 | 0.292000 | 0 | 0 |"
    )
    ablation_md.append(
        f"| + Ontology + Hard | {fmt(week10_hard_rank['mrr'])} | {fmt(week10_hard_rank['hits1'])} | {fmt(week10_hard_rank['hits3'])} | {fmt(week10_hard_rank['hits10'])} | {fmt(week10_hard_safe['contra_candidates_final'])} | {fmt(week10_hard_safe['QueryHasContraCandidateRate'])} | {fmt(week10_hard_safe['gold_in_topk_rate'])} | {fmt(week10_hard_safe['fallback_after_hard'])} | 0 |"
    )
    ablation_md.append(
        f"| + Ontology + Soft | {fmt(week10_soft_rank['mrr'])} | {fmt(week10_soft_rank['hits1'])} | {fmt(week10_soft_rank['hits3'])} | {fmt(week10_soft_rank['hits10'])} | {fmt(week10_soft_safe['contra_candidates_final'])} | {fmt(week10_soft_safe['QueryHasContraCandidateRate'])} | {fmt(week10_soft_safe['gold_in_topk_rate'])} | 0 | {fmt(week10_soft_safe['soft_demoted_contra_candidates'])} |"
    )
    ablation_md.append("")
    ablation_md.append("## Main takeaway")
    ablation_md.append(f"- main_row: `{decision['main_row']}`")
    ablation_md.append(f"- supporting_row: `{decision['supporting_row']}`")
    ablation_md.append(f"- reason: {decision['reason']}")
    ablation_md.append("")

    write_text("results/week10/safety_ablation_v0.md", "\n".join(ablation_md))

    closeout = []
    closeout.append("# Week 10 Closeout")
    closeout.append("")
    closeout.append("## 1. Goal of week 10")
    closeout.append(
        "Week 10 attached contraindication-aware handling to the ontology-supported branch from week 9, "
        "without changing the backbone. Two branches were evaluated: hard_main and soft_best."
    )
    closeout.append("")
    closeout.append("## 2. Main results")
    closeout.append(f"- hard_main ranking: {week10_hard_rank}")
    closeout.append(f"- soft_best ranking: {week10_soft_rank}")
    closeout.append(f"- hard_main safety proxy: {week10_hard_safe}")
    closeout.append(f"- soft_best safety proxy: {week10_soft_safe}")
    closeout.append("")
    closeout.append("## 3. Error review summary")
    for k, v in summary.items():
        closeout.append(f"- {k}: {v}")
    closeout.append("")
    closeout.append("## 4. Decision")
    closeout.append(f"- main_row: {decision['main_row']}")
    closeout.append(f"- supporting_row: {decision['supporting_row']}")
    closeout.append(f"- reason: {decision['reason']}")
    closeout.append("")
    closeout.append("## 5. Interpretation")
    closeout.append(
        "- hard_main is selected as the main week11 candidate because it fully removes contraindicated final candidates "
        "while keeping the same ranking metrics as soft_best."
    )
    closeout.append(
        "- soft_best remains useful as a supporting ablation because it demonstrates a softer trade-off without empty rows, "
        "but it still keeps contraindicated final candidates."
    )
    closeout.append(
        "- hard_main still uses fallback in a small number of queries, so week11 should include targeted case review "
        "to make sure fallback outputs remain interpretable."
    )
    closeout.append("")
    closeout.append("## 6. Handoff to week 11")
    closeout.append("- Main row for week 11: hard_main")
    closeout.append("- Supporting ablation row: soft_best")
    closeout.append("- Main metrics for week 11:")
    closeout.append("  - MRR / Hits@1 / Hits@3 / Hits@10")
    closeout.append("  - SafetyViolation@10")
    closeout.append("  - Contra@10")
    closeout.append("  - ConstraintViolationRate")
    closeout.append("  - QueryHasConstraintViolationRate")
    closeout.append("- Split priority: valid first, test only after the valid protocol is stable.")
    closeout.append("")
    closeout.append("## 7. Final status")
    closeout.append("CONDITIONAL GO to week 11.")
    closeout.append("")

    write_text("reports/week10/day7_week10_closeout.md", "\n".join(closeout))

    print("Saved: results/week10/safety_ablation_v0.md")
    print("Saved: reports/week10/day7_week10_closeout.md")
    print("Decision:", decision)
    print("Final status: CONDITIONAL GO to week 11")


if __name__ == "__main__":
    main()