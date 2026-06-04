#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json
import torch
import sys


REQUIRED = [
    Path("dataset/setting_a/11_ranker_v2/train_scores.pt"),
    Path("dataset/setting_a/11_ranker_v2/valid_scores.pt"),
    Path("dataset/setting_a/11_ranker_v2/test_scores.pt"),
    Path("dataset/setting_a/11_ranker_v2/score_dump_meta.json"),
    Path("dataset/setting_a/11_ranker_v2/train_top20_raw.json"),
    Path("dataset/setting_a/11_ranker_v2/valid_top20_raw.json"),
    Path("dataset/setting_a/11_ranker_v2/test_top20_raw.json"),
    Path("dataset/setting_a/11_ranker_v2/train_top20_drkgc_ready.json"),
    Path("dataset/setting_a/11_ranker_v2/valid_top20_drkgc_ready.json"),
    Path("dataset/setting_a/11_ranker_v2/test_top20_drkgc_ready.json"),
    Path("dataset/setting_a/11_ranker_v2/candidate_report.json"),
    Path("reports/week7/day3_candidate_quality.md"),
]


def main():
    missing = [str(p) for p in REQUIRED if not p.exists()]
    if missing:
        print("[FAIL] Missing files:")
        for x in missing:
            print(" -", x)
        sys.exit(1)

    report = json.load(open("dataset/setting_a/11_ranker_v2/candidate_report.json", "r", encoding="utf-8"))
    valid = report["splits"]["valid"]

    print("[OK] All required Day 3 files exist.")
    print("valid_recall@20_raw =", valid["recall_at_k_raw"])
    print("valid_top1_hit_ratio_raw =", valid["top1_hit_ratio_raw"])
    print("valid_inject_ratio_ready =", valid["inject_ratio_ready"])
    print("valid_unique_top1_count_raw =", valid["unique_top1_count_raw"])
    print("valid_top1_dominance_ratio_raw =", valid["top1_dominance_ratio_raw"])

    raw_valid = json.load(open("dataset/setting_a/11_ranker_v2/valid_top20_raw.json", "r", encoding="utf-8"))
    ready_valid = json.load(open("dataset/setting_a/11_ranker_v2/valid_top20_drkgc_ready.json", "r", encoding="utf-8"))

    print("\nFirst valid raw sample keys:", list(raw_valid[0].keys()))
    print("First valid ready sample keys:", list(ready_valid[0].keys()))
    print("First valid raw sample:", raw_valid[0])
    print("First valid ready sample:", ready_valid[0])

    print("\nSuggested manual review:")
    print("cat dataset/setting_a/11_ranker_v2/candidate_report.json")
    print("cat reports/week7/day3_candidate_quality.md")


if __name__ == "__main__":
    main()