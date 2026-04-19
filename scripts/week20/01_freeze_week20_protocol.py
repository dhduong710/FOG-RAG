from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(".").resolve()

W19_GO = ROOT / "results/week19/week19_go_decision.json"

TEST_EVAL_READY = {
    "backbone_raw": ROOT / "dataset/setting_b/08_n2_eval_test/test_backbone_raw_eval.json",
    "ontology_raw": ROOT / "dataset/setting_b/08_n2_eval_test/test_ontology_raw_eval.json",
    "soft_support_raw": ROOT / "dataset/setting_b/08_n2_eval_test/test_soft_support_raw_eval.json",
    "retrieval_main": ROOT / "dataset/setting_b/08_n2_eval_test/test_retrieval_main_eval.json",
}

TEST_STAGE_ARTIFACTS = {
    "backbone_raw": ROOT / "dataset/setting_a/23_noinj_source/test_top20_raw.json",
    "soft_support_raw": ROOT / "dataset/setting_a/26_n2_soft_support/test_top20_soft_support_main.json",
    "retrieval_main": ROOT / "dataset/setting_a/27_n2_fuzzy_retrieval/test_fuzzy_retrieval_main.json",
}

KGE_CANDIDATES = [
    ROOT / "dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt",
    ROOT / "dataset/setting_a/10_backbone_ready_real/entity_embeddings_rgcn.pt",
    ROOT / "dataset/setting_a/12_backbone_ready_ranker_v2/entity_embeddings_rgcn.pt",
]

MODEL_HINT_FILES = [
    ROOT / "configs/reference_backbone/setting_a_server_3b.yaml",
    ROOT / "configs/reference_backbone/backbone_valid_v2.yaml",
    ROOT / "configs/reference_backbone/rgcn_ranker_ft.yaml",
    ROOT / "configs/week12A/rgcn_ranker_ft.yaml",
]

OUT_JSON = ROOT / "results/week20/e2e_protocol_freeze.json"
OUT_MD = ROOT / "reports/week20/day1_protocol_freeze.md"

def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def summarize_json(path: Path):
    if not path.exists():
        return {"path": str(path), "exists": False}
    try:
        obj = read_json(path)
        out = {"path": str(path), "exists": True, "json_kind": type(obj).__name__}
        if isinstance(obj, list):
            out["num_rows"] = len(obj)
            if obj and isinstance(obj[0], dict):
                out["top_keys"] = list(obj[0].keys())[:20]
        elif isinstance(obj, dict):
            out["top_keys"] = list(obj.keys())[:20]
        return out
    except Exception as e:
        return {"path": str(path), "exists": True, "load_error": repr(e)}

def scan_checkpoints(root: Path):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        fn = set(filenames)
        has_graph = "graph_model.bin" in fn
        has_cfg = "adapter_config.json" in fn
        has_adapter = ("adapter_model.bin" in fn) or ("adapter_model.safetensors" in fn)
        if has_graph and has_cfg and has_adapter:
            p = Path(dirpath)
            found.append({
                "path": str(p),
                "has_graph_model": has_graph,
                "has_adapter_config": has_cfg,
                "has_adapter_weights": has_adapter,
            })
    found.sort(key=lambda x: x["path"])
    return found

def read_model_hints(files):
    hints = []
    keys = ["model_name_or_path", "base_model_name_or_path"]
    for path in files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        for line in lines:
            stripped = line.strip()
            for key in keys:
                if stripped.startswith(f"{key}:"):
                    value = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                    hints.append({
                        "source_file": str(path),
                        "key": key,
                        "value": value,
                    })
    return hints

def choose_primary_checkpoint(candidates):
    if not candidates:
        return None
    # prefer week20/19/18/17/16/15/14/13 naming if present, else shortest path
    score_rows = []
    for c in candidates:
        p = c["path"]
        score = 999
        for idx, token in enumerate(["week20", "week19", "week18", "week17", "week16", "week15", "week14", "week13", "week12A", "week12"]):
            if token in p:
                score = idx
                break
        score_rows.append((score, len(p), c))
    score_rows.sort(key=lambda x: (x[0], x[1]))
    return score_rows[0][2]

