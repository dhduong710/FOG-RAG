#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import random
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


def normalize_lookup(raw_lookup):
    """
    Ensure values are sorted unique lists of strings.
    """
    norm = {}
    for key, values in raw_lookup.items():
        key = str(key).strip()
        if values is None:
            values = []
        uniq = sorted({str(v).strip() for v in values if str(v).strip()})
        norm[key] = uniq
    return norm


def build_reverse_from_disease_lookup(contra_by_disease):
    reverse = {}
    for disease, drugs in contra_by_disease.items():
        for drug in drugs:
            reverse.setdefault(drug, set()).add(disease)
    return {drug: sorted(list(diseases)) for drug, diseases in reverse.items()}


def check_lookup_symmetry(contra_by_disease, contra_by_drug):
    mismatches = []

    # disease -> drug must exist in drug -> disease
    for disease, drugs in contra_by_disease.items():
        for drug in drugs:
            if disease not in set(contra_by_drug.get(drug, [])):
                mismatches.append(
                    {
                        "direction": "disease_to_drug_missing_in_reverse",
                        "disease": disease,
                        "drug": drug,
                    }
                )

    # drug -> disease must exist in disease -> drug
    for drug, diseases in contra_by_drug.items():
        for disease in diseases:
            if drug not in set(contra_by_disease.get(disease, [])):
                mismatches.append(
                    {
                        "direction": "drug_to_disease_missing_in_reverse",
                        "drug": drug,
                        "disease": disease,
                    }
                )

    return mismatches


def detect_candidate_field(row):
    if "candidate_entities" in row:
        return "candidate_entities"
    if "rank_entities" in row:
        return "rank_entities"
    raise KeyError("Cannot detect candidate field. Expected 'candidate_entities' or 'rank_entities'.")


def attach_contra_flags(candidate_rows, contra_by_disease):
    flagged_rows = []
    disease_counter = Counter()
    total_candidates = 0
    total_contra_candidates = 0
    query_has_contra_count = 0

    for row in candidate_rows:
        out = dict(row)
        disease = str(out.get("query_entity", "")).strip()
        cand_field = detect_candidate_field(out)
        candidates = [str(x).strip() for x in out.get(cand_field, [])]

        contra_set = set(contra_by_disease.get(disease, []))
        contra_flags = [1 if c in contra_set else 0 for c in candidates]
        contra_candidates = [c for c, f in zip(candidates, contra_flags) if f == 1]

        out["contra_flags"] = contra_flags
        out["contra_candidates"] = contra_candidates
        out["num_contra_candidates"] = sum(contra_flags)
        out["has_any_contra_candidate"] = int(sum(contra_flags) > 0)

        flagged_rows.append(out)

        total_candidates += len(candidates)
        total_contra_candidates += sum(contra_flags)
        if sum(contra_flags) > 0:
            query_has_contra_count += 1
            disease_counter[disease] += sum(contra_flags)

    summary = {
        "num_queries": len(candidate_rows),
        "total_candidates": total_candidates,
        "total_contra_candidates": total_contra_candidates,
        "query_has_contra_candidate_count": query_has_contra_count,
        "query_has_contra_candidate_rate": (
            query_has_contra_count / len(candidate_rows) if candidate_rows else 0.0
        ),
        "top_diseases_by_contra_count": disease_counter.most_common(20),
    }
    return flagged_rows, summary


def rebuild_valid_annotations_with_lookup(valid_annotations, contra_by_disease):
    checked = []
    total_pairs = 0
    total_positive = 0

    for row in valid_annotations:
        out = dict(row)
        disease = str(out.get("query_disease", "")).strip()
        candidate_drugs = [str(x).strip() for x in out.get("candidate_drugs", [])]
        contra_set = set(contra_by_disease.get(disease, []))

        contra_flags = [1 if drug in contra_set else 0 for drug in candidate_drugs]
        out["contra_flags_lookup_checked"] = contra_flags
        out["has_any_contra_candidate_lookup_checked"] = int(sum(contra_flags) > 0)

        gold_drug = str(out.get("gold_drug", "")).strip()
        out["gold_is_contraindicated_lookup_checked"] = int(gold_drug in contra_set)

        checked.append(out)
        total_pairs += len(candidate_drugs)
        total_positive += sum(contra_flags)

    stats = {
        "num_annotation_rows": len(valid_annotations),
        "num_annotation_candidate_pairs": total_pairs,
        "num_annotation_contra_pairs": total_positive,
    }
    return checked, stats


