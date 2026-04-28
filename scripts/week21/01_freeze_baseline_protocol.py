#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 21 Day 1
Freeze baseline-as-candidate-generator protocol.

Purpose:
- Week 21 does NOT evaluate baselines using classical full-universe filtered KGC metrics.
- Baselines are treated as upstream top-20 candidate generators for the downstream
  DrKGC/FOG-RAG prompting pipeline.
- This script writes:
    results/week21/baseline_protocol_freeze.json
    reports/week21/day1_baseline_protocol_freeze.md
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(".")
RESULTS_DIR = ROOT / "results" / "week21"
REPORTS_DIR = ROOT / "reports" / "week21"
SCRIPTS_DIR = ROOT / "scripts" / "week21"

OUT_JSON = RESULTS_DIR / "baseline_protocol_freeze.json"
OUT_MD = REPORTS_DIR / "day1_baseline_protocol_freeze.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_protocol() -> dict:
    protocol = {
        "week": 21,
        "day": 1,
        "artifact_name": "baseline_protocol_freeze",
        "created_at_utc": now_utc(),

        "theme": "Fair comparison of structure baselines as top-20 candidate generators",
        "main_question": (
            "If TransE / ComplEx / R-GCN / HRGAT are used as upstream top-20 "
            "candidate generators for the same (? drug, indication, disease) task, "
            "how strong are they compared with backbone_raw, soft_support_raw, "
            "and soft_support_fuzzy_retrieval_main?"
        ),

        "framing_statement": (
            "Structure baselines are evaluated as upstream candidate generators for the "
            "downstream DrKGC/FOG-RAG top-20 prompting pipeline. This is not a classical "
            "full-universe filtered KGC metric."
        ),

        "task_protocol": {
            "task_name": "Setting A head prediction",
            "query_form": "(?, indication, disease)",
            "missing_entity_type": "drug",
            "target_relation": "indication",
            "query_entity_type": "disease",
            "candidate_universe": "drug_only",
            "top_k": 20,
            "split_policy": "Use the same valid/test query sets as FOG-RAG locked evaluation",
            "gold_injection": "forbidden",
            "gold_injection_note": (
                "No baseline output may insert the gold answer into top-20 after retrieval."
            ),
        },

        "metric_protocol": {
            "main_metric": "reviewer_safe_mrr_at20",
            "rr_rule": "RR = 1/rank if rank <= 20 else 0",
            "gold_absent_policy": "gold_absent_from_top20_has_rr_0",
            "absent_rank_sentinel": 21,
            "rr_absent_policy": 0,
            "hits_rule": {
                "hits1_at20": "1 if gold_rank <= 1 else 0",
                "hits3_at20": "1 if gold_rank <= 3 else 0",
                "hits10_at20": "1 if gold_rank <= 10 else 0",
                "hits20_at20": "1 if gold_rank <= 20 else 0",
            },
            "required_metrics": [
                "gold_present_at20",
                "reviewer_safe_mrr_at20",
                "hits1_at20",
                "hits3_at20",
                "hits10_at20",
                "avg_gold_rank_absent_as_21",
                "gold_rank_21_count",
            ],
            "diagnostics": [
                "num_rows",
                "candidate_size",
                "candidate_universe_size",
                "same_query_set",
                "unique_top1_count",
                "top1_dominance",
            ],
            "forbidden_metric_interpretations": [
                "Do not call this Bordes et al. filtered metric.",
                "Do not call this DrKGC classical full-ranking metric.",
                "Do not use 1/21 for absent gold.",
                "Do not report gold-injected candidate metrics as reviewer-safe results.",
            ],
        },

        "baseline_scope": {
            "minimum_baselines": [
                "TransE",
                "ComplEx",
                "R-GCN",
                "HRGAT",
            ],
            "optional_baselines_if_available": [
                "DistMult",
                "RotatE",
            ],
            "baseline_role": "upstream_top20_candidate_generator",
            "required_baseline_output_schema": [
                "split",
                "model_name",
                "query_entity",
                "query_entity_id",
                "gold_entity",
                "gold_entity_id",
                "candidate_entities_top20",
                "candidate_entity_ids_top20",
                "scores_top20",
                "gold_rank_in_top20_or_21",
                "gold_present_top20",
            ],
        },

        "fograg_rows_for_comparison": [
            "backbone_raw",
            "soft_support_raw",
            "soft_support_fuzzy_retrieval_main",
        ],

        "out_of_scope_week21": [
            "classical_full_ranking_KGC_table",
            "Bordes_filtered_metric_claim",
            "dataset_2",
            "Mistral_or_extra_LLM",
            "fuzzy_encoder_promotion",
            "gold_injection",
            "main_row_change_before_clean_baseline_table",
        ],

        "expected_week21_outputs": {
            "results": [
                "results/week21/baseline_protocol_freeze.json",
                "results/week21/baseline_inventory.json",
                "results/week21/baseline_reviewer_safe_valid.json",
                "results/week21/baseline_reviewer_safe_test.json",
                "results/week21/baseline_main_table.json",
                "results/week21/baseline_ablation.json",
                "results/week21/baseline_vs_fograg_decision.json",
                "results/week21/week21_go_decision.json",
            ],
            "reports": [
                "reports/week21/day1_baseline_protocol_freeze.md",
                "reports/week21/day2_baseline_inventory.md",
                "reports/week21/day3_rerun_or_recollect_structure_baselines.md",
                "reports/week21/day4_reviewer_safe_metric_recompute.md",
                "reports/week21/day5_baseline_main_table.md",
                "reports/week21/day6_interpretation_and_paper_positioning.md",
                "reports/week21/day7_week21_closeout.md",
            ],
            "scripts": [
                "scripts/week21/01_freeze_baseline_protocol.py",
                "scripts/week21/02_inventory_baselines.py",
                "scripts/week21/03_rerun_or_collect_baselines.py",
                "scripts/week21/04_recompute_reviewer_safe_metrics.py",
                "scripts/week21/05_build_baseline_main_table.py",
                "scripts/week21/06_build_interpretation_assets.py",
                "scripts/week21/07_write_week21_closeout.py",
            ],
        },

        "paper_positioning_scenarios": {
            "A_fograg_strongest": (
                "FOG-RAG improves the DrKGC-compatible backbone and outperforms "
                "structure-only candidate generators under the downstream top-20 protocol."
            ),
            "B_baseline_slightly_higher": (
                "FOG-RAG is not necessarily the strongest pure candidate generator, "
                "but it improves the DrKGC-compatible source and provides evidence-aware "
                "retrieval with E2E confirmation."
            ),
            "C_baseline_clearly_higher": (
                "Consider a stronger-upstream branch using the strongest baseline as "
                "candidate source before opening Dataset 2."
            ),
        },

        "decision_after_day1": "PROTOCOL_FROZEN_READY_FOR_INVENTORY",
    }

    return protocol


