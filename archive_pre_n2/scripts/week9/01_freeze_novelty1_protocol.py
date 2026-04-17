import json
from pathlib import Path

ROOT = Path(".")
REPORT_DIR = ROOT / "reports" / "week9"
RESULT_DIR = ROOT / "results" / "week9"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

protocol = {
    "week": 9,
    "title": "Type filtering + schema validity groundwork for Novelty 1",
    "novelty_name": "ontology_only",
    "task": "head prediction (?, indication, disease)",
    "setting_anchor": "Setting A remains the fairness anchor",
    "backbone_reference": "week7-v2",
    "supporting_analysis_reference": "week8_posthoc_debias_only",
    "novelty_injection_point": "candidate_stage_only",
    "week_scope": [
        "freeze_protocol_for_novelty1",
        "type_filtering_drug_only",
        "schema_validity_check_for_candidate_path_evidence",
        "build_ontology_only_variant",
        "valid_side_sanity_evaluation"
    ],
    "variants": [
        "backbone",
        "backbone_plus_ontology"
    ],
    "decision_split": "valid",
    "test_usage": "artifact_prep_only",
    "ranking_metrics": [
        "MRR",
        "Hits@1",
        "Hits@3",
        "Hits@10"
    ],
    "constraint_metrics": [
        "ConstraintViolationRate",
        "remaining_non_drug_candidates",
        "invalid_paths_or_evidence_patterns"
    ],
    "supporting_analysis": [
        "filtered_candidate_count",
        "empty_query_count_after_filtering",
        "top1_dominance_ratio",
        "unique_top1_count",
        "error_cases_sample"
    ],
    "non_goals": [
        "fuzzy_confidence",
        "fuzzy_retrieval",
        "backbone_change",
        "hard_filter",
        "soft_penalty",
        "test_based_decision",
        "new_structure_baselines"
    ],
    "ontology_only_definition": {
        "candidate_type_constraint": "Drug_only",
        "schema_checks": [
            "candidate_type_validity",
            "path_domain_range_validity",
            "evidence_pattern_validity"
        ]
    },
    "week10_dependency": [
        "hard_filter",
        "soft_penalty"
    ],
    "go_condition": "ontology_only_branch_clean_traceable_ready_for_week10"
}

out_path = RESULT_DIR / "novelty1_protocol.json"
out_path.write_text(
    json.dumps(protocol, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Saved: {out_path}")
print("Summary:")
print(" - backbone_reference:", protocol["backbone_reference"])
print(" - novelty_injection_point:", protocol["novelty_injection_point"])
print(" - variants:", protocol["variants"])
print(" - decision_split:", protocol["decision_split"])
print(" - non_goals:", ", ".join(protocol["non_goals"]))