#!/usr/bin/env python3
import argparse
import csv
import json
import os
import pickle
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def save_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_pickle(path: Path):
    with path.open("rb") as f:
        return pickle.load(f)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)


def first_existing(paths: List[Path]) -> Optional[Path]:
    for p in paths:
        if p.exists():
            return p
    return None


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def safe_link_or_copy(src: Path, dst: Path, mode: str = "copy"):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        dst.unlink()

    if mode == "symlink":
        os.symlink(src.resolve(), dst)
    else:
        shutil.copy2(src, dst)


def read_type_map_tsv(path: Path) -> Dict[str, str]:
    import csv

    mapping = {}
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        if reader.fieldnames is None:
            raise ValueError(f"type_map.tsv has no header: {path}")

        # normalize header names
        fieldnames = [(x or "").strip().lstrip("\ufeff") for x in reader.fieldnames]
        reader.fieldnames = fieldnames

        # support both old 2-column schema and your current annotated schema
        if "final_type" in fieldnames:
            type_col = "final_type"
        elif "type" in fieldnames:
            type_col = "type"
        elif "raw_type" in fieldnames:
            type_col = "raw_type"
        else:
            raise KeyError(
                f"Cannot find type column in {path}. Headers = {fieldnames}. "
                f"Expected one of: final_type, type, raw_type."
            )

        for row in reader:
            row = {
                (k.strip().lstrip("\ufeff") if k is not None else k):
                (v.strip() if isinstance(v, str) else v)
                for k, v in row.items()
            }

            entity = (row.get("entity") or "").strip()
            etype = (row.get(type_col) or "").strip()

            if entity:
                mapping[entity] = etype

    return mapping


