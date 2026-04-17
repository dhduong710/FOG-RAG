#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def detect_cand_field(row: Dict[str, Any]) -> str:
    if "candidate_entities" in row:
        return "candidate_entities"
    if "rank_entities" in row:
        return "rank_entities"
    raise KeyError("Cannot detect candidate field.")


def final_contra_count(row: Dict[str, Any]) -> int:
    cand_field = detect_cand_field(row)
    cands = row.get(cand_field, [])
    contra_set = set(row.get("contra_candidates", []))
    return sum(1 for c in cands if c in contra_set)


def build_case_record(hard_row: Dict[str, Any], soft_row: Dict[str, Any]) -> Dict[str, Any]:
    hard_field = detect_cand_field(hard_row)
    soft_field = detect_cand_field(soft_row)

    hard_cands = hard_row.get(hard_field, [])
    soft_cands = soft_row.get(soft_field, [])
    gold = hard_row.get("gold_entity")

    record = {
        "query_entity": hard_row.get("query_entity"),
        "gold_entity": gold,
        "hard_candidates_top10": hard_cands[:10],
        "soft_candidates_top10": soft_cands[:10],
        "hard_num_candidates": len(hard_cands),
        "soft_num_candidates": len(soft_cands),
        "hard_fallback": int(hard_row.get("fallback_after_hard", 0)),
        "hard_gold_in_topk": int(gold in set(hard_cands)),
        "soft_gold_in_topk": int(gold in set(soft_cands)),
        "hard_final_contra_count": final_contra_count(hard_row),
        "soft_final_contra_count": final_contra_count(soft_row),
        "hard_removed_candidates": int(hard_row.get("hard_removed_candidates", 0)),
        "soft_demoted_contra_candidates": int(soft_row.get("soft_demoted_contra_candidates", 0)),
    }
    return record


def categorize_case(case: Dict[str, Any]) -> List[str]:
    tags = []

    if case["hard_fallback"] == 1:
        tags.append("hard_fallback_case")

    if case["hard_gold_in_topk"] == 0 and case["soft_gold_in_topk"] == 1:
        tags.append("gold_lost_by_hard")

    if case["hard_gold_in_topk"] == 1 and case["soft_gold_in_topk"] == 0:
        tags.append("gold_saved_by_hard_vs_soft")

    if case["soft_final_contra_count"] > 0:
        tags.append("soft_keeps_contra")

    if (
        case["hard_final_contra_count"] == 0
        and case["soft_final_contra_count"] > 0
        and case["hard_gold_in_topk"] >= case["soft_gold_in_topk"]
    ):
        tags.append("hard_cleaner_same_or_better")

    if case["hard_fallback"] == 1 and case["hard_num_candidates"] <= 3:
        tags.append("needs_manual_review")

    return tags


def collect_cases(hard_rows, soft_rows):
    if len(hard_rows) != len(soft_rows):
        raise ValueError("hard_rows and soft_rows must have the same length")

    all_cases = []
    grouped = {
        "hard_fallback_case": [],
        "gold_lost_by_hard": [],
        "gold_saved_by_hard_vs_soft": [],
        "soft_keeps_contra": [],
        "hard_cleaner_same_or_better": [],
        "needs_manual_review": [],
    }

    for h, s in zip(hard_rows, soft_rows):
        case = build_case_record(h, s)
        tags = categorize_case(case)
        case["tags"] = tags
        all_cases.append(case)

        for t in tags:
            grouped[t].append(case)

    summary = {k: len(v) for k, v in grouped.items()}
    return all_cases, grouped, summary


def decide_main_row(hard_rank, hard_safe, soft_rank, soft_safe):
    # simple rule based on current week10 intent:
    # prefer row with no contra final if ranking is not worse
    hard_score = (
        hard_rank["mrr"],
        hard_rank["hits10"],
        -hard_safe["contra_candidates_final"],
        -hard_safe["QueryHasContraCandidateRate"],
    )
    soft_score = (
        soft_rank["mrr"],
        soft_rank["hits10"],
        -soft_safe["contra_candidates_final"],
        -soft_safe["QueryHasContraCandidateRate"],
    )

    if hard_rank == soft_rank:
        return {
            "main_row": "hard_main",
            "supporting_row": "soft_best",
            "reason": (
                "Ranking metrics are identical, while hard_main fully removes contraindicated final candidates."
            ),
        }

    if hard_rank["mrr"] >= soft_rank["mrr"] and hard_safe["contra_candidates_final"] <= soft_safe["contra_candidates_final"]:
        return {
            "main_row": "hard_main",
            "supporting_row": "soft_best",
            "reason": "hard_main is at least as good on ranking and clearly cleaner on safety.",
        }

    return {
        "main_row": "soft_best",
        "supporting_row": "hard_main",
        "reason": "soft_best offers a better ranking-safety trade-off under the current rule.",
    }


