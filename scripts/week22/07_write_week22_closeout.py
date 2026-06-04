#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 22 Day 7: Close out PharmKG Dataset 2 setup.

This script validates Week 22 deliverables and writes:

- results/week22/week22_closeout.json
- results/week22/week22_go_decision.json
- reports/week22/day7_week22_closeout.md
- reports/week22/week22_closeout.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(".")

RESULT_DIR = ROOT / "results" / "week22"
REPORT_DIR = ROOT / "reports" / "week22"

DATASET_DIR = ROOT / "dataset" / "setting_c_pharmkg"
RAW_INV_DIR = DATASET_DIR / "00_raw_inventory"
TASK_DIR = DATASET_DIR / "01_task_spec"
SPLIT_DIR = DATASET_DIR / "02_splits"
GRAPH_DIR = DATASET_DIR / "03_graph"
BASELINE_DIR = DATASET_DIR / "04_baseline_outputs"
RAW_SOURCE_DIR = DATASET_DIR / "05_backbone_raw_source"
FOGRAG_READY_DIR = DATASET_DIR / "06_fograg_ready"

CLOSEOUT_JSON_PATH = RESULT_DIR / "week22_closeout.json"
GO_DECISION_PATH = RESULT_DIR / "week22_go_decision.json"
DAY7_REPORT_PATH = REPORT_DIR / "day7_week22_closeout.md"
WEEK_REPORT_PATH = REPORT_DIR / "week22_closeout.md"