def main():
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    week19 = read_json(W19_GO)
    checkpoint_candidates = scan_checkpoints(ROOT / "results")
    primary_checkpoint = choose_primary_checkpoint(checkpoint_candidates)
    model_hints = read_model_hints(MODEL_HINT_FILES)

    kge_existing = [str(p) for p in KGE_CANDIDATES if p.exists()]
    preferred_kge = kge_existing[0] if kge_existing else None

    prerequisites = {
        "week19_go_decision": summarize_json(W19_GO),
        "test_eval_ready": {k: summarize_json(v) for k, v in TEST_EVAL_READY.items()},
        "test_stage_artifacts": {k: summarize_json(v) for k, v in TEST_STAGE_ARTIFACTS.items()},
    }

    all_eval_ready_ok = all(v["exists"] and v.get("num_rows") == 500 for v in prerequisites["test_eval_ready"].values())
    all_stage_artifacts_ok = all(v["exists"] and v.get("num_rows") == 500 for v in prerequisites["test_stage_artifacts"].values())

    protocol = {
        "week": 20,
        "stage": "week20_protocol_freeze",
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "status": "READY_FOR_E2E_CONFIRMATION" if (week19["status"] == "GO_PAPER_ASSEMBLY" and all_eval_ready_ok and all_stage_artifacts_ok) else "BLOCKED",
        "theme": "Frozen end-to-end LLaMA confirmation + paper-ready assets",
        "week_type": "end_to_end_confirmation_week",
        "paper_facing_inputs": {
            "paper_main_row": week19["paper_facing_decision"]["paper_main_row"],
            "reference_row": week19["paper_facing_decision"]["reference_row"],
            "negative_control": week19["paper_facing_decision"]["negative_control"],
            "candidate_stage_intermediate": week19["paper_facing_decision"]["candidate_stage_intermediate"],
            "appendix_only": week19["paper_facing_decision"]["appendix_only"],
            "selected_source_variant": week19["paper_facing_decision"]["selected_source_variant"],
        },
        "frozen_e2e_rows": [
            "backbone_raw",
            "soft_support_raw",
            "soft_support_fuzzy_retrieval_main",
        ],
        "optional_appendix_rows": [
            "ontology_raw",
        ],
        "forbidden_changes": [
            "change paper_main_row",
            "change selected retrieval source variant",
            "promote encoder to main path",
            "open new dataset",
            "open many new models",
            "change reviewer-safe locked-test narrative",
        ],
        "infer_contract": {
            "required_dataset_files": ["train.json", "valid.json", "test.json"],
            "required_sample_fields": ["input", "output", "query_entity_id", "rank_entities_id", "subgraph"],
            "eval_split": "test",
            "main_e2e_rows": [
                "backbone_raw",
                "soft_support_raw",
                "soft_support_fuzzy_retrieval_main",
            ],
        },
        "checkpoint_inventory": {
            "num_candidates": len(checkpoint_candidates),
            "candidates": checkpoint_candidates[:50],
            "primary_candidate": primary_checkpoint,
        },
        "model_name_or_path_hints": model_hints,
        "kge_embedding_candidates_existing": kge_existing,
        "preferred_kge_embedding_path": preferred_kge,
        "prerequisites": prerequisites,
        "deliverables_day1": [
            "results/week20/e2e_protocol_freeze.json",
            "reports/week20/day1_protocol_freeze.md",
        ],
        "deliverables_day2_preview": [
            "dataset/setting_a/29_n2_e2e_infer_ready/test_backbone_raw_infer_ready.json",
            "dataset/setting_a/29_n2_e2e_infer_ready/test_soft_support_raw_infer_ready.json",
            "dataset/setting_a/29_n2_e2e_infer_ready/test_retrieval_main_infer_ready.json",
        ],
    }

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(protocol, f, ensure_ascii=False, indent=2)

    md = []
    md.append("# Day 1 — Week 20 Protocol Freeze")
    md.append("")
    md.append(f"- status: **{protocol['status']}**")
    md.append(f"- theme: **{protocol['theme']}**")
    md.append("")
    md.append("## 1. Frozen paper-facing rows")
    for k, v in protocol["paper_facing_inputs"].items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## 2. End-to-end confirmation rows")
    for x in protocol["frozen_e2e_rows"]:
        md.append(f"- `{x}`")
    md.append("")
    md.append("## 3. Infer contract")
    for k, v in protocol["infer_contract"].items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## 4. Checkpoint inventory")
    md.append(f"- num_candidates: `{protocol['checkpoint_inventory']['num_candidates']}`")
    md.append(f"- primary_candidate: `{protocol['checkpoint_inventory']['primary_candidate']}`")
    md.append("")
    md.append("## 5. Model hints")
    if model_hints:
        for h in model_hints:
            md.append(f"- `{h['source_file']}` | `{h['key']}` = `{h['value']}`")
    else:
        md.append("- No model hint found in scanned config files.")
    md.append("")
    md.append("## 6. Preferred KGE path")
    md.append(f"- `{preferred_kge}`")
    md.append("")
    md.append("## 7. Day-1 conclusion")
    if protocol["status"] == "READY_FOR_E2E_CONFIRMATION":
        md.append(
            "Week 20 is ready for frozen end-to-end confirmation. "
            "Day 2 should build infer-ready packages for backbone_raw, soft_support_raw, and soft_support_fuzzy_retrieval_main."
        )
    else:
        md.append(
            "Week 20 is blocked. Fix missing prerequisites before building infer-ready packages."
        )

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(protocol, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
