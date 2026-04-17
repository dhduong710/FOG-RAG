#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path: str):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def detect_candidate_field(row: Dict[str, Any]) -> str:
    if "candidate_entities" in row:
        return "candidate_entities"
    if "rank_entities" in row:
        return "rank_entities"
    raise KeyError("Cannot detect candidate field.")


def detect_candidate_id_field(row: Dict[str, Any]):
    if "candidate_entity_ids" in row:
        return "candidate_entity_ids"
    if "rank_entities_id" in row:
        return "rank_entities_id"
    return None


def aligned_list_fields(row: Dict[str, Any], cand_len: int) -> List[str]:
    keep = []
    for k, v in row.items():
        if isinstance(v, list) and len(v) == cand_len:
            keep.append(k)
    return keep


def build_soft_scores(cand_len: int, contra_flags: List[int], lambda_contra: float) -> List[float]:
    # base_score follows current candidate order from ontology-supported row
    # top candidate gets base_score near 1.0, lower ranks get smaller scores
    scores = []
    denom = max(1, cand_len - 1)
    for idx, flag in enumerate(contra_flags):
        base_score = 1.0 - (idx / denom)
        soft_score = base_score - lambda_contra * float(flag)
        scores.append(soft_score)
    return scores


def reorder_row_by_lambda(row: Dict[str, Any], lambda_contra: float) -> Dict[str, Any]:
    out = dict(row)

    cand_field = detect_candidate_field(row)
    id_field = detect_candidate_id_field(row)
    candidates = row.get(cand_field, [])
    cand_len = len(candidates)

    contra_flags = row.get("contra_flags")
    if contra_flags is None:
        raise KeyError("Input row is missing contra_flags. Run day2 script first.")
    if len(contra_flags) != cand_len:
        raise ValueError("contra_flags length mismatch.")

    list_fields = aligned_list_fields(row, cand_len)
    scores = build_soft_scores(cand_len, contra_flags, lambda_contra)

    # stable sort by descending score, preserve original order on ties
    order = sorted(range(cand_len), key=lambda i: (-scores[i], i))

    for field in list_fields:
        out[field] = [row[field][i] for i in order]

    out["soft_lambda"] = lambda_contra
    out["soft_variant"] = f"soft_lambda_{lambda_contra}"
    out["soft_scores"] = [scores[i] for i in order]

    old_cands = candidates
    new_cands = out[cand_field]

    old_top1 = old_cands[0] if old_cands else None
    new_top1 = new_cands[0] if new_cands else None
    old_top5 = set(old_cands[:5])
    new_top5 = set(new_cands[:5])

    out["top1_changed"] = int(old_top1 != new_top1)
    out["top5_changed"] = int(old_top5 != new_top5)
    out["avg_candidate_size"] = cand_len

    # count contra moved downward
    old_pos = {cand: idx for idx, cand in enumerate(old_cands)}
    new_pos = {cand: idx for idx, cand in enumerate(new_cands)}
    contra_cands = row.get("contra_candidates", [])
    demoted = 0
    for c in contra_cands:
        if c in old_pos and c in new_pos and new_pos[c] > old_pos[c]:
            demoted += 1

    out["soft_demoted_contra_candidates"] = demoted
    out["contra_candidates_final"] = len(contra_cands)
    out["query_has_contra_candidate"] = int(len(contra_cands) > 0)

    gold = row.get("gold_entity")
    out["gold_in_topk_soft"] = int(gold in set(new_cands))
    if "rank" in out and isinstance(out["rank"], int) and gold in new_cands:
        out["rank"] = new_cands.index(gold) + 1

    return out


def summarize_variant(rows: List[Dict[str, Any]], lambda_contra: float) -> Dict[str, Any]:
    num_queries = len(rows)
    total_candidates = 0
    total_contra_candidates = 0
    query_has_contra = 0
    gold_in_topk = 0
    top1_changed = 0
    top5_changed = 0
    demoted_total = 0

    for r in rows:
        cand_field = detect_candidate_field(r)
        cands = r.get(cand_field, [])
        total_candidates += len(cands)
        total_contra_candidates += int(r.get("contra_candidates_final", 0))
        query_has_contra += int(r.get("query_has_contra_candidate", 0))
        gold_in_topk += int(r.get("gold_in_topk_soft", 0))
        top1_changed += int(r.get("top1_changed", 0))
        top5_changed += int(r.get("top5_changed", 0))
        demoted_total += int(r.get("soft_demoted_contra_candidates", 0))

    return {
        "lambda_contra": lambda_contra,
        "num_queries": num_queries,
        "total_candidates": total_candidates,
        "avg_candidate_size": total_candidates / num_queries if num_queries else 0.0,
        "contra_candidates_final": total_contra_candidates,
        "QueryHasContraCandidateRate": query_has_contra / num_queries if num_queries else 0.0,
        "gold_in_topk": gold_in_topk,
        "gold_in_topk_rate": gold_in_topk / num_queries if num_queries else 0.0,
        "top1_changed_queries": top1_changed,
        "top5_changed_queries": top5_changed,
        "soft_demoted_contra_candidates": demoted_total,
        "strict_empty_after_soft": 0,
        "fallback_after_soft": 0,
    }


