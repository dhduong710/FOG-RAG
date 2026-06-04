#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 22 Day 1: Freeze Dataset 2 reviewer-safe protocol.

Purpose:
- Freeze the protocol before inspecting/optimizing PharmKG.
- Keep Dataset 2 aligned with Setting A / Week 21 reviewer-safe top-20 protocol.
- Prepare a data download plan for PharmKG-8k and raw PharmKG.

This script does NOT choose the target relation yet.
Relation/schema selection is Day 3.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(".")
RESULT_DIR = ROOT / "results" / "week22"
REPORT_DIR = ROOT / "reports" / "week22"
DATASET_DIR = ROOT / "dataset" / "setting_c_pharmkg"
RAW_INV_DIR = DATASET_DIR / "00_raw_inventory"
RAW_DATA_DIR = ROOT / "data" / "raw" / "pharmkg"

PROTOCOL_PATH = RESULT_DIR / "dataset2_protocol_freeze.json"
REPORT_PATH = REPORT_DIR / "day1_dataset2_protocol_freeze.md"
DOWNLOAD_PLAN_PATH = RAW_INV_DIR / "download_plan.json"


def ensure_dirs() -> None:
    for p in [RESULT_DIR, REPORT_DIR, RAW_INV_DIR, RAW_DATA_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def build_protocol() -> dict:
    now = datetime.now(timezone.utc).isoformat()

    return {
        "week": 22,
        "day": 1,
        "created_at_utc": now,
        "decision": "DATASET2_PROTOCOL_FROZEN_RELATION_PENDING",
        "dataset_2_name": "PharmKG candidate",
        "dataset_2_setting_name": "setting_c_pharmkg",

        "paper_role": {
            "purpose": "test_transferability_of_FOG_RAG_pipeline",
            "not_purpose": [
                "introduce_a_new_metric",
                "replace_PrimeKG_Setting_A_main_claim",
                "use_gold_injection",
                "run_full_FOG_RAG_stage_A_B_C_before_dataset_is_clean"
            ],
            "paper_framing": (
                "Dataset 2 is evaluated under the same top-20 no-injection "
                "reviewer-safe protocol as Setting A. The purpose is to test "
                "transferability of the FOG-RAG pipeline, not to introduce a "
                "different KGC metric."
            )
        },

        "task_template": {
            "incomplete_triple": "(?, therapeutic_relation_candidate, disease)",
            "missing_entity_type": "drug",
            "query_entity_type": "disease",
            "candidate_universe": "drug_only",
            "target_relation_status": "unresolved_until_day3",
            "target_relation_placeholder": "therapeutic_relation_candidate",
            "allowed_normalized_target_relation_names": [
                "indication",
                "treatment",
                "therapeutic_association",
                "therapeutic_association_proxy"
            ],
            "relation_warning": (
                "Do not call the selected PharmKG relation 'clinical indication' "
                "unless Day 3 schema inspection confirms that semantics."
            )
        },

        "candidate_protocol": {
            "top_k": 20,
            "gold_injection": False,
            "gold_injection_policy": "forbidden",
            "candidate_universe": "drug_only",
            "candidate_source_day1_status": "not_selected_yet",
            "main_fograg_source_preference": (
                "DrKGC-compatible structure source such as R-GCN or HRGAT; "
                "stronger sources such as ComplEx can be recorded as optional "
                "future/appendix branch if they outperform the DrKGC-compatible source."
            )
        },

        "reviewer_safe_metric_policy": {
            "main_metric": "reviewer_safe_mrr_at20",
            "rank_absent_sentinel": 21,
            "rr_policy": "RR = 1/rank if gold is present and rank <= 20 else 0",
            "rr_absent_policy": 0.0,
            "do_not_use": [
                "1/21 reciprocal rank for absent gold",
                "classical full-ranking filtered KGC metric name",
                "gold-injected candidate evaluation as main claim"
            ],
            "reported_metrics": [
                "gold_present_at20",
                "mrr_at20",
                "hits1_at20",
                "hits3_at20",
                "hits10_at20",
                "hits20_at20",
                "avg_gold_rank_absent_as_21",
                "gold_rank_21_count",
                "candidate_universe_size",
                "unique_top1_count",
                "top1_dominance"
            ]
        },

        "split_policy_later_days": {
            "seed": 2025,
            "preferred_valid_size": 500,
            "preferred_test_size": 500,
            "fallback_if_small_dataset": "valid/test = 10%/10%",
            "coverage_rule": [
                "valid/test gold drugs must appear in train",
                "valid/test query diseases must appear in train"
            ],
            "leak_policy": [
                "no exact valid positive triple in train",
                "no exact test positive triple in train",
                "no duplicate positive triples across train/valid/test",
                "no valid/test target triples included in train_enriched.tsv"
            ]
        },

        "day1_checks_expected": {
            "candidate_universe_is_drug_only": True,
            "top_k_is_20": True,
            "gold_injection_forbidden": True,
            "absent_rank_sentinel_is_21": True,
            "rr_absent_policy_is_zero": True,
            "target_relation_not_selected_yet": True
        }
    }


def build_download_plan() -> dict:
    return {
        "week": 22,
        "day": 1,
        "purpose": "Prepare PharmKG acquisition for Day 2 raw inventory.",
        "preferred_dataset": "PharmKG-8k",
        "sources_to_try": [
            {
                "name": "biomed-AI PharmKG GitHub PharmKG-8k",
                "priority": 1,
                "reason": (
                    "Contains pre-partitioned PharmKG-8k train/valid/test TSV files. "
                    "This is the most convenient source for Day 2 inventory."
                ),
                "files": [
                    {
                        "filename": "train.tsv",
                        "url": "https://raw.githubusercontent.com/biomed-AI/PharmKG/master/data/PharmKG-8k/train.tsv"
                    },
                    {
                        "filename": "valid.tsv",
                        "url": "https://raw.githubusercontent.com/biomed-AI/PharmKG/master/data/PharmKG-8k/valid.tsv"
                    },
                    {
                        "filename": "test.tsv",
                        "url": "https://raw.githubusercontent.com/biomed-AI/PharmKG/master/data/PharmKG-8k/test.tsv"
                    },
                    {
                        "filename": "entity2vec.txt",
                        "url": "https://raw.githubusercontent.com/biomed-AI/PharmKG/master/data/PharmKG-8k/entity2vec.txt"
                    },
                    {
                        "filename": "relation2vec.txt",
                        "url": "https://raw.githubusercontent.com/biomed-AI/PharmKG/master/data/PharmKG-8k/relation2vec.txt"
                    }
                ]
            },
            {
                "name": "Official PharmKG Zenodo raw archive",
                "priority": 2,
                "reason": (
                    "Official raw archive. Larger file. Use if GitHub split files "
                    "are insufficient for entity/relation/type mapping."
                ),
                "files": [
                    {
                        "filename": "raw_PharmKG-180k.zip",
                        "url": "https://zenodo.org/records/4077338/files/raw_PharmKG-180k.zip?download=1"
                    }
                ]
            },
            {
                "name": "MindRank-Biotech PharmKG repository",
                "priority": 3,
                "reason": (
                    "Original PharmKG code repository; useful for README statistics, "
                    "preprocessing notes, and Google Drive references if needed."
                ),
                "repo": "https://github.com/MindRank-Biotech/PharmKG"
            }
        ],
        "day2_inventory_questions": [
            "Which file contains triples?",
            "Do train/valid/test TSV files have three columns: head, relation, tail?",
            "Are entities named or ID-coded?",
            "Is there an explicit entity type map?",
            "Can Drug/Chemical and Disease entities be separated cleanly?",
            "Which relation can serve as treatment/indication/therapeutic association target?",
            "Do we need the larger Zenodo raw archive to recover entity names/types?"
        ],
        "local_raw_data_dir": str(RAW_DATA_DIR)
    }


def write_json(obj: dict, path: Path) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def write_report(protocol: dict, download_plan: dict) -> None:
    md = f"""# Week 22 Day 1 — Dataset 2 Protocol Freeze

## Decision

`{protocol["decision"]}`

Dataset 2 is currently treated as: **{protocol["dataset_2_name"]}**.

The selected relation is **not fixed today**. It remains:

`{protocol["task_template"]["target_relation_placeholder"]}`

Relation/schema selection will be done on Day 3 after raw inventory.

## Frozen task frame

- Incomplete triple: `{protocol["task_template"]["incomplete_triple"]}`
- Missing entity type: `{protocol["task_template"]["missing_entity_type"]}`
- Query entity type: `{protocol["task_template"]["query_entity_type"]}`
- Candidate universe: `{protocol["task_template"]["candidate_universe"]}`
- Top-K: `{protocol["candidate_protocol"]["top_k"]}`
- Gold injection: `{protocol["candidate_protocol"]["gold_injection_policy"]}`

## Reviewer-safe metric policy

Main metric:

`{protocol["reviewer_safe_metric_policy"]["main_metric"]}`

RR policy:

`{protocol["reviewer_safe_metric_policy"]["rr_policy"]}`

Absent-gold policy:

- descriptive rank sentinel = `{protocol["reviewer_safe_metric_policy"]["rank_absent_sentinel"]}`
- RR contribution = `{protocol["reviewer_safe_metric_policy"]["rr_absent_policy"]}`

Do **not** use 1/21 as reciprocal rank for absent gold.

## Paper framing

{protocol["paper_role"]["paper_framing"]}

## PharmKG data acquisition plan for Day 2

Preferred source: **{download_plan["preferred_dataset"]}**

Sources to try:

1. biomed-AI PharmKG GitHub PharmKG-8k:
   - train.tsv
   - valid.tsv
   - test.tsv
   - entity2vec.txt
   - relation2vec.txt

2. Official PharmKG Zenodo raw archive:
   - raw_PharmKG-180k.zip

3. MindRank-Biotech PharmKG repository:
   - README statistics
   - preprocessing notes
   - links to original/raw resources

## Day 1 checks

- candidate_universe = drug_only
- top_k = 20
- gold_injection = forbidden
- rr_absent_policy = 0
- absent_rank_sentinel = 21
- target relation is not selected yet

## Files written

- `{PROTOCOL_PATH}`
- `{DOWNLOAD_PLAN_PATH}`
- `{REPORT_PATH}`

## Next day

Day 2 will download or locate PharmKG files and run raw inventory:
file list, row counts, columns, sample rows, relation counts, and possible entity/type sources.
"""
    REPORT_PATH.write_text(md, encoding="utf-8")


def main() -> None:
    ensure_dirs()

    protocol = build_protocol()
    download_plan = build_download_plan()

    write_json(protocol, PROTOCOL_PATH)
    write_json(download_plan, DOWNLOAD_PLAN_PATH)
    write_report(protocol, download_plan)

    print("Saved:")
    print(f"  {PROTOCOL_PATH}")
    print(f"  {DOWNLOAD_PLAN_PATH}")
    print(f"  {REPORT_PATH}")

    checks = protocol["day1_checks_expected"]
    failed = [k for k, v in checks.items() if v is not True]
    if failed:
        raise RuntimeError(f"Day 1 protocol checks failed: {failed}")

    print("\nDay 1 protocol freeze: PASS")
    print(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()