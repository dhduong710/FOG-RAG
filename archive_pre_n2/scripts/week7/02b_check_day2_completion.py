#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json
import sys


REQUIRED_FILES = [
    Path("dataset/setting_a/11_ranker_v2/rgcn_ranker_v2_checkpoint.pt"),
    Path("dataset/setting_a/11_ranker_v2/ranker_v2_train_log.jsonl"),
    Path("dataset/setting_a/11_ranker_v2/ranker_v2_meta.json"),
    Path("reports/week7/day2_score_stats.json"),
    Path("reports/week7/day2_top1_probe.tsv"),
    Path("reports/week7/day2_ranker_v2_train.md"),
]


def main():
    missing = [str(p) for p in REQUIRED_FILES if not p.exists()]
    if missing:
        print("[FAIL] Missing required files:")
        for x in missing:
            print(" -", x)
        sys.exit(1)

    meta = json.load(open("dataset/setting_a/11_ranker_v2/ranker_v2_meta.json", "r", encoding="utf-8"))
    best_probe = meta.get("best_probe", {})
    best_stats = meta.get("best_stats", {})

    print("[OK] All required files exist.")
    print("best_epoch =", meta.get("best_epoch"))
    print("best_probe_recall20 =", best_probe.get("recall20"))
    print("best_probe_top1_hit_ratio =", best_probe.get("top1_hit_ratio"))
    print("best_probe_top1_dominance_ratio =", best_probe.get("top1_dominance_ratio"))
    print("pos_score_mean =", best_stats.get("pos_score_mean"))
    print("neg_score_mean =", best_stats.get("neg_score_mean"))
    print("score_gap_mean =", best_stats.get("score_gap_mean"))

    if best_stats.get("pos_score_mean") is not None and best_stats.get("neg_score_mean") is not None:
        if best_stats["pos_score_mean"] <= best_stats["neg_score_mean"]:
            print("[WARN] pos_score_mean <= neg_score_mean. Training may still be weak.")
        else:
            print("[OK] pos_score_mean > neg_score_mean.")

    print("\nSuggested manual review:")
    print("tail -10 dataset/setting_a/11_ranker_v2/ranker_v2_train_log.jsonl")
    print("cat dataset/setting_a/11_ranker_v2/ranker_v2_meta.json")
    print("cat reports/week7/day2_ranker_v2_train.md")


if __name__ == "__main__":
    main()