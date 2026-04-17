import json
from pathlib import Path

MAIN_MANIFEST = Path("dataset/setting_a/26_n2_soft_support/support_main_manifest.json")
MAIN_ROW = Path("dataset/setting_a/26_n2_soft_support/valid_top20_soft_support_main.json")
VALID_COMPARE = Path("results/week14/soft_support_valid_compare.json")
CASE_SAMPLES = Path("results/week14/soft_support_case_samples.json")
CASE_SUMMARY = Path("results/week14/soft_support_case_summary.json")
WEEK14_INPUT_MANIFEST = Path("results/week14/week14_input_manifest.json")

OUT_STAGE_FREEZE = Path("dataset/setting_a/26_n2_soft_support/support_stage_freeze_manifest.json")
OUT_STAGE_REPORT = Path("results/week14/soft_support_stage_report.json")
OUT_REFERENCE_TABLE = Path("results/week14/soft_support_reference_table.json")
OUT_CASEPACK = Path("results/week14/soft_support_main_casepack.json")
OUT_BRIDGE = Path("results/week14/week14_to_week15_bridge.json")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    main_manifest = load_json(MAIN_MANIFEST)
    valid_compare = load_json(VALID_COMPARE)
    case_samples = load_json(CASE_SAMPLES)
    case_summary = load_json(CASE_SUMMARY)
    input_manifest = load_json(WEEK14_INPUT_MANIFEST)

    row_summaries = valid_compare["row_summaries"]

    backbone = row_summaries["backbone_raw"]
    ontology = row_summaries["ontology_raw"]
    soft_support = row_summaries["soft_support_raw_b050"]
    bcap = row_summaries["soft_support_raw_bcap"]

    stage_freeze = {
        "week": 14,
        "stage": "soft_support_stage_freeze",
        "main_truth": "raw_no_injection",
        "decision_split": "valid",
        "selected_row_name": "soft_support_raw",
        "selected_variant_origin": "soft_support_raw_b050",
        "selected_row_path": str(MAIN_ROW),
        "selected_manifest_path": str(MAIN_MANIFEST),
        "frozen_reference_rows": {
            "backbone_raw": "dataset/setting_a/23_noinj_source/valid_top20_raw.json",
            "ontology_raw": "dataset/setting_a/24_noinj_ontology/valid_top20_ontology_raw.json",
            "soft_support_raw": str(MAIN_ROW)
        },
        "forbidden_next_week": [
            "revisiting b025",
            "reviving hard ontology gating",
            "changing the frozen raw source",
            "mixing injected artifacts into the main path"
        ],
        "notes": [
            "Week 14 closes the candidate-stage soft-support selection.",
            "Week 15 should treat soft_support_raw as the main intermediate row.",
            "Candidate-stage work is complete enough to move toward retrieval-stage preparation."
        ]
    }

    reference_table = {
        "reference_rows": [
            {
                "row_name": "backbone_raw",
                "role": "reference",
                **backbone
            },
            {
                "row_name": "ontology_raw",
                "role": "negative_control",
                **ontology
            },
            {
                "row_name": "soft_support_raw",
                "role": "main_intermediate",
                **soft_support
            }
        ],
        "contrast_row": {
            "row_name": "soft_support_raw_bcap",
            "role": "contrast_only",
            **bcap
        }
    }

    stage_report = {
        "week": 14,
        "stage": "candidate_stage_close_prep",
        "main_findings": {
            "selected_main_row": "soft_support_raw",
            "selected_variant_origin": "soft_support_raw_b050",
            "selected_metrics": soft_support,
            "backbone_reference_metrics": backbone,
            "ontology_negative_control_metrics": ontology,
            "contrast_metrics": bcap,
            "case_summary": case_summary
        },
        "scientific_interpretation": [
            "Binary ontology support remains a poor main positive signal on raw/no-injection candidates.",
            "A soft support score based on evidence-aware but anti-shortcut ranking improves over backbone_raw without worsened cases.",
            "The main remaining failure mode is raw-candidate bottleneck when gold is absent from the top-k."
        ]
    }

    casepack = {
        "summary": case_summary,
        "selected_row": "soft_support_raw",
        "selected_variant_origin": "soft_support_raw_b050",
        "top_improved_vs_backbone": case_samples["samples"]["top_improved_vs_backbone"][:8],
        "top_unchanged_bad_vs_backbone": case_samples["samples"]["top_unchanged_bad_vs_backbone"][:8],
        "top_improved_vs_bcap": case_samples["samples"]["top_improved_vs_bcap"][:8],
        "notes": [
            "This casepack is the compact evidence bundle for the Week 14 row decision.",
            "Use it next week when explaining why soft_support_raw is the right bridge into retrieval-stage work."
        ]
    }

    bridge = {
        "from_week": 14,
        "to_week": 15,
        "status": "READY_FOR_WEEK15",
        "ready_inputs": {
            "soft_support_raw": str(MAIN_ROW),
            "soft_support_manifest": str(MAIN_MANIFEST),
            "support_stage_freeze_manifest": str(OUT_STAGE_FREEZE),
            "reference_table": str(OUT_REFERENCE_TABLE),
            "casepack": str(OUT_CASEPACK)
        },
        "week15_entry_conditions": [
            "soft_support_raw is frozen",
            "backbone_raw / ontology_raw / soft_support_raw roles are frozen",
            "raw source remains unchanged",
            "candidate-stage conclusion is no longer being renegotiated"
        ],
        "week15_non_goals": [
            "do not change raw source",
            "do not reopen candidate-stage formula search",
            "do not use ontology_raw as a positive main signal"
        ],
        "recommended_direction": [
            "treat soft_support_raw as the fixed main intermediate row",
            "begin preparing retrieval-stage logic on top of frozen raw source and soft-support interpretation",
            "focus on path/subgraph selection quality next"
        ]
    }

    for path, obj in [
        (OUT_STAGE_FREEZE, stage_freeze),
        (OUT_REFERENCE_TABLE, reference_table),
        (OUT_STAGE_REPORT, stage_report),
        (OUT_CASEPACK, casepack),
        (OUT_BRIDGE, bridge),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "selected_main_row": "soft_support_raw",
        "selected_variant_origin": "soft_support_raw_b050",
        "bridge_status": "READY_FOR_WEEK15",
        "reference_rows": ["backbone_raw", "ontology_raw", "soft_support_raw"]
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()