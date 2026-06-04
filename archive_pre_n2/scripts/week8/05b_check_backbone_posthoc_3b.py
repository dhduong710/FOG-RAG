#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json
import sys

REQUIRED = [
    Path("results/week8/backbone_valid_posthoc_3b/checkpoint-final"),
    Path("results/week8/backbone_valid_posthoc_3b/valid_eval_posthoc_3b/eval_valid_posthoc_3b_metrics.json"),
    Path("results/week8/backbone_valid_posthoc_3b/valid_eval_posthoc_3b/eval_valid_posthoc_3b_prediction.json"),
    Path("results/week8/backbone_valid_posthoc_3b/valid_eval_posthoc_3b/eval_valid_posthoc_3b_error_cases.md"),
    Path("reports/week8/day5_valid_posthoc_3b.md"),
]

def main():
    missing = [str(p) for p in REQUIRED if not p.exists()]
    if missing:
        print("[FAIL] Missing posthoc 3B outputs:")
        for x in missing:
            print(" -", x)
        sys.exit(1)

    metrics = json.load(open("results/week8/backbone_valid_posthoc_3b/valid_eval_posthoc_3b/eval_valid_posthoc_3b_metrics.json", "r", encoding="utf-8"))
    print("[OK] Posthoc 3B required files exist.")
    print("mrr =", metrics.get("mrr"))
    print("hits1 =", metrics.get("hits1"))
    print("hits3 =", metrics.get("hits3"))
    print("hits10 =", metrics.get("hits10"))
    print("num_examples =", metrics.get("num_examples"))
    print("split =", metrics.get("split"))

    print("\nSuggested manual review:")
    print("cat results/week8/backbone_valid_posthoc_3b/valid_eval_posthoc_3b/eval_valid_posthoc_3b_metrics.json")
    print("cat reports/week8/day5_valid_posthoc_3b.md")
    print("tail -50 reports/week8/day5_train_backbone_posthoc_3b.log")
    print("tail -50 reports/week8/day5_eval_backbone_posthoc_3b.log")

if __name__ == "__main__":
    main()