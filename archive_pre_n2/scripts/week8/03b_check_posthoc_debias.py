#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json
import sys


REQUIRED = [
    Path("dataset/setting_a/15_posthoc_debias/valid_debias_sweep_results.json"),
    Path("reports/week8/day3_posthoc_debias_sweep.md"),
]

OPTIONAL_IF_APPLY = [
    Path("dataset/setting_a/15_posthoc_debias/best_lambda_artifacts/candidate_report.json"),
    Path("dataset/setting_a/15_posthoc_debias/best_lambda_artifacts/valid_top20_raw.json"),
    Path("dataset/setting_a/15_posthoc_debias/best_lambda_artifacts/valid_top20_drkgc_ready.json"),
]


def main():
    missing = [str(p) for p in REQUIRED if not p.exists()]
    if missing:
        print("[FAIL] Missing required files:")
        for x in missing:
            print(" -", x)
        sys.exit(1)

    sweep = json.load(open("dataset/setting_a/15_posthoc_debias/valid_debias_sweep_results.json", "r", encoding="utf-8"))
    best = sweep["best_row"]
    accepted = sweep["accepted_rows"]

    print("[OK] Post-hoc debias sweep files exist.")
    print("best_lambda =", best["lambda"])
    print("best_recall@20_raw =", best["recall_at_k_raw"])
    print("best_top1_hit_ratio_raw =", best["top1_hit_ratio_raw"])
    print("best_inject_ratio_ready =", best["inject_ratio_ready"])
    print("best_unique_top1_count_raw =", best["unique_top1_count_raw"])
    print("best_top1_dominance_ratio_raw =", best["top1_dominance_ratio_raw"])
    print("num_accepted_lambdas =", len(accepted))

    opt_missing = [str(p) for p in OPTIONAL_IF_APPLY if not p.exists()]
    if opt_missing:
        print("\n[WARN] Best-lambda full artifacts are missing:")
        for x in opt_missing:
            print(" -", x)
    else:
        report = json.load(open("dataset/setting_a/15_posthoc_debias/best_lambda_artifacts/candidate_report.json", "r", encoding="utf-8"))
        v = report["splits"]["valid"]
        print("\n[OK] Best-lambda full artifacts exist.")
        print("full_valid_recall@20_raw =", v["recall_at_k_raw"])
        print("full_valid_top1_hit_ratio_raw =", v["top1_hit_ratio_raw"])
        print("full_valid_inject_ratio_ready =", v["inject_ratio_ready"])
        print("full_valid_unique_top1_count_raw =", v["unique_top1_count_raw"])
        print("full_valid_top1_dominance_ratio_raw =", v["top1_dominance_ratio_raw"])

    print("\nSuggested manual review:")
    print("cat dataset/setting_a/15_posthoc_debias/valid_debias_sweep_results.json")
    print("cat reports/week8/day3_posthoc_debias_sweep.md")
    print("cat dataset/setting_a/15_posthoc_debias/best_lambda_artifacts/candidate_report.json")


if __name__ == "__main__":
    main()