#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(".")

SRC_KGE = ROOT / "scripts/week22/05_rerun_dataset2_baselines.py"
SRC_GNN = ROOT / "scripts/week22/05b_rerun_dataset2_gnn_baselines.py"

OUT_KGE = ROOT / "scripts/week26/03a_run_hetionet_kge_baselines.py"
OUT_GNN = ROOT / "scripts/week26/03b_run_hetionet_gnn_baselines.py"


def replace_function(text: str, func_name: str, replacement: str) -> str:
    pattern = re.compile(
        rf"def {func_name}\(.*?\n(?=\ndef |\nclass |\nif __name__|$)",
        re.DOTALL,
    )
    new_text, n = pattern.subn(replacement.rstrip() + "\n", text)
    if n != 1:
        raise RuntimeError(f"Expected to replace exactly one function: {func_name}, replaced={n}")
    return new_text


def common_hetionet_replacements(text: str) -> str:
    replacements = {
        '"setting_c_pharmkg"': '"setting_d_hetionet"',
        '"week22"': '"week26"',
        '"dataset2_baseline_reviewer_safe_valid.json"': '"hetionet_baseline_reviewer_safe_valid.json"',
        '"dataset2_baseline_reviewer_safe_test.json"': '"hetionet_baseline_reviewer_safe_test.json"',
        '"dataset2_baseline_main_table.json"': '"hetionet_baseline_main_table.json"',
        '"day5_baseline_rerun_dataset2.md"': '"day3_hetionet_structure_baselines.md"',
        'TARGET_RELATION = "T"': 'TARGET_RELATION = "CtD"',
        'TARGET_RELATION_NORMALIZED = "therapeutic_association_proxy"': 'TARGET_RELATION_NORMALIZED = "compound_treats_disease"',
        "PharmKG Dataset 2": "Hetionet",
        "PharmKG-8k task-specific therapeutic_association_proxy benchmark": "Hetionet v1.0 compound_treats_disease benchmark",
        "PharmKG-8k task-specific benchmark": "Hetionet v1.0 compound_treats_disease benchmark",
        "Dataset 2": "Hetionet",
        "dataset2": "hetionet",
        "drug_only_from_train_T_heads": "Compound",
        "therapeutic_association_proxy": "compound_treats_disease",
        "(?, T, disease)": "(?, CtD, disease)",
        "Relation normalized: `compound_treats_disease`": "Relation normalized: `compound_treats_disease`",
    }
    for a, b in replacements.items():
        text = text.replace(a, b)
    return text


def patch_kge() -> None:
    if not SRC_KGE.exists():
        raise FileNotFoundError(SRC_KGE)

    text = SRC_KGE.read_text(encoding="utf-8")
    text = common_hetionet_replacements(text)

    text = replace_function(
        text,
        "load_eval_rows",
        '''
def load_eval_rows(split: str) -> list[dict[str, Any]]:
    return read_json(SPLIT_DIR / f"{split}_target_rows.json")
''',
    )

    text = replace_function(
        text,
        "load_candidate_ids",
        '''
def load_candidate_ids(entity2id: dict[str, int]) -> tuple[list[str], torch.LongTensor]:
    obj = read_json(SPLIT_DIR / "candidate_universe_compound.json")
    names = obj["candidate_entities"]
    if "candidate_entity_ids" in obj:
        ids = [int(x) for x in obj["candidate_entity_ids"]]
    else:
        ids = [entity2id[x] for x in names]
    return names, torch.LongTensor(ids)
''',
    )

    # Keep report text cleaner.
    text = text.replace(
        "# Week 22 Day 5 — Hetionet Structure Baselines",
        "# Week 26 Day 3 — Hetionet Structure Baselines",
    )
    text = text.replace(
        "- Dataset: Hetionet task-specific benchmark",
        "- Dataset: Hetionet v1.0",
    )
    text = text.replace(
        "- Relation normalized: `compound_treats_disease`",
        "- Relation normalized: `compound_treats_disease`",
    )

    OUT_KGE.parent.mkdir(parents=True, exist_ok=True)
    OUT_KGE.write_text(text, encoding="utf-8")
    OUT_KGE.chmod(0o755)
    print(f"[write] {OUT_KGE}")


def patch_gnn() -> None:
    if not SRC_GNN.exists():
        raise FileNotFoundError(SRC_GNN)

    text = SRC_GNN.read_text(encoding="utf-8")
    text = common_hetionet_replacements(text)

    text = replace_function(
        text,
        "load_eval_rows",
        '''
def load_eval_rows(split: str) -> list[dict[str, Any]]:
    return read_json(SPLIT_DIR / f"{split}_target_rows.json")
''',
    )

    text = replace_function(
        text,
        "load_candidate_universe",
        '''
def load_candidate_universe(entity2id: dict[str, int]) -> tuple[list[str], torch.LongTensor]:
    obj = read_json(SPLIT_DIR / "candidate_universe_compound.json")
    names = obj["candidate_entities"]
    if "candidate_entity_ids" in obj:
        ids = [int(x) for x in obj["candidate_entity_ids"]]
    else:
        ids = [int(entity2id[name]) for name in names]
    return names, torch.LongTensor(ids)
''',
    )

    text = text.replace(
        "# Week 22 Day 5 \x14 Hetionet Structure Baselines",
        "# Week 26 Day 3 — Hetionet Structure Baselines",
    )
    text = text.replace(
        "# Week 22 Day 5 — Hetionet Structure Baselines",
        "# Week 26 Day 3 — Hetionet Structure Baselines",
    )

    OUT_GNN.parent.mkdir(parents=True, exist_ok=True)
    OUT_GNN.write_text(text, encoding="utf-8")
    OUT_GNN.chmod(0o755)
    print(f"[write] {OUT_GNN}")


def main() -> None:
    patch_kge()
    patch_gnn()
    print("[DONE] generated Hetionet Day 3 baseline scripts")


if __name__ == "__main__":
    main()