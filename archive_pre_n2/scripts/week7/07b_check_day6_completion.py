#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from pathlib import Path
import sys


REQUIRED = [
    Path("results/week7/backbone_valid_v2_short/checkpoint-final"),
    Path("results/week7/backbone_valid_v2_short/valid_eval_v2/eval_valid_v2_metrics.json"),
    Path("results/week7/backbone_valid_v2_short/valid_eval_v2/eval_valid_v2_prediction.json"),
    Path("results/week7/backbone_valid_v2_short/valid_eval_v2/eval_valid_v2_error_cases.md"),
    Path("reports/week7/day6_valid_eval_v2.md"),
]


def main():
    missing = [str(p) for p in REQUIRED if not p.exists()]
    if missing:
        print("[FAIL] Missing Day 6 outputs:")
        for x in missing:
            print(" -", x)
        sys.exit(1)

    metrics = json.load(open("results/week7/backbone_valid_v2_short/valid_eval_v2/eval_valid_v2_metrics.json", "r", encoding="utf-8"))
    print("[OK] Day 6 required files exist.")
    print("mrr =", metrics.get("mrr"))
    print("hits1 =", metrics.get("hits1"))
    print("hits3 =", metrics.get("hits3"))
    print("hits10 =", metrics.get("hits10"))
    print("num_examples =", metrics.get("num_examples"))
    print("split =", metrics.get("split"))

    print("\nSuggested manual review:")
    print("cat results/week7/backbone_valid_v2_short/valid_eval_v2/eval_valid_v2_metrics.json")
    print("cat reports/week7/day6_valid_eval_v2.md")
    print("tail -50 reports/week7/day6_train_backbone_v2.log")
    print("tail -50 reports/week7/day6_eval_backbone_v2.log")


if __name__ == "__main__":
    main()