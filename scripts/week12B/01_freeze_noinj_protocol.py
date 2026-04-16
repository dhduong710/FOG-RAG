from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    protocol = {
        "week": "12B",
        "theme": "no_injection_rerun_for_novelty1",
        "goal": "Evaluate Novelty 1 more transparently on raw R-GCN candidate retrieval without using gold injection as the main scientific truth.",
        "main_truth": "no_injection",
        "supporting_truth": "injected_reranker_ready",
        "raw_source_of_truth": {
            "dir": "dataset/setting_a/21_ranker_rescue",
            "reason": [
                "best frozen raw retriever output currently available",
                "small improvement over previous retriever but still the strongest raw source currently available",
                "does not imply a full project-wide base reset"
            ]
        },
        "frozen_rows": [
            "backbone_raw",
            "ontology_raw",
            "hard_main_raw",
            "soft_best_raw"
        ],
        "split_policy": {
            "decision_split": "valid",
            "test_used_for_decision_before_valid_clean": False
        },
        "evaluator_semantics": {
            "if_gold_in_candidate_list": "rank = gold_position + 1",
            "if_gold_not_in_candidate_list": "rank = len(candidate_list) + 1",
            "gold_injection_allowed": False,
            "hidden_fallback_allowed": False
        },
        "out_of_scope": [
            "novelty2",
            "fuzzy_retrieval",
            "fuzzy_graph_encoder",
            "retriever_finetuning",
            "hard_soft_redesign",
            "ontology_redesign"
        ]
    }

    out_dir = Path("results/week12B/protocol_freeze")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / "noinj_protocol.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(protocol, f, indent=2, ensure_ascii=False)

    print(f"Saved protocol to: {out_path}")


if __name__ == "__main__":
    main()