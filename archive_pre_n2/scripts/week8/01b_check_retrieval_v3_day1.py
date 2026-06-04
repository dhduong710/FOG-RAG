#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json
import sys


REQUIRED = [
    Path("dataset/setting_a/13_retrieval_v3_prep/collapse_summary.json"),
    Path("dataset/setting_a/13_retrieval_v3_prep/collapse_drug_list.txt"),
    Path("dataset/setting_a/13_retrieval_v3_prep/drug_bias_stats.json"),
    Path("dataset/setting_a/13_retrieval_v3_prep/train_hard_negative_pools.json"),
    Path("dataset/setting_a/13_retrieval_v3_prep/valid_hard_negative_probe.json"),
    Path("reports/week8/day1_retrieval_v3_prep.md"),
]


def main():
    missing = [str(p) for p in REQUIRED if not p.exists()]
    if missing:
        print("[FAIL] Missing files:")
        for x in missing:
            print(" -", x)
        sys.exit(1)

    summary = json.load(open("dataset/setting_a/13_retrieval_v3_prep/collapse_summary.json", "r", encoding="utf-8"))
    train_pools = json.load(open("dataset/setting_a/13_retrieval_v3_prep/train_hard_negative_pools.json", "r", encoding="utf-8"))

    print("[OK] All retrieval-v3 Day 1 files exist.")
    print("collapse_topn =", summary["config"]["collapse_topn"])
    print("num_collapse_drugs =", len(summary["collapse_summary"]["collapse_drugs"]))
    print("train_hard_pool_mean =", train_pools["summary"]["hard_pool_size_mean"])
    print("train_hard_pool_min =", train_pools["summary"]["hard_pool_size_min"])
    print("train_hard_pool_max =", train_pools["summary"]["hard_pool_size_max"])

    first = train_pools["rows"][0]
    print("\nFirst train hard pool sample keys:", list(first.keys()))
    print("First query:", first["query_entity"])
    print("First gold:", first["gold_entity"])
    print("First hard pool size:", first["hard_pool_size"])
    print("First hard negatives:", first["hard_negative_entities"][:10])

    print("\nSuggested manual review:")
    print("cat dataset/setting_a/13_retrieval_v3_prep/collapse_summary.json")
    print("head -20 dataset/setting_a/13_retrieval_v3_prep/collapse_drug_list.txt")
    print("cat reports/week8/day1_retrieval_v3_prep.md")


if __name__ == "__main__":
    main()