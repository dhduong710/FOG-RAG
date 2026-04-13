#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path


def build_protocol():
    protocol = {
        "week": 10,
        "title": "Novelty 1 safety phase: hard filtering + soft penalization on ontology-supported branch",
        "goal": (
            "Attach contraindication-aware handling to the week9 ontology-supported candidate branch "
            "without changing the backbone or moving beyond candidate-stage intervention."
        ),
        "references": {
            "backbone_reference": "week7-v2",
            "ontology_reference": "week9_ontology_only",
            "week9_role": "groundwork_supporting_row"
        },
        "novelty_injection_point": "candidate_stage_only",
        "decision_split": "valid",
        "test_usage": "not_used_for_decision_week10",
        "non_goals": [
            "no_fuzzy_confidence",
            "no_fuzzy_retrieval",
            "no_fuzzy_graph_encoder",
            "no_backbone_change",
            "no_test_based_decision",
            "no_final_setting_b_claims"
        ],
        "rows": [
            {
                "row_id": "backbone",
                "source": "week7-v2",
                "description": "Main backbone reference row"
            },
            {
                "row_id": "ontology",
                "source": "week9_ontology_only",
                "description": "Ontology-supported reference row"
            },
            {
                "row_id": "ontology_hard",
                "source": "week10_hard_main",
                "description": "Ontology-supported + contraindication-aware hard filtering"
            },
            {
                "row_id": "ontology_soft",
                "source": "week10_soft_best",
                "description": "Ontology-supported + contraindication-aware soft penalization"
            }
        ],
        "hard_policy": {
            "variants": ["hard_strict", "hard_main"],
            "hard_strict_definition": (
                "Keep only ontology-supported and non-contra candidates; if empty, remain empty."
            ),
            "hard_main_definition": (
                "Keep ontology-supported and non-contra candidates; if empty, fallback only to "
                "non-contra candidates from the type-filtered list."
            ),
            "fallback_policy": {
                "enabled_for": ["hard_main"],
                "source": "type_filtered_non_contra_only",
                "allow_reintroduce_contra": False,
                "notes": "Fallback must never reintroduce contraindicated candidates."
            }
        },
        "soft_policy": {
            "base_row": "week9_ontology_only",
            "candidate_set_behavior": "keep_candidate_set",
            "contra_behavior": "demote_contra_candidates_only",
            "lambda_sweep": [0.25, 0.5, 1.0, 2.0],
            "selection_rule": (
                "Choose soft_best as the lambda that gives the best safety-ranking trade-off "
                "on valid without making the branch too conservative."
            )
        },
        "artifacts": {
            "candidate_dir": "dataset/setting_a/19_contra_aware",
            "setting_b_support_dir": "dataset/setting_b/04_contra_checked",
            "results_dir": "results/week10",
            "reports_dir": "reports/week10"
        },
        "expected_candidate_artifacts": [
            "valid_top20_hard_strict.json",
            "valid_top20_hard_main.json",
            "valid_top20_soft_lambda_0.25.json",
            "valid_top20_soft_lambda_0.5.json",
            "valid_top20_soft_lambda_1.0.json",
            "valid_top20_soft_lambda_2.0.json",
            "valid_top20_soft_best.json",
            "hard_filter_report.json",
            "soft_penalty_sweep_report.json",
            "contra_candidate_flags_valid.json"
        ],
        "main_ranking_metrics": [
            "MRR",
            "Hits@1",
            "Hits@3",
            "Hits@10"
        ],
        "main_safety_proxy_metrics": [
            "contra_candidates_final",
            "QueryHasContraCandidateRate",
            "strict_empty_after_hard",
            "fallback_after_hard",
            "fallback_after_soft",
            "gold_in_topk",
            "avg_candidate_size",
            "hard_removed_candidates",
            "soft_demoted_contra_candidates"
        ],
        "supporting_analysis": [
            "direct_only_queries",
            "mechanism_only_queries",
            "mixed_support_queries",
            "gold_lost_by_hard",
            "gold_saved_by_soft",
            "error_case_review_10_to_20_cases"
        ],
        "not_main_metrics_this_week": [
            "SafetyViolation@10",
            "Contra@10",
            "final_setting_b_test_numbers",
            "fuzzy_path_confidence_metrics"
        ],
        "week11_handoff_rule": {
            "main_candidate_row_must_be_one_of": ["hard_main", "soft_best"],
            "selection_priority": (
                "Prefer the row that is clearly cleaner than backbone/week9 while remaining usable "
                "for week11 Setting B evaluation."
            )
        }
    }
    return protocol


