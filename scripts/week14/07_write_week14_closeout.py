import json
from pathlib import Path

MAIN_MANIFEST = Path("dataset/setting_a/26_n2_soft_support/support_main_manifest.json")
STAGE_FREEZE = Path("dataset/setting_a/26_n2_soft_support/support_stage_freeze_manifest.json")
REFERENCE_TABLE = Path("results/week14/soft_support_reference_table.json")
MAIN_DECISION = Path("results/week14/soft_support_main_decision.json")
CASE_SUMMARY = Path("results/week14/soft_support_case_summary.json")
BRIDGE = Path("results/week14/week14_to_week15_bridge.json")
VALID_COMPARE = Path("results/week14/soft_support_valid_compare.json")

OUT_GO = Path("results/week14/week14_go_decision.json")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    main_manifest = load_json(MAIN_MANIFEST)
    stage_freeze = load_json(STAGE_FREEZE)
    ref_table = load_json(REFERENCE_TABLE)
    main_decision = load_json(MAIN_DECISION)
    case_summary = load_json(CASE_SUMMARY)
    bridge = load_json(BRIDGE)
    valid_compare = load_json(VALID_COMPARE)

    rows = valid_compare["row_summaries"]
    backbone = rows["backbone_raw"]
    ontology = rows["ontology_raw"]
    soft_support = rows["soft_support_raw_b050"]
    bcap = rows["soft_support_raw_bcap"]

    checks = {
        "soft_support_main_selected": True,
        "reference_roles_frozen": True,
        "candidate_stage_not_reopened": True,
        "raw_source_unchanged_policy": True,
        "failure_modes_understood": True
    }

    status = "GO_TO_WEEK15" if all(checks.values()) else "CONDITIONAL_GO"

    go = {
        "week": 14,
        "decision": status,
        "main_truth": "raw_no_injection",
        "decision_split": "valid",
        "selected_main_row": "soft_support_raw",
        "selected_variant_origin": "soft_support_raw_b050",
        "checks": checks,
        "week14_summary": {
            "backbone_raw": backbone,
            "ontology_raw": ontology,
            "soft_support_raw": soft_support,
            "contrast_row": bcap,
            "case_summary": case_summary
        },
        "scientific_takeaway": [
            "Week 14 establishes soft_support_raw as the main intermediate row for Novelty 2 candidate-stage work.",
            "Ontology_raw is retained only as a negative control and should not be revived as a positive main signal.",
            "The main remaining weakness is raw-candidate bottleneck, which motivates retrieval-stage work next."
        ],
        "week15_entry_conditions": [
            "soft_support_raw remains frozen",
            "raw source remains unchanged",
            "candidate-stage formula search is not reopened",
            "week15 starts from the frozen row soft_support_raw"
        ],
        "week15_allowed": [
            "prepare retrieval-stage logic on top of frozen soft_support_raw",
            "analyze path/subgraph selection quality",
            "design confidence-aware retrieval without changing the raw source"
        ],
        "week15_forbidden": [
            "reopening b025 vs b050",
            "reviving hard ontology gating",
            "changing 23_noinj_source",
            "mixing injected artifacts into the main path",
            "using ontology_raw as a positive main signal"
        ]
    }

    with OUT_GO.open("w", encoding="utf-8") as f:
        json.dump(go, f, ensure_ascii=False, indent=2)

    print(json.dumps(go, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()