def choose_soft_best(summary_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Heuristic:
    # 1) prefer larger demotion of contra candidates
    # 2) then prefer higher gold_in_topk_rate
    # 3) then prefer fewer top1 changes (more stable)
    ranked = sorted(
        summary_rows,
        key=lambda x: (
            -x["soft_demoted_contra_candidates"],
            -x["gold_in_topk_rate"],
            x["top1_changed_queries"],
        ),
    )
    return ranked[0]


def write_markdown_report(path: str, summaries: List[Dict[str, Any]], best_row: Dict[str, Any], sample_rows: List[Dict[str, Any]]):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# Week 10 - Day 4 Soft Penalty")
    lines.append("")
    lines.append("## Sweep summary")
    for s in summaries:
        lines.append(f"### lambda = {s['lambda_contra']}")
        lines.append(f"- num_queries: {s['num_queries']}")
        lines.append(f"- contra_candidates_final: {s['contra_candidates_final']}")
        lines.append(f"- QueryHasContraCandidateRate: {s['QueryHasContraCandidateRate']:.6f}")
        lines.append(f"- gold_in_topk_rate: {s['gold_in_topk_rate']:.6f}")
        lines.append(f"- top1_changed_queries: {s['top1_changed_queries']}")
        lines.append(f"- top5_changed_queries: {s['top5_changed_queries']}")
        lines.append(f"- soft_demoted_contra_candidates: {s['soft_demoted_contra_candidates']}")
        lines.append("")

    lines.append("## Current soft_best")
    lines.append(f"- lambda_contra: {best_row['lambda_contra']}")
    lines.append(f"- gold_in_topk_rate: {best_row['gold_in_topk_rate']:.6f}")
    lines.append(f"- soft_demoted_contra_candidates: {best_row['soft_demoted_contra_candidates']}")
    lines.append("")
    lines.append("## Sample changed rows")
    for i, r in enumerate(sample_rows[:5]):
        cand_field = detect_candidate_field(r)
        lines.append(f"### Sample {i}")
        lines.append(f"- query_entity: {r.get('query_entity')}")
        lines.append(f"- gold_entity: {r.get('gold_entity')}")
        lines.append(f"- top1_changed: {r.get('top1_changed')}")
        lines.append(f"- top5_changed: {r.get('top5_changed')}")
        lines.append(f"- contra_candidates: {r.get('contra_candidates', [])[:10]}")
        lines.append(f"- reordered_candidates: {r.get(cand_field, [])[:10]}")
        lines.append("")
    lines.append("## Notes")
    lines.append("- Day 4 keeps candidate set size fixed and only demotes contraindicated candidates.")
    lines.append("- No strict-empty behavior should be introduced by soft penalty.")
    lines.append("- Day 5 will run valid-side sanity evaluation with the backbone checkpoint.")
    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_flagged_valid",
        default="dataset/setting_a/19_contra_aware/contra_candidate_flags_valid.json",
    )
    parser.add_argument(
        "--output_dir",
        default="dataset/setting_a/19_contra_aware",
    )
    parser.add_argument(
        "--report_json",
        default="dataset/setting_a/19_contra_aware/soft_penalty_sweep_report.json",
    )
    parser.add_argument(
        "--report_md",
        default="reports/week10/day4_soft_penalty.md",
    )
    parser.add_argument(
        "--lambdas",
        nargs="+",
        type=float,
        default=[0.25, 0.5, 1.0, 2.0],
    )
    args = parser.parse_args()

    rows = load_json(args.input_flagged_valid)
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    Path("reports/week10").mkdir(parents=True, exist_ok=True)

    summaries = []
    saved_paths = []
    best_lambda_to_path = {}

    for lam in args.lambdas:
        variant_rows = [reorder_row_by_lambda(r, lam) for r in rows]
        out_path = Path(args.output_dir) / f"valid_top20_soft_lambda_{lam}.json"
        save_json(variant_rows, out_path)
        summary = summarize_variant(variant_rows, lam)
        summaries.append(summary)
        saved_paths.append(str(out_path))
        best_lambda_to_path[str(lam)] = str(out_path)

    best_row = choose_soft_best(summaries)

    # save best alias
    best_src = Path(best_lambda_to_path[str(best_row["lambda_contra"])])
    best_dst = Path(args.output_dir) / "valid_top20_soft_best.json"
    shutil.copyfile(best_src, best_dst)

    sweep_report = {
        "input": args.input_flagged_valid,
        "lambdas": args.lambdas,
        "saved_paths": saved_paths,
        "summaries": summaries,
        "best_row": best_row,
        "best_alias_path": str(best_dst),
    }
    save_json(sweep_report, args.report_json)

    # collect a few changed samples from best row
    best_rows = load_json(best_dst)
    changed_samples = [r for r in best_rows if r.get("top1_changed") == 1 or r.get("top5_changed") == 1]
    write_markdown_report(args.report_md, summaries, best_row, changed_samples)

    print(f"Saved: {args.report_json}")
    print(f"Saved: {args.report_md}")
    print(f"Saved: {best_dst}")
    print("Sweep summaries:")
    for s in summaries:
        print(s)
    print("Current soft_best =", best_row)


if __name__ == "__main__":
    main()