from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List


@dataclass
class RequiredPath:
    name: str
    path: str
    required: bool = True
    note: str = ""


def build_required_paths(repo_root: Path) -> List[RequiredPath]:
    return [
        RequiredPath(
            name="train_graph",
            path="dataset/setting_a/02_graph/train_enriched.tsv",
            note="Training graph thật dùng để train/export coarse ranker.",
        ),
        RequiredPath(
            name="split_train",
            path="dataset/setting_a/01_split/train.tsv",
            note="Split train của Setting A.",
        ),
        RequiredPath(
            name="split_valid",
            path="dataset/setting_a/01_split/valid.tsv",
            note="Split valid của Setting A.",
        ),
        RequiredPath(
            name="split_test",
            path="dataset/setting_a/01_split/test.tsv",
            note="Split test của Setting A (không dùng để tuning tuần 6).",
        ),
        RequiredPath(
            name="entity2id",
            path="dataset/setting_a/04_drkgc_json/entity2id.pkl",
            note="ID map đã khóa từ tuần 2/5.",
        ),
        RequiredPath(
            name="id2entity",
            path="dataset/setting_a/04_drkgc_json/id2entity.pkl",
            note="ID map ngược.",
        ),
        RequiredPath(
            name="relation2id",
            path="dataset/setting_a/04_drkgc_json/relation2id.pkl",
            note="Relation map.",
        ),
        RequiredPath(
            name="id2relation",
            path="dataset/setting_a/04_drkgc_json/id2relation.pkl",
            note="Relation map ngược.",
        ),
        RequiredPath(
            name="week5_backbone_train_json",
            path="dataset/setting_a/08_backbone_ready/train.json",
            note="Backbone-ready package tuần 5 để đối chiếu.",
        ),
        RequiredPath(
            name="week5_backbone_valid_json",
            path="dataset/setting_a/08_backbone_ready/valid.json",
            note="Backbone-ready package tuần 5 để đối chiếu.",
        ),
        RequiredPath(
            name="week5_backbone_test_json",
            path="dataset/setting_a/08_backbone_ready/test.json",
            note="Backbone-ready package tuần 5 để đối chiếu.",
        ),
        RequiredPath(
            name="week5_rgcn_embedding",
            path="dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt",
            note="Embedding thật tuần 5, tuần 6 vẫn reuse.",
        ),
        RequiredPath(
            name="week5_manifest",
            path="dataset/setting_a/08_backbone_ready/backbone_ready_manifest.json",
            required=False,
            note="Nếu có thì đọc để tham khảo metadata.",
        ),
    ]


def path_status(repo_root: Path, items: List[RequiredPath]) -> List[Dict]:
    rows = []
    for item in items:
        full = repo_root / item.path
        rows.append(
            {
                "name": item.name,
                "path": item.path,
                "exists": full.exists(),
                "required": item.required,
                "note": item.note,
            }
        )
    return rows


