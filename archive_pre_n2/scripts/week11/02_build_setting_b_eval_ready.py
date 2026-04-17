#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def load_type_map_tsv(path):
    type_map = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            entity = row["entity"].strip()
            final_type = row["final_type"].strip()
            type_map[entity] = final_type
    return type_map


def detect_candidate_field(row):
    if "rank_entities" in row:
        return "rank_entities"
    if "candidate_entities" in row:
        return "candidate_entities"
    raise KeyError("Cannot detect candidate entity field.")


def detect_candidate_id_field(row):
    if "rank_entities_id" in row:
        return "rank_entities_id"
    if "candidate_entity_ids" in row:
        return "candidate_entity_ids"
    return None


def build_annotation_index(rows):
    """
    Key by (query_disease, gold_drug)
    """
    idx = {}
    for row in rows:
        key = (
            str(row["query_disease"]).strip(),
            str(row["gold_drug"]).strip(),
        )
        idx[key] = row
    return idx


def build_conflict_lookup(annotation_rows):
    """
    For each (query_disease, candidate_drug) pair, recover conflict flag
    from valid_b_annotations_contra_checked.json if present.
    """
    lookup = {}
    for row in annotation_rows:
        disease = str(row["query_disease"]).strip()
        cands = [str(x).strip() for x in row.get("candidate_drugs", [])]
        conflict_flags = row.get("conflict_flags", [])
        if isinstance(conflict_flags, list) and len(conflict_flags) == len(cands):
            for drug, flag in zip(cands, conflict_flags):
                lookup[(disease, drug)] = int(flag)
    return lookup


def build_contra_lookup(annotation_rows):
    """
    Use checked annotations as a disease->candidate contra lookup where available.
    Falls back later to existing row-specific contra flags if present.
    """
    lookup = {}
    for row in annotation_rows:
        disease = str(row["query_disease"]).strip()
        cands = [str(x).strip() for x in row.get("candidate_drugs", [])]
        flags = (
            row.get("contra_flags_lookup_checked")
            or row.get("contra_flags")
            or []
        )
        if isinstance(flags, list) and len(flags) == len(cands):
            for drug, flag in zip(cands, flags):
                lookup[(disease, drug)] = int(flag)
    return lookup


def make_eval_rows(
    source_name,
    candidate_rows,
    annotation_index,
    type_map,
    contra_lookup,
    conflict_lookup,
):
    eval_rows = []
    unmatched = []
    sample_rows = []

    for row in candidate_rows:
        query_disease = str(row.get("query_entity", "")).strip()
        gold_drug = str(row.get("gold_entity", "")).strip()
        key = (query_disease, gold_drug)

        ann = annotation_index.get(key)
        if ann is None:
            unmatched.append({
                "query_disease": query_disease,
                "gold_drug": gold_drug,
            })
            continue

        cand_field = detect_candidate_field(row)
        cands = [str(x).strip() for x in row.get(cand_field, [])]

        cand_id_field = detect_candidate_id_field(row)
        cand_ids = row.get(cand_id_field, None) if cand_id_field is not None else None

        candidate_types_final = [type_map.get(c, "Other") for c in cands]
        contra_flags_final = [int(contra_lookup.get((query_disease, c), 0)) for c in cands]
        conflict_flags_final = [int(conflict_lookup.get((query_disease, c), 0)) for c in cands]

        eval_row = {
            "query_disease": query_disease,
            "gold_drug": gold_drug,
            "setting_a_relation": ann.get("setting_a_relation", "indication"),
            "row_source": source_name,
            "candidate_drugs_final": cands,
            "candidate_types_final": candidate_types_final,
            "contra_flags_final": contra_flags_final,
            "conflict_flags_final": conflict_flags_final,
            "gold_type": ann.get("gold_type", type_map.get(gold_drug, "Drug")),
            "gold_is_contraindicated": int(ann.get("gold_is_contraindicated_lookup_checked", ann.get("gold_is_contraindicated", 0))),
            "gold_conflict_flag": int(ann.get("gold_conflict_flag", 0)),
            "has_any_contra_candidate_final": int(sum(contra_flags_final) > 0),
            "row_has_gold_in_topk": int(gold_drug in set(cands)),
            "candidate_count_final": len(cands),
        }

        if cand_ids is not None:
            eval_row["candidate_drug_ids_final"] = cand_ids

        # keep a bit of traceability from source row
        for extra_key in [
            "triple",
            "triple_id",
            "query_entity_id",
            "gold_entity_id",
            "rank",
            "hard_variant",
            "soft_variant",
            "soft_lambda",
            "fallback_after_hard",
            "strict_empty_after_hard",
            "ontology_filter_applied",
            "ontology_filter_mode",
            "ontology_fallback_used",
        ]:
            if extra_key in row:
                eval_row[extra_key] = row[extra_key]

        eval_rows.append(eval_row)

        if len(sample_rows) < 5:
            sample_rows.append({
                "query_disease": query_disease,
                "gold_drug": gold_drug,
                "candidate_count_final": len(cands),
                "row_has_gold_in_topk": eval_row["row_has_gold_in_topk"],
                "has_any_contra_candidate_final": eval_row["has_any_contra_candidate_final"],
                "top5_candidates": cands[:5],
            })

    summary = {
        "row_source": source_name,
        "num_rows_input": len(candidate_rows),
        "num_rows_matched": len(eval_rows),
        "num_rows_unmatched": len(unmatched),
        "avg_candidate_size": (
            sum(r["candidate_count_final"] for r in eval_rows) / len(eval_rows)
            if eval_rows else 0.0
        ),
        "rows_with_gold_in_topk": sum(r["row_has_gold_in_topk"] for r in eval_rows),
        "rows_with_any_contra_candidate_final": sum(r["has_any_contra_candidate_final"] for r in eval_rows),
        "candidate_type_distribution_top": Counter(
            t for r in eval_rows for t in r["candidate_types_final"]
        ).most_common(10),
        "sample_rows": sample_rows,
    }

    return eval_rows, unmatched, summary