def build_markdown(protocol: dict) -> str:
    lines = []
    lines.append("# Week 10 - Day 1 Protocol Freeze")
    lines.append("")
    lines.append("## 1. Goal")
    lines.append(protocol["goal"])
    lines.append("")
    lines.append("## 2. Main references")
    lines.append(f"- Backbone reference: `{protocol['references']['backbone_reference']}`")
    lines.append(f"- Ontology reference: `{protocol['references']['ontology_reference']}`")
    lines.append(f"- Week9 role: `{protocol['references']['week9_role']}`")
    lines.append("")
    lines.append("## 3. Injection point")
    lines.append(f"- Novelty injection point: `{protocol['novelty_injection_point']}`")
    lines.append(f"- Decision split: `{protocol['decision_split']}`")
    lines.append(f"- Test usage: `{protocol['test_usage']}`")
    lines.append("")
    lines.append("## 4. Rows to compare this week")
    for row in protocol["rows"]:
        lines.append(f"- `{row['row_id']}`: {row['description']} (source={row['source']})")
    lines.append("")
    lines.append("## 5. Hard policy")
    lines.append(f"- Variants: {', '.join(protocol['hard_policy']['variants'])}")
    lines.append(f"- hard_strict: {protocol['hard_policy']['hard_strict_definition']}")
    lines.append(f"- hard_main: {protocol['hard_policy']['hard_main_definition']}")
    lines.append(f"- Fallback source: `{protocol['hard_policy']['fallback_policy']['source']}`")
    lines.append(
        f"- Reintroduce contraindicated candidates allowed? "
        f"`{protocol['hard_policy']['fallback_policy']['allow_reintroduce_contra']}`"
    )
    lines.append("")
    lines.append("## 6. Soft policy")
    lines.append(f"- Base row: `{protocol['soft_policy']['base_row']}`")
    lines.append(f"- Candidate set behavior: `{protocol['soft_policy']['candidate_set_behavior']}`")
    lines.append(f"- Contra behavior: `{protocol['soft_policy']['contra_behavior']}`")
    lines.append(f"- Lambda sweep: {protocol['soft_policy']['lambda_sweep']}")
    lines.append("")
    lines.append("## 7. Main metrics for week10")
    lines.append("### Ranking")
    for x in protocol["main_ranking_metrics"]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("### Safety proxy")
    for x in protocol["main_safety_proxy_metrics"]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## 8. Not main metrics this week")
    for x in protocol["not_main_metrics_this_week"]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## 9. Week11 handoff rule")
    lines.append(
        f"- Main row for week11 must be selected from: "
        f"{protocol['week11_handoff_rule']['main_candidate_row_must_be_one_of']}"
    )
    lines.append(f"- Selection priority: {protocol['week11_handoff_rule']['selection_priority']}")
    lines.append("")
    return "\n".join(lines)


def main():
    protocol = build_protocol()

    report_dir = Path("reports/week10")
    result_dir = Path("results/week10")
    script_dir = Path("scripts/week10")

    report_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)
    script_dir.mkdir(parents=True, exist_ok=True)

    protocol_path = result_dir / "novelty1_safety_protocol.json"
    report_path = report_dir / "day1_protocol_freeze.md"

    with protocol_path.open("w", encoding="utf-8") as f:
        json.dump(protocol, f, indent=2, ensure_ascii=False)

    md = build_markdown(protocol)
    with report_path.open("w", encoding="utf-8") as f:
        f.write(md)

    print(f"Saved: {protocol_path}")
    print(f"Saved: {report_path}")
    print("Rows:", [x["row_id"] for x in protocol["rows"]])
    print("Soft lambdas:", protocol["soft_policy"]["lambda_sweep"])
    print("Decision split:", protocol["decision_split"])


if __name__ == "__main__":
    main()