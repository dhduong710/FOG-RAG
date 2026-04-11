#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json
import sys

REQUIRED = [
    Path("results/week7/backbone_valid_v2_8b_full/checkpoint-final"),
    Path("results/week7/backbone_valid_v2_8b_full/valid_eval_8b/eval_valid_8b_metrics.json"),
    Path("results/week7/backbone_valid_v2_8b_full/valid_eval_8b/eval_valid_8b_prediction.json"),
    Path("results/week7/backbone_valid_v2_8b_full/valid_eval_8b/eval_valid_8b_error_cases.md"),
    Path("reports/week7/day6_8b_valid_eval.md"),
]

def main():
    missing = [str(p) for p in REQUIRED if not p.exists()]
    if missing:
        print("[FAIL] Missing 8B outputs:")
        for x in missing:
            print(" -", x)
        sys.exit(1)

    metrics = json.load(open("results/week7/backbone_valid_v2_8b_full/valid_eval_8b/eval_valid_8b_metrics.json", "r", encoding="utf-8"))
    print("[OK] 8B required files exist.")
    print("mrr =", metrics.get("mrr"))
    print("hits1 =", metrics.get("hits1"))
    print("hits3 =", metrics.get("hits3"))
    print("hits10 =", metrics.get("hits10"))
    print("num_examples =", metrics.get("num_examples"))
    print("split =", metrics.get("split"))

    print("\nSuggested manual review:")
    print("cat results/week7/backbone_valid_v2_8b_full/valid_eval_8b/eval_valid_8b_metrics.json")
    print("cat reports/week7/day6_8b_valid_eval.md")
    print("tail -50 reports/week7/day6_8b_train.log")
    print("tail -50 reports/week7/day6_8b_eval.log")

if __name__ == "__main__":
    main()