def write_markdown_report(path, source_summaries):
    lines = []
    lines.append("# Week 11 - Day 2 Eval-Ready Build")
    lines.append("")
    lines.append("## Sources built")
    for source_name, s in source_summaries.items():
        lines.append(f"### {source_name}")
        lines.append(f"- num_rows_input: {s['num_rows_input']}")
        lines.append(f"- num_rows_matched: {s['num_rows_matched']}")
        lines.append(f"- num_rows_unmatched: {s['num_rows_unmatched']}")
        lines.append(f"- avg_candidate_size: {s['avg_candidate_size']:.6f}")
        lines.append(f"- rows_with_gold_in_topk: {s['rows_with_gold_in_topk']}")
        lines.append(f"- rows_with_any_contra_candidate_final: {s['rows_with_any_contra_candidate_final']}")
        lines.append(f"- candidate_type_distribution_top: {s['candidate_type_distribution_top']}")
        lines.append("")
    lines.append("## Notes")
    lines.append("- Day 2 only builds Setting B eval-ready inputs.")
    lines.append("- Day 3 will prioritize hard_main valid evaluation.")
    lines.append("- Day 4 will evaluate soft_best valid under the same Setting B protocol.")
    lines.append("")

    write_path = Path(path)
    write_path.parent.mkdir(parents=True, exist_ok=True)
    with open(write_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--valid_annotations",
        default="dataset/setting_b/04_contra_checked/valid_b_annotations_contra_checked.json",
    )
    parser.add_argument(
        "--type_map_tsv",
        default="dataset/setting_b/01_annotations/type_map.tsv",
    )
    parser.add_argument(
        "--backbone_valid",
        default="dataset/setting_a/12_backbone_ready_ranker_v2/valid.json",
    )
    parser.add_argument(
        "--ontology_valid",
        default="dataset/setting_a/18_ontology_only_eval_ready/valid.json",
    )
    parser.add_argument(
        "--hard_valid",
        default="dataset/setting_a/19_contra_aware_eval_ready/hard_main/valid.json",
    )
    parser.add_argument(
        "--soft_valid",
        default="dataset/setting_a/19_contra_aware_eval_ready/soft_best/valid.json",
    )
    parser.add_argument(
        "--out_dir",
        default="dataset/setting_b/05_eval_week11",
    )
    parser.add_argument(
        "--report_md",
        default="reports/week11/day2_eval_ready.md",
    )
    args = parser.parse_args()

    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    Path("reports/week11").mkdir(parents=True, exist_ok=True)

    valid_annotations = load_json(args.valid_annotations)
    annotation_index = build_annotation_index(valid_annotations)
    conflict_lookup = build_conflict_lookup(valid_annotations)
    contra_lookup = build_contra_lookup(valid_annotations)
    type_map = load_type_map_tsv(args.type_map_tsv)

    sources = {
        "backbone": load_json(args.backbone_valid),
        "ontology": load_json(args.ontology_valid),
        "hard_main": load_json(args.hard_valid),
        "soft_best": load_json(args.soft_valid),
    }

    all_summary = {}
    all_unmatched = {}

    for source_name, rows in sources.items():
        eval_rows, unmatched, summary = make_eval_rows(
            source_name=source_name,
            candidate_rows=rows,
            annotation_index=annotation_index,
            type_map=type_map,
            contra_lookup=contra_lookup,
            conflict_lookup=conflict_lookup,
        )
        save_json(eval_rows, Path(args.out_dir) / f"valid_{source_name}_eval.json")
        all_summary[source_name] = summary
        all_unmatched[source_name] = unmatched[:50]

    save_json(
        {
            "source_summaries": all_summary,
            "unmatched_examples": all_unmatched,
        },
        Path(args.out_dir) / "eval_ready_summary.json",
    )

    write_markdown_report(args.report_md, all_summary)

    print(f"Saved eval-ready files to: {args.out_dir}")
    for k, s in all_summary.items():
        print(
            k,
            {
                "num_rows_matched": s["num_rows_matched"],
                "num_rows_unmatched": s["num_rows_unmatched"],
                "avg_candidate_size": round(s["avg_candidate_size"], 6),
                "rows_with_gold_in_topk": s["rows_with_gold_in_topk"],
                "rows_with_any_contra_candidate_final": s["rows_with_any_contra_candidate_final"],
            },
        )
    print(f"Saved report: {args.report_md}")


if __name__ == "__main__":
    main()