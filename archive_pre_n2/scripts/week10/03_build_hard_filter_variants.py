#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path):
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


def detect_candidate_id_field(row: Dict[str, Any]) -> str:
    if "candidate_entity_ids" in row:
        return "candidate_entity_ids"
    if "rank_entities_id" in row:
        return "rank_entities_id"
    return None


def row_key(row: Dict[str, Any], idx: int) -> Tuple:
    triple_id = row.get("triple_id")
    if triple_id is not None:
        return ("triple_id", tuple(triple_id))
    triple = row.get("triple")
    if triple is not None:
        return ("triple", tuple(triple))
    return ("fallback", row.get("query_entity"), row.get("gold_entity"), idx)


def build_index(rows: List[Dict[str, Any]]) -> Dict[Tuple, Dict[str, Any]]:
    out = {}
    for i, row in enumerate(rows):
        out[row_key(row, i)] = row
    return out


def subset_row(
    row: Dict[str, Any],
    keep_indices: List[int],
    variant_name: str,
    strict_empty_after_hard: int,
    fallback_after_hard: int,
) -> Dict[str, Any]:
    out = dict(row)

    cand_field = detect_candidate_field(row)
    id_field = detect_candidate_id_field(row)

    old_cands = row.get(cand_field, [])
    new_cands = [old_cands[i] for i in keep_indices]
    out[cand_field] = new_cands

    if id_field is not None and row.get(id_field) is not None:
        old_ids = row.get(id_field, [])
        out[id_field] = [old_ids[i] for i in keep_indices]

    # If there is an aligned per-candidate field, subset it too when lengths match
    per_candidate_fields = [
        "contra_flags",
        "candidate_support_types",
        "candidate_types",
        "contra_flags_lookup_checked",
    ]
    for field in per_candidate_fields:
        vals = row.get(field)
        if isinstance(vals, list) and len(vals) == len(old_cands):
            out[field] = [vals[i] for i in keep_indices]

    out["hard_variant"] = variant_name
    out["num_candidates_before_hard"] = len(old_cands)
    out["num_candidates_after_hard"] = len(new_cands)
    out["hard_removed_candidates"] = len(old_cands) - len(new_cands)
    out["strict_empty_after_hard"] = strict_empty_after_hard
    out["fallback_after_hard"] = fallback_after_hard

    gold = row.get("gold_entity")
    out["gold_in_topk_hard"] = int(gold in set(new_cands))
    out["gold_removed_by_hard"] = int((gold in set(old_cands)) and (gold not in set(new_cands)))

    # update rank if possible
    if "rank" in out and isinstance(out["rank"], int):
        if gold in new_cands:
            out["rank"] = new_cands.index(gold) + 1
        else:
            # keep as-is for traceability; downstream reranker may still use candidate list only
            pass

    return out


def non_contra_indices_from_flags(row: Dict[str, Any]) -> List[int]:
    cand_field = detect_candidate_field(row)
    cands = row.get(cand_field, [])
    flags = row.get("contra_flags")
    if flags is None:
        raise KeyError("Input row is missing contra_flags. Run day2 script first.")
    if len(flags) != len(cands):
        raise ValueError("contra_flags length != candidate list length.")
    return [i for i, f in enumerate(flags) if int(f) == 0]


