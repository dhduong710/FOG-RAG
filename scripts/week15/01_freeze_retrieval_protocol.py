from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Tuple


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_query_key(row: Dict[str, Any]) -> str:
    """
    Ưu tiên query_entity_id nếu có, fallback sang query_entity.
    Chuẩn hóa thành string để so set an toàn.
    """
    if "query_entity_id" in row:
        return f"id::{row['query_entity_id']}"
    if "query_entity" in row:
        return f"name::{row['query_entity']}"
    raise KeyError("Row does not contain query_entity_id or query_entity.")


def count_candidates(row: Dict[str, Any]) -> int | None:
    for key in [
        "candidate_entities",
        "candidate_drugs",
        "rank_entities",
    ]:
        value = row.get(key)
        if isinstance(value, list):
            return len(value)
    return None


def summarize_first_row(row: Dict[str, Any]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "keys": list(row.keys()),
    }
    for key in [
        "split",
        "query_entity",
        "query_entity_id",
        "gold_entity",
        "gold_entity_id",
        "variant_name",
    ]:
        if key in row:
            summary[key] = row[key]

    cand_count = count_candidates(row)
    if cand_count is not None:
        summary["candidate_count"] = cand_count

    return summary


def index_by_query(rows: List[Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
    idx: Dict[str, Dict[str, Any]] = {}
    duplicates: List[str] = []
    for row in rows:
        key = get_query_key(row)
        if key in idx:
            duplicates.append(key)
        idx[key] = row
    return idx, duplicates


def compare_query_sets(
    raw_rows: List[Dict[str, Any]],
    evidence_rows: List[Dict[str, Any]],
    support_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    raw_idx, raw_dups = index_by_query(raw_rows)
    evidence_idx, evidence_dups = index_by_query(evidence_rows)
    support_idx, support_dups = index_by_query(support_rows)

    raw_keys = set(raw_idx.keys())
    evidence_keys = set(evidence_idx.keys())
    support_keys = set(support_idx.keys())

    return {
        "raw_count": len(raw_rows),
        "evidence_count": len(evidence_rows),
        "support_count": len(support_rows),
        "raw_unique_queries": len(raw_keys),
        "evidence_unique_queries": len(evidence_keys),
        "support_unique_queries": len(support_keys),
        "raw_duplicates": raw_dups[:20],
        "evidence_duplicates": evidence_dups[:20],
        "support_duplicates": support_dups[:20],
        "raw_minus_evidence": sorted(list(raw_keys - evidence_keys))[:20],
        "evidence_minus_raw": sorted(list(evidence_keys - raw_keys))[:20],
        "raw_minus_support": sorted(list(raw_keys - support_keys))[:20],
        "support_minus_raw": sorted(list(support_keys - raw_keys))[:20],
        "triple_intersection_size": len(raw_keys & evidence_keys & support_keys),
        "raw_vs_evidence_exact_match": raw_keys == evidence_keys,
        "raw_vs_support_exact_match": raw_keys == support_keys,
        "all_three_exact_match": (raw_keys == evidence_keys == support_keys),
    }


def main() -> None:
    root = Path(__file__).resolve().parents[2]

    paths = {
        "raw_source": root / "dataset/setting_a/23_noinj_source/valid_top20_raw.json",
        "aligned_evidence": root / "dataset/setting_a/24b_noinj_evidence/valid_aligned_evidence.json",
        "soft_support_main": root / "dataset/setting_a/26_n2_soft_support/valid_top20_soft_support_main.json",
        "ontology_raw": root / "dataset/setting_a/24_noinj_ontology/valid_top20_ontology_raw.json",
        "type_map": root / "dataset/setting_b/01_annotations/type_map.tsv",
        "schema_rules": root / "dataset/setting_b/01_annotations/schema_rules.json",
        "path_templates": root / "dataset/setting_b/01_annotations/path_templates.yaml",
        "valid_b_annotations": root / "dataset/setting_b/04_contra_checked/valid_b_annotations_contra_checked.json",
        "reference_backbone_dir": root / "results/reference_rows/backbone_raw_valid",
        "report_out": root / "reports/week15/day1_protocol_freeze.md",
        "manifest_out": root / "results/week15/week15_input_manifest.json",
    }

    missing = [name for name, path in paths.items() if name.endswith("_out") is False and not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required week-15 inputs: " + ", ".join(missing)
        )

    raw_rows = load_json(paths["raw_source"])
    evidence_rows = load_json(paths["aligned_evidence"])
    support_rows = load_json(paths["soft_support_main"])
    ontology_rows = load_json(paths["ontology_raw"])

    if not isinstance(raw_rows, list) or not raw_rows:
        raise ValueError("raw_source must be a non-empty JSON list.")
    if not isinstance(evidence_rows, list) or not evidence_rows:
        raise ValueError("aligned_evidence must be a non-empty JSON list.")
    if not isinstance(support_rows, list) or not support_rows:
        raise ValueError("soft_support_main must be a non-empty JSON list.")
    if not isinstance(ontology_rows, list) or not ontology_rows:
        raise ValueError("ontology_raw must be a non-empty JSON list.")

    query_compare = compare_query_sets(raw_rows, evidence_rows, support_rows)

    manifest = {
        "week": 15,
        "theme": "Start retrieval-stage on top of frozen soft_support_raw",
        "decision_split": "valid",
        "main_truth": "raw/no-injection",
        "reference_row": "backbone_raw",
        "negative_control": "ontology_raw",
        "main_intermediate_input": "soft_support_raw",
        "target_output_row": "soft_support_fuzzy_retrieval_v1",
        "allowed_main_inputs": {
            "raw_source": {
                "path": str(paths["raw_source"].relative_to(root)),
                "sha256": sha256_of_file(paths["raw_source"]),
                "num_rows": len(raw_rows),
                "first_row_summary": summarize_first_row(raw_rows[0]),
            },
            "aligned_evidence": {
                "path": str(paths["aligned_evidence"].relative_to(root)),
                "sha256": sha256_of_file(paths["aligned_evidence"]),
                "num_rows": len(evidence_rows),
                "first_row_summary": summarize_first_row(evidence_rows[0]),
            },
            "soft_support_main": {
                "path": str(paths["soft_support_main"].relative_to(root)),
                "sha256": sha256_of_file(paths["soft_support_main"]),
                "num_rows": len(support_rows),
                "first_row_summary": summarize_first_row(support_rows[0]),
            },
        },
        "lookup_inputs": {
            "type_map": str(paths["type_map"].relative_to(root)),
            "schema_rules": str(paths["schema_rules"].relative_to(root)),
            "path_templates": str(paths["path_templates"].relative_to(root)),
            "valid_b_annotations": str(paths["valid_b_annotations"].relative_to(root)),
        },
        "comparison_only_inputs": {
            "ontology_raw": {
                "path": str(paths["ontology_raw"].relative_to(root)),
                "sha256": sha256_of_file(paths["ontology_raw"]),
                "num_rows": len(ontology_rows),
                "first_row_summary": summarize_first_row(ontology_rows[0]),
            },
            "reference_backbone_dir": str(paths["reference_backbone_dir"].relative_to(root)),
        },
        "forbidden_actions": [
            "change_raw_source",
            "reopen_candidate_stage_variants",
            "use_ontology_raw_as_positive_signal",
            "run_test",
            "enable_fuzzy_encoder",
            "run_end_to_end_reranker_training",
        ],
        "query_alignment_check": query_compare,
    }

    paths["manifest_out"].parent.mkdir(parents=True, exist_ok=True)
    with paths["manifest_out"].open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print("=" * 80)
    print("WEEK 15 INPUT MANIFEST WRITTEN")
    print(paths["manifest_out"])
    print("=" * 80)
    print("raw_rows               =", len(raw_rows))
    print("evidence_rows          =", len(evidence_rows))
    print("soft_support_rows      =", len(support_rows))
    print("ontology_rows          =", len(ontology_rows))
    print("all_three_exact_match  =", query_compare["all_three_exact_match"])
    print("raw_vs_evidence_match  =", query_compare["raw_vs_evidence_exact_match"])
    print("raw_vs_support_match   =", query_compare["raw_vs_support_exact_match"])
    print("intersection_size      =", query_compare["triple_intersection_size"])
    print("=" * 80)

    # Fail hard nếu ba nguồn chính không align exact.
    if not query_compare["all_three_exact_match"]:
        raise RuntimeError(
            "Query sets do not align exactly across raw_source, aligned_evidence, and soft_support_main."
        )


if __name__ == "__main__":
    main()