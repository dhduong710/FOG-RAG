#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import Counter
from typing import Any, Dict, List, Tuple

import torch
import yaml


# ============================================================
# Config
# ============================================================

@dataclass
class DebiasConfig:
    seed: int
    train_scores_path: str
    valid_scores_path: str
    test_scores_path: str
    drug_bias_stats_path: str
    week7_candidate_report_path: str
    output_dir: str
    report_dir: str
    bias_field: str
    bias_normalization: str
    lambdas: List[float]
    recall_drop_tolerance: float
    min_top1_dominance_improve: float
    min_unique_top1_gain: int
    apply_best_to_all_splits: bool
    k: int


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


def write_tsv(path: Path, rows: List[Dict[str, Any]], columns: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("\t".join(columns) + "\n")
        for row in rows:
            vals = []
            for c in columns:
                v = row.get(c, "")
                if isinstance(v, list):
                    v = " | ".join(str(x) for x in v)
                vals.append(str(v))
            f.write("\t".join(vals) + "\n")


# ============================================================
# Bias helpers
# ============================================================

def normalize_bias(values: List[float], mode: str) -> List[float]:
    if not values:
        return []

    if mode == "minmax":
        lo = min(values)
        hi = max(values)
        if hi == lo:
            return [0.0 for _ in values]
        return [(x - lo) / (hi - lo) for x in values]

    if mode == "zscore":
        mu = sum(values) / len(values)
        var = sum((x - mu) ** 2 for x in values) / max(1, len(values))
        std = math.sqrt(var)
        if std == 0.0:
            return [0.0 for _ in values]
        return [(x - mu) / std for x in values]

    raise ValueError(f"Unsupported bias_normalization: {mode}")


def build_bias_tensor(
    score_dump: Dict[str, Any],
    drug_bias_stats: Dict[str, Any],
    bias_field: str,
    bias_normalization: str,
) -> Tuple[torch.Tensor, Dict[int, float]]:
    candidate_ids = score_dump["candidate_universe_entity_ids"].tolist()

    bias_table = drug_bias_stats["bias_table_sorted"]
    raw_map = {}
    for row in bias_table:
        if bias_field not in row:
            raise KeyError(f"bias_field '{bias_field}' not found in bias table row.")
        raw_map[int(row["drug_id"])] = float(row[bias_field])

    raw_values = [raw_map.get(int(drug_id), 0.0) for drug_id in candidate_ids]
    norm_values = normalize_bias(raw_values, bias_normalization)

    bias_map = {int(drug_id): float(v) for drug_id, v in zip(candidate_ids, norm_values)}
    bias_tensor = torch.tensor(norm_values, dtype=torch.float32)
    return bias_tensor, bias_map


# ============================================================
# Candidate building
# ============================================================

def build_raw_and_ready_for_dump(
    dump: Dict[str, Any],
    scores: torch.Tensor,
    split_name: str,
    k: int,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
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
            raise ValueError(f"Gold drug id {gold_id} not in candidate universe.")

        gold_score = float(row_scores[universe_index[gold_id]].item())

        topk_scores, topk_idx = torch.topk(row_scores, k=k, largest=True, sorted=True)
        topk_idx_list = topk_idx.tolist()
        raw_candidate_ids = [candidate_universe_ids[j] for j in topk_idx_list]
        raw_candidate_names = [candidate_universe_names[j] for j in topk_idx_list]

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


# ============================================================
# Sweep logic
# ============================================================

def choose_best_lambda(
    sweep_rows: List[Dict[str, Any]],
    baseline: Dict[str, Any],
    recall_drop_tolerance: float,
    min_top1_dominance_improve: float,
    min_unique_top1_gain: int,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    accepted = []

    base_recall = baseline["recall_at_k_raw"]
    base_dom = baseline["top1_dominance_ratio_raw"]
    base_unique = baseline["unique_top1_count_raw"]

    for row in sweep_rows:
        lam = row["lambda"]
        if lam == 0.0:
            continue

        recall_ok = row["recall_at_k_raw"] >= (base_recall - recall_drop_tolerance)
        collapse_ok = (
            row["top1_dominance_ratio_raw"] <= (base_dom - min_top1_dominance_improve)
            or row["unique_top1_count_raw"] >= (base_unique + min_unique_top1_gain)
        )

        if recall_ok and collapse_ok:
            accepted.append(row)

    if accepted:
        accepted = sorted(
            accepted,
            key=lambda x: (
                -x["recall_at_k_raw"],
                x["top1_dominance_ratio_raw"],
                -x["unique_top1_count_raw"],
                -x["top1_hit_ratio_raw"],
                x["lambda"],
            ),
        )
        return accepted[0], accepted

    # fallback: choose best tradeoff, but mark it as not accepted
    ranked = sorted(
        sweep_rows,
        key=lambda x: (
            -(100.0 * x["recall_at_k_raw"]
              - 8.0 * x["top1_dominance_ratio_raw"]
              + 0.25 * x["unique_top1_count_raw"]
              + 1.0 * x["top1_hit_ratio_raw"]
              - 1.0 * x["inject_ratio_ready"]),
            x["lambda"],
        ),
    )
    return ranked[0], accepted


def write_markdown_report(
    path: Path,
    cfg: DebiasConfig,
    baseline: Dict[str, Any],
    best_row: Dict[str, Any],
    accepted_rows: List[Dict[str, Any]],
    sweep_rows: List[Dict[str, Any]],
    accepted_flag: bool,
):
    lines = []
    lines.append("# Week8 — post-hoc debias sweep on week7-v2")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Sweep lambda on valid using post-hoc score debias.")
    lines.append("- Keep week7-v2 scores fixed and only penalize globally collapse-prone drugs.")
    lines.append("- Check whether recall can be preserved while collapse decreases.")
    lines.append("")

    lines.append("## Baseline (lambda = 0)")
    lines.append("")
    lines.append(f"- recall@20_raw = `{baseline['recall_at_k_raw']}`")
    lines.append(f"- top1_hit_ratio_raw = `{baseline['top1_hit_ratio_raw']}`")
    lines.append(f"- inject_ratio_ready = `{baseline['inject_ratio_ready']}`")
    lines.append(f"- unique_top1_count_raw = `{baseline['unique_top1_count_raw']}`")
    lines.append(f"- top1_dominance_ratio_raw = `{baseline['top1_dominance_ratio_raw']}`")
    lines.append("")

    lines.append("## Best lambda")
    lines.append("")
    lines.append(f"- lambda = `{best_row['lambda']}`")
    lines.append(f"- accepted_under_rule = `{accepted_flag}`")
    lines.append(f"- recall@20_raw = `{best_row['recall_at_k_raw']}`")
    lines.append(f"- top1_hit_ratio_raw = `{best_row['top1_hit_ratio_raw']}`")
    lines.append(f"- inject_ratio_ready = `{best_row['inject_ratio_ready']}`")
    lines.append(f"- unique_top1_count_raw = `{best_row['unique_top1_count_raw']}`")
    lines.append(f"- top1_dominance_ratio_raw = `{best_row['top1_dominance_ratio_raw']}`")
    lines.append("")
    lines.append(f"- delta_recall@20_raw = `{round(best_row['recall_at_k_raw'] - baseline['recall_at_k_raw'], 6)}`")
    lines.append(f"- delta_top1_hit_ratio_raw = `{round(best_row['top1_hit_ratio_raw'] - baseline['top1_hit_ratio_raw'], 6)}`")
    lines.append(f"- delta_inject_ratio_ready = `{round(best_row['inject_ratio_ready'] - baseline['inject_ratio_ready'], 6)}`")
    lines.append(f"- delta_unique_top1_count_raw = `{best_row['unique_top1_count_raw'] - baseline['unique_top1_count_raw']}`")
    lines.append(f"- delta_top1_dominance_ratio_raw = `{round(best_row['top1_dominance_ratio_raw'] - baseline['top1_dominance_ratio_raw'], 6)}`")
    lines.append("")

    lines.append("## Acceptance rule")
    lines.append("")
    lines.append(f"- recall_drop_tolerance = `{cfg.recall_drop_tolerance}`")
    lines.append(f"- min_top1_dominance_improve = `{cfg.min_top1_dominance_improve}`")
    lines.append(f"- min_unique_top1_gain = `{cfg.min_unique_top1_gain}`")
    lines.append(f"- num_accepted_lambdas = `{len(accepted_rows)}`")
    lines.append("")

    lines.append("## Sweep overview")
    lines.append("")
    for row in sweep_rows:
        lines.append(
            f"- lambda={row['lambda']} | recall@20={row['recall_at_k_raw']} | "
            f"top1_hit={row['top1_hit_ratio_raw']} | inject={row['inject_ratio_ready']} | "
            f"unique_top1={row['unique_top1_count_raw']} | dom={row['top1_dominance_ratio_raw']}"
        )
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("- If an accepted lambda exists, this is the last cheap improvement worth keeping before stopping refinement.")
    lines.append("- If no accepted lambda exists, keep week7-v2 as the main retrieval result and stop further refinement.")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to configs/week8/posthoc_debias_sweep.yaml")
    args = parser.parse_args()

    cfg = DebiasConfig(**load_yaml(Path(args.config)))
    random.seed(cfg.seed)

    output_dir = Path(cfg.output_dir)
    report_dir = Path(cfg.report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    train_dump = torch.load(cfg.train_scores_path, map_location="cpu")
    valid_dump = torch.load(cfg.valid_scores_path, map_location="cpu")
    test_dump = torch.load(cfg.test_scores_path, map_location="cpu")

    week7_candidate_report = load_json(Path(cfg.week7_candidate_report_path))
    baseline_from_report = week7_candidate_report["splits"]["valid"]

    drug_bias_stats = load_json(Path(cfg.drug_bias_stats_path))
    valid_bias_tensor, valid_bias_map = build_bias_tensor(
        score_dump=valid_dump,
        drug_bias_stats=drug_bias_stats,
        bias_field=cfg.bias_field,
        bias_normalization=cfg.bias_normalization,
    )

    valid_scores = valid_dump["scores"].to(torch.float32)
    sweep_rows = []
    all_valid_outputs = {}

    for lam in cfg.lambdas:
        debiased_scores = valid_scores - float(lam) * valid_bias_tensor.unsqueeze(0)

        raw_rows, ready_rows, split_report = build_raw_and_ready_for_dump(
            dump=valid_dump,
            scores=debiased_scores,
            split_name="valid",
            k=cfg.k,
        )
        row = {"lambda": float(lam), **split_report}
        sweep_rows.append(row)
        all_valid_outputs[str(lam)] = {
            "valid_top20_raw": raw_rows,
            "valid_top20_drkgc_ready": ready_rows,
            "valid_report": split_report,
        }

    # baseline row must be lambda 0
    baseline_candidates = [x for x in sweep_rows if float(x["lambda"]) == 0.0]
    if not baseline_candidates:
        raise RuntimeError("No lambda=0.0 row found in sweep.")
    baseline = baseline_candidates[0]

    best_row, accepted_rows = choose_best_lambda(
        sweep_rows=sweep_rows,
        baseline=baseline,
        recall_drop_tolerance=cfg.recall_drop_tolerance,
        min_top1_dominance_improve=cfg.min_top1_dominance_improve,
        min_unique_top1_gain=cfg.min_unique_top1_gain,
    )
    accepted_flag = len(accepted_rows) > 0 and best_row in accepted_rows

    # save sweep summary
    save_json(output_dir / "valid_debias_sweep_results.json", {
        "config": asdict(cfg),
        "baseline_from_candidate_report": baseline_from_report,
        "baseline_from_sweep": baseline,
        "accepted_rows": accepted_rows,
        "best_row": best_row,
        "all_rows": sweep_rows,
    })

    # save valid raw/ready for all lambdas
    for lam_str, payload in all_valid_outputs.items():
        lam_dir = output_dir / "valid_by_lambda" / f"lambda_{lam_str}"
        save_json(lam_dir / "valid_top20_raw.json", payload["valid_top20_raw"])
        save_json(lam_dir / "valid_top20_drkgc_ready.json", payload["valid_top20_drkgc_ready"])
        save_json(lam_dir / "valid_report.json", payload["valid_report"])

    # apply best lambda to all splits if asked
    if cfg.apply_best_to_all_splits:
        best_lambda = float(best_row["lambda"])

        train_bias_tensor, _ = build_bias_tensor(
            score_dump=train_dump,
            drug_bias_stats=drug_bias_stats,
            bias_field=cfg.bias_field,
            bias_normalization=cfg.bias_normalization,
        )
        test_bias_tensor, _ = build_bias_tensor(
            score_dump=test_dump,
            drug_bias_stats=drug_bias_stats,
            bias_field=cfg.bias_field,
            bias_normalization=cfg.bias_normalization,
        )

        train_scores = train_dump["scores"].to(torch.float32) - best_lambda * train_bias_tensor.unsqueeze(0)
        valid_scores_best = valid_scores - best_lambda * valid_bias_tensor.unsqueeze(0)
        test_scores = test_dump["scores"].to(torch.float32) - best_lambda * test_bias_tensor.unsqueeze(0)

        train_raw, train_ready, train_report = build_raw_and_ready_for_dump(train_dump, train_scores, "train", cfg.k)
        valid_raw, valid_ready, valid_report = build_raw_and_ready_for_dump(valid_dump, valid_scores_best, "valid", cfg.k)
        test_raw, test_ready, test_report = build_raw_and_ready_for_dump(test_dump, test_scores, "test", cfg.k)

        best_dir = output_dir / "best_lambda_artifacts"
        save_json(best_dir / "train_top20_raw.json", train_raw)
        save_json(best_dir / "valid_top20_raw.json", valid_raw)
        save_json(best_dir / "test_top20_raw.json", test_raw)
        save_json(best_dir / "train_top20_drkgc_ready.json", train_ready)
        save_json(best_dir / "valid_top20_drkgc_ready.json", valid_ready)
        save_json(best_dir / "test_top20_drkgc_ready.json", test_ready)

        candidate_report = {
            "week": 8,
            "stage": "posthoc_debias",
            "goal": "Apply best valid lambda from post-hoc debias sweep to all splits.",
            "config": asdict(cfg),
            "best_lambda": best_lambda,
            "accepted_under_rule": accepted_flag,
            "splits": {
                "train": train_report,
                "valid": valid_report,
                "test": test_report,
            },
            "important_note": "This is a post-hoc debias adjustment on week7-v2 scores, not a retrained ranker.",
        }
        save_json(best_dir / "candidate_report.json", candidate_report)

        # top changed valid cases vs baseline
        baseline_valid_rows = all_valid_outputs["0.0"]["valid_top20_raw"]
        best_valid_rows = valid_raw

        base_map = {(int(x["query_entity_id"]), int(x["gold_entity_id"])): x for x in baseline_valid_rows}
        best_map = {(int(x["query_entity_id"]), int(x["gold_entity_id"])): x for x in best_valid_rows}

        changed_rows = []
        for k in sorted(set(base_map) & set(best_map)):
            a = base_map[k]
            b = best_map[k]
            delta_rank = int(a["gold_rank_in_full_universe"]) - int(b["gold_rank_in_full_universe"])
            changed_rows.append({
                "query_entity": a["query_entity"],
                "gold_entity": a["gold_entity"],
                "baseline_gold_rank_in_full_universe": a["gold_rank_in_full_universe"],
                "best_gold_rank_in_full_universe": b["gold_rank_in_full_universe"],
                "delta_rank": delta_rank,
                "baseline_gold_in_top20_raw": a["gold_in_topk_raw"],
                "best_gold_in_top20_raw": b["gold_in_topk_raw"],
                "baseline_top5": a["candidate_entities"][:5],
                "best_top5": b["candidate_entities"][:5],
            })

        changed_rows = sorted(changed_rows, key=lambda x: (-x["delta_rank"], x["best_gold_rank_in_full_universe"]))
        write_tsv(
            best_dir / "valid_changed_cases.tsv",
            changed_rows[:100],
            [
                "query_entity",
                "gold_entity",
                "baseline_gold_rank_in_full_universe",
                "best_gold_rank_in_full_universe",
                "delta_rank",
                "baseline_gold_in_top20_raw",
                "best_gold_in_top20_raw",
                "baseline_top5",
                "best_top5",
            ],
        )

    write_markdown_report(
        path=report_dir / "day3_posthoc_debias_sweep.md",
        cfg=cfg,
        baseline=baseline,
        best_row=best_row,
        accepted_rows=accepted_rows,
        sweep_rows=sweep_rows,
        accepted_flag=accepted_flag,
    )

    print("Saved:")
    print("-", output_dir / "valid_debias_sweep_results.json")
    print("-", report_dir / "day3_posthoc_debias_sweep.md")
    if cfg.apply_best_to_all_splits:
        print("-", output_dir / "best_lambda_artifacts" / "candidate_report.json")


if __name__ == "__main__":
    main()