def build_protocol_dict(repo_root: Path, statuses: List[Dict]) -> Dict:
    protocol = {
        "week": 6,
        "title": "Real coarse ranker for Setting A + rebuild backbone-ready JSON + retrain backbone",
        "repo_root": str(repo_root.resolve()),
        "goal": "Replace current mock-like candidate source with a real coarse ranker while keeping the backbone path fixed.",
        "frozen_backbone": {
            "llm": "meta-llama/Llama-3.2-3B",
            "graph_branch": "existing week5 graph branch",
            "entity_embedding": "dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt",
            "candidate_k": 20,
            "subgraph_tau": 100,
            "learning_rate": 2e-4,
            "lora_r": 32,
            "lora_alpha": 32,
            "lora_dropout": 0.1,
        },
        "primary_ranker": {
            "type": "R-GCN-based scorer",
            "query_form": "(?, indication, disease)",
            "candidate_universe": "Drug-only",
        },
        "scientific_protocol": {
            "valid_only_for_scientific_checking": True,
            "test_untouched_until_valid_non_degenerate": True,
            "fuzzy_enabled": False,
            "safety_enabled_in_main_path": False,
        },
        "candidate_artifacts": {
            "top20_raw": {
                "purpose": "Measure candidate retrieval quality directly.",
                "metrics": [
                    "candidate_recall@20",
                    "top1_hit_ratio",
                    "gold_rank_distribution",
                    "candidate_type_purity",
                ],
                "gold_injection_allowed": False,
            },
            "top20_drkgc_ready": {
                "purpose": "Feed into DrKGC-style reranking pipeline.",
                "metrics": [
                    "inject_count",
                    "inject_ratio",
                    "reranking_MRR",
                    "reranking_Hits@1/3/10",
                ],
                "gold_injection_allowed": True,
                "important_note": "Gold injection must be logged explicitly and never hidden.",
            },
        },
        "day1_decisions": [
            "Week-6 goal is to replace the current mock-like candidate source.",
            "Primary coarse ranker = R-GCN-based scorer on Setting A.",
            "Candidate universe is Drug-only.",
            "Candidate size remains K = 20.",
            "Backbone path remains Llama-3.2-3B + existing graph branch.",
            "Fuzzy and safety modules remain disabled in the main path.",
            "Valid is the only split used for scientific checking this week.",
            "Test remains untouched until valid becomes non-degenerate.",
        ],
        "required_inputs": statuses,
        "expected_outputs_day1": [
            "reports/week6/day1_week6_protocol.md",
            "dataset/setting_a/09_real_coarse_ranker/week6_protocol.json",
        ],
        "expected_outputs_week6": [
            "dataset/setting_a/09_real_coarse_ranker/train_scores.pt",
            "dataset/setting_a/09_real_coarse_ranker/valid_scores.pt",
            "dataset/setting_a/09_real_coarse_ranker/test_scores.pt",
            "dataset/setting_a/09_real_coarse_ranker/train_top20_raw.json",
            "dataset/setting_a/09_real_coarse_ranker/valid_top20_raw.json",
            "dataset/setting_a/09_real_coarse_ranker/test_top20_raw.json",
            "dataset/setting_a/09_real_coarse_ranker/train_top20_drkgc_ready.json",
            "dataset/setting_a/09_real_coarse_ranker/valid_top20_drkgc_ready.json",
            "dataset/setting_a/09_real_coarse_ranker/test_top20_drkgc_ready.json",
            "dataset/setting_a/09_real_coarse_ranker/candidate_recall_report.json",
            "dataset/setting_a/10_backbone_ready_real/train.json",
            "dataset/setting_a/10_backbone_ready_real/valid.json",
            "dataset/setting_a/10_backbone_ready_real/test.json",
            "dataset/setting_a/10_backbone_ready_real/backbone_ready_real_manifest.json",
        ],
    }
    return protocol


