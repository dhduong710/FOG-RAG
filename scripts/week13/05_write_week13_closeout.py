import json
from pathlib import Path

PROTOCOL_PATH = Path("results/week13/n2_file_registry.json")
FEATURE_MANIFEST_PATH = Path("dataset/setting_a/25_n2_support_features/support_feature_manifest.json")
FEATURE_SUMMARY_PATH = Path("results/week13/support_feature_summary.json")
FORMULA_PROBE_PATH = Path("results/week13/support_formula_probe.json")
CASE_COMPARE_PATH = Path("results/week13/support_case_compare_summary.json")

OUT_JSON = Path("results/week13/week13_go_decision.json")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    registry = load_json(PROTOCOL_PATH)
    feat_manifest = load_json(FEATURE_MANIFEST_PATH)
    feat_summary = load_json(FEATURE_SUMMARY_PATH)
    formula_probe = load_json(FORMULA_PROBE_PATH)
    case_compare = load_json(CASE_COMPARE_PATH)

    best_formula = formula_probe["best_formula_by_mrr_like"]
    best_formula_metrics = formula_probe["formula_summaries"][best_formula]

    go = {
        "week": 13,
        "branch": registry.get("branch", "week_13"),
        "decision": "GO_TO_WEEK14",
        "main_truth": registry.get("main_truth", "raw_no_injection"),
        "decision_split": registry.get("decision_split", "valid"),
        "week13_outputs_confirmed": {
            "file_registry_frozen": True,
            "support_feature_table_built": True,
            "support_feature_audit_built": True,
            "support_formula_probe_built": True,
            "support_case_review_built": True
        },
        "main_findings": {
            "constant_features_dropped": feat_summary["recommended_drop_from_main_score"],
            "primary_features_from_audit": feat_summary["recommended_primary_features"],
            "supporting_only_features_from_audit": feat_summary["recommended_supporting_only_features"],
            "best_formula_family": best_formula,
            "best_formula_metrics": best_formula_metrics,
            "case_review_summary": case_compare
        },
        "week14_policy": {
            "surviving_formula_family": "B_evidence_minus_direct",
            "do_not_use_as_positive_main_signal": [
                "type_valid_flag",
                "schema_valid_flag",
                "type_filtered_keep_flag",
                "ontology_keep_flag",
                "candidate_query_edge_count"
            ],
            "keep_as_supporting_or_diagnostic_only": [
                "contra_flag",
                "contra_penalty",
                "query_edge_touch_count"
            ],
            "main_direction": [
                "evidence-aware scoring",
                "anti-shortcut direct-link penalty",
                "no hard ontology gating revival"
            ]
        },
        "scientific_interpretation": [
            "Week 13 confirms that binary ontology support is not a good main positive signal on raw/no-injection candidates.",
            "A lightweight evidence-aware but anti-shortcut score can improve ranking inside the raw top-k without worsening cases.",
            "The remaining dominant failure mode is raw-candidate bottleneck when gold is absent from the top-k."
        ],
        "notes": [
            "Week 14 should build a cleaner soft_support_raw branch using the surviving formula family.",
            "Week 14 should not yet move to test.",
            "Week 14 should still treat this as candidate-stage work, not final novelty2 closure."
        ]
    }

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(go, f, ensure_ascii=False, indent=2)

    print(json.dumps(go, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()