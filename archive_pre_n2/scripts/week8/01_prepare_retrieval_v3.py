#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Tuple

import torch
import yaml


# ============================================================
# Config
# ============================================================

@dataclass
class PrepConfig:
    seed: int
    train_scores_path: str
    valid_scores_path: str
    train_top20_raw_json: str
    valid_top20_raw_json: str
    week7_candidate_report_path: str
    week7_8b_valid_report_path: str
    output_dir: str
    report_dir: str
    collapse_topn: int
    bias_topn: int
    hard_pool_size: int
    raw_topk_keep: int
    collapse_keep: int
    bias_keep: int


# ============================================================
# IO utils
# ============================================================

def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def zscore(values: List[float]) -> List[float]:
    if not values:
        return []
    mu = sum(values) / len(values)
    var = sum((x - mu) ** 2 for x in values) / max(1, len(values))
    std = math.sqrt(var)
    if std == 0:
        return [0.0 for _ in values]
    return [(x - mu) / std for x in values]


def safe_ratio(a: float, b: float) -> float:
    return float(a) / float(b) if b else 0.0


# ============================================================
# Core
# ============================================================

def build_id_name_maps(score_dump: Dict[str, Any]) -> Tuple[List[int], List[str], Dict[int, str], Dict[str, int]]:
    ids = score_dump["candidate_universe_entity_ids"].tolist()
    names = score_dump["candidate_universe_entity_names"]
    id_to_name = {int(i): n for i, n in zip(ids, names)}
    name_to_id = {n: int(i) for i, n in zip(ids, names)}
    return ids, names, id_to_name, name_to_id


def compute_top1_counter(raw_rows: List[Dict[str, Any]]) -> Counter:
    c = Counter()
    for row in raw_rows:
        if row["candidate_entities"]:
            c[row["candidate_entities"][0]] += 1
    return c