def write_markdown_report(
    path,
    args_dict,
    lookup_summary,
    annotation_summary,
    mismatch_count,
    flagged_rows,
    seed=2025,
):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    sample_rows = flagged_rows[:3]
    lines = []
    lines.append("# Week 10 - Day 2 Contra Lookup")
    lines.append("")
    lines.append("## Inputs")
    lines.append(f"- ontology candidates: `{args_dict['ontology_candidates']}`")
    lines.append(f"- contra_by_disease: `{args_dict['contra_by_disease']}`")
    lines.append(f"- contra_by_drug: `{args_dict['contra_by_drug']}`")
    lines.append(f"- valid annotations: `{args_dict['valid_annotations']}`")
    lines.append("")
    lines.append("## Lookup summary")
    lines.append(f"- num_queries: {lookup_summary['num_queries']}")
    lines.append(f"- total_candidates: {lookup_summary['total_candidates']}")
    lines.append(f"- total_contra_candidates: {lookup_summary['total_contra_candidates']}")
    lines.append(
        f"- query_has_contra_candidate_count: {lookup_summary['query_has_contra_candidate_count']}"
    )
    lines.append(
        f"- query_has_contra_candidate_rate: {lookup_summary['query_has_contra_candidate_rate']:.6f}"
    )
    lines.append(f"- lookup_symmetry_mismatches: {mismatch_count}")
    lines.append("")
    lines.append("## Valid annotation summary")
    lines.append(f"- num_annotation_rows: {annotation_summary['num_annotation_rows']}")
    lines.append(
        f"- num_annotation_candidate_pairs: {annotation_summary['num_annotation_candidate_pairs']}"
    )
    lines.append(
        f"- num_annotation_contra_pairs: {annotation_summary['num_annotation_contra_pairs']}"
    )
    lines.append("")
    lines.append("## Top diseases by contra count")
    for disease, cnt in lookup_summary["top_diseases_by_contra_count"][:10]:
        lines.append(f"- {disease}: {cnt}")
    lines.append("")
    lines.append("## Sample flagged rows")
    for i, row in enumerate(sample_rows):
        lines.append(f"### Sample {i}")
        lines.append(f"- query_entity: {row.get('query_entity')}")
        lines.append(f"- num_contra_candidates: {row.get('num_contra_candidates')}")
        lines.append(f"- contra_candidates: {row.get('contra_candidates', [])[:10]}")
        lines.append("")
    lines.append("## Notes")
    lines.append("- Day 2 only builds traceable contra lookup and candidate flags.")
    lines.append("- Day 3 will use these flags to build hard_strict and hard_main.")
    lines.append("- Day 4 will use the same flags to build soft-penalty variants.")
    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ontology_candidates",
        default="dataset/setting_a/18_ontology_only/valid_top20_ontology_only.json",
    )
    parser.add_argument(
        "--contra_by_disease",
        default="dataset/setting_b/00_safety_labels/contra_by_disease.json",
    )
    parser.add_argument(
        "--contra_by_drug",
        default="dataset/setting_b/00_safety_labels/contra_by_drug.json",
    )
    parser.add_argument(
        "--valid_annotations",
        default="dataset/setting_b/02_eval_ready/valid_b_annotations.json",
    )
    parser.add_argument(
        "--out_candidate_flags",
        default="dataset/setting_a/19_contra_aware/contra_candidate_flags_valid.json",
    )
    parser.add_argument(
        "--out_lookup_disease",
        default="dataset/setting_b/04_contra_checked/contra_lookup_by_disease.json",
    )
    parser.add_argument(
        "--out_lookup_drug",
        default="dataset/setting_b/04_contra_checked/contra_lookup_by_drug.json",
    )
    parser.add_argument(
        "--out_valid_annotations",
        default="dataset/setting_b/04_contra_checked/valid_b_annotations_contra_checked.json",
    )
    parser.add_argument(
        "--out_summary",
        default="dataset/setting_b/04_contra_checked/contra_check_summary.json",
    )
    parser.add_argument(
        "--out_report",
        default="reports/week10/day2_contra_lookup.md",
    )
    args = parser.parse_args()

    Path("dataset/setting_a/19_contra_aware").mkdir(parents=True, exist_ok=True)
    Path("dataset/setting_b/04_contra_checked").mkdir(parents=True, exist_ok=True)
    Path("reports/week10").mkdir(parents=True, exist_ok=True)

    candidate_rows = load_json(args.ontology_candidates)
    contra_by_disease = normalize_lookup(load_json(args.contra_by_disease))
    contra_by_drug = normalize_lookup(load_json(args.contra_by_drug))
    valid_annotations = load_json(args.valid_annotations)

    # Save normalized forward lookup
    save_json(contra_by_disease, args.out_lookup_disease)

    # Rebuild reverse lookup from disease-based lookup and compare with provided reverse lookup
    rebuilt_reverse = build_reverse_from_disease_lookup(contra_by_disease)
    mismatches = check_lookup_symmetry(contra_by_disease, contra_by_drug)

    # Save a cleaned reverse lookup that is guaranteed to match the disease-based source
    save_json(rebuilt_reverse, args.out_lookup_drug)

    flagged_rows, lookup_summary = attach_contra_flags(candidate_rows, contra_by_disease)
    save_json(flagged_rows, args.out_candidate_flags)

    checked_annotations, annotation_summary = rebuild_valid_annotations_with_lookup(
        valid_annotations, contra_by_disease
    )
    save_json(checked_annotations, args.out_valid_annotations)

    summary = {
        "inputs": {
            "ontology_candidates": args.ontology_candidates,
            "contra_by_disease": args.contra_by_disease,
            "contra_by_drug": args.contra_by_drug,
            "valid_annotations": args.valid_annotations,
        },
        "lookup_summary": lookup_summary,
        "annotation_summary": annotation_summary,
        "lookup_symmetry_mismatch_count": len(mismatches),
        "lookup_symmetry_mismatch_examples": mismatches[:100],
    }
    save_json(summary, args.out_summary)

    write_markdown_report(
        path=args.out_report,
        args_dict=vars(args),
        lookup_summary=lookup_summary,
        annotation_summary=annotation_summary,
        mismatch_count=len(mismatches),
        flagged_rows=flagged_rows,
    )

    print(f"Saved: {args.out_lookup_disease}")
    print(f"Saved: {args.out_lookup_drug}")
    print(f"Saved: {args.out_candidate_flags}")
    print(f"Saved: {args.out_valid_annotations}")
    print(f"Saved: {args.out_summary}")
    print(f"Saved: {args.out_report}")
    print(f"num_queries = {lookup_summary['num_queries']}")
    print(f"total_candidates = {lookup_summary['total_candidates']}")
    print(f"total_contra_candidates = {lookup_summary['total_contra_candidates']}")
    print(f"query_has_contra_candidate_count = {lookup_summary['query_has_contra_candidate_count']}")
    print(f"lookup_symmetry_mismatch_count = {len(mismatches)}")


if __name__ == "__main__":
    main()