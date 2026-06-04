from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    protocol = {
        "week": "12A",
        "theme": "rgcn_retriever_rescue_before_novelty2",
        "goal": "Check whether a finetuned R-GCN coarse retriever reduces gold-injection dependence enough to justify resetting the candidate-source base before Novelty 2.",
        "frozen_protocol": {
            "task": "head_prediction_(?, indication, disease)",
            "candidate_universe": "drug_only",
            "k": 20,
            "decision_split": "valid",
            "test_used_for_decision_before_go": False
        },
        "artifact_layers": {
            "top20_raw": "true retrieval quality",
            "top20_drkgc_ready": "reranker-ready artifact with explicit gold injection logging"
        },
        "current_reference": {
            "retriever_dir": "dataset/setting_a/11_ranker_v2",
            "backbone_ready_dir": "dataset/setting_a/12_backbone_ready_ranker_v2",
            "valid_metrics": {
                "recall_at_20_raw": 0.192,
                "inject_ratio_ready": 0.808,
                "top1_hit_ratio_raw": 0.018
            }
        },
        "frozen_later_reference_rows": {
            "backbone": "current_backbone_reference",
            "novelty1_main": "ontology_hard"
        },
        "go_no_go_gate": {
            "no_go": {
                "recall_at_20_raw_lt": 0.25,
                "inject_ratio_ready_gt": 0.75
            },
            "conditional_go": {
                "recall_at_20_raw_gte": 0.25,
                "recall_at_20_raw_lt": 0.35,
                "inject_ratio_ready_gte": 0.65,
                "inject_ratio_ready_lte": 0.75,
                "requires_extra_signals": [
                    "top1_improvement",
                    "diversity_or_collapse_improvement"
                ]
            },
            "strong_go": {
                "recall_at_20_raw_gte": 0.35,
                "inject_ratio_ready_lte": 0.65,
                "requires": [
                    "short_valid_backbone_rerun_not_collapsed"
                ]
            }
        },
        "allowed_if_go": [
            "build_new_candidate_artifacts",
            "build_new_backbone_ready_package",
            "run_short_valid_backbone_rerun"
        ],
        "out_of_scope": [
            "novelty2",
            "fuzzy_retrieval",
            "fuzzy_graph_encoder",
            "ontology_redesign",
            "hard_soft_redesign",
            "llm_change",
            "paper_final_claim"
        ]
    }

    current_reference_registry = {
        "required_existing_inputs": [
            "dataset/setting_a/11_ranker_v2/valid_scores.pt",
            "dataset/setting_a/11_ranker_v2/valid_top20_raw.json",
            "dataset/setting_a/11_ranker_v2/valid_top20_drkgc_ready.json",
            "dataset/setting_a/12_backbone_ready_ranker_v2/train.json",
            "dataset/setting_a/12_backbone_ready_ranker_v2/valid.json",
            "dataset/setting_a/12_backbone_ready_ranker_v2/test.json"
        ]
    }

    out_dir = Path("results/week12A/protocol_freeze")
    out_dir.mkdir(parents=True, exist_ok=True)

    protocol_path = out_dir / "retriever_rescue_protocol.json"
    registry_path = out_dir / "current_reference_registry.json"

    with protocol_path.open("w", encoding="utf-8") as f:
        json.dump(protocol, f, indent=2, ensure_ascii=False)

    with registry_path.open("w", encoding="utf-8") as f:
        json.dump(current_reference_registry, f, indent=2, ensure_ascii=False)

    print(f"Saved protocol to: {protocol_path}")
    print(f"Saved reference registry to: {registry_path}")


if __name__ == "__main__":
    main()