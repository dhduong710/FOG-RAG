from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime


ROOT = Path(".").resolve()

# ===== Fixed week-17 protocol =====
WEEK = 17
THEME = "encoder_readiness_check"
MAIN_INPUT_ROW = "soft_support_fuzzy_retrieval_main"
MAIN_OUTPUT_ROW = "soft_support_fuzzy_encoder_probe_v0"
DECISION_SPLIT = "valid"

# Main inputs
INPUTS = {
    "raw_source": "dataset/setting_a/23_noinj_source/valid_top20_raw.json",
    "soft_support_main": "dataset/setting_a/26_n2_soft_support/valid_top20_soft_support_main.json",
    "retrieval_main": "dataset/setting_a/27_n2_fuzzy_retrieval/valid_fuzzy_retrieval_main.json",
    "type_map": "dataset/setting_b/01_annotations/type_map.tsv",
    "schema_rules": "dataset/setting_b/01_annotations/schema_rules.json",
    "path_templates": "dataset/setting_b/01_annotations/path_templates.yaml",
    "valid_b_annotations": "dataset/setting_b/04_contra_checked/valid_b_annotations_contra_checked.json",
}

# Output targets for day 1
OUTPUTS = {
    "protocol_report": "reports/week17/day1_protocol_freeze.md",
    "readiness_manifest": "results/week17/encoder_readiness_manifest.json",
    "week17_dataset_dir": "dataset/setting_a/28_n2_fuzzy_encoder",
    "week17_config_dir": "configs/week17",
    "week17_script_dir": "scripts/week17",
    "week17_result_dir": "results/week17",
    "week17_report_dir": "reports/week17",
}

FORBIDDEN_ACTIONS = [
    "Do not change raw source.",
    "Do not reopen candidate-stage formulas or rows.",
    "Do not change retrieval main row during day 1.",
    "Do not run test split.",
    "Do not commit to full encoder stage yet.",
    "Do not introduce multiple encoder variants in week 17.",
    "Do not start long-run end-to-end training.",
]

SUCCESS_CRITERIA = [
    "All week-17 folders exist.",
    "All required input files exist.",
    "Protocol freeze markdown is written.",
    "Encoder readiness manifest is written.",
    "Week-17 main input/output and constraints are unambiguous.",
]

DAY1_DECISIONS = [
    "Week 17 is encoder-readiness week, not full encoder week.",
    f"Decision split = {DECISION_SPLIT}.",
    f"Main input row = {MAIN_INPUT_ROW}.",
    f"Main output row = {MAIN_OUTPUT_ROW}.",
    "Exactly one encoder probe v0 is allowed this week.",
    "Reference comparisons will use soft_support_raw and retrieval_main.",
    "Test split is forbidden this week.",
    "Candidate-stage and retrieval-stage main rows remain frozen.",
]


def ensure_dirs() -> None:
    for key, rel_path in OUTPUTS.items():
        if key.endswith("_dir"):
            (ROOT / rel_path).mkdir(parents=True, exist_ok=True)


def check_inputs() -> dict:
    input_status = {}
    for name, rel_path in INPUTS.items():
        p = ROOT / rel_path
        input_status[name] = {
            "path": rel_path,
            "exists": p.exists(),
            "size_bytes": p.stat().st_size if p.exists() else None,
        }
    return input_status


def build_manifest(input_status: dict) -> dict:
    missing = [k for k, v in input_status.items() if not v["exists"]]
    manifest = {
        "week": WEEK,
        "theme": THEME,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "decision_split": DECISION_SPLIT,
        "main_input_row": MAIN_INPUT_ROW,
        "main_output_row": MAIN_OUTPUT_ROW,
        "reference_rows": [
            "soft_support_raw",
            "soft_support_fuzzy_retrieval_main",
        ],
        "week_mode": "encoder_readiness_check_but_not_commit_yet",
        "allowed_actions": [
            "build encoder input package from retrieval main",
            "run one minimal encoder probe v0",
            "valid-only comparison",
            "subset dryrun before any full-valid run",
        ],
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "success_criteria": SUCCESS_CRITERIA,
        "input_files": input_status,
        "missing_inputs": missing,
        "status": "READY" if not missing else "BLOCKED",
    }
    return manifest


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def write_markdown(path: Path, manifest: dict) -> None:
    lines = []
    lines.append(f"# Week {WEEK} Day 1 — Protocol Freeze\n")
    lines.append(f"## Theme\n- {THEME}\n")
    lines.append("## Day-1 decisions")
    for item in DAY1_DECISIONS:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Main rows")
    lines.append(f"- Main input row: `{MAIN_INPUT_ROW}`")
    lines.append(f"- Main output row: `{MAIN_OUTPUT_ROW}`")
    lines.append(f"- Decision split: `{DECISION_SPLIT}`")
    lines.append("")
    lines.append("## Reference rows for compare")
    for row in manifest["reference_rows"]:
        lines.append(f"- `{row}`")
    lines.append("")
    lines.append("## Allowed actions this week")
    for item in manifest["allowed_actions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Forbidden actions this week")
    for item in manifest["forbidden_actions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Input file status")
    for name, meta in manifest["input_files"].items():
        status = "OK" if meta["exists"] else "MISSING"
        lines.append(f"- `{name}`: {status} — `{meta['path']}`")
    lines.append("")
    lines.append("## Success criteria")
    for item in manifest["success_criteria"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Day-1 conclusion")
    lines.append(f"- Status: **{manifest['status']}**")
    if manifest["missing_inputs"]:
        lines.append("- Missing inputs detected:")
        for name in manifest["missing_inputs"]:
            lines.append(f"  - `{name}`")
    else:
        lines.append("- All required inputs are present. Week 17 can proceed to Day 2.")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    input_status = check_inputs()
    manifest = build_manifest(input_status)

    json_path = ROOT / OUTPUTS["readiness_manifest"]
    md_path = ROOT / OUTPUTS["protocol_report"]

    write_json(json_path, manifest)
    write_markdown(md_path, manifest)

    print(f"[OK] Wrote: {json_path}")
    print(f"[OK] Wrote: {md_path}")
    print(f"[STATUS] {manifest['status']}")
    if manifest["missing_inputs"]:
        print("[MISSING INPUTS]")
        for name in manifest["missing_inputs"]:
            print(f" - {name}")


if __name__ == "__main__":
    main()