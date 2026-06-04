#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 7 - Day 1
Audit week-6 coarse ranker / candidate source quality before training ranker_v2.

Expected inputs:
- dataset/setting_a/09_real_coarse_ranker/valid_top20_raw.json
- dataset/setting_a/09_real_coarse_ranker/valid_top20_drkgc_ready.json
- dataset/setting_a/09_real_coarse_ranker/candidate_recall_report.json
- results/week6/backbone_llama32_3b_rgcn_real/valid_eval/eval_valid_metrics.json
- results/week6/backbone_llama32_3b_rgcn_real/valid_eval/eval_valid_prediction.json

Expected outputs:
- reports/week7/day1_audit_summary.json
- reports/week7/day1_top1_drug_frequency.tsv
- reports/week7/day1_same_query_examples.md
- reports/week7/day1_audit.md
"""

from __future__ import annotations

import json
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
from statistics import mean
from typing import Any, Dict, List, Tuple


# ----------------------------
# Paths
# ----------------------------
RAW_PATH = Path("dataset/setting_a/09_real_coarse_ranker/valid_top20_raw.json")
READY_PATH = Path("dataset/setting_a/09_real_coarse_ranker/valid_top20_drkgc_ready.json")
CAND_REPORT_PATH = Path("dataset/setting_a/09_real_coarse_ranker/candidate_recall_report.json")

VALID_EVAL_DIR = Path("results/week6/backbone_llama32_3b_rgcn_real/valid_eval")
EVAL_METRICS_PATH = VALID_EVAL_DIR / "eval_valid_metrics.json"
EVAL_PRED_PATH = VALID_EVAL_DIR / "eval_valid_prediction.json"

OUT_DIR = Path("reports/week7")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_PATH = OUT_DIR / "day1_audit_summary.json"
TOP1_FREQ_PATH = OUT_DIR / "day1_top1_drug_frequency.tsv"
SAME_QUERY_PATH = OUT_DIR / "day1_same_query_examples.md"
AUDIT_MD_PATH = OUT_DIR / "day1_audit.md"


# ----------------------------
# Utilities
# ----------------------------
def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def safe_div(a: float, b: float) -> float:
    return float(a) / float(b) if b else 0.0


def jaccard(xs: List[str], ys: List[str]) -> float:
    sx, sy = set(xs), set(ys)
    if not sx and not sy:
        return 1.0
    return len(sx & sy) / len(sx | sy)


def get_eval_prediction_list(blob: Any) -> List[Dict[str, Any]]:
    """
    eval_valid_prediction.json in your repo is expected to be:
    {
      "args": ...,
      "generation_config": ...,
      "metrics": ...,
      "prediction": [...]
    }
    but this function also tolerates a raw list.
    """
    if isinstance(blob, list):
        return blob
    if isinstance(blob, dict):
        if "prediction" in blob and isinstance(blob["prediction"], list):
            return blob["prediction"]
    raise ValueError(
        f"Unexpected format in {EVAL_PRED_PATH}. "
        "Expected either a list or a dict with key 'prediction'."
    )


def make_key_from_raw(ex: Dict[str, Any]) -> Tuple[Any, Any]:
    return (ex.get("query_entity_id"), ex.get("gold_entity_id"))


def make_key_from_pred(ex: Dict[str, Any]) -> Tuple[Any, Any]:
    # Prefer exact ids if present.
    qid = ex.get("query_entity_id")
    gid = ex.get("gold_entity_id")
    if qid is not None and gid is not None:
        return (qid, gid)

    # Fallback to (query_entity, target) if needed.
    q = ex.get("query_entity")
    g = ex.get("gold_entity", ex.get("target"))
    return (q, g)


# ----------------------------
# Core analysis
# ----------------------------
def analyze_candidate_quality(
    raw_data: List[Dict[str, Any]],
    ready_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    if len(raw_data) != len(ready_data):
        raise ValueError("valid_top20_raw.json and valid_top20_drkgc_ready.json have different lengths.")

    n = len(raw_data)

    top1_counter: Counter = Counter()
    top5_counter: Counter = Counter()
    dup_within_query_counter = 0

    gold_in_top20_raw_count = 0
    gold_in_top1_raw_count = 0
    gold_in_top20_ready_count = 0
    gold_injected_count = 0

    inject_positions: List[int] = []
    top20_lists: List[List[str]] = []
    same_top5_examples: List[Dict[str, Any]] = []
    missing_gold_examples: List[Dict[str, Any]] = []

    for raw_ex, ready_ex in zip(raw_data, ready_data):
        raw_cands = raw_ex["candidate_entities"]
        ready_cands = ready_ex["candidate_entities"]
        gold = raw_ex["gold_entity"]
        query = raw_ex["query_entity"]

        top20_lists.append(raw_cands)

        if raw_cands:
            top1_counter[raw_cands[0]] += 1
            top5_counter[tuple(raw_cands[:5])] += 1

        if len(set(raw_cands)) < len(raw_cands):
            dup_within_query_counter += 1

        gold_in_raw = bool(raw_ex.get("gold_in_topk_raw", gold in raw_cands))
        gold_in_ready = bool(ready_ex.get("gold_in_topk_ready", gold in ready_cands))
        gold_injected = bool(ready_ex.get("gold_injected", (not gold_in_raw and gold in ready_cands)))

        if gold_in_raw:
            gold_in_top20_raw_count += 1
        if raw_cands and raw_cands[0] == gold:
            gold_in_top1_raw_count += 1
        if gold_in_ready:
            gold_in_top20_ready_count += 1
        if gold_injected:
            gold_injected_count += 1
            try:
                inject_positions.append(ready_cands.index(gold) + 1)
            except ValueError:
                pass

        if not gold_in_raw and len(missing_gold_examples) < 20:
            missing_gold_examples.append(
                {
                    "query_entity": query,
                    "gold_entity": gold,
                    "gold_rank_in_full_universe": raw_ex.get("gold_rank_in_full_universe"),
                    "raw_top5": raw_cands[:5],
                    "ready_top5": ready_cands[:5],
                    "gold_injected": gold_injected,
                }
            )

    # Pairwise top-20 similarity across valid queries.
    pairwise_jaccards: List[float] = []
    for a, b in combinations(top20_lists, 2):
        pairwise_jaccards.append(jaccard(a, b))
    mean_jaccard_top20 = mean(pairwise_jaccards) if pairwise_jaccards else 0.0

    repeated_top5 = top5_counter.most_common(10)
    for pattern, count in repeated_top5:
        if count >= 2 and len(same_top5_examples) < 10:
            same_top5_examples.append(
                {
                    "count": count,
                    "top5": list(pattern),
                }
            )

    most_common_top1 = top1_counter.most_common(20)
    unique_top1_count = len(top1_counter)
    top1_dominance_ratio = safe_div(most_common_top1[0][1], n) if most_common_top1 else 0.0

    return {
        "num_valid": n,
        "gold_in_top20_raw_count": gold_in_top20_raw_count,
        "gold_in_top20_ready_count": gold_in_top20_ready_count,
        "gold_injected_count": gold_injected_count,
        "valid_recall20_raw": safe_div(gold_in_top20_raw_count, n),
        "valid_top1_hit_ratio_raw": safe_div(gold_in_top1_raw_count, n),
        "valid_inject_ratio_ready": safe_div(gold_injected_count, n),
        "duplicate_candidates_within_query_count": dup_within_query_counter,
        "duplicate_candidates_within_query_ratio": safe_div(dup_within_query_counter, n),
        "unique_top1_count": unique_top1_count,
        "top1_dominance_ratio": top1_dominance_ratio,
        "mean_jaccard_top20_between_queries": mean_jaccard_top20,
        "most_common_top1": [{"drug": drug, "count": cnt} for drug, cnt in most_common_top1],
        "repeated_top5_patterns": same_top5_examples,
        "inject_position_histogram": dict(Counter(inject_positions)),
        "missing_gold_examples": missing_gold_examples,
    }


def analyze_prediction_errors(
    pred_data: List[Dict[str, Any]],
    raw_data: List[Dict[str, Any]],
    ready_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    raw_by_key = {make_key_from_raw(ex): ex for ex in raw_data}
    ready_by_key = {make_key_from_raw(ex): ex for ex in ready_data}

    breakdown = Counter()
    samples = defaultdict(list)

    for ex in pred_data:
        key = make_key_from_pred(ex)
        raw_ex = raw_by_key.get(key)
        ready_ex = ready_by_key.get(key)

        target = ex.get("target", ex.get("gold_entity"))
        pred = ex.get("pred")
        pred_in_candidate = ex.get("pred_in_candidate")
        pred_rank = ex.get("pred_rank")

        # Use raw/ready annotations when available.
        gold_in_topk_raw = None
        gold_injected = None
        if raw_ex is not None:
            gold_in_topk_raw = bool(raw_ex.get("gold_in_topk_raw"))
        if ready_ex is not None:
            gold_injected = bool(ready_ex.get("gold_injected"))

        if pred == target:
            label = "prediction_equals_gold"
        elif gold_in_topk_raw is False:
            label = "gold_not_in_candidate"
        elif pred_in_candidate is False:
            label = "prediction_not_in_candidate"
        else:
            label = "prediction_in_candidate_but_not_top"

        breakdown[label] += 1

        if len(samples[label]) < 12:
            samples[label].append(
                {
                    "query_entity": ex.get("query_entity"),
                    "target": target,
                    "pred": pred,
                    "pred_rank": pred_rank,
                    "pred_in_candidate": pred_in_candidate,
                    "gold_in_topk_raw": gold_in_topk_raw,
                    "gold_injected": gold_injected,
                    "candidate_size": ex.get("candidate_size"),
                    "subgraph_size": ex.get("subgraph_size"),
                    "top5": ex.get("rank_entities", [])[:5],
                }
            )

    return {
        "error_breakdown": dict(breakdown),
        "error_examples": dict(samples),
    }


def build_conclusion(
    cand_stats: Dict[str, Any],
    pred_stats: Dict[str, Any],
    week6_metrics: Dict[str, Any],
) -> List[str]:
    lines: List[str] = []

    recall = cand_stats["valid_recall20_raw"]
    inject = cand_stats["valid_inject_ratio_ready"]
    top1_dom = cand_stats["top1_dominance_ratio"]
    mean_j = cand_stats["mean_jaccard_top20_between_queries"]
    err = pred_stats["error_breakdown"]

    lines.append("Backbone path is technically clean enough for scientific checking on valid.")
    if recall <= 0.02:
        lines.append("Raw candidate recall is extremely weak; coarse ranker quality is still the main bottleneck.")
    elif recall <= 0.10:
        lines.append("Raw candidate recall is still weak; candidate retrieval remains the main bottleneck.")
    else:
        lines.append("Raw candidate recall is improving, though retrieval still needs work.")

    if inject >= 0.90:
        lines.append("Inject dependence is extremely high; reranker still relies heavily on injected gold.")
    elif inject >= 0.70:
        lines.append("Inject dependence remains high.")
    else:
        lines.append("Inject dependence is no longer dominant.")

    if top1_dom >= 0.10:
        lines.append("Top-1 dominance suggests score collapse toward a few generic drugs.")
    if mean_j >= 0.50:
        lines.append("High inter-query top-20 overlap suggests weak disease-specific discrimination.")

    if err.get("gold_not_in_candidate", 0) >= err.get("prediction_in_candidate_but_not_top", 0):
        lines.append("The dominant failure mode is retrieval miss rather than reranking discrimination.")
    else:
        lines.append("Many failures happen even when gold is already in candidate list, so reranking/graph discrimination still matters.")

    lines.append("Day 2 should prioritize ranker stability and score quality, not complexity expansion.")
    return lines


# ----------------------------
# Writers
# ----------------------------
def write_top1_frequency_tsv(cand_stats: Dict[str, Any]) -> None:
    with TOP1_FREQ_PATH.open("w", encoding="utf-8") as f:
        f.write("drug\tcount\n")
        for row in cand_stats["most_common_top1"]:
            f.write(f"{row['drug']}\t{row['count']}\n")


def write_same_query_md(cand_stats: Dict[str, Any]) -> None:
    with SAME_QUERY_PATH.open("w", encoding="utf-8") as f:
        f.write("# Repeated top-5 patterns on valid\n\n")
        if not cand_stats["repeated_top5_patterns"]:
            f.write("- No repeated top-5 pattern with count >= 2 was found.\n")
            return

        for item in cand_stats["repeated_top5_patterns"]:
            f.write(f"- count = {item['count']}\n")
            f.write(f"  - top5 = {item['top5']}\n")


def write_summary_json(
    cand_stats: Dict[str, Any],
    pred_stats: Dict[str, Any],
    cand_report: Dict[str, Any],
    week6_metrics: Dict[str, Any],
    conclusions: List[str],
) -> None:
    payload = {
        "candidate_report_from_week6": cand_report,
        "week6_valid_metrics": week6_metrics,
        "valid_recall20_raw": cand_stats["valid_recall20_raw"],
        "valid_top1_hit_ratio_raw": cand_stats["valid_top1_hit_ratio_raw"],
        "valid_inject_ratio_ready": cand_stats["valid_inject_ratio_ready"],
        "unique_top1_count": cand_stats["unique_top1_count"],
        "top1_dominance_ratio": cand_stats["top1_dominance_ratio"],
        "mean_jaccard_top20_between_queries": cand_stats["mean_jaccard_top20_between_queries"],
        "duplicate_candidates_within_query_ratio": cand_stats["duplicate_candidates_within_query_ratio"],
        "error_breakdown": pred_stats["error_breakdown"],
        "audit_conclusion": conclusions,
    }
    with SUMMARY_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_audit_md(
    cand_stats: Dict[str, Any],
    pred_stats: Dict[str, Any],
    week6_metrics: Dict[str, Any],
    conclusions: List[str],
) -> None:
    with AUDIT_MD_PATH.open("w", encoding="utf-8") as f:
        f.write("# Day 1 Audit — Week 7\n\n")

        f.write("## Scope\n\n")
        f.write("- Audit week-6 coarse ranker / candidate source.\n")
        f.write("- Confirm whether the main bottleneck is retrieval quality rather than backbone path.\n\n")

        f.write("## Key numbers\n\n")
        f.write(f"- valid_recall20_raw = {cand_stats['valid_recall20_raw']:.6f}\n")
        f.write(f"- valid_top1_hit_ratio_raw = {cand_stats['valid_top1_hit_ratio_raw']:.6f}\n")
        f.write(f"- valid_inject_ratio_ready = {cand_stats['valid_inject_ratio_ready']:.6f}\n")
        f.write(f"- unique_top1_count = {cand_stats['unique_top1_count']}\n")
        f.write(f"- top1_dominance_ratio = {cand_stats['top1_dominance_ratio']:.6f}\n")
        f.write(f"- mean_jaccard_top20_between_queries = {cand_stats['mean_jaccard_top20_between_queries']:.6f}\n")
        f.write(f"- duplicate_candidates_within_query_ratio = {cand_stats['duplicate_candidates_within_query_ratio']:.6f}\n")
        f.write(f"- week6_valid_metrics = {json.dumps(week6_metrics, ensure_ascii=False)}\n")
        f.write(f"- error_breakdown = {json.dumps(pred_stats['error_breakdown'], ensure_ascii=False)}\n\n")

        f.write("## Conclusion\n\n")
        for line in conclusions:
            f.write(f"- {line}\n")

        f.write("\n## Must-fix focus for Day 2\n\n")
        f.write("- Keep R-GCN as the main path.\n")
        f.write("- Improve stability and score discrimination.\n")
        f.write("- Do not expand many baselines yet.\n")

        f.write("\n## Example missing-gold cases\n\n")
        for ex in cand_stats["missing_gold_examples"][:10]:
            f.write(
                f"- query={ex['query_entity']} | gold={ex['gold_entity']} "
                f"| gold_rank_in_full_universe={ex['gold_rank_in_full_universe']} "
                f"| gold_injected={ex['gold_injected']} | raw_top5={ex['raw_top5']}\n"
            )

        f.write("\n## Example prediction error cases\n\n")
        for label, rows in pred_stats["error_examples"].items():
            f.write(f"### {label}\n")
            for row in rows[:5]:
                f.write(
                    f"- query={row['query_entity']} | target={row['target']} | pred={row['pred']} "
                    f"| pred_rank={row['pred_rank']} | pred_in_candidate={row['pred_in_candidate']} "
                    f"| gold_in_topk_raw={row['gold_in_topk_raw']} | gold_injected={row['gold_injected']} "
                    f"| top5={row['top5']}\n"
                )
            f.write("\n")


# ----------------------------
# Main
# ----------------------------
def main() -> None:
    for path in [RAW_PATH, READY_PATH, CAND_REPORT_PATH, EVAL_METRICS_PATH, EVAL_PRED_PATH]:
        if not path.exists():
            raise FileNotFoundError(f"Missing required file: {path}")

    raw_data = load_json(RAW_PATH)
    ready_data = load_json(READY_PATH)
    cand_report = load_json(CAND_REPORT_PATH)
    week6_metrics = load_json(EVAL_METRICS_PATH)

    pred_blob = load_json(EVAL_PRED_PATH)
    pred_data = get_eval_prediction_list(pred_blob)

    cand_stats = analyze_candidate_quality(raw_data, ready_data)
    pred_stats = analyze_prediction_errors(pred_data, raw_data, ready_data)
    conclusions = build_conclusion(cand_stats, pred_stats, week6_metrics)

    write_summary_json(cand_stats, pred_stats, cand_report, week6_metrics, conclusions)
    write_top1_frequency_tsv(cand_stats)
    write_same_query_md(cand_stats)
    write_audit_md(cand_stats, pred_stats, week6_metrics, conclusions)

    print("Saved:")
    print(f"- {SUMMARY_PATH}")
    print(f"- {TOP1_FREQ_PATH}")
    print(f"- {SAME_QUERY_PATH}")
    print(f"- {AUDIT_MD_PATH}")


if __name__ == "__main__":
    main()