def build_hard_variants(
    ontology_rows: List[Dict[str, Any]],
    type_filtered_rows: List[Dict[str, Any]],
):
    type_idx = build_index(type_filtered_rows)

    hard_strict_rows = []
    hard_main_rows = []

    stats = {
        "num_queries": len(ontology_rows),
        "strict_empty_after_hard": 0,
        "fallback_after_hard_main": 0,
        "total_removed_candidates_strict": 0,
        "total_removed_candidates_main": 0,
        "gold_removed_by_hard_strict": 0,
        "gold_removed_by_hard_main": 0,
        "gold_in_topk_hard_strict": 0,
        "gold_in_topk_hard_main": 0,
        "missing_type_filtered_match": 0,
    }

    for i, row in enumerate(ontology_rows):
        key = row_key(row, i)
        type_row = type_idx.get(key)

        strict_keep = non_contra_indices_from_flags(row)
        strict_empty = int(len(strict_keep) == 0)

        strict_row = subset_row(
            row=row,
            keep_indices=strict_keep,
            variant_name="hard_strict",
            strict_empty_after_hard=strict_empty,
            fallback_after_hard=0,
        )
        hard_strict_rows.append(strict_row)

        stats["strict_empty_after_hard"] += strict_empty
        stats["total_removed_candidates_strict"] += strict_row["hard_removed_candidates"]
        stats["gold_removed_by_hard_strict"] += strict_row["gold_removed_by_hard"]
        stats["gold_in_topk_hard_strict"] += strict_row["gold_in_topk_hard"]

        # hard_main
        if len(strict_keep) > 0:
            main_row = subset_row(
                row=row,
                keep_indices=strict_keep,
                variant_name="hard_main",
                strict_empty_after_hard=0,
                fallback_after_hard=0,
            )
        else:
            # fallback only to type-filtered non-contra candidates
            if type_row is None:
                stats["missing_type_filtered_match"] += 1
                fallback_keep = []
                base_for_fallback = row
            else:
                base_for_fallback = type_row
                fallback_keep = non_contra_indices_from_flags(type_row) if "contra_flags" in type_row else []

                # If type_row came from week9 and has no contra_flags, compute from contra_candidates if available
                if "contra_flags" not in type_row:
                    cand_field = detect_candidate_field(type_row)
                    cands = type_row.get(cand_field, [])
                    contra_candidates = set(row.get("contra_candidates", []))
                    fallback_keep = [j for j, cand in enumerate(cands) if cand not in contra_candidates]

            main_row = subset_row(
                row=base_for_fallback,
                keep_indices=fallback_keep,
                variant_name="hard_main",
                strict_empty_after_hard=0,
                fallback_after_hard=1,
            )
            main_row["fallback_source"] = "type_filtered_non_contra_only"

            # Preserve original ontology row identifiers if fallback row came from another source
            for meta_field in [
                "triple", "triple_id", "type", "query_entity", "query_entity_id",
                "gold_entity", "gold_entity_id"
            ]:
                if meta_field in row:
                    main_row[meta_field] = row[meta_field]

            stats["fallback_after_hard_main"] += 1

        hard_main_rows.append(main_row)
        stats["total_removed_candidates_main"] += main_row["hard_removed_candidates"]
        stats["gold_removed_by_hard_main"] += main_row["gold_removed_by_hard"]
        stats["gold_in_topk_hard_main"] += main_row["gold_in_topk_hard"]

    # finalize means
    if stats["num_queries"] > 0:
        stats["avg_removed_candidates_strict"] = stats["total_removed_candidates_strict"] / stats["num_queries"]
        stats["avg_removed_candidates_main"] = stats["total_removed_candidates_main"] / stats["num_queries"]
        stats["strict_empty_rate"] = stats["strict_empty_after_hard"] / stats["num_queries"]
        stats["fallback_rate_hard_main"] = stats["fallback_after_hard_main"] / stats["num_queries"]
        stats["gold_in_topk_rate_hard_strict"] = stats["gold_in_topk_hard_strict"] / stats["num_queries"]
        stats["gold_in_topk_rate_hard_main"] = stats["gold_in_topk_hard_main"] / stats["num_queries"]

    return hard_strict_rows, hard_main_rows, stats


