from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PATHS = {
    "raw_source": ROOT / "dataset/setting_a/23_noinj_source/valid_top20_raw.json",
    "aligned_evidence": ROOT / "dataset/setting_a/24b_noinj_evidence/valid_aligned_evidence.json",
    "soft_support_main": ROOT / "dataset/setting_a/26_n2_soft_support/valid_top20_soft_support_main.json",
    "retrieval_v1": ROOT / "dataset/setting_a/27_n2_fuzzy_retrieval/valid_fuzzy_retrieval_v1.json",
    "retrieval_v1_manifest": ROOT / "dataset/setting_a/27_n2_fuzzy_retrieval/path_score_manifest.json",
    "type_map": ROOT / "dataset/setting_b/01_annotations/type_map.tsv",
    "schema_rules": ROOT / "dataset/setting_b/01_annotations/schema_rules.json",
    "path_templates": ROOT / "dataset/setting_b/01_annotations/path_templates.yaml",
    "valid_b_annotations": ROOT / "dataset/setting_b/04_contra_checked/valid_b_annotations_contra_checked.json",
    "reference_backbone_dir": ROOT / "results/reference_rows/backbone_raw_valid",
    "ontology_raw": ROOT / "dataset/setting_a/24_noinj_ontology/valid_top20_ontology_raw.json",
    "week15_go_decision": ROOT / "results/week15/week15_go_decision.json",
}

OUT_MANIFEST = ROOT / "results/week16/retrieval_variant_manifest.json"


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def summarize_json_list(path: Path) -> Dict[str, Any]:
    rows = load_json(path)
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{path} is not a non-empty JSON list.")
    first = rows[0]
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256_of_file(path),
        "num_rows": len(rows),
        "first_row_keys": list(first.keys()),
        "split": first.get("split"),
        "query_entity": first.get("query_entity"),
        "query_entity_id": first.get("query_entity_id"),
        "gold_entity": first.get("gold_entity"),
        "gold_entity_id": first.get("gold_entity_id"),
        "variant_name": first.get("variant_name"),
    }


def main() -> None:
    missing = [name for name, path in REQUIRED_PATHS.items() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required week-16 inputs: " + ", ".join(missing))

    week15_go = load_json(REQUIRED_PATHS["week15_go_decision"])
    if week15_go.get("decision") != "GO":
        raise RuntimeError("Week 15 decision is not GO. Week 16 protocol should not be frozen yet.")

    manifest = {
        "week": 16,
        "theme": "retrieval_sweep_and_main_row_selection",
        "decision_split": "valid",
        "main_truth": "raw/no-injection",
        "reference_row": "backbone_raw",
        "negative_control": "ontology_raw",
        "main_intermediate_input": "soft_support_raw",
        "reference_retrieval_row": "soft_support_fuzzy_retrieval_v1",
        "target_output_row": "soft_support_fuzzy_retrieval_main",
        "allowed_main_inputs": {
            "raw_source": summarize_json_list(REQUIRED_PATHS["raw_source"]),
            "aligned_evidence": summarize_json_list(REQUIRED_PATHS["aligned_evidence"]),
            "soft_support_main": summarize_json_list(REQUIRED_PATHS["soft_support_main"]),
            "retrieval_v1": summarize_json_list(REQUIRED_PATHS["retrieval_v1"]),
            "retrieval_v1_manifest": {
                "path": str(REQUIRED_PATHS["retrieval_v1_manifest"].relative_to(ROOT)),
                "sha256": sha256_of_file(REQUIRED_PATHS["retrieval_v1_manifest"]),
            },
        },
        "lookup_inputs": {
            "type_map": str(REQUIRED_PATHS["type_map"].relative_to(ROOT)),
            "schema_rules": str(REQUIRED_PATHS["schema_rules"].relative_to(ROOT)),
            "path_templates": str(REQUIRED_PATHS["path_templates"].relative_to(ROOT)),
            "valid_b_annotations": str(REQUIRED_PATHS["valid_b_annotations"].relative_to(ROOT)),
        },
        "comparison_only_inputs": {
            "reference_backbone_dir": str(REQUIRED_PATHS["reference_backbone_dir"].relative_to(ROOT)),
            "ontology_raw": str(REQUIRED_PATHS["ontology_raw"].relative_to(ROOT)),
        },
        "planned_variants": [
            {
                "name": "soft_support_fuzzy_retrieval_v1",
                "role": "frozen_reference_row_from_week15",
            },
            {
                "name": "soft_support_fuzzy_retrieval_tight",
                "role": "smaller_budget_variant",
                "allowed_changes": ["retain_ratio", "min_keep"],
            },
            {
                "name": "soft_support_fuzzy_retrieval_directplus",
                "role": "stronger_direct_shortcut_penalty_variant",
                "allowed_changes": ["direct_shortcut_penalty"],
            },
            {
                "name": "soft_support_fuzzy_retrieval_loose",
                "role": "optional_looser_budget_variant",
                "allowed_changes": ["retain_ratio", "min_keep"],
                "optional": True,
            },
        ],
        "allowed_sweep_axes": [
            "retrieval_budget_or_retain_ratio",
            "direct_shortcut_penalty",
            "at_most_one_small_coverage_policy_tweak",
        ],
        "forbidden_actions": [
            "change_raw_source",
            "reopen_candidate_stage",
            "change_soft_support_raw",
            "use_ontology_raw_as_positive_signal",
            "run_test",
            "enable_fuzzy_encoder",
            "run_end_to_end_reranker_training",
            "open_too_many_retrieval_variants",
        ],
        "week15_bridge": {
            "decision": week15_go["decision"],
            "main_output_row": week15_go["main_output_row"],
            "shortcut_gain_vs_soft_support": week15_go["week15_main_findings"]["shortcut_gain_vs_soft_support"],
            "candidate_coverage_preserved_rate": week15_go["week15_main_findings"]["candidate_coverage_preserved_rate"],
            "ranking_proxy_hold": {
                "mrr_like_soft_support": week15_go["week15_main_findings"]["mrr_like_soft_support"],
                "mrr_like_fuzzy_v1": week15_go["week15_main_findings"]["mrr_like_fuzzy_v1"],
                "hits1_like_soft_support": week15_go["week15_main_findings"]["hits1_like_soft_support"],
                "hits1_like_fuzzy_v1": week15_go["week15_main_findings"]["hits1_like_fuzzy_v1"],
                "avg_gold_rank_soft_support": week15_go["week15_main_findings"]["avg_gold_rank_soft_support"],
                "avg_gold_rank_fuzzy_v1": week15_go["week15_main_findings"]["avg_gold_rank_fuzzy_v1"],
            },
        },
    }

    OUT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with OUT_MANIFEST.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print("=" * 80)
    print("WEEK 16 RETRIEVAL VARIANT MANIFEST WRITTEN")
    print(OUT_MANIFEST)
    print("=" * 80)
    print("theme =", manifest["theme"])
    print("decision_split =", manifest["decision_split"])
    print("main_intermediate_input =", manifest["main_intermediate_input"])
    print("reference_retrieval_row =", manifest["reference_retrieval_row"])
    print("target_output_row =", manifest["target_output_row"])
    print("num_planned_variants =", len(manifest["planned_variants"]))
    print("=" * 80)


if __name__ == "__main__":
    main()