def make_markdown(protocol: Dict) -> str:
    rows = []
    for item in protocol["required_inputs"]:
        mark = "OK" if item["exists"] else "MISSING"
        rows.append(
            f"| {item['name']} | `{item['path']}` | {mark} | {'yes' if item['required'] else 'no'} | {item['note']} |"
        )

    decisions_md = "\n".join([f"{i+1}. {d}" for i, d in enumerate(protocol["day1_decisions"])])
    outputs_day1_md = "\n".join([f"- `{x}`" for x in protocol["expected_outputs_day1"]])
    outputs_week6_md = "\n".join([f"- `{x}`" for x in protocol["expected_outputs_week6"]])

    md = f"""# Week 6 - Day 1 Protocol Lock

## 1. Day-1 objective
Replace the current mock-like candidate source **at the protocol level first**,
while keeping the backbone path fixed.

## 2. Frozen backbone from week 5
- LLM: `{protocol['frozen_backbone']['llm']}`
- Graph branch: `{protocol['frozen_backbone']['graph_branch']}`
- Entity embeddings: `{protocol['frozen_backbone']['entity_embedding']}`
- K: `{protocol['frozen_backbone']['candidate_k']}`
- tau: `{protocol['frozen_backbone']['subgraph_tau']}`
- LR: `{protocol['frozen_backbone']['learning_rate']}`
- LoRA: `{protocol['frozen_backbone']['lora_r']}/{protocol['frozen_backbone']['lora_alpha']}/{protocol['frozen_backbone']['lora_dropout']}`

## 3. Fixed decisions
{decisions_md}

## 4. Candidate artifact separation
### top20_raw
- direct artifact for candidate retrieval quality
- no gold injection
- used for recall@20, top1 ratio, rank distribution, type purity

### top20_drkgc_ready
- artifact for DrKGC-style reranking
- gold injection allowed when necessary
- inject count / inject ratio must be logged clearly

## 5. Scientific checking policy
- valid only for scientific checking this week
- test untouched until valid becomes non-degenerate
- fuzzy disabled in main path
- safety disabled in main path

## 6. Required input audit
| name | path | exists | required | note |
|---|---|---|---|---|
{chr(10).join(rows)}

## 7. Day-1 outputs
{outputs_day1_md}

## 8. Expected week-6 outputs
{outputs_week6_md}

## 9. End-of-day self-check
- Can I explain the difference between `top20_raw` and `top20_drkgc_ready`?
- Am I keeping the backbone path unchanged from week 5?
- Am I using valid only for scientific checking?
- Is test still untouched?
- Have I stated explicitly whether gold injection is allowed, where, and how it will be logged?

## 10. Warning conditions
- Mixing candidate retrieval evaluation with reranker evaluation
- Rebuilding JSON without preserving a raw top20 artifact
- Touching test before valid becomes non-degenerate
- Changing LLM / graph branch / hyperparameters at the same time as candidate source
"""
    return md


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo_root", type=str, default=".")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    reports_dir = repo_root / "reports" / "week6"
    ranker_dir = repo_root / "dataset" / "setting_a" / "09_real_coarse_ranker"
    real_ready_dir = repo_root / "dataset" / "setting_a" / "10_backbone_ready_real"

    reports_dir.mkdir(parents=True, exist_ok=True)
    ranker_dir.mkdir(parents=True, exist_ok=True)
    real_ready_dir.mkdir(parents=True, exist_ok=True)

    required = build_required_paths(repo_root)
    statuses = path_status(repo_root, required)
    protocol = build_protocol_dict(repo_root, statuses)

    protocol_json_path = ranker_dir / "week6_protocol.json"
    report_md_path = reports_dir / "day1_week6_protocol.md"

    with open(protocol_json_path, "w", encoding="utf-8") as f:
        json.dump(protocol, f, ensure_ascii=False, indent=2)

    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write(make_markdown(protocol))

    missing_required = [x for x in statuses if x["required"] and not x["exists"]]

    print("=" * 80)
    print("WEEK 6 - DAY 1 PROTOCOL LOCK COMPLETE")
    print(f"Saved JSON : {protocol_json_path}")
    print(f"Saved MD   : {report_md_path}")
    print("=" * 80)

    if missing_required:
        print("WARNING: missing required inputs:")
        for item in missing_required:
            print(f"- {item['name']}: {item['path']}")
        print("Day 1 protocol can still be written, but Day 2 train/export may be blocked.")
    else:
        print("All required inputs found. You are ready to enter Day 2.")

    print("=" * 80)
    print("END-OF-DAY CHECK")
    print("1. top20_raw vs top20_drkgc_ready are separated")
    print("2. backbone path frozen")
    print("3. valid only for scientific checking")
    print("4. test untouched")
    print("5. gold injection policy is explicit")
    print("=" * 80)


if __name__ == "__main__":
    main()