def validate_protocol(protocol: dict) -> None:
    task = protocol["task_protocol"]
    metric = protocol["metric_protocol"]

    assert task["query_form"] == "(?, indication, disease)"
    assert task["missing_entity_type"] == "drug"
    assert task["candidate_universe"] == "drug_only"
    assert task["top_k"] == 20
    assert task["gold_injection"] == "forbidden"

    assert metric["main_metric"] == "reviewer_safe_mrr_at20"
    assert metric["rr_rule"] == "RR = 1/rank if rank <= 20 else 0"
    assert metric["absent_rank_sentinel"] == 21
    assert metric["rr_absent_policy"] == 0

    forbidden = "gold_injection" in protocol["out_of_scope_week21"]
    assert forbidden, "gold_injection must be listed as out of scope for Week 21"


def write_json(protocol: dict) -> None:
    OUT_JSON.write_text(
        json.dumps(protocol, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_report(protocol: dict) -> None:
    task = protocol["task_protocol"]
    metric = protocol["metric_protocol"]

    md = f"""# Week 21 Day 1 — Baseline Protocol Freeze

## Decision

**{protocol["decision_after_day1"]}**

## Theme

{protocol["theme"]}

## Main question

{protocol["main_question"]}

## Required framing statement

> {protocol["framing_statement"]}

## Frozen task protocol

| Field | Value |
|---|---|
| Task | {task["task_name"]} |
| Query form | `{task["query_form"]}` |
| Missing entity type | `{task["missing_entity_type"]}` |
| Target relation | `{task["target_relation"]}` |
| Query entity type | `{task["query_entity_type"]}` |
| Candidate universe | `{task["candidate_universe"]}` |
| Top-k | `{task["top_k"]}` |
| Gold injection | `{task["gold_injection"]}` |

## Frozen metric protocol

| Field | Value |
|---|---|
| Main metric | `{metric["main_metric"]}` |
| RR rule | `{metric["rr_rule"]}` |
| Gold absent policy | `{metric["gold_absent_policy"]}` |
| Absent rank sentinel | `{metric["absent_rank_sentinel"]}` |
| RR for absent gold | `{metric["rr_absent_policy"]}` |

## Required metrics

{chr(10).join([f"- `{m}`" for m in metric["required_metrics"]])}

## Diagnostics to collect

{chr(10).join([f"- `{m}`" for m in metric["diagnostics"]])}

## Baselines in scope

Minimum baselines:

{chr(10).join([f"- `{b}`" for b in protocol["baseline_scope"]["minimum_baselines"]])}

Optional baselines if already available:

{chr(10).join([f"- `{b}`" for b in protocol["baseline_scope"]["optional_baselines_if_available"]])}

## FOG-RAG rows for comparison

{chr(10).join([f"- `{r}`" for r in protocol["fograg_rows_for_comparison"]])}

## Explicitly out of scope in Week 21

{chr(10).join([f"- `{x}`" for x in protocol["out_of_scope_week21"]])}

## Forbidden interpretations

{chr(10).join([f"- {x}" for x in metric["forbidden_metric_interpretations"]])}

## Paper-positioning scenarios prepared

### Scenario A — FOG-RAG strongest

{protocol["paper_positioning_scenarios"]["A_fograg_strongest"]}

### Scenario B — One baseline slightly higher

{protocol["paper_positioning_scenarios"]["B_baseline_slightly_higher"]}

### Scenario C — Baseline clearly higher

{protocol["paper_positioning_scenarios"]["C_baseline_clearly_higher"]}

## Next step

Proceed to **Day 2 — Baseline inventory audit**.

Day 2 should identify which baseline artifacts already exist, which ones can be recollected, and which ones must be rerun.
"""

    OUT_MD.write_text(md, encoding="utf-8")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    protocol = build_protocol()
    validate_protocol(protocol)
    write_json(protocol)
    write_report(protocol)

    print("=" * 100)
    print("WEEK 21 DAY 1 — BASELINE PROTOCOL FREEZE")
    print("=" * 100)
    print(f"JSON written:   {OUT_JSON}")
    print(f"Report written: {OUT_MD}")
    print()
    print("Frozen protocol summary:")
    print(f"  task              = {protocol['task_protocol']['query_form']}")
    print(f"  candidate universe= {protocol['task_protocol']['candidate_universe']}")
    print(f"  top_k             = {protocol['task_protocol']['top_k']}")
    print(f"  gold injection    = {protocol['task_protocol']['gold_injection']}")
    print(f"  main metric       = {protocol['metric_protocol']['main_metric']}")
    print(f"  rr rule           = {protocol['metric_protocol']['rr_rule']}")
    print(f"  absent rank       = {protocol['metric_protocol']['absent_rank_sentinel']}")
    print(f"  absent rr         = {protocol['metric_protocol']['rr_absent_policy']}")
    print()
    print("Decision:", protocol["decision_after_day1"])
    print("=" * 100)


if __name__ == "__main__":
    main()