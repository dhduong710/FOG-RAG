from __future__ import annotations

import json
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path


RAW_DIR = Path("dataset/setting_a/23_noinj_source")
OUT_DIR = Path("dataset/setting_a/24_noinj_ontology")
LOG_DIR = Path("results/week12B/build_ontology_raw")


def run_cmd(cmd: list[str], log_path: Path) -> None:
    print("Running:", " ".join(shlex.quote(x) for x in cmd))
    with log_path.open("w", encoding="utf-8") as log_f:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            print(line, end="")
            log_f.write(line)
        ret = proc.wait()
    if ret != 0:
        raise SystemExit(f"Command failed with return code {ret}: {' '.join(cmd)}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    required = [
        RAW_DIR / "valid_top20_raw.json",
        RAW_DIR / "test_top20_raw.json",
        Path("dataset/setting_b/01_annotations/type_map.tsv"),
        Path("dataset/setting_b/01_annotations/schema_rules.json"),
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs:\n" + "\n".join(missing))

    meta = {
        "timestamp_start": datetime.now().isoformat(),
        "raw_input_dir": str(RAW_DIR),
        "output_dir": str(OUT_DIR),
        "notes": [
            "Week 12B builds ontology-only variants from raw/no-injection source.",
            "Gold injection must not be reintroduced in this branch.",
            "Reuse Week-9 logic whenever possible."
        ]
    }

    FALLBACK_TYPE_JSON = "dataset/setting_b/01_ontology/entity_name_to_type.json"
    TYPE_MAP_TSV = "dataset/setting_b/01_annotations/type_map.tsv"
    SCHEMA_RULES_JSON = "dataset/setting_b/01_annotations/schema_rules.json"
    PATH_TEMPLATES_YAML = "dataset/setting_b/01_annotations/path_templates.yaml"
    ID2ENTITY_PATH = "dataset/setting_a/04_drkgc_json/id2entity.pkl"
    ID2RELATION_PATH = "dataset/setting_a/04_drkgc_json/id2relation.pkl"

    VALID_EVIDENCE = "dataset/setting_a/20_test_rerun_eval_ready/backbone/valid.json"
    TEST_EVIDENCE = "dataset/setting_a/20_test_rerun_eval_ready/backbone/test.json"

    # 1) Type-filter valid
    cmd_valid_type = [
        sys.executable,
        "scripts/week9/02_build_type_filtered_candidates.py",
        "--input_candidates", str(RAW_DIR / "valid_top20_raw.json"),
        "--type_map_tsv", TYPE_MAP_TSV,
        "--fallback_type_json", FALLBACK_TYPE_JSON,
        "--output_filtered_candidates", str(OUT_DIR / "valid_top20_type_filtered_raw.json"),
        "--output_filter_report", str(OUT_DIR / "type_filter_report_valid.json"),
        "--output_md_report", str(OUT_DIR / "type_filter_report_valid.md"),
        "--target_type", "Drug",
        "--sample_limit", "50",
    ]

    # 2) Type-filter test
    cmd_test_type = [
        sys.executable,
        "scripts/week9/02_build_type_filtered_candidates.py",
        "--input_candidates", str(RAW_DIR / "test_top20_raw.json"),
        "--type_map_tsv", TYPE_MAP_TSV,
        "--fallback_type_json", FALLBACK_TYPE_JSON,
        "--output_filtered_candidates", str(OUT_DIR / "test_top20_type_filtered_raw.json"),
        "--output_filter_report", str(OUT_DIR / "type_filter_report_test.json"),
        "--output_md_report", str(OUT_DIR / "type_filter_report_test.md"),
        "--target_type", "Drug",
        "--sample_limit", "50",
    ]

    # 3) Schema-validity check valid
    cmd_valid_schema = [
        sys.executable,
        "scripts/week9/03_check_schema_validity.py",
        "--candidate_artifact", str(OUT_DIR / "valid_top20_type_filtered_raw.json"),
        "--evidence_artifact", VALID_EVIDENCE,
        "--id2entity_path", ID2ENTITY_PATH,
        "--id2relation_path", ID2RELATION_PATH,
        "--type_map_tsv", TYPE_MAP_TSV,
        "--fallback_type_json", FALLBACK_TYPE_JSON,
        "--schema_rules_json", SCHEMA_RULES_JSON,
        "--path_templates_yaml", PATH_TEMPLATES_YAML,
        "--output_report_json", str(OUT_DIR / "schema_validity_valid.json"),
        "--output_report_md", str(OUT_DIR / "schema_validity_valid.md"),
        "--max_path_len", "3",
        "--topn_candidates_for_path_check", "5",
        "--sample_limit", "50",
    ]

    # 4) Schema-validity check test
    cmd_test_schema = [
        sys.executable,
        "scripts/week9/03_check_schema_validity.py",
        "--candidate_artifact", str(OUT_DIR / "test_top20_type_filtered_raw.json"),
        "--evidence_artifact", TEST_EVIDENCE,
        "--id2entity_path", ID2ENTITY_PATH,
        "--id2relation_path", ID2RELATION_PATH,
        "--type_map_tsv", TYPE_MAP_TSV,
        "--fallback_type_json", FALLBACK_TYPE_JSON,
        "--schema_rules_json", SCHEMA_RULES_JSON,
        "--path_templates_yaml", PATH_TEMPLATES_YAML,
        "--output_report_json", str(OUT_DIR / "schema_validity_test.json"),
        "--output_report_md", str(OUT_DIR / "schema_validity_test.md"),
        "--max_path_len", "3",
        "--topn_candidates_for_path_check", "5",
        "--sample_limit", "50",
    ]

    # 5) Build ontology-only valid
    cmd_valid_onto = [
        sys.executable,
        "scripts/week9/04_build_ontology_only_variant.py",
        "--input_candidates", str(OUT_DIR / "valid_top20_type_filtered_raw.json"),
        "--input_evidence", VALID_EVIDENCE,
        "--id2entity_path", ID2ENTITY_PATH,
        "--id2relation_path", ID2RELATION_PATH,
        "--type_map_tsv", TYPE_MAP_TSV,
        "--fallback_type_json", FALLBACK_TYPE_JSON,
        "--schema_rules_json", SCHEMA_RULES_JSON,
        "--path_templates_yaml", PATH_TEMPLATES_YAML,
        "--output_candidates", str(OUT_DIR / "valid_top20_ontology_raw.json"),
        "--output_report_json", str(OUT_DIR / "ontology_filter_report_valid.json"),
        "--output_report_md", str(OUT_DIR / "ontology_filter_report_valid.md"),
        "--max_path_len", "3",
        "--sample_limit", "50",
    ]

    # 6) Build ontology-only test
    cmd_test_onto = [
        sys.executable,
        "scripts/week9/04_build_ontology_only_variant.py",
        "--input_candidates", str(OUT_DIR / "test_top20_type_filtered_raw.json"),
        "--input_evidence", TEST_EVIDENCE,
        "--id2entity_path", ID2ENTITY_PATH,
        "--id2relation_path", ID2RELATION_PATH,
        "--type_map_tsv", TYPE_MAP_TSV,
        "--fallback_type_json", FALLBACK_TYPE_JSON,
        "--schema_rules_json", SCHEMA_RULES_JSON,
        "--path_templates_yaml", PATH_TEMPLATES_YAML,
        "--output_candidates", str(OUT_DIR / "test_top20_ontology_raw.json"),
        "--output_report_json", str(OUT_DIR / "ontology_filter_report_test.json"),
        "--output_report_md", str(OUT_DIR / "ontology_filter_report_test.md"),
        "--max_path_len", "3",
        "--sample_limit", "50",
    ]

    commands = [
    ("01_valid_type_filter.log", cmd_valid_type),
    ("02_test_type_filter.log", cmd_test_type),
    ("03_valid_schema_check.log", cmd_valid_schema),
    ("04_test_schema_check.log", cmd_test_schema),
    ("05_valid_ontology.log", cmd_valid_onto),
    ("06_test_ontology.log", cmd_test_onto),
]

    for log_name, cmd in commands:
        run_cmd(cmd, LOG_DIR / log_name)

    meta["timestamp_end"] = datetime.now().isoformat()
    meta["produced_files"] = [
        str(OUT_DIR / "valid_top20_type_filtered_raw.json"),
        str(OUT_DIR / "test_top20_type_filtered_raw.json"),
        str(OUT_DIR / "valid_top20_ontology_raw.json"),
        str(OUT_DIR / "test_top20_ontology_raw.json"),
        str(OUT_DIR / "ontology_filter_report.json"),
        str(OUT_DIR / "schema_validity_report.json"),
    ]

    with (OUT_DIR / "prep_meta.json").open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print("Finished building ontology_raw branch.")
    print(json.dumps(meta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()