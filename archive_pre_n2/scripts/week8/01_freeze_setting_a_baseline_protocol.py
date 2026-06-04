#!/usr/bin/env python3
import csv
import json
import os
from pathlib import Path
from datetime import datetime


ROOT = Path(".")
DATASET_DIR = ROOT / "dataset" / "setting_a"
REPORT_DIR = ROOT / "reports" / "week8"
OUT_DATA_DIR = DATASET_DIR / "17_structure_baselines"
TABLE_DIR = ROOT / "results" / "week8" / "baseline_table_v0"

VALID_TSV = DATASET_DIR / "01_split" / "valid.tsv"

REQUIRED_PATHS = {
    "valid_split": DATASET_DIR / "01_split" / "valid.tsv",
    "test_split": DATASET_DIR / "01_split" / "test.tsv",
    "train_split": DATASET_DIR / "01_split" / "train.tsv",
    "entity2id": DATASET_DIR / "04_drkgc_json" / "entity2id.pkl",
    "id2entity": DATASET_DIR / "04_drkgc_json" / "id2entity.pkl",
    "relation2id": DATASET_DIR / "04_drkgc_json" / "relation2id.pkl",
    "id2relation": DATASET_DIR / "04_drkgc_json" / "id2relation.pkl",
    "week7_backbone_reference": ROOT / "results" / "week7" / "backbone_valid_v2_short" / "valid_eval_v2" / "eval_valid_v2_metrics.json",
    "week7_backbone_reference_8b": ROOT / "results" / "week7" / "backbone_valid_v2_8b_full" / "valid_eval_8b" / "eval_valid_8b_metrics.json",
    "week8_posthoc_reference": ROOT / "results" / "week8" / "backbone_valid_posthoc_3b" / "valid_eval_posthoc_3b" / "eval_valid_posthoc_3b_metrics.json",
}

BASELINE_REGISTRY = [
    {
        "name": "R-GCN",
        "category": "graph",
        "status": "required",
        "planned_train_script": "scripts/week8/02_eval_rgcn_structure_baseline.py",
        "planned_eval_script": "scripts/week8/02_eval_rgcn_structure_baseline.py",
    },
    {
        "name": "HRGAT",
        "category": "graph",
        "status": "required",
        "planned_train_script": "scripts/week8/03_train_hrgat_baseline.py",
        "planned_eval_script": "scripts/week8/04_eval_hrgat_structure_baseline.py",
    },
    {
        "name": "ComplEx",
        "category": "kge",
        "status": "preferred",
        "planned_train_script": "scripts/week8/05_train_complex_baseline.py",
        "planned_eval_script": "scripts/week8/06_eval_complex_structure_baseline.py",
    },
    {
        "name": "TransE",
        "category": "kge",
        "status": "optional",
        "planned_train_script": "scripts/week8/07_train_transe_baseline.py",
        "planned_eval_script": "scripts/week8/08_eval_transe_structure_baseline.py",
    },
]

TABLE_SCHEMA = {
    "table_a_structure_only": {
        "title": "Setting A structure-only baselines",
        "columns": [
            "Method",
            "Category",
            "Valid MRR",
            "Hits@1",
            "Hits@3",
            "Hits@10",
            "Notes",
        ],
        "notes": [
            "All rows must use the same evaluator.",
            "Task = head prediction (?, indication, disease).",
            "Universe = drug-only.",
            "Decision split = valid.",
        ],
    },
    "table_b_reference_rows": {
        "title": "Candidate-aware reranker reference rows",
        "columns": [
            "Method",
            "Protocol",
            "Valid MRR",
            "Hits@1",
            "Hits@3",
            "Hits@10",
            "Notes",
        ],
        "notes": [
            "Reference/supporting rows only.",
            "Do not mix directly with structure-only baselines without explicit protocol note.",
            "week7-v2 is the main backbone reference.",
            "posthoc debias is supporting retrieval-side analysis only.",
        ],
    },
}

PROTOCOL = {
    "week_name": "week8_structural_baselines_setting_a_table_v0",
    "created_at": None,
    "task": {
        "name": "Setting A structural baseline evaluation",
        "query_form": "(?, indication, disease)",
        "prediction_type": "head_prediction",
        "relation": "indication",
    },
    "candidate_universe": {
        "name": "drug_only",
        "description": "All structural baselines must rank over the full drug-only universe.",
    },
    "decision_policy": {
        "primary_split": "valid",
        "test_policy": "Do not prioritize test this week. Only use later if table v0 is stable.",
    },
    "metrics": {
        "main": ["mrr", "hits1", "hits3", "hits10"],
        "supporting_only": ["top1_dominance_ratio", "unique_top1_count", "top5_case_review"],
        "excluded_from_main_table": ["inject_ratio_ready", "candidate_ready_reranker_metrics"],
    },
    "backbone_reference_policy": {
        "main_reference": "week7-v2",
        "supporting_analysis_only": "posthoc_debias_lambda_0.05",
    },
    "baseline_registry": BASELINE_REGISTRY,
    "table_policy": {
        "use_two_sections": True,
        "section_a": "structure_only_baselines",
        "section_b": "candidate_aware_reference_rows",
        "warning": "Do not mix structure-only baselines and candidate-aware reranker rows into one undifferentiated table.",
    },
}


