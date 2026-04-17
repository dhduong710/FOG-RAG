#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="Collect best/worst cases from eval prediction file")
    p.add_argument("--prediction_path", default="results/week5/backbone_llama32_3b_rgcn/eval_valid_prediction.json")
    p.add_argument("--output_md", default="results/week5/backbone_llama32_3b_rgcn/eval_valid_error_cases.md")
    return p.parse_args()


def category_of_case(ex):
    pred = (ex.get("pred") or "").strip()
    pred_rank = ex.get("pred_rank", 999999)
    in_cand = ex.get("pred_in_candidate", False)

    if pred_rank == 1:
        return "hit@1"
    if not pred:
        return "empty_prediction"
    if not in_cand:
        return "prediction_not_in_candidate"
    return "prediction_in_candidate_but_not_top"


def brief_case(ex):
    return {
        "query_entity": ex.get("query_entity"),
        "target": ex.get("target"),
        "pred": ex.get("pred"),
        "pred_rank": ex.get("pred_rank"),
        "gold_rank_before_llm": ex.get("rank"),
        "candidate_size": ex.get("candidate_size"),
        "subgraph_size": ex.get("subgraph_size"),
        "top5_candidates": ex.get("rank_entities", [])[:5],
        "category": category_of_case(ex),
    }


def main():
    args = parse_args()

    payload = json.load(open(args.prediction_path, "r", encoding="utf-8"))
    metrics = payload["metrics"]
    preds = payload["prediction"]

    preds_sorted_best = sorted(preds, key=lambda x: x.get("pred_rank", 999999))
    preds_sorted_worst = sorted(preds, key=lambda x: x.get("pred_rank", -1), reverse=True)

    best5 = [brief_case(x) for x in preds_sorted_best[:5]]
    worst5 = [brief_case(x) for x in preds_sorted_worst[:5]]

    category_counts = {}
    for ex in preds:
        c = category_of_case(ex)
        category_counts[c] = category_counts.get(c, 0) + 1

    md = []
    md.append("# Week 5 - Day 6 Error Case Report")
    md.append("")
    md.append("## Overall metrics")
    for k, v in metrics.items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## Category counts")
    for k, v in sorted(category_counts.items()):
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## 5 best cases")
    md.append("```json")
    md.append(json.dumps(best5, ensure_ascii=False, indent=2))
    md.append("```")
    md.append("")
    md.append("## 5 worst cases")
    md.append("```json")
    md.append(json.dumps(worst5, ensure_ascii=False, indent=2))
    md.append("```")
    md.append("")
    md.append("## Notes")
    md.append("- `prediction_not_in_candidate` often suggests reranking/generation drift.")
    md.append("- `prediction_in_candidate_but_not_top` often suggests candidate quality or graph signal may be insufficient.")
    md.append("- This report is mechanical; final interpretation should still be read manually.")

    Path(args.output_md).write_text("\n".join(md), encoding="utf-8")
    print("Saved:", args.output_md)


if __name__ == "__main__":
    main()