REQUIRED_BASELINES = ["transe", "distmult", "complex", "rotate", "rgcn", "hrgat"]


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def exists(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def check_file(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
    }


def load_core_artifacts() -> dict[str, Any]:
    artifacts = {
        "protocol": read_json(RESULT_DIR / "dataset2_protocol_freeze.json", default={}),
        "raw_inventory": read_json(RESULT_DIR / "dataset2_raw_inventory.json", default={}),
        "task_spec": read_json(RESULT_DIR / "dataset2_task_spec.json", default={}),
        "split_summary": read_json(RESULT_DIR / "dataset2_split_summary.json", default={}),
        "leak_check": read_json(RESULT_DIR / "dataset2_leak_check.json", default={}),
        "baseline_table": read_json(RESULT_DIR / "dataset2_baseline_main_table.json", default={}),
        "source_selection": read_json(RESULT_DIR / "dataset2_source_selection.json", default={}),
        "prep_manifest": read_json(FOGRAG_READY_DIR / "prep_manifest.json", default={}),
    }
    return artifacts


def summarize_baselines(baseline_table: dict[str, Any]) -> dict[str, Any]:
    valid = baseline_table.get("valid", [])
    test = baseline_table.get("test", [])

    valid_models = {row.get("model_name") for row in valid}
    test_models = {row.get("model_name") for row in test}

    missing_valid = [m for m in REQUIRED_BASELINES if m not in valid_models]
    missing_test = [m for m in REQUIRED_BASELINES if m not in test_models]

    best_valid = valid[0] if valid else None
    best_test = test[0] if test else None

    rgcn_valid = next((r for r in valid if r.get("model_name") == "rgcn"), None)
    rgcn_test = next((r for r in test if r.get("model_name") == "rgcn"), None)
    hrgat_valid = next((r for r in valid if r.get("model_name") == "hrgat"), None)
    hrgat_test = next((r for r in test if r.get("model_name") == "hrgat"), None)

    return {
        "required_models": REQUIRED_BASELINES,
        "valid_models": sorted(list(valid_models)),
        "test_models": sorted(list(test_models)),
        "missing_valid": missing_valid,
        "missing_test": missing_test,
        "best_valid": best_valid,
        "best_test": best_test,
        "rgcn_valid": rgcn_valid,
        "rgcn_test": rgcn_test,
        "hrgat_valid": hrgat_valid,
        "hrgat_test": hrgat_test,
        "all_six_ready": not missing_valid and not missing_test,
    }


def validate_ready_package(prep_manifest: dict[str, Any]) -> dict[str, Any]:
    required_ready_files = [
        FOGRAG_READY_DIR / "train.json",
        FOGRAG_READY_DIR / "valid.json",
        FOGRAG_READY_DIR / "test.json",
        FOGRAG_READY_DIR / "prompt_lexicon.json",
        FOGRAG_READY_DIR / "rules.json",
        FOGRAG_READY_DIR / "support_schema.json",
        FOGRAG_READY_DIR / "prep_manifest.json",
        FOGRAG_READY_DIR / "entity2id.pkl",
        FOGRAG_READY_DIR / "id2entity.pkl",
        FOGRAG_READY_DIR / "relation2id.pkl",
        FOGRAG_READY_DIR / "id2relation.pkl",
    ]

    file_checks = [check_file(p) for p in required_ready_files]
    missing = [c["path"] for c in file_checks if not c["exists"]]

    train_rows = read_json(FOGRAG_READY_DIR / "train.json", default=[])
    valid_rows = read_json(FOGRAG_READY_DIR / "valid.json", default=[])
    test_rows = read_json(FOGRAG_READY_DIR / "test.json", default=[])

    def row_ok(row: dict[str, Any]) -> bool:
        required = {
            "triple",
            "triple_id",
            "type",
            "query_entity",
            "query_entity_id",
            "rank_entities",
            "rank_entities_id",
            "rank",
            "input",
            "output",
            "subgraph",
        }
        if not required.issubset(row.keys()):
            return False
        if row.get("type") != "predicted_head":
            return False
        if "[QUERY]" not in row.get("input", ""):
            return False
        if "[ENTITY]" not in row.get("input", ""):
            return False
        return True

    sample_schema_ok = (
        bool(train_rows) and row_ok(train_rows[0])
        and bool(valid_rows) and row_ok(valid_rows[0])
        and bool(test_rows) and row_ok(test_rows[0])
    )

    return {
        "file_checks": file_checks,
        "missing_files": missing,
        "num_train_rows": len(train_rows),
        "num_valid_rows": len(valid_rows),
        "num_test_rows": len(test_rows),
        "sample_schema_ok": sample_schema_ok,
        "manifest_decision": prep_manifest.get("decision"),
        "leak_sanity": prep_manifest.get("leak_sanity", {}),
        "ready_summary": prep_manifest.get("ready_summary", {}),
        "package_ready": (
            not missing
            and sample_schema_ok
            and prep_manifest.get("decision") == "FOGRAG_READY_PACKAGE_BUILT"
            and prep_manifest.get("leak_sanity", {}).get("decision") == "PASS"
        ),
    }


def decide_week22(
    artifacts: dict[str, Any],
    baseline_summary: dict[str, Any],
    ready_validation: dict[str, Any],
) -> tuple[str, list[str]]:
    notes = []

    task_decision = artifacts["task_spec"].get("decision")
    split_decision = artifacts["split_summary"].get("decision")
    leak_decision = artifacts["leak_check"].get("decision")
    prep_decision = artifacts["prep_manifest"].get("decision")

    if task_decision != "GO_TASK_SELECTED_PROXY_SCHEMA":
        notes.append(f"Task decision not GO_TASK_SELECTED_PROXY_SCHEMA: {task_decision}")

    if split_decision != "SPLIT_GRAPH_READY":
        notes.append(f"Split decision not SPLIT_GRAPH_READY: {split_decision}")

    if leak_decision != "PASS":
        notes.append(f"Leak decision not PASS: {leak_decision}")

    if not baseline_summary["all_six_ready"]:
        notes.append(
            "Missing baseline outputs: "
            f"valid={baseline_summary['missing_valid']}, test={baseline_summary['missing_test']}"
        )

    if not ready_validation["package_ready"]:
        notes.append(f"FOG-RAG ready package incomplete or failed: {prep_decision}")

    if not notes:
        return "GO_WEEK23_FOGRAG_TRANSFER", [
            "Dataset 2 protocol is frozen.",
            "PharmKG task/schema selected with relation T as therapeutic_association_proxy.",
            "Coverage-safe split and train_enriched graph are ready.",
            "Leak checks passed.",
            "All six baselines are available.",
            "FOG-RAG-ready package is built with R-GCN as main source.",
        ]

    if task_decision != "GO_TASK_SELECTED_PROXY_SCHEMA":
        return "PARTIAL_READY_SCHEMA_NEEDS_FIX", notes

    if split_decision != "SPLIT_GRAPH_READY" or leak_decision != "PASS":
        return "PARTIAL_READY_SPLIT_OR_LEAK_NEEDS_FIX", notes

    if not baseline_summary["all_six_ready"]:
        return "PARTIAL_READY_BASELINE_NEEDS_FIX", notes

    if not ready_validation["package_ready"]:
        return "PARTIAL_READY_FOGRAG_PACKAGE_NEEDS_FIX", notes

    return "PARTIAL_READY_UNKNOWN_FIX_NEEDED", notes


def build_closeout() -> tuple[dict[str, Any], dict[str, Any]]:
    artifacts = load_core_artifacts()
    baseline_summary = summarize_baselines(artifacts["baseline_table"])
    ready_validation = validate_ready_package(artifacts["prep_manifest"])

    final_decision, decision_notes = decide_week22(
        artifacts=artifacts,
        baseline_summary=baseline_summary,
        ready_validation=ready_validation,
    )

    task_spec = artifacts["task_spec"]
    split_summary = artifacts["split_summary"]
    leak_check = artifacts["leak_check"]
    prep_manifest = artifacts["prep_manifest"]

    closeout = {
        "week": 22,
        "theme": "Dataset 2 feasibility and FOG-RAG transfer setup",
        "final_decision": final_decision,
        "decision_notes": decision_notes,

        "dataset2": {
            "name": "PharmKG-8k",
            "setting": "setting_c_pharmkg",
            "target_relation_raw": task_spec.get("task", {}).get("target_relation_raw"),
            "target_relation_normalized": task_spec.get("task", {}).get("target_relation_normalized"),
            "paper_label": task_spec.get("task", {}).get("target_relation_paper_label"),
            "direction": task_spec.get("task", {}).get("direction"),
            "task_template": task_spec.get("task", {}).get("task_template"),
            "prediction_type": task_spec.get("task", {}).get("prediction_type"),
            "candidate_universe": task_spec.get("task", {}).get("candidate_universe"),
            "paper_warning": "Do not call relation T clinical indication; use therapeutic association proxy.",
        },

        "split_and_graph": {
            "decision": split_summary.get("decision"),
            "final_split_sizes": split_summary.get("final_split_sizes"),
            "entity_relation_counts": split_summary.get("entity_relation_counts"),
            "leak_decision": leak_check.get("decision"),
            "exact_leak_checks": leak_check.get("exact_leak_checks"),
            "coverage_checks": leak_check.get("coverage_checks"),
        },

        "baseline_summary": baseline_summary,

        "source_selection": {
            "main_fograg_source": prep_manifest.get("source_selection", {}).get("main_fograg_source"),
            "drkgc_aligned_alternative": prep_manifest.get("source_selection", {}).get("drkgc_aligned_alternative"),
            "best_valid_structure_source": baseline_summary.get("best_valid"),
            "best_test_structure_source": baseline_summary.get("best_test"),
        },

        "fograg_ready_package": ready_validation,

        "method_alignment_answers": {
            "primekg_train_gold_in_candidates": (
                "Yes. DrKGC-style supervised training requires the gold answer to be present "
                "in the candidate/options list. The reviewer-sensitive issue is valid/test "
                "gold injection, not train supervision."
            ),
            "pharmkg_train_gold_in_candidates": (
                "Yes. Day 6 train_top20_supervised is gold-first for supervised training only. "
                "Valid/test remain raw no-injection."
            ),
            "rules": (
                "PrimeKG used manually fixed/hard-coded biomedical rules because relation semantics "
                "were explicit. PharmKG uses a fixed no-rule fallback policy because relation labels "
                "are compact codes without explicit semantics. Both avoid rule mining."
            ),
            "question_lexicon": (
                "Yes. PharmKG has prompt_lexicon.json with the template: "
                "What drug is therapeutically associated with {}?"
            ),
        },

        "known_limitations": [
            "PharmKG relation T is treated as a therapeutic association proxy, not a confirmed clinical indication relation.",
            "Entity type map is task-specific: T heads are Drug/Chemical candidates and T tails are Disease queries.",
            "Current valid/test R-GCN Gold@20 is low, so Week 23 should treat raw candidate bottleneck as central.",
            "Day 6 subgraphs are fixed at graph_size=100; fuzzy retrieval in Week 23 should test whether smaller weighted evidence can preserve performance.",
            "HRGAT is retained as a DrKGC-aligned alternative, but R-GCN is selected as main source for pipeline continuity and stronger test MRR@20.",
        ],

        "week23_recommendation": {
            "recommended_status": "Start FOG-RAG transfer",
            "main_rows_to_build": [
                "backbone_raw",
                "ontology_raw_negative_control",
                "soft_support_raw",
                "fuzzy_retrieval_main",
            ],
            "optional_rows": [
                "hrgat_source_alternative",
                "fuzzy_encoder_probe_appendix_only",
            ],
        },
    }

    go_decision = {
        "week": 22,
        "decision": final_decision,
        "go_week23_fograg_transfer": final_decision == "GO_WEEK23_FOGRAG_TRANSFER",
        "notes": decision_notes,
        "required_next_week": closeout["week23_recommendation"],
    }

    return closeout, go_decision


def fmt_metric(row: dict[str, Any] | None, key: str) -> str:
    if not row:
        return "NA"
    value = row.get(key)
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def render_baseline_table(rows: list[dict[str, Any]]) -> str:
    lines = []
    lines.append("| Model | Gold@20 | MRR@20 | H@1 | H@3 | H@10 | H@20 | Rank21 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for row in rows:
        lines.append(
            f"| {row['model_name']} | "
            f"{row['gold_present_at20']:.3f} | "
            f"{row['mrr_at20']:.6f} | "
            f"{row['hits1_at20']:.3f} | "
            f"{row['hits3_at20']:.3f} | "
            f"{row['hits10_at20']:.3f} | "
            f"{row['hits20_at20']:.3f} | "
            f"{row['gold_rank_21_count']} |"
        )
    return "\n".join(lines)


def write_reports(closeout: dict[str, Any], go_decision: dict[str, Any]) -> None:
    baseline = closeout["baseline_summary"]
    split_graph = closeout["split_and_graph"]
    ready = closeout["fograg_ready_package"]
    dataset2 = closeout["dataset2"]

    valid_table = render_baseline_table(
        sorted(
            [
                row for row in read_json(RESULT_DIR / "dataset2_baseline_main_table.json").get("valid", [])
            ],
            key=lambda x: x["mrr_at20"],
            reverse=True,
        )
    )
    test_table = render_baseline_table(
        sorted(
            [
                row for row in read_json(RESULT_DIR / "dataset2_baseline_main_table.json").get("test", [])
            ],
            key=lambda x: x["mrr_at20"],
            reverse=True,
        )
    )

    ready_summary = ready.get("ready_summary", {})

    md = f"""# Week 22 Closeout — PharmKG Dataset 2 Feasibility and FOG-RAG Transfer Setup

## Final decision

`{closeout["final_decision"]}`

## Decision notes

{chr(10).join(f"- {note}" for note in closeout["decision_notes"])}

## Dataset 2 selected task

- Dataset: `{dataset2["name"]}`
- Setting: `{dataset2["setting"]}`
- Task: `{dataset2["task_template"]}`
- Prediction type: `{dataset2["prediction_type"]}`
- Direction: `{dataset2["direction"]}`
- Raw relation code: `{dataset2["target_relation_raw"]}`
- Normalized relation name: `{dataset2["target_relation_normalized"]}`
- Candidate universe: `{dataset2["candidate_universe"]}`

Important paper wording:

`relation T = therapeutic association proxy`

Do **not** call relation T clinical indication.

## Split and graph

- Split decision: `{split_graph["decision"]}`
- Leak decision: `{split_graph["leak_decision"]}`

Final split sizes:

- train: `{split_graph["final_split_sizes"]["train"]}`
- valid: `{split_graph["final_split_sizes"]["valid"]}`
- test: `{split_graph["final_split_sizes"]["test"]}`

Entity/graph stats:

- num entities: `{split_graph["entity_relation_counts"]["num_entities"]}`
- num relations: `{split_graph["entity_relation_counts"]["num_relations"]}`
- candidate drugs: `{split_graph["entity_relation_counts"]["num_candidate_drugs"]}`
- query diseases: `{split_graph["entity_relation_counts"]["num_query_diseases"]}`
- train enriched triples: `{split_graph["entity_relation_counts"]["train_enriched_triples"]}`

Exact leak checks:

- valid positive in train: `{split_graph["exact_leak_checks"]["valid_positive_in_train_count"]}`
- test positive in train: `{split_graph["exact_leak_checks"]["test_positive_in_train_count"]}`
- valid/test overlap: `{split_graph["exact_leak_checks"]["valid_test_positive_overlap_count"]}`
- selected valid/test target in train_enriched: `{split_graph["exact_leak_checks"]["selected_valid_or_test_target_in_train_enriched_count"]}`

## Baseline table — validation

{valid_table}

## Baseline table — test

{test_table}

## Source selection

- Main FOG-RAG source: `{closeout["source_selection"]["main_fograg_source"]}`
- DrKGC-aligned alternative: `{closeout["source_selection"]["drkgc_aligned_alternative"]}`
- Best valid baseline: `{baseline["best_valid"]["model_name"]}` with MRR@20 `{baseline["best_valid"]["mrr_at20"]:.6f}`
- Best test baseline: `{baseline["best_test"]["model_name"]}` with MRR@20 `{baseline["best_test"]["mrr_at20"]:.6f}`

R-GCN is selected as the main FOG-RAG source because it is aligned with the PrimeKG FOG-RAG pipeline and has the strongest test MRR@20 among GNN-style sources.

## FOG-RAG-ready package

- Package ready: `{ready["package_ready"]}`
- Manifest decision: `{ready["manifest_decision"]}`
- Leak sanity: `{ready["leak_sanity"].get("decision")}`

Ready split summary:

| Split | Rows | Avg candidates | Gold in list | Rank21 | Avg subgraph |
|---|---:|---:|---:|---:|---:|
| train | {ready_summary["train"]["num_rows"]} | {ready_summary["train"]["avg_candidate_size"]:.2f} | {ready_summary["train"]["gold_in_final_list_rate"]:.3f} | {ready_summary["train"]["rank21_count"]} | {ready_summary["train"]["avg_subgraph_size"]:.2f} |
| valid | {ready_summary["valid"]["num_rows"]} | {ready_summary["valid"]["avg_candidate_size"]:.2f} | {ready_summary["valid"]["gold_in_final_list_rate"]:.3f} | {ready_summary["valid"]["rank21_count"]} | {ready_summary["valid"]["avg_subgraph_size"]:.2f} |
| test | {ready_summary["test"]["num_rows"]} | {ready_summary["test"]["avg_candidate_size"]:.2f} | {ready_summary["test"]["gold_in_final_list_rate"]:.3f} | {ready_summary["test"]["rank21_count"]} | {ready_summary["test"]["avg_subgraph_size"]:.2f} |

## Answers to alignment questions

### 1. Did PrimeKG use gold in train candidates?

Yes. DrKGC-style supervised training requires the gold answer to be present in the answer options. The reviewer-sensitive issue is valid/test gold injection, not train supervision.

For PharmKG, `train_top20_supervised.json` is gold-first for train only. Valid/test are raw no-injection.

### 2. Did PharmKG use hard-coded rules?

PharmKG uses a fixed/manual retrieval policy, but does not claim semantic hard-coded rule sequences because PharmKG-8k only exposes compact relation codes. This is reviewer-safe.

PrimeKG used manual biomedical rules because relation semantics were explicit. PharmKG uses a fixed no-rule fallback: shortest paths plus incident-edge fill. Both avoid rule mining.

### 3. Did PharmKG use a question lexicon?

Yes. PharmKG has `prompt_lexicon.json`.

Prompt:

`What drug is therapeutically associated with {{}}?`

## Known limitations

{chr(10).join(f"- {item}" for item in closeout["known_limitations"])}

## Week 23 recommendation

Start FOG-RAG transfer with:

1. `backbone_raw`
2. `ontology_raw_negative_control`
3. `soft_support_raw`
4. `fuzzy_retrieval_main`

Optional:

- `hrgat_source_alternative`
- `fuzzy_encoder_probe_appendix_only`

## Files written

- `results/week22/week22_closeout.json`
- `results/week22/week22_go_decision.json`
- `reports/week22/day7_week22_closeout.md`
- `reports/week22/week22_closeout.md`
"""

    DAY7_REPORT_PATH.write_text(md, encoding="utf-8")
    WEEK_REPORT_PATH.write_text(md, encoding="utf-8")


def main() -> None:
    closeout, go_decision = build_closeout()

    write_json(closeout, CLOSEOUT_JSON_PATH)
    write_json(go_decision, GO_DECISION_PATH)
    write_reports(closeout, go_decision)

    print("Saved:")
    print(f"  {CLOSEOUT_JSON_PATH}")
    print(f"  {GO_DECISION_PATH}")
    print(f"  {DAY7_REPORT_PATH}")
    print(f"  {WEEK_REPORT_PATH}")

    print("\nFinal decision:", closeout["final_decision"])
    print("GO Week 23:", go_decision["go_week23_fograg_transfer"])

    print("\nDecision notes:")
    for note in closeout["decision_notes"]:
        print(" -", note)

    if closeout["final_decision"] != "GO_WEEK23_FOGRAG_TRANSFER":
        raise RuntimeError(
            f"Week 22 closeout is not GO: {closeout['final_decision']}"
        )


if __name__ == "__main__":
    main()