def write_markdown_report(path, hard_rank, hard_safe, soft_rank, soft_safe, summary, decision, grouped):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# Week 10 - Day 6 Error Review")
    lines.append("")
    lines.append("## Ranking metrics")
    lines.append("### hard_main")
    lines.append(f"- MRR: {hard_rank['mrr']}")
    lines.append(f"- Hits@1: {hard_rank['hits1']}")
    lines.append(f"- Hits@3: {hard_rank['hits3']}")
    lines.append(f"- Hits@10: {hard_rank['hits10']}")
    lines.append("")
    lines.append("### soft_best")
    lines.append(f"- MRR: {soft_rank['mrr']}")
    lines.append(f"- Hits@1: {soft_rank['hits1']}")
    lines.append(f"- Hits@3: {soft_rank['hits3']}")
    lines.append(f"- Hits@10: {soft_rank['hits10']}")
    lines.append("")
    lines.append("## Safety proxy metrics")
    lines.append("### hard_main")
    for k, v in hard_safe.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("### soft_best")
    for k, v in soft_safe.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Case summary")
    for k, v in summary.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Decision")
    lines.append(f"- main_row: {decision['main_row']}")
    lines.append(f"- supporting_row: {decision['supporting_row']}")
    lines.append(f"- reason: {decision['reason']}")
    lines.append("")
    lines.append("## Sample manual-review cases")
    for i, case in enumerate(grouped["needs_manual_review"][:5]):
        lines.append(f"### Case {i}")
        lines.append(f"- query_entity: {case['query_entity']}")
        lines.append(f"- gold_entity: {case['gold_entity']}")
        lines.append(f"- hard_fallback: {case['hard_fallback']}")
        lines.append(f"- hard_candidates_top10: {case['hard_candidates_top10']}")
        lines.append(f"- soft_candidates_top10: {case['soft_candidates_top10']}")
        lines.append(f"- tags: {case['tags']}")
        lines.append("")
    lines.append("## Notes")
    lines.append("- If ranking metrics stay identical, safety dominates the week10 decision.")
    lines.append("- hard_main should become the week11 main row unless fallback cases look biologically implausible.")
    lines.append("- soft_best remains useful as a supporting ablation row showing the trade-off.")
    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hard_json", default="dataset/setting_a/19_contra_aware/valid_top20_hard_main.json")
    parser.add_argument("--soft_json", default="dataset/setting_a/19_contra_aware/valid_top20_soft_best.json")
    parser.add_argument("--hard_rank", default="results/week10/hard_valid/ranking_metrics.json")
    parser.add_argument("--hard_safe", default="results/week10/hard_valid/safety_proxy_metrics.json")
    parser.add_argument("--soft_rank", default="results/week10/soft_valid/ranking_metrics.json")
    parser.add_argument("--soft_safe", default="results/week10/soft_valid/safety_proxy_metrics.json")
    parser.add_argument("--out_json", default="results/week10/safety_error_cases.json")
    parser.add_argument("--out_md", default="reports/week10/day6_error_review.md")
    args = parser.parse_args()

    hard_rows = load_json(args.hard_json)
    soft_rows = load_json(args.soft_json)
    hard_rank = load_json(args.hard_rank)
    hard_safe = load_json(args.hard_safe)
    soft_rank = load_json(args.soft_rank)
    soft_safe = load_json(args.soft_safe)

    all_cases, grouped, summary = collect_cases(hard_rows, soft_rows)
    decision = decide_main_row(hard_rank, hard_safe, soft_rank, soft_safe)

    payload = {
        "summary": summary,
        "decision": decision,
        "hard_ranking_metrics": hard_rank,
        "hard_safety_proxy_metrics": hard_safe,
        "soft_ranking_metrics": soft_rank,
        "soft_safety_proxy_metrics": soft_safe,
        "sample_cases": {
            k: v[:20] for k, v in grouped.items()
        }
    }
    save_json(payload, args.out_json)
    write_markdown_report(args.out_md, hard_rank, hard_safe, soft_rank, soft_safe, summary, decision, grouped)

    print("Case summary:", summary)
    print("Decision:", decision)
    print(f"Saved: {args.out_json}")
    print(f"Saved: {args.out_md}")


if __name__ == "__main__":
    main()