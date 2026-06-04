from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime


ROOT = Path(".").resolve()

# ===== Week 18 frozen decisions =====
WEEK = 18
THEME = "lock_retrieval_main_and_prepare_clean_evaluation_package"

MAIN_TRUTH = "raw_no_injection"
DECISION_SPLIT = "valid"

REFERENCE_ROW = "backbone_raw"
NEGATIVE_CONTROL_ROW = "ontology_raw"
INTERMEDIATE_ROW = "soft_support_raw"
MAIN_ROW = "soft_support_fuzzy_retrieval_main"
APPENDIX_ROW = "soft_support_fuzzy_encoder_probe_v0"

TEST_MODE = "readiness_only_not_official_locked_test"

INPUTS = {
    "week17_go_decision": "results/week17/week17_go_decision.json",
    "backbone_reference_valid": "results/reference_rows/backbone_raw_valid",
    "raw_source_valid": "dataset/setting_a/23_noinj_source/valid_top20_raw.json",
    "ontology_raw_valid": "dataset/setting_a/24_noinj_ontology/valid_top20_ontology_raw.json",
    "soft_support_valid": "dataset/setting_a/26_n2_soft_support/valid_top20_soft_support_main.json",
    "retrieval_main_valid": "dataset/setting_a/27_n2_fuzzy_retrieval/valid_fuzzy_retrieval_main.json",
    "encoder_probe_valid": "dataset/setting_a/28_n2_fuzzy_encoder/valid_fuzzy_encoder_probe_v0.json",
    "setting_b_valid_annotations": "dataset/setting_b/04_contra_checked/valid_b_annotations_contra_checked.json",
    "type_map": "dataset/setting_b/01_annotations/type_map.tsv",
    "schema_rules": "dataset/setting_b/01_annotations/schema_rules.json",
    "path_templates": "dataset/setting_b/01_annotations/path_templates.yaml",
}

OUTPUT_DIRS = [
    "configs/week18",
    "scripts/week18",
    "results/week18",
    "reports/week18",
    "dataset/setting_b/07_n2_eval_valid",
    "dataset/setting_b/08_n2_eval_test",
]

OUTPUT_FILES = {
    "protocol_report": "reports/week18/day1_protocol_freeze.md",
    "row_lock_report": "results/week18/retrieval_main_lock_report.json",
}

FORBIDDEN_ACTIONS = [
    "Do not reopen candidate-stage.",
    "Do not change retrieval main row.",
    "Do not promote encoder probe to main row.",
    "Do not run official locked test this week.",
    "Do not introduce new retrieval or encoder variants.",
    "Do not mix appendix row into the main 4-row valid table.",
]

MAIN_TABLE_ROWS = [
    REFERENCE_ROW,
    NEGATIVE_CONTROL_ROW,
    INTERMEDIATE_ROW,
    MAIN_ROW,
]

APPENDIX_ROWS = [
    APPENDIX_ROW,
]

SUCCESS_CRITERIA = [
    "Week-18 protocol is frozen with no ambiguity about row roles.",
    "Retrieval main is explicitly locked as the main row after week 17.",
    "Encoder probe is explicitly positioned as appendix/supporting only.",
    "Valid is the decision split for week 18.",
    "Test is limited to readiness/package check only.",
    "Main table row set is fixed to 4 scientific rows.",
]

DAY1_DECISIONS = [
    f"Main truth = {MAIN_TRUTH}.",
    f"Decision split = {DECISION_SPLIT}.",
    f"Reference row = {REFERENCE_ROW}.",
    f"Negative control row = {NEGATIVE_CONTROL_ROW}.",
    f"Intermediate row = {INTERMEDIATE_ROW}.",
    f"Main row = {MAIN_ROW}.",
    f"Appendix row = {APPENDIX_ROW}.",
    f"Test mode = {TEST_MODE}.",
]


def ensure_dirs() -> None:
    for rel in OUTPUT_DIRS:
        (ROOT / rel).mkdir(parents=True, exist_ok=True)


def check_inputs() -> dict:
    status = {}
    for name, rel_path in INPUTS.items():
        p = ROOT / rel_path
        status[name] = {
            "path": rel_path,
            "exists": p.exists(),
            "is_dir": p.is_dir() if p.exists() else False,
            "size_bytes": p.stat().st_size if p.exists() and p.is_file() else None,
        }
    return status


def build_report(input_status: dict) -> dict:
    missing = [k for k, v in input_status.items() if not v["exists"]]

    return {
        "week": WEEK,
        "theme": THEME,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "week_mode": "row_lock_and_evaluation_prep",
        "main_truth": MAIN_TRUTH,
        "decision_split": DECISION_SPLIT,
        "test_mode": TEST_MODE,
        "row_roles": {
            "reference_row": REFERENCE_ROW,
            "negative_control_row": NEGATIVE_CONTROL_ROW,
            "intermediate_row": INTERMEDIATE_ROW,
            "main_row": MAIN_ROW,
            "appendix_row": APPENDIX_ROW,
        },
        "main_table_rows": MAIN_TABLE_ROWS,
        "appendix_rows": APPENDIX_ROWS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "success_criteria": SUCCESS_CRITERIA,
        "input_files": input_status,
        "missing_inputs": missing,
        "status": "READY" if not missing else "BLOCKED",
        "week17_dependency": {
            "required_final_decision": "NO_GO_FOR_FULL_ENCODER_STAGE",
            "required_main_row_after_week17": "soft_support_fuzzy_retrieval_main",
        },
    }


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def write_md(path: Path, report: dict) -> None:
    lines = []
    lines.append("# Week 18 Day 1 — Protocol Freeze\n")
    lines.append("## Theme")
    lines.append(f"- {THEME}")
    lines.append("")
    lines.append("## Day-1 decisions")
    for item in DAY1_DECISIONS:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Row roles")
    for k, v in report["row_roles"].items():
        lines.append(f"- **{k}**: `{v}`")
    lines.append("")
    lines.append("## Main valid table rows")
    for row in report["main_table_rows"]:
        lines.append(f"- `{row}`")
    lines.append("")
    lines.append("## Appendix / supporting rows")
    for row in report["appendix_rows"]:
        lines.append(f"- `{row}`")
    lines.append("")
    lines.append("## Forbidden actions")
    for item in report["forbidden_actions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Input status")
    for name, meta in report["input_files"].items():
        ok = "OK" if meta["exists"] else "MISSING"
        lines.append(f"- `{name}`: {ok} — `{meta['path']}`")
    lines.append("")
    lines.append("## Success criteria")
    for item in report["success_criteria"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Conclusion")
    lines.append(f"- Status: **{report['status']}**")
    if report["missing_inputs"]:
        lines.append("- Missing inputs:")
        for x in report["missing_inputs"]:
            lines.append(f"  - `{x}`")
    else:
        lines.append("- All required inputs are present. Week 18 can proceed to Day 2.")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    ensure_dirs()
    input_status = check_inputs()
    report = build_report(input_status)

    json_path = ROOT / OUTPUT_FILES["row_lock_report"]
    md_path = ROOT / OUTPUT_FILES["protocol_report"]

    write_json(json_path, report)
    write_md(md_path, report)

    print(f"[OK] wrote {json_path}")
    print(f"[OK] wrote {md_path}")
    print(f"[STATUS] {report['status']}")
    if report["missing_inputs"]:
        print("[MISSING INPUTS]")
        for name in report["missing_inputs"]:
            print(" -", name)


if __name__ == "__main__":
    main()