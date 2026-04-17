#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json
import sys


REQUIRED = [
    Path("reports/week7/day4_compare_summary.json"),
    Path("reports/week7/day4_rank_distribution_comparison.json"),
    Path("reports/week7/day4_improved_cases.tsv"),
    Path("reports/week7/day4_worsened_cases.tsv"),
    Path("reports/week7/day4_compare_week6_vs_week7.md"),
]


def main():
    missing = [str(p) for p in REQUIRED if not p.exists()]
    if missing:
        print("[FAIL] Missing files:")
        for x in missing:
            print(" -", x)
        sys.exit(1)

    summary = json.load(open("reports/week7/day4_compare_summary.json", "r", encoding="utf-8"))
    d = summary["delta_valid"]
    cats = summary["per_query_comparison"]["category_counts"]
    injects = summary["per_query_comparison"]["inject_transition_counts"]

    print("[OK] All required Day 4 files exist.")
    print("delta_recall@20_raw =", d["delta_recall_at_20_raw"])
    print("delta_top1_hit_ratio_raw =", d["delta_top1_hit_ratio_raw"])
    print("delta_inject_ratio_ready =", d["delta_inject_ratio_ready"])
    print("improved_to_top20 =", cats.get("improved_to_top20", 0))
    print("worsened_out_of_top20 =", cats.get("worsened_out_of_top20", 0))
    print("still_missing =", cats.get("still_missing", 0))
    print("still_hit =", cats.get("still_hit", 0))
    print("inject_removed =", injects.get("inject_removed", 0))
    print("inject_still_needed =", injects.get("inject_still_needed", 0))

    print("\nSuggested manual review:")
    print("cat reports/week7/day4_compare_summary.json")
    print("cat reports/week7/day4_compare_week6_vs_week7.md")
    print("head -20 reports/week7/day4_improved_cases.tsv")
    print("head -20 reports/week7/day4_worsened_cases.tsv")


if __name__ == "__main__":
    main()