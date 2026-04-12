#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json
import sys


REQUIRED = [
    Path("dataset/setting_a/14_ranker_v3_day2b/rgcn_ranker_v3_day2b_checkpoint.pt"),
    Path("dataset/setting_a/14_ranker_v3_day2b/ranker_v3_day2b_train_log.jsonl"),
    Path("dataset/setting_a/14_ranker_v3_day2b/ranker_v3_day2b_meta.json"),
    Path("dataset/setting_a/14_ranker_v3_day2b/sampled_train_negatives_day2b.json"),
    Path("reports/week8/day2b_ranker_v3_train.md"),
    Path("reports/week8/day2b_ranker_v3_score_stats.json"),
    Path("reports/week8/day2b_ranker_v3_top1_probe.tsv"),
]


def main():
    missing = [str(p) for p in REQUIRED if not p.exists()]
    if missing:
        print("[FAIL] Missing files:")
        for x in missing:
            print(" -", x)
        sys.exit(1)

    meta = json.load(open("dataset/setting_a/14_ranker_v3_day2b/ranker_v3_day2b_meta.json", "r", encoding="utf-8"))
    best_probe = meta["best_probe"]
    best_stats = meta["best_stats"]

    print("[OK] All retrieval-v3 Day 2b files exist.")
    print("best_epoch =", meta["best_epoch"])
    print("valid_probe_recall20 =", best_probe["recall20"])
    print("valid_probe_top1_hit_ratio =", best_probe["top1_hit_ratio"])
    print("valid_probe_unique_top1_count =", best_probe["unique_top1_count"])
    print("valid_probe_top1_dominance_ratio =", best_probe["top1_dominance_ratio"])
    print("pos_score_mean =", best_stats["pos_score_mean"])
    print("neg_score_mean =", best_stats["neg_score_mean"])
    print("score_gap_mean =", best_stats["score_gap_mean"])

    sample = json.load(open("dataset/setting_a/14_ranker_v3_day2b/sampled_train_negatives_day2b.json", "r", encoding="utf-8"))
    print("\nSampled negative summary:", sample["summary"])
    if sample["rows"]:
        print("First sampled row:", sample["rows"][0])

    print("\nSuggested manual review:")
    print("cat dataset/setting_a/14_ranker_v3_day2b/ranker_v3_day2b_meta.json")
    print("tail -10 dataset/setting_a/14_ranker_v3_day2b/ranker_v3_day2b_train_log.jsonl")
    print("cat reports/week8/day2b_ranker_v3_train.md")


if __name__ == "__main__":
    main()