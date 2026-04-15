from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    protocol = {
        "week": 12,
        "theme": "fixed_confidence_fuzzy_retrieval",
        "goal": "Apply fixed-confidence fuzzy retrieval on top of the hard-main branch without changing candidate generation.",
        "main_reference_rows": {
            "backbone": "week7_v2_backbone",
            "main_novelty1": "ontology_hard",
            "supporting_novelty1": "ontology_soft"
        },
        "novelty2_injection_point": {
            "candidate_generation_changed": False,
            "ontology_filtering_changed": False,
            "hard_soft_logic_changed": False,
            "subgraph_retrieval_changed": True,
            "fuzzy_graph_encoder_changed": False,
            "llm_backbone_changed": False
        },
        "comparison_rows_week12": [
            "backbone",
            "ontology_hard",
            "ontology_hard_fuzzy_retrieval"
        ],
        "optional_rows": [
            "ontology_soft_fuzzy_retrieval"
        ],
        "decision_split": {
            "primary": "valid",
            "test_used_for_decision": False
        },
        "out_of_scope": [
            "learned_confidence",
            "fuzzy_graph_encoder",
            "candidate_stage_redesign",
            "llm_change",
            "test_side_final_claim"
        ],
        "metrics": {
            "ranking": ["mrr", "hits1", "hits3", "hits10"],
            "retrieval_evidence": [
                "avg_subgraph_size",
                "avg_retained_path_count",
                "avg_path_confidence",
                "avg_path_relevance",
                "low_confidence_drop_rate",
                "ontology_valid_retained_path_rate"
            ]
        },
        "base_artifacts": {
            "dev_valid_package": "dataset/setting_a/19_contra_aware_eval_ready/hard_main",
            "official_frozen_package": "dataset/setting_a/20_test_rerun_eval_ready/hard_main"
        },
        "success_conditions": [
            "fuzzy retrieval branch runs cleanly on valid",
            "ranking does not collapse",
            "retrieval artifacts are traceable",
            "subgraph/path quality is more interpretable",
            "tau/path-budget sensitivity is feasible"
        ],
        "failure_conditions": [
            "protocol changes mid-week",
            "candidate generation is changed accidentally",
            "valid and test are mixed",
            "confidence design is not explainable",
            "retrieval artifacts are not traceable"
        ]
    }

    out_dir = Path("results/week12/protocol_freeze")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / "novelty2_week12_protocol.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(protocol, f, indent=2, ensure_ascii=False)

    input_registry = {
        "expected_inputs": [
            "dataset/setting_a/19_contra_aware_eval_ready/hard_main/train.json",
            "dataset/setting_a/19_contra_aware_eval_ready/hard_main/valid.json",
            "dataset/setting_a/19_contra_aware_eval_ready/hard_main/test.json",
            "dataset/setting_a/20_test_rerun_eval_ready/hard_main/train.json",
            "dataset/setting_a/20_test_rerun_eval_ready/hard_main/valid.json",
            "dataset/setting_a/20_test_rerun_eval_ready/hard_main/test.json"
        ]
    }

    registry_path = out_dir / "input_registry.json"
    with registry_path.open("w", encoding="utf-8") as f:
        json.dump(input_registry, f, indent=2, ensure_ascii=False)

    print(f"Saved protocol to: {out_path}")
    print(f"Saved input registry to: {registry_path}")


if __name__ == "__main__":
    main()