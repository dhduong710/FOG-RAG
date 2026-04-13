#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import ast
import json
from pathlib import Path


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def detect_cand_field(row):
    if "candidate_entities" in row:
        return "candidate_entities"
    if "rank_entities" in row:
        return "rank_entities"
    raise KeyError("Cannot detect candidate field")


def parse_metrics_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    # expected line: ranking metrics: {'mrr': ..., 'hits1': ...}
    prefix = "ranking metrics:"
    if prefix not in text:
        raise ValueError(f"Cannot parse metrics from {path}")
    payload = text.split(prefix, 1)[1].strip()
    metrics = ast.literal_eval(payload)
    return metrics


def summarize_candidate_artifact(rows):
    num_queries = len(rows)
    total_candidates = 0
    total_final_contra = 0
    query_has_contra = 0
    gold_in_topk = 0
    strict_empty_after_hard = 0
    fallback_after_hard = 0
    fallback_after_soft = 0
    hard_removed_candidates = 0
    soft_demoted_contra_candidates = 0

    for r in rows:
        cand_field = detect_cand_field(r)
        cands = r.get(cand_field, [])
        total_candidates += len(cands)

        contra_set = set(r.get("contra_candidates", []))
        final_contra = sum(1 for c in cands if c in contra_set)
        total_final_contra += final_contra
        query_has_contra += int(final_contra > 0)

        gold = r.get("gold_entity")
        gold_in_topk += int(gold in set(cands))

        strict_empty_after_hard += int(r.get("strict_empty_after_hard", 0))
        fallback_after_hard += int(r.get("fallback_after_hard", 0))
        fallback_after_soft += int(r.get("fallback_after_soft", 0))
        hard_removed_candidates += int(r.get("hard_removed_candidates", 0))
        soft_demoted_contra_candidates += int(r.get("soft_demoted_contra_candidates", 0))

    return {
        "num_queries": num_queries,
        "contra_candidates_final": total_final_contra,
        "QueryHasContraCandidateRate": query_has_contra / num_queries if num_queries else 0.0,
        "strict_empty_after_hard": strict_empty_after_hard,
        "fallback_after_hard": fallback_after_hard,
        "fallback_after_soft": fallback_after_soft,
        "gold_in_topk": gold_in_topk,
        "gold_in_topk_rate": gold_in_topk / num_queries if num_queries else 0.0,
        "avg_candidate_size": total_candidates / num_queries if num_queries else 0.0,
        "hard_removed_candidates": hard_removed_candidates,
        "soft_demoted_contra_candidates": soft_demoted_contra_candidates,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics_txt", required=True)
    parser.add_argument("--candidate_json", required=True)
    parser.add_argument("--out_dir", required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()

    rows = load_json(args.candidate_json)
    ranking_metrics = parse_metrics_txt(args.metrics_txt)
    safety_proxy = summarize_candidate_artifact(rows)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    candidate_summary = {
        "label": args.label,
        "candidate_json": args.candidate_json,
        "metrics_txt": args.metrics_txt,
        "num_rows": len(rows),
    }

    save_json(ranking_metrics, out_dir / "ranking_metrics.json")
    save_json(safety_proxy, out_dir / "safety_proxy_metrics.json")
    save_json(candidate_summary, out_dir / "candidate_summary.json")

    print(f"[{args.label}] ranking_metrics = {ranking_metrics}")
    print(f"[{args.label}] safety_proxy = {safety_proxy}")
    print(f"Saved outputs to: {out_dir}")


if __name__ == "__main__":
    main()