def write_day3_report(report_path: str, stats: Dict[str, Any], hard_strict_rows, hard_main_rows):
    sample_pairs = []
    for s, m in zip(hard_strict_rows, hard_main_rows):
        if s.get("strict_empty_after_hard") == 1 or m.get("fallback_after_hard") == 1:
            sample_pairs.append((s, m))
        if len(sample_pairs) >= 5:
            break

    lines = []
    lines.append("# Week 10 - Day 3 Hard Filter")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- num_queries: {stats['num_queries']}")
    lines.append(f"- strict_empty_after_hard: {stats['strict_empty_after_hard']}")
    lines.append(f"- strict_empty_rate: {stats.get('strict_empty_rate', 0.0):.6f}")
    lines.append(f"- fallback_after_hard_main: {stats['fallback_after_hard_main']}")
    lines.append(f"- fallback_rate_hard_main: {stats.get('fallback_rate_hard_main', 0.0):.6f}")
    lines.append(f"- total_removed_candidates_strict: {stats['total_removed_candidates_strict']}")
    lines.append(f"- total_removed_candidates_main: {stats['total_removed_candidates_main']}")
    lines.append(f"- gold_removed_by_hard_strict: {stats['gold_removed_by_hard_strict']}")
    lines.append(f"- gold_removed_by_hard_main: {stats['gold_removed_by_hard_main']}")
    lines.append(f"- gold_in_topk_rate_hard_strict: {stats.get('gold_in_topk_rate_hard_strict', 0.0):.6f}")
    lines.append(f"- gold_in_topk_rate_hard_main: {stats.get('gold_in_topk_rate_hard_main', 0.0):.6f}")
    lines.append(f"- missing_type_filtered_match: {stats['missing_type_filtered_match']}")
    lines.append("")
    lines.append("## Policy")
    lines.append("- hard_strict keeps only ontology-supported + non-contra candidates.")
    lines.append("- hard_main also forbids contra candidates, but allows fallback to type-filtered non-contra candidates.")
    lines.append("- hard_main fallback must never reintroduce contraindicated candidates.")
    lines.append("")
    lines.append("## Sample strict vs main cases")
    for idx, (s, m) in enumerate(sample_pairs):
        s_field = detect_candidate_field(s)
        m_field = detect_candidate_field(m)
        lines.append(f"### Case {idx}")
        lines.append(f"- query_entity: {s.get('query_entity')}")
        lines.append(f"- gold_entity: {s.get('gold_entity')}")
        lines.append(f"- hard_strict_candidates: {s.get(s_field, [])[:10]}")
        lines.append(f"- hard_main_candidates: {m.get(m_field, [])[:10]}")
        lines.append(f"- strict_empty_after_hard: {s.get('strict_empty_after_hard')}")
        lines.append(f"- fallback_after_hard: {m.get('fallback_after_hard')}")
        lines.append("")
    lines.append("## Notes")
    lines.append("- Day 3 only builds hard variants and traces how strict the branch becomes.")
    lines.append("- Day 4 will build soft-penalty variants for trade-off comparison.")
    lines.append("")

    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ontology_flagged_valid",
        default="dataset/setting_a/19_contra_aware/contra_candidate_flags_valid.json",
    )
    parser.add_argument(
        "--type_filtered_valid",
        default="dataset/setting_a/18_ontology_only/valid_top20_type_filtered.json",
    )
    parser.add_argument(
        "--out_hard_strict",
        default="dataset/setting_a/19_contra_aware/valid_top20_hard_strict.json",
    )
    parser.add_argument(
        "--out_hard_main",
        default="dataset/setting_a/19_contra_aware/valid_top20_hard_main.json",
    )
    parser.add_argument(
        "--out_report_json",
        default="dataset/setting_a/19_contra_aware/hard_filter_report.json",
    )
    parser.add_argument(
        "--out_report_md",
        default="reports/week10/day3_hard_filter.md",
    )
    args = parser.parse_args()

    ontology_rows = load_json(args.ontology_flagged_valid)
    type_filtered_rows = load_json(args.type_filtered_valid)

    hard_strict_rows, hard_main_rows, stats = build_hard_variants(ontology_rows, type_filtered_rows)

    save_json(hard_strict_rows, args.out_hard_strict)
    save_json(hard_main_rows, args.out_hard_main)
    save_json(stats, args.out_report_json)
    write_day3_report(args.out_report_md, stats, hard_strict_rows, hard_main_rows)

    print(f"Saved: {args.out_hard_strict}")
    print(f"Saved: {args.out_hard_main}")
    print(f"Saved: {args.out_report_json}")
    print(f"Saved: {args.out_report_md}")
    print(f"num_queries = {stats['num_queries']}")
    print(f"strict_empty_after_hard = {stats['strict_empty_after_hard']}")
    print(f"fallback_after_hard_main = {stats['fallback_after_hard_main']}")
    print(f"gold_removed_by_hard_strict = {stats['gold_removed_by_hard_strict']}")
    print(f"gold_removed_by_hard_main = {stats['gold_removed_by_hard_main']}")


if __name__ == "__main__":
    main()