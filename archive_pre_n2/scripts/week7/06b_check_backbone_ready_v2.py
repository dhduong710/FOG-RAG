#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from pathlib import Path
import sys


REQUIRED = [
    Path("dataset/setting_a/12_backbone_ready_ranker_v2/train.json"),
    Path("dataset/setting_a/12_backbone_ready_ranker_v2/valid.json"),
    Path("dataset/setting_a/12_backbone_ready_ranker_v2/test.json"),
    Path("dataset/setting_a/12_backbone_ready_ranker_v2/entity2id.pkl"),
    Path("dataset/setting_a/12_backbone_ready_ranker_v2/id2entity.pkl"),
    Path("dataset/setting_a/12_backbone_ready_ranker_v2/relation2id.pkl"),
    Path("dataset/setting_a/12_backbone_ready_ranker_v2/id2relation.pkl"),
    Path("dataset/setting_a/12_backbone_ready_ranker_v2/manifest.json"),
    Path("reports/week7/day5_backbone_ready_v2.md"),
    Path("reports/week7/day5_prepare_backbone_ready_v2.log"),
]


REQUIRED_KEYS = [
    "triple",
    "triple_id",
    "type",
    "query_entity",
    "query_entity_id",
    "rank_entities",
    "rank_entities_id",
    "rank",
    "gold_entity",
    "gold_entity_id",
    "gold_in_topk_raw",
    "gold_in_topk_ready",
    "gold_injected",
    "gold_rank_in_full_universe",
    "input",
    "output",
    "subgraph",
]


def count_exact_leaks(data):
    leak = 0
    for item in data:
        gold = tuple(item["triple_id"])
        if any(tuple(x) == gold for x in item.get("subgraph", [])):
            leak += 1
    return leak


def check_split(path: Path, name: str):
    data = json.load(open(path, "r", encoding="utf-8"))
    if not data:
        raise ValueError(f"{name} split is empty: {path}")

    first = data[0]
    missing_keys = [k for k in REQUIRED_KEYS if k not in first]
    if missing_keys:
        raise ValueError(f"{name} first sample is missing keys: {missing_keys}")

    candidate_len_bad = 0
    rank_mismatch = 0
    subgraph_sizes = []

    for ex in data:
        if len(ex["rank_entities"]) != 20 or len(ex["rank_entities_id"]) != 20:
            candidate_len_bad += 1

        try:
            computed_rank = ex["rank_entities_id"].index(ex["gold_entity_id"]) + 1
        except ValueError:
            computed_rank = None

        if computed_rank != ex["rank"]:
            rank_mismatch += 1

        subgraph_sizes.append(len(ex.get("subgraph", [])))

    leak_count = count_exact_leaks(data)

    return {
        "split": name,
        "num_examples": len(data),
        "candidate_len_bad": candidate_len_bad,
        "rank_mismatch": rank_mismatch,
        "subgraph_size_min": min(subgraph_sizes),
        "subgraph_size_max": max(subgraph_sizes),
        "subgraph_size_mean": sum(subgraph_sizes) / len(subgraph_sizes),
        "exact_leak_count": leak_count,
        "first_sample": first,
    }


def main():
    missing = [str(p) for p in REQUIRED if not p.exists()]
    if missing:
        print("[FAIL] Missing files:")
        for x in missing:
            print(" -", x)
        sys.exit(1)

    train_stats = check_split(Path("dataset/setting_a/12_backbone_ready_ranker_v2/train.json"), "train")
    valid_stats = check_split(Path("dataset/setting_a/12_backbone_ready_ranker_v2/valid.json"), "valid")
    test_stats = check_split(Path("dataset/setting_a/12_backbone_ready_ranker_v2/test.json"), "test")

    print("[OK] All required Day 5 files exist.")
    print(json.dumps({
        "train": train_stats,
        "valid": valid_stats,
        "test": test_stats,
    }, ensure_ascii=False, indent=2))

    if valid_stats["exact_leak_count"] != 0 or test_stats["exact_leak_count"] != 0:
        print("[WARN] exact leakage detected in valid/test.")
    else:
        print("[OK] valid/test exact leak count = 0.")

    print("\nSuggested manual review:")
    print("cat dataset/setting_a/12_backbone_ready_ranker_v2/manifest.json")
    print("cat reports/week7/day5_backbone_ready_v2.md")
    print("tail -50 reports/week7/day5_prepare_backbone_ready_v2.log")


if __name__ == "__main__":
    main()