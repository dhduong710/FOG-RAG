#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path


def build_protocol():
    protocol = {
        "week": 11,
        "title": "Setting B evaluation + variant decision + ablation v1",
        "goal": (
            "Evaluate Novelty 1 on Setting B using valid-first protocol, "
            "compare backbone / ontology / hard_main / soft_best, "
            "and choose the main paper variant before moving to month 4."
        ),
        "references": {
            "backbone_reference": "week7-v2",
            "ontology_reference": "week9_ontology_only",
            "safety_main_candidate": "week10_hard_main",
            "safety_supporting_candidate": "week10_soft_best",
        },
        "rows": [
            {
                "row_id": "backbone",
                "source": "week7-v2",
                "role": "reference",
                "description": "Backbone reference row evaluated under Setting B protocol",
            },
            {
                "row_id": "ontology",
                "source": "week9_ontology_only",
                "role": "reference",
                "description": "Ontology-only supporting row",
            },
            {
                "row_id": "hard_main",
                "source": "week10_hard_main",
                "role": "main_candidate",
                "description": "Ontology + contraindication-aware hard filtering row",
            },
            {
                "row_id": "soft_best",
                "source": "week10_soft_best",
                "role": "supporting_candidate",
                "description": "Ontology + contraindication-aware soft penalty row",
            },
        ],
        "evaluation_scope": {
            "setting": "Setting B",
            "decision_split": "valid",
            "test_policy": "run_only_after_valid_protocol_is_clean",
            "novelty_injection_point": "candidate_stage_only",
            "retrain_backbone": False,
        },
        "main_metrics": {
            "ranking": [
                "MRR",
                "Hits@1",
                "Hits@3",
                "Hits@10",
            ],
            "safety": [
                "SafetyViolation@10",
                "Contra@10",
            ],
            "constraint": [
                "ConstraintViolationRate",
                "QueryHasConstraintViolationRate",
            ],
        },
        "deliverables_this_week": [
            "setting_b_valid_metrics_for_all_rows",
            "variant_comparison_json",
            "ablation_novelty1_v1_md",
            "week11_closeout",
        ],
        "non_goals": [
            "no_new_fuzzy_module",
            "no_hard_soft_logic_rewrite",
            "no_backbone_retraining",
            "no_new_structure_baseline",
            "no_final_acceptance_claim",
        ],
        "decision_rule": {
            "default_main_variant": "hard_main",
            "supporting_variant": "soft_best",
            "main_selection_rule": (
                "Prefer the row that keeps ranking stable while improving Setting B safety "
                "and constraint metrics most clearly."
            ),
            "override_condition": (
                "Only replace hard_main if soft_best produces clearly better end-to-end "
                "Setting B trade-off or hard_main shows unacceptable fallback artifacts."
            ),
        },
        "expected_outputs": {
            "results_dirs": [
                "results/week11/backbone_valid",
                "results/week11/ontology_valid",
                "results/week11/hard_main_valid",
                "results/week11/soft_best_valid",
            ],
            "comparison_files": [
                "results/week11/variant_comparison.json",
                "results/week11/ablation_novelty1_v1.json",
                "results/week11/ablation_novelty1_v1.md",
            ],
            "reports": [
                "reports/week11/day1_protocol_freeze.md",
            ],
        },
    }
    return protocol


def build_markdown(protocol):
    lines = []
    lines.append("# Week 11 - Day 1 Protocol Freeze")
    lines.append("")
    lines.append("## 1. Goal")
    lines.append(protocol["goal"])
    lines.append("")
    lines.append("## 2. References")
    lines.append(f"- Backbone reference: `{protocol['references']['backbone_reference']}`")
    lines.append(f"- Ontology reference: `{protocol['references']['ontology_reference']}`")
    lines.append(f"- Safety main candidate: `{protocol['references']['safety_main_candidate']}`")
    lines.append(f"- Safety supporting candidate: `{protocol['references']['safety_supporting_candidate']}`")
    lines.append("")
    lines.append("## 3. Rows to compare")
    for row in protocol["rows"]:
        lines.append(
            f"- `{row['row_id']}` ({row['role']}): {row['description']} [source={row['source']}]"
        )
    lines.append("")
    lines.append("## 4. Evaluation scope")
    lines.append(f"- Setting: `{protocol['evaluation_scope']['setting']}`")
    lines.append(f"- Decision split: `{protocol['evaluation_scope']['decision_split']}`")
    lines.append(f"- Test policy: `{protocol['evaluation_scope']['test_policy']}`")
    lines.append(f"- Novelty injection point: `{protocol['evaluation_scope']['novelty_injection_point']}`")
    lines.append(f"- Retrain backbone: `{protocol['evaluation_scope']['retrain_backbone']}`")
    lines.append("")
    lines.append("## 5. Main metrics")
    lines.append("### Ranking")
    for x in protocol["main_metrics"]["ranking"]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("### Safety")
    for x in protocol["main_metrics"]["safety"]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("### Constraint")
    for x in protocol["main_metrics"]["constraint"]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## 6. Non-goals")
    for x in protocol["non_goals"]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## 7. Decision rule")
    lines.append(f"- Default main variant: `{protocol['decision_rule']['default_main_variant']}`")
    lines.append(f"- Supporting variant: `{protocol['decision_rule']['supporting_variant']}`")
    lines.append(f"- Main selection rule: {protocol['decision_rule']['main_selection_rule']}")
    lines.append(f"- Override condition: {protocol['decision_rule']['override_condition']}")
    lines.append("")
    lines.append("## 8. Expected outputs")
    lines.append("### Results directories")
    for x in protocol["expected_outputs"]["results_dirs"]:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("### Comparison files")
    for x in protocol["expected_outputs"]["comparison_files"]:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## 9. End-of-week target")
    lines.append("- Have a clean Setting B valid comparison table.")
    lines.append("- Choose the main paper variant.")
    lines.append("- Produce ablation v1 for Novelty 1.")
    lines.append("")
    return "\n".join(lines)


def main():
    protocol = build_protocol()

    Path("reports/week11").mkdir(parents=True, exist_ok=True)
    Path("results/week11").mkdir(parents=True, exist_ok=True)
    Path("scripts/week11").mkdir(parents=True, exist_ok=True)

    protocol_path = Path("results/week11/setting_b_eval_protocol.json")
    report_path = Path("reports/week11/day1_protocol_freeze.md")

    with open(protocol_path, "w", encoding="utf-8") as f:
        json.dump(protocol, f, indent=2, ensure_ascii=False)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(build_markdown(protocol))

    print(f"Saved: {protocol_path}")
    print(f"Saved: {report_path}")
    print("Rows =", [x["row_id"] for x in protocol["rows"]])
    print("Decision split =", protocol["evaluation_scope"]["decision_split"])
    print("Default main variant =", protocol["decision_rule"]["default_main_variant"])


if __name__ == "__main__":
    main()