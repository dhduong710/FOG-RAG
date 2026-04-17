#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main():
    print("=" * 80)
    print("Week 5 Day 1 - Freeze Inputs and Decision")
    print("ROOT =", ROOT)
    print("=" * 80)

    required_files = {
        "split_meta": ROOT / "dataset/setting_a/01_split/split_meta.json",
        "graph_stats": ROOT / "dataset/setting_a/02_graph/graph_stats_deg1000_final.json",
        "candidate_meta": ROOT / "dataset/setting_a/03_candidates/candidate_meta.json",
        "entity2id_pkl": ROOT / "dataset/setting_a/04_drkgc_json/entity2id.pkl",
        "id2entity_pkl": ROOT / "dataset/setting_a/04_drkgc_json/id2entity.pkl",
        "relation2id_pkl": ROOT / "dataset/setting_a/04_drkgc_json/relation2id.pkl",
        "id2relation_pkl": ROOT / "dataset/setting_a/04_drkgc_json/id2relation.pkl",
        "pilot_train_json": ROOT / "dataset/setting_a/07_pilot_ready/train.json",
        "pilot_valid_json": ROOT / "dataset/setting_a/07_pilot_ready/valid.json",
        "pilot_test_json": ROOT / "dataset/setting_a/07_pilot_ready/test.json",
        "pilot_ready_meta": ROOT / "dataset/setting_a/07_pilot_ready/pilot_ready_meta.json",
        "resource_plan_json": ROOT / "reports/week4/day6_resource_plan.json",
        "month1_closeout": ROOT / "reports/week4/day7_month_1_closeout.md",
        "local_debug_cfg": ROOT / "configs/week5/setting_a_local_debug.yaml",
        "server_cfg": ROOT / "configs/week5/setting_a_server_3b.yaml",
        "rgcn_cfg": ROOT / "configs/week5/rgcn_setting_a.yaml",
    }

    # create week5 directories first
    dirs_to_create = [
        ROOT / "configs/week5",
        ROOT / "scripts/week5",
        ROOT / "reports/week5",
        ROOT / "results/week5",
        ROOT / "results/week5/backbone_llama32_3b_rgcn",
        ROOT / "results/week5/rgcn_setting_a",
        ROOT / "runs/week5",
        ROOT / "dataset/setting_a/08_backbone_ready",
    ]
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)

    missing = []
    for name, path in required_files.items():
        if not path.exists():
            missing.append((name, path))

    if missing:
        print("\n[ERROR] Missing required files:")
        for name, path in missing:
            print(f"  - {name}: {rel(path)}")
        raise SystemExit(
            "\nStop here. Fix missing month-1 artifacts / week-5 configs before continuing."
        )

    split_meta = load_json(required_files["split_meta"])
    graph_stats = load_json(required_files["graph_stats"])
    candidate_meta = load_json(required_files["candidate_meta"])
    pilot_meta = load_json(required_files["pilot_ready_meta"])
    resource_plan = load_json(required_files["resource_plan_json"])

    checks = {
        "split_train_ok": split_meta.get("split_sizes", {}).get("train") == 8388,
        "split_valid_ok": split_meta.get("split_sizes", {}).get("valid") == 500,
        "split_test_ok": split_meta.get("split_sizes", {}).get("test") == 500,
        "split_seed_ok": split_meta.get("seed") == 2025,
        "candidate_k_ok": candidate_meta.get("k") == 20,
        "candidate_type_drug_ok": candidate_meta.get("candidate_type") == "drug",
        "candidate_gold_included_ok": candidate_meta.get("gold_included") is True,
        "pilot_valid_leak_zero_ok": pilot_meta.get("valid_exact_leak_count") == 0,
        "pilot_test_leak_zero_ok": pilot_meta.get("test_exact_leak_count") == 0,
        "graph_total_triples_ok": graph_stats.get("num_total_enriched_triples") == 136351,
        "graph_num_entities_ok": graph_stats.get("num_entities") == 10453,
        "graph_num_rel_types_ok": graph_stats.get("num_relation_types") == 4,
    }

    relation_types = graph_stats.get("relation_types", [])
    expected_relations = {"associated_with", "indication", "ppi", "target"}
    checks["graph_relations_ok"] = set(relation_types) == expected_relations

    all_checks_ok = all(checks.values())

    decision_lines = [
        "1. Week-5 goal is full Setting-A backbone reproduction, not metric chasing.",
        "2. Local machine is debug/pilot only.",
        "3. Server is the only place for full backbone runs.",
        "4. Primary week-5 LLM = Llama-3.2-3B.",
        "5. Primary structural embedding source = R-GCN export for Setting A.",
        "6. No fuzzy / safety module is enabled in the main training path this week.",
        "7. No second LLM branch unless the first full run is stable.",
    ]

    decision_md = f"""# Day 1 Week 5 Decision

## 1. Week-5 role
Week 5 is the first full **Setting-A backbone reproduction** week.
This is **not** a metric-chasing week.

## 2. Locked decisions
""" + "\n".join([f"- {x}" for x in decision_lines]) + f"""

## 3. Why these decisions are frozen today
- Month 1 already confirmed that the pilot pipeline works.
- Week 5 must now move from pilot artifacts to the first real full-Setting-A backbone path.
- Local and server must not be mixed.
- No fuzzy or safety extension should be enabled before the backbone path is stable.

## 4. Frozen compute split
### Local
- debug only
- dry run only
- small subset infer only
- bug reproduction only
- primary model: TinyLlama-1.1B

### Server
- full backbone train
- full valid infer
- real checkpointing
- primary model: Llama-3.2-3B

## 5. Month-1 prerequisite summary
- split sizes: {split_meta.get("split_sizes")}
- split seed: {split_meta.get("seed")}
- candidate K: {candidate_meta.get("k")}
- candidate type: {candidate_meta.get("candidate_type")}
- pilot leak (valid/test): {pilot_meta.get("valid_exact_leak_count")} / {pilot_meta.get("test_exact_leak_count")}
- enriched graph triples: {graph_stats.get("num_total_enriched_triples")}
- enriched graph entities: {graph_stats.get("num_entities")}
- enriched graph relations: {relation_types}

## 6. Input-freeze checks
""" + "\n".join([f"- [{ 'x' if v else ' ' }] {k}" for k, v in checks.items()]) + f"""

## 7. Current judgment
**{'READY' if all_checks_ok else 'NOT READY'}** to enter week-5 day-2 backbone-ready packaging.

## 8. Next action for day 2
Create `dataset/setting_a/08_backbone_ready/` cleanly from the frozen month-1 artifacts,
without mixing pilot-ready and full-ready paths.
"""

    write_text(ROOT / "reports/week5/day1_week5_decision.md", decision_md)

    manifest = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "week": 5,
        "day": 1,
        "goal": "Freeze week-5 backbone path and separate local/server roles.",
        "month1_prerequisites": {
            "split_meta": split_meta,
            "graph_stats_deg1000_final": graph_stats,
            "candidate_meta": candidate_meta,
            "pilot_ready_meta": pilot_meta,
            "week4_resource_plan": resource_plan,
        },
        "checks": checks,
        "all_checks_ok": all_checks_ok,
        "frozen_decisions": {
            "local_role": "debug/pilot only",
            "server_role": "full backbone only",
            "primary_llm_week5": "meta-llama/Llama-3.2-3B",
            "primary_local_model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            "primary_embedding_source": "R-GCN export for Setting A",
            "candidate_k": 20,
            "subgraph_tau": 100,
            "lora": {"r": 32, "alpha": 32, "dropout": 0.1},
            "learning_rate": 2e-4,
            "enable_fuzzy": False,
            "enable_safety_in_main_path": False,
            "second_llm_branch_allowed": False,
        },
        "required_files": {k: rel(v) for k, v in required_files.items()},
        "next_action": "Prepare dataset/setting_a/08_backbone_ready on day 2.",
    }

    write_json(ROOT / "results/week5/week5_input_freeze_manifest.json", manifest)

    print("\nSaved:")
    print("  - reports/week5/day1_week5_decision.md")
    print("  - results/week5/week5_input_freeze_manifest.json")
    print("\nChecks:")
    for k, v in checks.items():
        print(f"  - {k}: {v}")

    if all_checks_ok:
        print("\n[OK] Day-1 freeze checks passed.")
        print("You can move to day 2 after reviewing the decision report.")
    else:
        print("\n[WARN] Some checks failed.")
        print("Do NOT continue to day 2 packaging until the failed checks are resolved.")


if __name__ == "__main__":
    main()