def count_tsv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        rows = list(reader)
    # support both header/no-header
    if not rows:
        return 0
    first = rows[0]
    if len(first) >= 3 and first[0] == "head" and first[1] == "relation" and first[2] == "tail":
        return len(rows) - 1
    return len(rows)


def mkdirs():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)


def check_required_paths():
    status = {}
    missing = []
    for key, path in REQUIRED_PATHS.items():
        exists = path.exists()
        status[key] = {
            "path": str(path),
            "exists": exists,
        }
        if not exists:
            missing.append(str(path))
    return status, missing


def build_protocol_dict():
    protocol = dict(PROTOCOL)
    protocol["created_at"] = datetime.now().isoformat(timespec="seconds")
    protocol["valid_size_detected"] = count_tsv_rows(VALID_TSV) if VALID_TSV.exists() else None
    return protocol


def write_json(path: Path, obj):
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def write_markdown(report_path: Path, protocol: dict, path_status: dict):
    required_rows = []
    preferred_rows = []
    optional_rows = []

    for row in protocol["baseline_registry"]:
        if row["status"] == "required":
            required_rows.append(f"- {row['name']}")
        elif row["status"] == "preferred":
            preferred_rows.append(f"- {row['name']}")
        else:
            optional_rows.append(f"- {row['name']}")

    md = f"""# Day 1 Protocol Freeze

## 1. Scope
- Freeze structural baseline protocol for Setting A
- Freeze baseline registry for the week
- Freeze table schema v0

## 2. Locked protocol
- Task: head prediction `(?, indication, disease)`
- Universe: drug-only
- Main decision split: valid
- Main metrics: MRR, Hits@1, Hits@3, Hits@10
- Detected valid size: {protocol.get("valid_size_detected")}

## 3. Backbone reference policy
- Main backbone reference: week7-v2
- Supporting analysis only: posthoc debias λ=0.05

## 4. Baseline registry
### Required
{os.linesep.join(required_rows)}

### Preferred
{os.linesep.join(preferred_rows)}

### Optional
{os.linesep.join(optional_rows)}

## 5. Table policy
- Use 2 sections:
  1. Structure-only baselines
  2. Candidate-aware reranker reference rows
- Do not mix both protocols into one undifferentiated table.

## 6. Required path check
"""
    for key, info in path_status.items():
        mark = "OK" if info["exists"] else "MISSING"
        md += f"- [{mark}] `{key}` -> `{info['path']}`\n"

    md += """
## 7. Main warning
If protocol is not frozen on day 1, all following metrics/tables can become inconsistent.

## 8. Day-1 conclusion
Protocol is frozen for:
- valid-first structural baseline evaluation
- drug-only universe
- clean structure-only table v0
- separate reference section for candidate-aware reranker rows
"""
    report_path.write_text(md, encoding="utf-8")


def write_table_readme(path: Path):
    text = """# baseline_table_v0

This folder stores the first clean Setting-A result table.

## Intended outputs
- setting_a_structure_table_v0.csv
- setting_a_structure_table_v0.md
- setting_a_reference_rows.md
- table_schema.json

## Important policy
Do not mix structure-only baselines and candidate-aware reranker rows into one undifferentiated table.
"""
    path.write_text(text, encoding="utf-8")


def main():
    mkdirs()

    protocol = build_protocol_dict()
    path_status, missing = check_required_paths()

    protocol_path = OUT_DATA_DIR / "protocol_freeze.json"
    table_schema_path = TABLE_DIR / "table_schema.json"
    report_path = REPORT_DIR / "day1_protocol_freeze.md"
    readme_path = TABLE_DIR / "README.md"

    write_json(protocol_path, protocol)
    write_json(table_schema_path, TABLE_SCHEMA)
    write_markdown(report_path, protocol, path_status)
    write_table_readme(readme_path)

    print("Saved:")
    print(f"- {protocol_path}")
    print(f"- {table_schema_path}")
    print(f"- {report_path}")
    print(f"- {readme_path}")
    print()

    if missing:
        print("WARNING: missing required paths detected:")
        for p in missing:
            print(f"- {p}")
        raise SystemExit(1)

    print("Day-1 protocol freeze completed successfully.")


if __name__ == "__main__":
    main()