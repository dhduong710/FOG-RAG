#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
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


def normalize_contra_lookup(contra_by_disease):
    lookup = {}
    for disease, drugs in contra_by_disease.items():
        disease = str(disease).strip()
        for drug in drugs:
            lookup[(disease, str(drug).strip())] = 1
    return lookup


def build_checked_test_annotations(test_annotations, contra_lookup):
    checked = []
    for row in test_annotations:
        out = dict(row)
        disease = str(out["query_disease"]).strip()
        cands = [str(x).strip() for x in out.get("candidate_drugs", [])]
        contra_flags = [int(contra_lookup.get((disease, c), 0)) for c in cands]
        out["contra_flags_lookup_checked"] = contra_flags
        out["has_any_contra_candidate_lookup_checked"] = int(sum(contra_flags) > 0)

        gold = str(out["gold_drug"]).strip()
        out["gold_is_contraindicated_lookup_checked"] = int(contra_lookup.get((disease, gold), 0))
        checked.append(out)
    return checked


def build_annotation_index(rows):
    idx = {}
    for row in rows:
        key = (
            str(row["query_disease"]).strip(),
            str(row["gold_drug"]).strip(),
        )
        idx[key] = row
    return idx


def make_eval_rows(row_source, candidate_rows, ann_index, type_map):
    eval_rows = []
    unmatched = []

    for row in candidate_rows:
        q = str(row.get("query_entity", "")).strip()
        g = str(row.get("gold_entity", "")).strip()
        ann = ann_index.get((q, g))
        if ann is None:
            unmatched.append({"query_disease": q, "gold_drug": g})
            continue

        cand_field = detect_candidate_field(row)
        cands = [str(x).strip() for x in row.get(cand_field, [])]

        cand_id_field = detect_candidate_id_field(row)
        cand_ids = row.get(cand_id_field, None) if cand_id_field else None

        ann_cands = [str(x).strip() for x in ann.get("candidate_drugs", [])]
        ann_contra = ann.get("contra_flags_lookup_checked", [])
        ann_conflict = ann.get("conflict_flags", [])

        contra_map = {}
        conflict_map = {}
        if len(ann_cands) == len(ann_contra):
            for d, f in zip(ann_cands, ann_contra):
                contra_map[d] = int(f)
        if len(ann_cands) == len(ann_conflict):
            for d, f in zip(ann_cands, ann_conflict):
                conflict_map[d] = int(f)

        eval_row = {
            "query_disease": q,
            "gold_drug": g,
            "setting_a_relation": ann.get("setting_a_relation", "indication"),
            "row_source": row_source,
            "candidate_drugs_final": cands,
            "candidate_types_final": [type_map.get(c, "Drug") for c in cands],
            "contra_flags_final": [contra_map.get(c, 0) for c in cands],
            "conflict_flags_final": [conflict_map.get(c, 0) for c in cands],
            "gold_is_contraindicated": int(ann.get("gold_is_contraindicated_lookup_checked", ann.get("gold_is_contraindicated", 0))),
            "gold_conflict_flag": int(ann.get("gold_conflict_flag", 0)),
            "row_has_gold_in_topk": int(g in set(cands)),
            "candidate_count_final": len(cands),
        }
        if cand_ids is not None:
            eval_row["candidate_drug_ids_final"] = cand_ids

        eval_rows.append(eval_row)

    summary = {
        "row_source": row_source,
        "num_rows_input": len(candidate_rows),
        "num_rows_matched": len(eval_rows),
        "num_rows_unmatched": len(unmatched),
        "avg_candidate_size": (
            sum(r["candidate_count_final"] for r in eval_rows) / len(eval_rows)
            if eval_rows else 0.0
        ),
        "rows_with_gold_in_topk": sum(int(r["row_has_gold_in_topk"]) for r in eval_rows),
        "rows_with_any_contra_candidate_final": sum(int(sum(r["contra_flags_final"]) > 0) for r in eval_rows),
        "unmatched_examples": unmatched[:20],
    }
    return eval_rows, summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_annotations", default="dataset/setting_b/02_eval_ready/test_b_annotations.json")
    parser.add_argument("--contra_by_disease", default="dataset/setting_b/04_contra_checked/contra_lookup_by_disease.json")
    parser.add_argument("--type_map_tsv", default="dataset/setting_b/01_annotations/type_map.tsv")
    parser.add_argument("--backbone_test", default="dataset/setting_a/12_backbone_ready_ranker_v2/test.json")
    parser.add_argument("--ontology_test", default="dataset/setting_a/18_ontology_only/test_top20_ontology_only.json")
    parser.add_argument("--hard_test", default="dataset/setting_a/19_contra_aware/test_top20_hard_main.json")
    parser.add_argument("--soft_test", default="dataset/setting_a/19_contra_aware/test_top20_soft_best.json")
    parser.add_argument("--out_dir", default="dataset/setting_b/06_eval_week11_test")
    args = parser.parse_args()

    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    Path("dataset/setting_b/04_contra_checked").mkdir(parents=True, exist_ok=True)

    test_annotations = load_json(args.test_annotations)
    contra_by_disease = load_json(args.contra_by_disease)
    contra_lookup = normalize_contra_lookup(contra_by_disease)
    type_map = load_type_map_tsv(args.type_map_tsv)

    checked_test = build_checked_test_annotations(test_annotations, contra_lookup)
    checked_path = "dataset/setting_b/04_contra_checked/test_b_annotations_contra_checked.json"
    save_json(checked_test, checked_path)

    ann_index = build_annotation_index(checked_test)

    sources = {
        "backbone": load_json(args.backbone_test),
        "ontology": load_json(args.ontology_test),
        "hard_main": load_json(args.hard_test),
        "soft_best": load_json(args.soft_test),
    }

    summaries = {}
    for name, rows in sources.items():
        eval_rows, summary = make_eval_rows(name, rows, ann_index, type_map)
        save_json(eval_rows, Path(args.out_dir) / f"test_{name}_eval.json")
        summaries[name] = summary

    save_json(
        {
            "checked_test_annotations_path": checked_path,
            "source_summaries": summaries,
        },
        Path(args.out_dir) / "test_eval_ready_summary.json",
    )

    print(f"Saved: {checked_path}")
    print(f"Saved: {Path(args.out_dir) / 'test_eval_ready_summary.json'}")
    for k, v in summaries.items():
        print(k, v)


if __name__ == "__main__":
    main()