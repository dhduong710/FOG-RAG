from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(".").resolve()

EXPECTED_TEST_SOURCES = {
    "backbone_raw_test_source": "results/reference_rows/backbone_raw_test",
    "raw_source_test": "dataset/setting_a/23_noinj_source/test_top20_raw.json",
    "ontology_raw_test": "dataset/setting_a/24_noinj_ontology/test_top20_ontology_raw.json",
    "soft_support_raw_test": "dataset/setting_a/26_n2_soft_support/test_top20_soft_support_main.json",
    "retrieval_main_test": "dataset/setting_a/27_n2_fuzzy_retrieval/test_fuzzy_retrieval_main.json",
    "setting_b_test_annotations": "dataset/setting_b/04_contra_checked/test_b_annotations_contra_checked.json",
}

OPTIONAL_TEST_SOURCES = {
    "encoder_probe_test_optional": "dataset/setting_a/28_n2_fuzzy_encoder/test_fuzzy_encoder_probe_v0.json",
}

OUT_JSON = ROOT / "results/week18/test_readiness_manifest.json"
OUT_MD = ROOT / "reports/week18/day5_test_readiness.md"


def check_path(rel_path: str) -> dict:
    p = ROOT / rel_path
    info = {
        "path": rel_path,
        "exists": p.exists(),
        "is_file": p.is_file() if p.exists() else False,
        "is_dir": p.is_dir() if p.exists() else False,
        "size_bytes": p.stat().st_size if p.exists() and p.is_file() else None,
    }

    if p.exists() and p.is_file():
        try:
            if p.suffix.lower() == ".json":
                with p.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    info["json_kind"] = "list"
                    info["num_rows"] = len(data)
                    info["top_keys"] = list(data[0].keys()) if data else []
                elif isinstance(data, dict):
                    info["json_kind"] = "dict"
                    info["top_keys"] = list(data.keys())
            else:
                info["json_kind"] = "non_json_file"
        except Exception as e:
            info["json_read_error"] = str(e)

    return info


def readiness_decision(required: dict) -> tuple[str, list[str]]:
    missing = [k for k, v in required.items() if not v["exists"]]

    notes = []

    if missing:
        notes.append(f"Missing required test sources: {missing}")

    # critical minimum
    critical = [
        "raw_source_test",
        "ontology_raw_test",
        "setting_b_test_annotations",
    ]
    critical_missing = [k for k in critical if not required[k]["exists"]]

    if critical_missing:
        notes.append(f"Critical missing sources: {critical_missing}")
        return "BLOCKED", notes

    # fully ready requires all 4 row families + annotations
    required_main_rows = [
        "raw_source_test",
        "ontology_raw_test",
        "soft_support_raw_test",
        "retrieval_main_test",
        "setting_b_test_annotations",
    ]
    missing_main = [k for k in required_main_rows if not required[k]["exists"]]

    if missing_main:
        notes.append(f"Main locked-test sources still missing: {missing_main}")
        return "PARTIAL_READY", notes

    notes.append("All required main test sources exist.")
    return "READY_FOR_LOCKED_TEST", notes


def main():
    required_status = {k: check_path(v) for k, v in EXPECTED_TEST_SOURCES.items()}
    optional_status = {k: check_path(v) for k, v in OPTIONAL_TEST_SOURCES.items()}

    decision, notes = readiness_decision(required_status)

    schema_notes = []

    # Optional sanity checks
    for key in ["raw_source_test", "ontology_raw_test", "soft_support_raw_test", "retrieval_main_test"]:
        meta = required_status.get(key, {})
        if meta.get("exists") and meta.get("is_file") and meta.get("json_kind") == "list":
            top_keys = set(meta.get("top_keys", []))
            if "query_entity" not in top_keys or "gold_entity" not in top_keys:
                schema_notes.append(f"{key}: missing query/gold fields in top-level keys.")
        elif meta.get("exists") and meta.get("is_dir"):
            schema_notes.append(f"{key}: exists as directory; manual inspection may be needed.")

    report = {
        "week": 18,
        "day": 5,
        "mode": "test_readiness_check_only",
        "main_row_after_week17": "soft_support_fuzzy_retrieval_main",
        "official_test_run_in_week18": False,
        "required_test_sources": required_status,
        "optional_test_sources": optional_status,
        "schema_notes": schema_notes,
        "decision": decision,
        "decision_notes": notes,
        "recommended_next_step": (
            "Proceed to locked test only after all main test sources are present and canonical."
            if decision == "READY_FOR_LOCKED_TEST"
            else "Do not run official locked test yet; finish missing main test sources first."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = []
    lines.append("# Week 18 Day 5 — Test Readiness\n")
    lines.append("## Decision")
    lines.append(f"- **{report['decision']}**")
    lines.append(f"- Recommended next step: `{report['recommended_next_step']}`")
    lines.append("")
    lines.append("## Required test sources")
    for k, v in required_status.items():
        lines.append(
            f"- `{k}`: exists=`{v['exists']}` is_file=`{v['is_file']}` is_dir=`{v['is_dir']}` path=`{v['path']}`"
        )
    lines.append("")
    lines.append("## Optional test sources")
    for k, v in optional_status.items():
        lines.append(
            f"- `{k}`: exists=`{v['exists']}` is_file=`{v['is_file']}` is_dir=`{v['is_dir']}` path=`{v['path']}`"
        )
    lines.append("")
    lines.append("## Schema notes")
    if schema_notes:
        for x in schema_notes:
            lines.append(f"- {x}")
    else:
        lines.append("- No obvious schema issues detected in the inspected test files.")
    lines.append("")
    lines.append("## Decision notes")
    for x in notes:
        lines.append(f"- {x}")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote {OUT_JSON}")
    print(f"[OK] wrote {OUT_MD}")
    print(json.dumps({
        "decision": report["decision"],
        "decision_notes": report["decision_notes"],
        "schema_notes": report["schema_notes"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()