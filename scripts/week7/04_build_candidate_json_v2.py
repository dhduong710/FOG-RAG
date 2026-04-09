#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 7 - Day 3
Build top20_raw / top20_drkgc_ready JSONs and candidate_report.json from score dumps.

Inputs:
- dataset/setting_a/11_ranker_v2/train_scores.pt
- dataset/setting_a/11_ranker_v2/valid_scores.pt
- dataset/setting_a/11_ranker_v2/test_scores.pt

Outputs:
- dataset/setting_a/11_ranker_v2/train_top20_raw.json
- dataset/setting_a/11_ranker_v2/valid_top20_raw.json
- dataset/setting_a/11_ranker_v2/test_top20_raw.json
- dataset/setting_a/11_ranker_v2/train_top20_drkgc_ready.json
- dataset/setting_a/11_ranker_v2/valid_top20_drkgc_ready.json
- dataset/setting_a/11_ranker_v2/test_top20_drkgc_ready.json
- dataset/setting_a/11_ranker_v2/candidate_report.json
- reports/week7/day3_candidate_quality.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections import Counter
from typing import Any, Dict, List, Tuple

import torch


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def load_score_dump(path: Path) -> Dict[str, Any]:
    return torch.load(path, map_location="cpu")


def build_raw_and_ready_for_split(
    dump: Dict[str, Any],
    split_name: str,
    k: int,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    scores: torch.Tensor = dump["scores"].to(torch.float32)  # [N, Nc]
    candidate_universe_ids: List[int] = dump["candidate_universe_entity_ids"].tolist()
    candidate_universe_names: List[str] = dump["candidate_universe_entity_names"]

    id_to_name = {eid: name for eid, name in zip(candidate_universe_ids, candidate_universe_names)}
    universe_index = {eid: idx for idx, eid in enumerate(candidate_universe_ids)}

    query_entity_ids = dump["query_entity_ids"].tolist()
    query_entity_names = dump["query_entity_names"]
    gold_entity_ids = dump["gold_entity_ids"].tolist()
    gold_entity_names = dump["gold_entity_names"]

    n = len(query_entity_ids)
    if n != scores.size(0):
        raise ValueError(f"Mismatch in split {split_name}: num queries != score rows")

    top1_counter = Counter()
    rank_distribution_raw_top50 = Counter()

    raw_rows = []
    ready_rows = []

    recall_at_k_raw = 0
    top1_hit_ratio_raw_count = 0
    inject_count_ready = 0

    for i in range(n):
        row_scores = scores[i]  # [Nc]
        gold_id = int(gold_entity_ids[i])
        query_id = int(query_entity_ids[i])

        if gold_id not in universe_index:
            raise ValueError(
                f"Gold drug id {gold_id} is not found in candidate universe for split {split_name}"
            )

        gold_score = float(row_scores[universe_index[gold_id]].item())

        # Exact raw top-k
        topk_scores, topk_idx = torch.topk(row_scores, k=k, largest=True, sorted=True)
        topk_idx_list = topk_idx.tolist()
        raw_candidate_ids = [candidate_universe_ids[j] for j in topk_idx_list]
        raw_candidate_names = [candidate_universe_names[j] for j in topk_idx_list]

        # Gold rank in full universe (1 = best), counting strictly greater scores.
        # Ties are rare; this yields a stable and practical rank.
        gold_rank_in_full_universe = int((row_scores > gold_score).sum().item()) + 1

        gold_in_topk_raw = bool(gold_rank_in_full_universe <= k)

        if gold_in_topk_raw:
            recall_at_k_raw += 1
        if raw_candidate_ids and raw_candidate_ids[0] == gold_id:
            top1_hit_ratio_raw_count += 1

        if raw_candidate_names:
            top1_counter[raw_candidate_names[0]] += 1

        if gold_rank_in_full_universe <= 50:
            rank_distribution_raw_top50[str(gold_rank_in_full_universe)] += 1

        raw_row = {
            "split": split_name,
            "query_entity": query_entity_names[i],
            "query_entity_id": query_id,
            "gold_entity": gold_entity_names[i],
            "gold_entity_id": gold_id,
            "candidate_entities": raw_candidate_names,
            "candidate_entity_ids": raw_candidate_ids,
            "gold_rank_in_full_universe": gold_rank_in_full_universe,
            "gold_in_topk_raw": gold_in_topk_raw,
        }
        raw_rows.append(raw_row)

        # drkgc_ready: inject gold into position K if missing
        ready_candidate_ids = list(raw_candidate_ids)
        ready_candidate_names = list(raw_candidate_names)
        gold_injected = False

        if not gold_in_topk_raw:
            gold_injected = True
            inject_count_ready += 1
            if len(ready_candidate_ids) < k:
                ready_candidate_ids.append(gold_id)
                ready_candidate_names.append(gold_entity_names[i])
            else:
                ready_candidate_ids[-1] = gold_id
                ready_candidate_names[-1] = gold_entity_names[i]

        gold_in_topk_ready = gold_id in ready_candidate_ids

        ready_row = {
            "split": split_name,
            "query_entity": query_entity_names[i],
            "query_entity_id": query_id,
            "gold_entity": gold_entity_names[i],
            "gold_entity_id": gold_id,
            "candidate_entities": ready_candidate_names,
            "candidate_entity_ids": ready_candidate_ids,
            "gold_rank_in_full_universe": gold_rank_in_full_universe,
            "gold_in_topk_raw": gold_in_topk_raw,
            "gold_in_topk_ready": bool(gold_in_topk_ready),
            "gold_injected": bool(gold_injected),
        }
        ready_rows.append(ready_row)

    unique_top1_count_raw = len(top1_counter)
    most_common_top1_raw = top1_counter.most_common(10)
    top1_dominance_ratio_raw = (most_common_top1_raw[0][1] / n) if most_common_top1_raw else 0.0

    split_report = {
        "split": split_name,
        "num_queries": n,
        "k": k,
        "recall_at_k_raw": round(recall_at_k_raw / n, 6),
        "top1_hit_ratio_raw": round(top1_hit_ratio_raw_count / n, 6),
        "inject_count_ready": inject_count_ready,
        "inject_ratio_ready": round(inject_count_ready / n, 6),
        "rank_distribution_raw_top50": dict(rank_distribution_raw_top50),
        "unique_top1_count_raw": unique_top1_count_raw,
        "top1_dominance_ratio_raw": round(top1_dominance_ratio_raw, 6),
        "top1_frequency_raw_top10": [{"drug": name, "count": cnt} for name, cnt in most_common_top1_raw],
    }

    return raw_rows, ready_rows, split_report


def write_markdown_report(
    md_path: Path,
    candidate_report: Dict[str, Any],
    maybe_week6_report: Dict[str, Any] | None = None,
) -> None:
    splits = candidate_report["splits"]
    valid = splits["valid"]

    lines = []
    lines.append("# Day 3 — Candidate quality from ranker_v2")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Score full train/valid/test using the best ranker_v2 checkpoint.")
    lines.append("- Build top20_raw and top20_drkgc_ready artifacts.")
    lines.append("- Evaluate candidate retrieval quality on valid as the main scientific signal.")
    lines.append("")

    lines.append("## Current valid numbers")
    lines.append("")
    lines.append(f"- valid_recall@20_raw = `{valid['recall_at_k_raw']}`")
    lines.append(f"- valid_top1_hit_ratio_raw = `{valid['top1_hit_ratio_raw']}`")
    lines.append(f"- valid_inject_ratio_ready = `{valid['inject_ratio_ready']}`")
    lines.append(f"- valid_unique_top1_count_raw = `{valid['unique_top1_count_raw']}`")
    lines.append(f"- valid_top1_dominance_ratio_raw = `{valid['top1_dominance_ratio_raw']}`")
    lines.append("")

    if maybe_week6_report is not None:
        w6_valid = maybe_week6_report["splits"]["valid"]
        lines.append("## Comparison against week 6")
        lines.append("")
        lines.append(f"- week6_valid_recall@20_raw = `{w6_valid['recall_at_k_raw']}`")
        lines.append(f"- week7_valid_recall@20_raw = `{valid['recall_at_k_raw']}`")
        lines.append(f"- week6_valid_inject_ratio_ready = `{w6_valid['inject_ratio_ready']}`")
        lines.append(f"- week7_valid_inject_ratio_ready = `{valid['inject_ratio_ready']}`")
        lines.append(f"- week6_valid_top1_hit_ratio_raw = `{w6_valid['top1_hit_ratio_raw']}`")
        lines.append(f"- week7_valid_top1_hit_ratio_raw = `{valid['top1_hit_ratio_raw']}`")
        lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("- If valid_recall@20_raw improved clearly over week 6, ranker_v2 is moving in the right direction.")
    lines.append("- If valid_inject_ratio_ready decreased clearly, reranker is less dependent on gold injection.")
    lines.append("- If top1_dominance_ratio_raw is still very high, score collapse is still a concern.")
    lines.append("- Day 4 should compare week6 vs week7 directly on the same valid queries.")
    lines.append("")

    md_path.parent.mkdir(parents=True, exist_ok=True)
    with md_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--score-dir",
        default="dataset/setting_a/11_ranker_v2",
        help="Directory containing *_scores.pt",
    )
    parser.add_argument("--k", type=int, default=20)
    parser.add_argument(
        "--week6-report",
        default="dataset/setting_a/09_real_coarse_ranker/candidate_recall_report.json",
        help="Optional week6 candidate report for easy comparison.",
    )
    parser.add_argument(
        "--report-dir",
        default="reports/week7",
        help="Output report dir",
    )
    args = parser.parse_args()

    score_dir = Path(args.score_dir)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    train_dump = load_score_dump(score_dir / "train_scores.pt")
    valid_dump = load_score_dump(score_dir / "valid_scores.pt")
    test_dump = load_score_dump(score_dir / "test_scores.pt")

    train_raw, train_ready, train_report = build_raw_and_ready_for_split(train_dump, "train", args.k)
    valid_raw, valid_ready, valid_report = build_raw_and_ready_for_split(valid_dump, "valid", args.k)
    test_raw, test_ready, test_report = build_raw_and_ready_for_split(test_dump, "test", args.k)

    save_json(score_dir / "train_top20_raw.json", train_raw)
    save_json(score_dir / "valid_top20_raw.json", valid_raw)
    save_json(score_dir / "test_top20_raw.json", test_raw)

    save_json(score_dir / "train_top20_drkgc_ready.json", train_ready)
    save_json(score_dir / "valid_top20_drkgc_ready.json", valid_ready)
    save_json(score_dir / "test_top20_drkgc_ready.json", test_ready)

    candidate_report = {
        "week": 7,
        "day": 3,
        "goal": "Build ranker_v2 candidate JSON and analyze candidate retrieval quality.",
        "splits": {
            "train": train_report,
            "valid": valid_report,
            "test": test_report,
        },
        "important_note": "Scientific judgment for week 7 still relies primarily on valid; test artifacts are built mechanically but should not be used for tuning decisions.",
    }
    save_json(score_dir / "candidate_report.json", candidate_report)

    maybe_week6_report = None
    week6_path = Path(args.week6_report)
    if week6_path.exists():
        maybe_week6_report = json.load(open(week6_path, "r", encoding="utf-8"))

    write_markdown_report(
        md_path=report_dir / "day3_candidate_quality.md",
        candidate_report=candidate_report,
        maybe_week6_report=maybe_week6_report,
    )

    print("Saved:")
    print(f"- {score_dir / 'train_top20_raw.json'}")
    print(f"- {score_dir / 'valid_top20_raw.json'}")
    print(f"- {score_dir / 'test_top20_raw.json'}")
    print(f"- {score_dir / 'train_top20_drkgc_ready.json'}")
    print(f"- {score_dir / 'valid_top20_drkgc_ready.json'}")
    print(f"- {score_dir / 'test_top20_drkgc_ready.json'}")
    print(f"- {score_dir / 'candidate_report.json'}")
    print(f"- {report_dir / 'day3_candidate_quality.md'}")


if __name__ == "__main__":
    main()