def normalize_answer_text(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x.strip()
    return str(x).strip()


def normalize_entity_name(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x.strip()
    return str(x).strip()


def get_required_field_status(ex: Dict[str, Any]) -> Dict[str, bool]:
    required = ["input", "output", "query_entity_id", "rank_entities_id", "subgraph"]
    return {k: (k in ex and ex[k] is not None) for k in required}


def check_rank_entity_types(ex: Dict[str, Any], type_map: Dict[str, str]):
    """
    Returns:
      all_drug_ok, num_checked, bad_entities_debug
    """
    rank_entities = ex.get("rank_entities", [])
    if not isinstance(rank_entities, list) or not rank_entities:
        return False, 0, []

    bad = []
    for ent in rank_entities:
        ent_name = normalize_entity_name(ent)
        etype = (type_map.get(ent_name) or "").strip()

        if etype != "Drug":
            bad.append({
                "entity": ent_name,
                "mapped_type": etype if etype else None,
            })

    return len(bad) == 0, len(rank_entities), bad[:10]  


def check_gold_in_candidates(ex: Dict[str, Any]) -> bool:
    gold = normalize_answer_text(ex.get("output"))
    rank_entities = ex.get("rank_entities", [])
    if not gold or not isinstance(rank_entities, list):
        return False
    rank_entities = [normalize_entity_name(x) for x in rank_entities]
    return gold in rank_entities


def check_subgraph_nonempty(ex: Dict[str, Any]) -> bool:
    sg = ex.get("subgraph", [])
    return isinstance(sg, list) and len(sg) > 0


def check_id_consistency(
    ex: Dict[str, Any],
    entity2id: Dict[str, int],
    id2entity: Dict[int, str],
) -> Dict[str, Any]:
    result = {
        "query_entity_id_in_range": False,
        "rank_entity_ids_all_in_range": False,
        "query_entity_name_match": None,
        "rank_entities_name_match_count": None,
        "rank_entities_name_match_total": None,
    }

    # query id in range
    qid = ex.get("query_entity_id", None)
    if isinstance(qid, int) and qid in id2entity:
        result["query_entity_id_in_range"] = True

    # rank ids in range
    rank_ids = ex.get("rank_entities_id", [])
    if isinstance(rank_ids, list) and all(isinstance(x, int) and x in id2entity for x in rank_ids):
        result["rank_entity_ids_all_in_range"] = True

    # optional name check for query entity
    qname = ex.get("query_entity", None)
    if qname is not None and isinstance(qid, int) and qid in id2entity:
        result["query_entity_name_match"] = (normalize_entity_name(qname) == normalize_entity_name(id2entity[qid]))

    # optional name check for rank entities
    rank_entities = ex.get("rank_entities", None)
    if isinstance(rank_entities, list) and isinstance(rank_ids, list) and len(rank_entities) == len(rank_ids):
        ok = 0
        total = len(rank_ids)
        for name, idx in zip(rank_entities, rank_ids):
            if isinstance(idx, int) and idx in id2entity:
                if normalize_entity_name(name) == normalize_entity_name(id2entity[idx]):
                    ok += 1
        result["rank_entities_name_match_count"] = ok
        result["rank_entities_name_match_total"] = total

    return result


def summarize_split(
    split_name: str,
    data: List[Dict[str, Any]],
    entity2id: Dict[str, int],
    id2entity: Dict[int, str],
    type_map: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    stats = {
        "split": split_name,
        "num_samples": len(data),
        "required_field_missing_count": 0,
        "required_field_missing_examples": [],
        "candidate_len_min": None,
        "candidate_len_max": None,
        "subgraph_len_min": None,
        "subgraph_len_max": None,
        "subgraph_empty_count": 0,
        "gold_in_candidate_count": 0,
        "id_mismatch_count": 0,
        "query_id_bad_count": 0,
        "rank_ids_bad_count": 0,
        "rank_name_match_partial_count": 0,
        "rank_name_match_fail_examples": [],
        "all_candidates_are_drug_count": 0,
        "candidate_type_checkable_count": 0,
        "candidate_non_drug_examples": [],
        "sample_examples": [],
    }

    candidate_lens = []
    subgraph_lens = []

    for i, ex in enumerate(data):
        field_status = get_required_field_status(ex)
        if not all(field_status.values()):
            stats["required_field_missing_count"] += 1
            if len(stats["required_field_missing_examples"]) < 5:
                stats["required_field_missing_examples"].append({
                    "index": i,
                    "missing_fields": [k for k, v in field_status.items() if not v]
                })

        rank_ids = ex.get("rank_entities_id", [])
        if isinstance(rank_ids, list):
            candidate_lens.append(len(rank_ids))

        subgraph = ex.get("subgraph", [])
        if isinstance(subgraph, list):
            subgraph_lens.append(len(subgraph))
            if len(subgraph) == 0:
                stats["subgraph_empty_count"] += 1

        if check_gold_in_candidates(ex):
            stats["gold_in_candidate_count"] += 1

        id_check = check_id_consistency(ex, entity2id, id2entity)
        bad_id = False
        if not id_check["query_entity_id_in_range"]:
            stats["query_id_bad_count"] += 1
            bad_id = True
        if not id_check["rank_entity_ids_all_in_range"]:
            stats["rank_ids_bad_count"] += 1
            bad_id = True
        if bad_id:
            stats["id_mismatch_count"] += 1

        if id_check["rank_entities_name_match_count"] is not None:
            if id_check["rank_entities_name_match_count"] != id_check["rank_entities_name_match_total"]:
                stats["rank_name_match_partial_count"] += 1
                if len(stats["rank_name_match_fail_examples"]) < 5:
                    stats["rank_name_match_fail_examples"].append({
                        "index": i,
                        "matched": id_check["rank_entities_name_match_count"],
                        "total": id_check["rank_entities_name_match_total"],
                    })

        if type_map is not None:
            all_drug_ok, num_checked, bad_ents = check_rank_entity_types(ex, type_map)
            if num_checked > 0:
                stats["candidate_type_checkable_count"] += 1
                if all_drug_ok:
                    stats["all_candidates_are_drug_count"] += 1
                else:
                    if len(stats["candidate_non_drug_examples"]) < 5:
                        stats["candidate_non_drug_examples"].append({
                            "index": i,
                            "bad_entities": bad_ents
                        })

        if len(stats["sample_examples"]) < 3:
            stats["sample_examples"].append({
                "index": i,
                "output": ex.get("output"),
                "query_entity_id": ex.get("query_entity_id"),
                "num_rank_entities_id": len(ex.get("rank_entities_id", [])) if isinstance(ex.get("rank_entities_id", []), list) else None,
                "num_subgraph_triples": len(ex.get("subgraph", [])) if isinstance(ex.get("subgraph", []), list) else None,
            })

    if candidate_lens:
        stats["candidate_len_min"] = min(candidate_lens)
        stats["candidate_len_max"] = max(candidate_lens)
    if subgraph_lens:
        stats["subgraph_len_min"] = min(subgraph_lens)
        stats["subgraph_len_max"] = max(subgraph_lens)

    return stats


def parse_args():
    parser = argparse.ArgumentParser(description="Prepare dataset/setting_a/08_check_backbone_ready package.")

    parser.add_argument("--link-mode", choices=["copy", "symlink"], default="copy")

    parser.add_argument(
        "--train-src",
        type=str,
        default="dataset/setting_a/08_backbone_ready/train.json",
        help="Source full train JSON.",
    )
    parser.add_argument(
        "--valid-src",
        type=str,
        default="dataset/setting_a/08_backbone_ready/valid.json",
        help="Source full valid JSON.",
    )
    parser.add_argument(
        "--test-src",
        type=str,
        default="dataset/setting_a/08_backbone_ready/test.json",
        help="Source full test JSON.",
    )

    parser.add_argument(
        "--entity2id",
        type=str,
        default="dataset/setting_a/04_drkgc_json/entity2id.pkl",
    )
    parser.add_argument(
        "--id2entity",
        type=str,
        default="dataset/setting_a/04_drkgc_json/id2entity.pkl",
    )
    parser.add_argument(
        "--relation2id",
        type=str,
        default="dataset/setting_a/04_drkgc_json/relation2id.pkl",
    )
    parser.add_argument(
        "--id2relation",
        type=str,
        default="dataset/setting_a/04_drkgc_json/id2relation.pkl",
    )
    parser.add_argument(
        "--type-map",
        type=str,
        default="dataset/setting_b/01_annotations/type_map.tsv",
    )
    parser.add_argument(
        "--split-meta",
        type=str,
        default="dataset/setting_a/01_split/split_meta.json",
    )
    parser.add_argument(
        "--dst-dir",
        type=str,
        default="dataset/setting_a/08_check_backbone_ready",
    )
    parser.add_argument(
        "--report-path",
        type=str,
        default="reports/week5/day2_check_backbone_ready_report.md",
    )
    parser.add_argument(
        "--manifest-path",
        type=str,
        default="dataset/setting_a/08_check_backbone_ready/check_backbone_ready_manifest.json",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    train_src = ROOT / args.train_src
    valid_src = ROOT / args.valid_src
    test_src = ROOT / args.test_src

    entity2id_path = ROOT / args.entity2id
    id2entity_path = ROOT / args.id2entity
    relation2id_path = ROOT / args.relation2id
    id2relation_path = ROOT / args.id2relation
    type_map_path = ROOT / args.type_map
    split_meta_path = ROOT / args.split_meta

    dst_dir = ROOT / args.dst_dir
    report_path = ROOT / args.report_path
    manifest_path = ROOT / args.manifest_path

    ensure_dir(dst_dir)
    ensure_dir(report_path.parent)

    required = {
        "train_src": train_src,
        "valid_src": valid_src,
        "test_src": test_src,
        "entity2id": entity2id_path,
        "id2entity": id2entity_path,
        "relation2id": relation2id_path,
        "id2relation": id2relation_path,
        "split_meta": split_meta_path,
    }

    missing = {k: rel(v) for k, v in required.items() if not v.exists()}
    if missing:
        raise FileNotFoundError(
            "Missing required files:\n" + "\n".join([f"- {k}: {p}" for k, p in missing.items()])
        )

    use_type_map = type_map_path.exists()

    print("=" * 80)
    print("Week 5 Day 2 - Check Prepare Backbone Ready Package")
    print("=" * 80)
    print("Train src :", rel(train_src))
    print("Valid src :", rel(valid_src))
    print("Test src  :", rel(test_src))
    print("Dst dir   :", rel(dst_dir))
    print("Link mode :", args.link_mode)
    print("Type map  :", rel(type_map_path) if use_type_map else "(not found, candidate type audit will be skipped)")
    print("=" * 80)

    # Load artifacts
    train_data = load_json(train_src)
    valid_data = load_json(valid_src)
    test_data = load_json(test_src)

    entity2id = load_pickle(entity2id_path)
    id2entity = load_pickle(id2entity_path)
    relation2id = load_pickle(relation2id_path)
    id2relation = load_pickle(id2relation_path)
    split_meta = load_json(split_meta_path)
    type_map = read_type_map_tsv(type_map_path) if use_type_map else None

    # Normalize id2entity/id2relation keys if needed
    # Some pickles may store keys as strings; try to convert to int when possible.
    if len(id2entity) > 0:
        sample_key = next(iter(id2entity.keys()))
        if not isinstance(sample_key, int):
            id2entity = {int(k): v for k, v in id2entity.items()}
    if len(id2relation) > 0:
        sample_key = next(iter(id2relation.keys()))
        if not isinstance(sample_key, int):
            id2relation = {int(k): v for k, v in id2relation.items()}

    # Split size checks
    expected_train = split_meta.get("split_sizes", {}).get("train", 8388)
    expected_valid = split_meta.get("split_sizes", {}).get("valid", 500)
    expected_test = split_meta.get("split_sizes", {}).get("test", 500)

    split_size_checks = {
        "train_size_ok": len(train_data) == expected_train,
        "valid_size_ok": len(valid_data) == expected_valid,
        "test_size_ok": len(test_data) == expected_test,
    }

    # Summaries
    train_stats = summarize_split("train", train_data, entity2id, id2entity, type_map)
    valid_stats = summarize_split("valid", valid_data, entity2id, id2entity, type_map)
    test_stats = summarize_split("test", test_data, entity2id, id2entity, type_map)

    # Global checks
    global_checks = {
        **split_size_checks,
        "entity2id_nonempty": len(entity2id) > 0,
        "id2entity_nonempty": len(id2entity) > 0,
        "relation2id_nonempty": len(relation2id) > 0,
        "id2relation_nonempty": len(id2relation) > 0,
        "entity_map_size_match": len(entity2id) == len(id2entity),
        "relation_map_size_match": len(relation2id) == len(id2relation),
        "train_missing_field_zero": train_stats["required_field_missing_count"] == 0,
        "valid_missing_field_zero": valid_stats["required_field_missing_count"] == 0,
        "test_missing_field_zero": test_stats["required_field_missing_count"] == 0,
        "train_gold_in_candidate_all": train_stats["gold_in_candidate_count"] == len(train_data),
        "valid_gold_in_candidate_all": valid_stats["gold_in_candidate_count"] == len(valid_data),
        "test_gold_in_candidate_all": test_stats["gold_in_candidate_count"] == len(test_data),
        "train_id_mismatch_zero": train_stats["id_mismatch_count"] == 0,
        "valid_id_mismatch_zero": valid_stats["id_mismatch_count"] == 0,
        "test_id_mismatch_zero": test_stats["id_mismatch_count"] == 0,
    }

    if use_type_map:
        global_checks.update({
            "train_candidates_all_drug": train_stats["all_candidates_are_drug_count"] == train_stats["candidate_type_checkable_count"],
            "valid_candidates_all_drug": valid_stats["all_candidates_are_drug_count"] == valid_stats["candidate_type_checkable_count"],
            "test_candidates_all_drug": test_stats["all_candidates_are_drug_count"] == test_stats["candidate_type_checkable_count"],
        })

    all_ok = all(global_checks.values())

    # Copy or symlink artifacts
    dst_files = {
        "train.json": dst_dir / "train.json",
        "valid.json": dst_dir / "valid.json",
        "test.json": dst_dir / "test.json",
        "entity2id.pkl": dst_dir / "entity2id.pkl",
        "id2entity.pkl": dst_dir / "id2entity.pkl",
        "relation2id.pkl": dst_dir / "relation2id.pkl",
        "id2relation.pkl": dst_dir / "id2relation.pkl",
    }

    safe_link_or_copy(train_src, dst_files["train.json"], args.link_mode)
    safe_link_or_copy(valid_src, dst_files["valid.json"], args.link_mode)
    safe_link_or_copy(test_src, dst_files["test.json"], args.link_mode)
    safe_link_or_copy(entity2id_path, dst_files["entity2id.pkl"], args.link_mode)
    safe_link_or_copy(id2entity_path, dst_files["id2entity.pkl"], args.link_mode)
    safe_link_or_copy(relation2id_path, dst_files["relation2id.pkl"], args.link_mode)
    safe_link_or_copy(id2relation_path, dst_files["id2relation.pkl"], args.link_mode)

    manifest = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "week": 5,
        "day": 2,
        "purpose": "Check if the backbone-ready package is properly prepared for month-2 reproduction.",
        "source_files": {
            "train_json": rel(train_src),
            "valid_json": rel(valid_src),
            "test_json": rel(test_src),
            "entity2id": rel(entity2id_path),
            "id2entity": rel(id2entity_path),
            "relation2id": rel(relation2id_path),
            "id2relation": rel(id2relation_path),
            "type_map": rel(type_map_path) if use_type_map else None,
            "split_meta": rel(split_meta_path),
        },
        "destination_dir": rel(dst_dir),
        "link_mode": args.link_mode,
        "split_meta": split_meta,
        "num_entities": len(entity2id),
        "num_relations": len(relation2id),
        "global_checks": global_checks,
        "all_ok": all_ok,
        "split_summaries": {
            "train": train_stats,
            "valid": valid_stats,
            "test": test_stats,
        },
        "notes": {
            "candidate_k_train": train_stats["candidate_len_max"],
            "candidate_k_valid": valid_stats["candidate_len_max"],
            "candidate_k_test": test_stats["candidate_len_max"],
            "embedding_file_status": "Pending day 3: entity_embeddings_rgcn.pt will be added after R-GCN export.",
        },
    }

    save_json(manifest_path, manifest)

    report = f"""# Day 2 Backbone-Ready Report

## 1. Goal
Check if a **full Setting-A backbone-ready package** is properly prepared for week-5 reproduction,
without mixing it with pilot-only artifacts.

## 2. Source files
- train: `{rel(train_src)}`
- valid: `{rel(valid_src)}`
- test: `{rel(test_src)}`
- entity2id: `{rel(entity2id_path)}`
- id2entity: `{rel(id2entity_path)}`
- relation2id: `{rel(relation2id_path)}`
- id2relation: `{rel(id2relation_path)}`
- split_meta: `{rel(split_meta_path)}`
- type_map: `{rel(type_map_path) if use_type_map else "NOT FOUND (type audit skipped)"}`

## 3. Destination
- `{rel(dst_dir)}`

## 4. Global checks
""" + "\n".join([f"- [{'x' if v else ' '}] {k}" for k, v in global_checks.items()]) + f"""

## 5. Split summaries

### Train
- num_samples: {train_stats['num_samples']}
- candidate_len_min/max: {train_stats['candidate_len_min']} / {train_stats['candidate_len_max']}
- subgraph_len_min/max: {train_stats['subgraph_len_min']} / {train_stats['subgraph_len_max']}
- required_field_missing_count: {train_stats['required_field_missing_count']}
- subgraph_empty_count: {train_stats['subgraph_empty_count']}
- gold_in_candidate_count: {train_stats['gold_in_candidate_count']}
- id_mismatch_count: {train_stats['id_mismatch_count']}
- candidate_type_checkable_count: {train_stats['candidate_type_checkable_count']}
- all_candidates_are_drug_count: {train_stats['all_candidates_are_drug_count']}

### Valid
- num_samples: {valid_stats['num_samples']}
- candidate_len_min/max: {valid_stats['candidate_len_min']} / {valid_stats['candidate_len_max']}
- subgraph_len_min/max: {valid_stats['subgraph_len_min']} / {valid_stats['subgraph_len_max']}
- required_field_missing_count: {valid_stats['required_field_missing_count']}
- subgraph_empty_count: {valid_stats['subgraph_empty_count']}
- gold_in_candidate_count: {valid_stats['gold_in_candidate_count']}
- id_mismatch_count: {valid_stats['id_mismatch_count']}
- candidate_type_checkable_count: {valid_stats['candidate_type_checkable_count']}
- all_candidates_are_drug_count: {valid_stats['all_candidates_are_drug_count']}

### Test
- num_samples: {test_stats['num_samples']}
- candidate_len_min/max: {test_stats['candidate_len_min']} / {test_stats['candidate_len_max']}
- subgraph_len_min/max: {test_stats['subgraph_len_min']} / {test_stats['subgraph_len_max']}
- required_field_missing_count: {test_stats['required_field_missing_count']}
- subgraph_empty_count: {test_stats['subgraph_empty_count']}
- gold_in_candidate_count: {test_stats['gold_in_candidate_count']}
- id_mismatch_count: {test_stats['id_mismatch_count']}
- candidate_type_checkable_count: {test_stats['candidate_type_checkable_count']}
- all_candidates_are_drug_count: {test_stats['all_candidates_are_drug_count']}

## 6. Example samples
### Train examples
{json.dumps(train_stats['sample_examples'], ensure_ascii=False, indent=2)}

### Valid examples
{json.dumps(valid_stats['sample_examples'], ensure_ascii=False, indent=2)}

### Test examples
{json.dumps(test_stats['sample_examples'], ensure_ascii=False, indent=2)}

## 7. Warning examples
### Missing fields
{json.dumps({
    "train": train_stats["required_field_missing_examples"],
    "valid": valid_stats["required_field_missing_examples"],
    "test": test_stats["required_field_missing_examples"],
}, ensure_ascii=False, indent=2)}

### Candidate non-drug examples
{json.dumps({
    "train": train_stats["candidate_non_drug_examples"],
    "valid": valid_stats["candidate_non_drug_examples"],
    "test": test_stats["candidate_non_drug_examples"],
}, ensure_ascii=False, indent=2)}

### Rank-name mismatch examples
{json.dumps({
    "train": train_stats["rank_name_match_fail_examples"],
    "valid": valid_stats["rank_name_match_fail_examples"],
    "test": test_stats["rank_name_match_fail_examples"],
}, ensure_ascii=False, indent=2)}

## 8. Judgment
**{'READY' if all_ok else 'NOT READY'}** for day-3 real embedding export.

## 9. Next step
Day 3 will export the first real embedding source:
`dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt`
"""

    save_text(report_path, report)

    print("\nSaved backbone-ready package:")
    for k, v in dst_files.items():
        print(f"  - {rel(v)}")

    print(f"\nSaved manifest: {rel(manifest_path)}")
    print(f"Saved report  : {rel(report_path)}")

    print("\nGlobal checks:")
    for k, v in global_checks.items():
        print(f"  - {k}: {v}")

    if all_ok:
        print("\n[OK] Day-2 backbone-ready packaging passed.")
        print("You can move to day 3 after manually reviewing the report.")
    else:
        print("\n[WARN] Day-2 packaging finished, but some checks failed.")
        print("Do NOT move to day 3 until the failed checks are understood and fixed.")


if __name__ == "__main__":
    main()