def build_bias_table(
    train_dump: Dict[str, Any],
    train_raw: List[Dict[str, Any]],
    valid_raw: List[Dict[str, Any]],
    collapse_topn: int,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    candidate_ids, candidate_names, id_to_name, name_to_id = build_id_name_maps(train_dump)

    train_scores: torch.Tensor = train_dump["scores"].to(torch.float32)  # [Nq, Nc]
    train_gold_ids = train_dump["gold_entity_ids"].tolist()

    train_gold_counter = Counter(train_gold_ids)
    top1_train_counter = compute_top1_counter(train_raw)
    top1_valid_counter = compute_top1_counter(valid_raw)

    mean_scores = train_scores.mean(dim=0).tolist()
    std_scores = train_scores.std(dim=0).tolist()

    gold_freq_values = [train_gold_counter.get(int(drug_id), 0) for drug_id in candidate_ids]
    top1_train_values = [top1_train_counter.get(id_to_name[int(drug_id)], 0) for drug_id in candidate_ids]
    top1_valid_values = [top1_valid_counter.get(id_to_name[int(drug_id)], 0) for drug_id in candidate_ids]

    z_mean_score = zscore(mean_scores)
    z_gold_freq = zscore([float(x) for x in gold_freq_values])
    z_top1_train = zscore([float(x) for x in top1_train_values])
    z_top1_valid = zscore([float(x) for x in top1_valid_values])

    table = []
    for idx, drug_id in enumerate(candidate_ids):
        drug_name = id_to_name[int(drug_id)]

        # collapse score emphasizes "predicted too often as top1"
        collapse_score = (
            1.5 * z_top1_train[idx]
            + 1.0 * z_top1_valid[idx]
            + 0.75 * z_mean_score[idx]
            + 0.25 * z_gold_freq[idx]
        )

        table.append({
            "drug_id": int(drug_id),
            "drug_name": drug_name,
            "train_gold_freq": int(gold_freq_values[idx]),
            "train_gold_ratio": round(safe_ratio(gold_freq_values[idx], len(train_gold_ids)), 8),
            "train_top1_count_raw": int(top1_train_values[idx]),
            "train_top1_ratio_raw": round(safe_ratio(top1_train_values[idx], len(train_raw)), 8),
            "valid_top1_count_raw": int(top1_valid_values[idx]),
            "valid_top1_ratio_raw": round(safe_ratio(top1_valid_values[idx], len(valid_raw)), 8),
            "mean_score_train": round(float(mean_scores[idx]), 8),
            "std_score_train": round(float(std_scores[idx]), 8),
            "collapse_score": round(float(collapse_score), 8),
        })

    # collapse drugs: top by collapse score
    collapse_sorted = sorted(
        table,
        key=lambda x: (
            -x["collapse_score"],
            -x["train_top1_count_raw"],
            -x["valid_top1_count_raw"],
            -x["mean_score_train"],
            x["drug_name"],
        )
    )
    collapse_drugs = collapse_sorted[:collapse_topn]

    summary = {
        "num_drugs_in_universe": len(candidate_ids),
        "top10_train_top1_raw": top1_train_counter.most_common(10),
        "top10_valid_top1_raw": top1_valid_counter.most_common(10),
        "collapse_topn": collapse_topn,
        "collapse_drugs": collapse_drugs,
    }
    return table, collapse_drugs, summary


def build_hard_negative_pools(
    rows: List[Dict[str, Any]],
    bias_table_sorted: List[Dict[str, Any]],
    collapse_drugs: List[Dict[str, Any]],
    hard_pool_size: int,
    raw_topk_keep: int,
    collapse_keep: int,
    bias_keep: int,
) -> List[Dict[str, Any]]:
    collapse_ids = [x["drug_id"] for x in collapse_drugs[:collapse_keep]]
    collapse_names = {x["drug_id"]: x["drug_name"] for x in collapse_drugs[:collapse_keep]}

    bias_ids = [x["drug_id"] for x in bias_table_sorted[:bias_keep]]
    bias_names = {x["drug_id"]: x["drug_name"] for x in bias_table_sorted[:bias_keep]}

    pools = []

    for row in rows:
        gold_id = int(row["gold_entity_id"])
        query_id = int(row["query_entity_id"])

        seen = set()
        hard_ids: List[int] = []
        hard_names: List[str] = []

        # part A: keep top raw candidates except gold
        for cid, cname in zip(row["candidate_entity_ids"][:raw_topk_keep], row["candidate_entities"][:raw_topk_keep]):
            cid = int(cid)
            if cid == gold_id or cid in seen:
                continue
            seen.add(cid)
            hard_ids.append(cid)
            hard_names.append(cname)

        # part B: add collapse drugs
        for cid in collapse_ids:
            if cid == gold_id or cid in seen:
                continue
            seen.add(cid)
            hard_ids.append(cid)
            hard_names.append(collapse_names[cid])

        # part C: add bias-heavy drugs
        for cid in bias_ids:
            if cid == gold_id or cid in seen:
                continue
            seen.add(cid)
            hard_ids.append(cid)
            hard_names.append(bias_names[cid])

        # cap size
        hard_ids = hard_ids[:hard_pool_size]
        hard_names = hard_names[:hard_pool_size]

        pools.append({
            "query_entity": row["query_entity"],
            "query_entity_id": query_id,
            "gold_entity": row["gold_entity"],
            "gold_entity_id": gold_id,
            "hard_negative_entity_ids": hard_ids,
            "hard_negative_entities": hard_names,
            "raw_non_gold_count_used": min(raw_topk_keep, len(row["candidate_entity_ids"])) - (1 if gold_id in row["candidate_entity_ids"][:raw_topk_keep] else 0),
            "collapse_pool_size_used": sum(1 for x in hard_ids if x in set(collapse_ids)),
            "bias_pool_size_used": sum(1 for x in hard_ids if x in set(bias_ids)),
            "hard_pool_size": len(hard_ids),
        })

    return pools


def summarize_hard_pools(pools: List[Dict[str, Any]]) -> Dict[str, Any]:
    sizes = [x["hard_pool_size"] for x in pools]
    mean_size = mean(sizes) if sizes else 0.0

    # frequency of hard negatives
    neg_counter = Counter()
    for row in pools:
        for name in row["hard_negative_entities"]:
            neg_counter[name] += 1

    return {
        "num_queries": len(pools),
        "hard_pool_size_min": min(sizes) if sizes else 0,
        "hard_pool_size_max": max(sizes) if sizes else 0,
        "hard_pool_size_mean": round(float(mean_size), 4),
        "top20_hard_negative_frequency": neg_counter.most_common(20),
    }


def write_day1_markdown(
    path: Path,
    cfg: PrepConfig,
    collapse_summary: Dict[str, Any],
    hard_train_summary: Dict[str, Any],
    week7_candidate_report: Dict[str, Any] | None,
    week7_8b_report_text: str | None,
):
    lines = []
    lines.append("# Week8 / retrieval-v3 Day 1 — hard negatives + bias stats")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Prepare collapse-aware hard negatives for retrieval-v3.")
    lines.append("- Build drug bias statistics from week7 score dumps.")
    lines.append("- Confirm that retrieval, not backbone size, remains the main bottleneck.")
    lines.append("")

    if week7_candidate_report is not None:
        v = week7_candidate_report["splits"]["valid"]
        lines.append("## Current week7 retrieval context")
        lines.append("")
        lines.append(f"- valid_recall@20_raw = `{v['recall_at_k_raw']}`")
        lines.append(f"- valid_top1_hit_ratio_raw = `{v['top1_hit_ratio_raw']}`")
        lines.append(f"- valid_inject_ratio_ready = `{v['inject_ratio_ready']}`")
        lines.append(f"- valid_unique_top1_count_raw = `{v['unique_top1_count_raw']}`")
        lines.append(f"- valid_top1_dominance_ratio_raw = `{v['top1_dominance_ratio_raw']}`")
        lines.append("")

    lines.append("## Collapse drugs")
    lines.append("")
    for row in collapse_summary["collapse_drugs"][:10]:
        lines.append(
            f"- {row['drug_name']} | collapse_score={row['collapse_score']} "
            f"| train_top1={row['train_top1_count_raw']} | valid_top1={row['valid_top1_count_raw']} "
            f"| mean_score_train={row['mean_score_train']}"
        )
    lines.append("")

    lines.append("## Hard negative pool summary")
    lines.append("")
    lines.append(f"- num_queries = `{hard_train_summary['num_queries']}`")
    lines.append(f"- hard_pool_size_min = `{hard_train_summary['hard_pool_size_min']}`")
    lines.append(f"- hard_pool_size_max = `{hard_train_summary['hard_pool_size_max']}`")
    lines.append(f"- hard_pool_size_mean = `{hard_train_summary['hard_pool_size_mean']}`")
    lines.append("")
    lines.append("Top hard negatives:")
    for name, cnt in hard_train_summary["top20_hard_negative_frequency"][:10]:
        lines.append(f"- {name}: {cnt}")
    lines.append("")

    lines.append("## Conclusion")
    lines.append("")
    lines.append("- Day 2 should train retrieval-v3 with mixed negatives: raw top-k non-gold + collapse drugs + bias-heavy drugs.")
    lines.append("- If retrieval-v3 still collapses after this, it becomes reasonable to stop refinement and use the current results.")
    lines.append("")

    if week7_8b_report_text:
        lines.append("## Note")
        lines.append("")
        lines.append("- 8B only improved very slightly over week7 3B, so this refinement focuses on retrieval quality rather than LLM capacity.")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to configs/week8/retrieval_v3_day1.yaml")
    args = parser.parse_args()

    cfg = PrepConfig(**load_yaml(Path(args.config)))
    random.seed(cfg.seed)

    output_dir = Path(cfg.output_dir)
    report_dir = Path(cfg.report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    train_dump = torch.load(cfg.train_scores_path, map_location="cpu")
    valid_dump = torch.load(cfg.valid_scores_path, map_location="cpu")

    train_raw = load_json(Path(cfg.train_top20_raw_json))
    valid_raw = load_json(Path(cfg.valid_top20_raw_json))

    # Build bias/collapse table
    bias_table, collapse_drugs, collapse_summary = build_bias_table(
        train_dump=train_dump,
        train_raw=train_raw,
        valid_raw=valid_raw,
        collapse_topn=cfg.collapse_topn,
    )

    # bias table sorted
    bias_table_sorted = sorted(
        bias_table,
        key=lambda x: (
            -x["collapse_score"],
            -x["train_top1_count_raw"],
            -x["valid_top1_count_raw"],
            -x["mean_score_train"],
            x["drug_name"],
        )
    )

    # Hard pools
    train_pools = build_hard_negative_pools(
        rows=train_raw,
        bias_table_sorted=bias_table_sorted[:cfg.bias_topn],
        collapse_drugs=collapse_drugs,
        hard_pool_size=cfg.hard_pool_size,
        raw_topk_keep=cfg.raw_topk_keep,
        collapse_keep=cfg.collapse_keep,
        bias_keep=cfg.bias_keep,
    )
    valid_probe_pools = build_hard_negative_pools(
        rows=valid_raw,
        bias_table_sorted=bias_table_sorted[:cfg.bias_topn],
        collapse_drugs=collapse_drugs,
        hard_pool_size=cfg.hard_pool_size,
        raw_topk_keep=cfg.raw_topk_keep,
        collapse_keep=cfg.collapse_keep,
        bias_keep=cfg.bias_keep,
    )

    hard_train_summary = summarize_hard_pools(train_pools)
    hard_valid_summary = summarize_hard_pools(valid_probe_pools)

    # Optional context
    week7_candidate_report = None
    if Path(cfg.week7_candidate_report_path).exists():
        week7_candidate_report = load_json(Path(cfg.week7_candidate_report_path))

    week7_8b_report_text = None
    if Path(cfg.week7_8b_valid_report_path).exists():
        week7_8b_report_text = Path(cfg.week7_8b_valid_report_path).read_text(encoding="utf-8")

    # Save outputs
    save_json(output_dir / "drug_bias_stats.json", {
        "config": asdict(cfg),
        "num_drugs": len(bias_table_sorted),
        "bias_table_sorted": bias_table_sorted,
    })

    save_json(output_dir / "train_hard_negative_pools.json", {
        "config": asdict(cfg),
        "split": "train",
        "summary": hard_train_summary,
        "rows": train_pools,
    })

    save_json(output_dir / "valid_hard_negative_probe.json", {
        "config": asdict(cfg),
        "split": "valid",
        "summary": hard_valid_summary,
        "rows": valid_probe_pools,
    })

    with (output_dir / "collapse_drug_list.txt").open("w", encoding="utf-8") as f:
        for row in collapse_drugs:
            f.write(
                f"{row['drug_id']}\t{row['drug_name']}\t"
                f"collapse_score={row['collapse_score']}\t"
                f"train_top1={row['train_top1_count_raw']}\t"
                f"valid_top1={row['valid_top1_count_raw']}\t"
                f"mean_score_train={row['mean_score_train']}\n"
            )

    collapse_summary_payload = {
        "config": asdict(cfg),
        "collapse_summary": collapse_summary,
        "train_hard_negative_summary": hard_train_summary,
        "valid_hard_negative_summary": hard_valid_summary,
        "important_note": "These artifacts are intended for retrieval-v3 training with collapse-aware hard negatives and optional score debiasing.",
    }
    save_json(output_dir / "collapse_summary.json", collapse_summary_payload)

    write_day1_markdown(
        path=report_dir / "day1_retrieval_v3_prep.md",
        cfg=cfg,
        collapse_summary=collapse_summary,
        hard_train_summary=hard_train_summary,
        week7_candidate_report=week7_candidate_report,
        week7_8b_report_text=week7_8b_report_text,
    )

    print("Saved:")
    print("-", output_dir / "collapse_summary.json")
    print("-", output_dir / "collapse_drug_list.txt")
    print("-", output_dir / "drug_bias_stats.json")
    print("-", output_dir / "train_hard_negative_pools.json")
    print("-", output_dir / "valid_hard_negative_probe.json")
    print("-", report_dir / "day1_retrieval_v3_prep.md")


if __name__ == "__main__":
    main()