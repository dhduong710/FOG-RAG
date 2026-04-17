#!/usr/bin/env python3
import argparse
import csv
import json
import pickle
from collections import Counter
from pathlib import Path

import numpy as np
import torch


def load_pickle(path: Path):
    with path.open("rb") as f:
        return pickle.load(f)


def read_tsv_triples(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        all_rows = list(reader)

    if not all_rows:
        return rows

    # support both header / no-header
    start = 1 if all_rows[0][:3] == ["head", "relation", "tail"] else 0
    for row in all_rows[start:]:
        if len(row) < 3:
            continue
        rows.append({
            "head": row[0],
            "relation": row[1],
            "tail": row[2],
        })
    return rows


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj):
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def extract_score_tensor(obj):
    # direct tensor
    if isinstance(obj, torch.Tensor):
        return obj

    if isinstance(obj, np.ndarray):
        return torch.from_numpy(obj)

    # dict-like containers
    if isinstance(obj, dict):
        candidate_keys = [
            "scores",
            "score_matrix",
            "logits",
            "all_scores",
            "valid_scores",
            "tensor",
        ]
        for k in candidate_keys:
            if k in obj:
                v = obj[k]
                if isinstance(v, torch.Tensor):
                    return v
                if isinstance(v, np.ndarray):
                    return torch.from_numpy(v)

    raise ValueError("Cannot extract score tensor from score file.")


def recursively_find_candidate_lists(obj, target_len=None):
    found = []

    def walk(x, path="root"):
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, f"{path}.{k}")
        elif isinstance(x, list):
            if len(x) > 0 and all(isinstance(i, int) for i in x):
                if target_len is None or len(x) == target_len:
                    found.append((path, x))
            else:
                for idx, v in enumerate(x):
                    walk(v, f"{path}[{idx}]")

    walk(obj)
    return found


def extract_universe_ids_from_meta(meta, num_cols):
    preferred_key_words = [
        "drug_universe",
        "candidate_universe",
        "universe_entity_ids",
        "candidate_entity_ids",
        "drug_entity_ids",
        "all_candidate_ids",
    ]

    # first: exact-ish keyword search on top level
    if isinstance(meta, dict):
        for k, v in meta.items():
            if isinstance(v, list) and len(v) == num_cols and all(isinstance(i, int) for i in v):
                lk = k.lower()
                if any(word in lk for word in preferred_key_words):
                    return v, f"meta_top_level:{k}"

    # second: recursive search
    all_lists = recursively_find_candidate_lists(meta, target_len=num_cols)
    for path, arr in all_lists:
        pl = path.lower()
        if any(word in pl for word in preferred_key_words):
            return arr, f"meta_recursive:{path}"

    # third: unique candidate if only one exists
    if len(all_lists) == 1:
        return all_lists[0][1], f"meta_single_candidate:{all_lists[0][0]}"

    return None, None


def fallback_drug_universe_ids(raw_indication_tsv: Path, entity2id: dict, num_cols: int):
    rows = read_tsv_triples(raw_indication_tsv)
    drug_names = sorted({r["head"] for r in rows})
    drug_ids = []
    missing = []
    for name in drug_names:
        if name in entity2id:
            drug_ids.append(int(entity2id[name]))
        else:
            missing.append(name)

    drug_ids = sorted(drug_ids)
    if len(drug_ids) != num_cols:
        raise ValueError(
            f"Fallback drug universe size mismatch: derived={len(drug_ids)} vs score_cols={num_cols}"
        )
    return drug_ids, missing


def compute_ranks(score_matrix, gold_ids, universe_ids):
    col_of_entity = {eid: idx for idx, eid in enumerate(universe_ids)}

    gold_ranks = []
    top1_col = []
    top5_cols = []

    scores_np = score_matrix.detach().cpu().float().numpy()

    for i in range(scores_np.shape[0]):
        row = scores_np[i]
        gold_id = gold_ids[i]
        if gold_id not in col_of_entity:
            raise ValueError(f"Gold entity id {gold_id} not found in universe ids.")

        gold_col = col_of_entity[gold_id]
        gold_score = row[gold_col]

        # rank = 1 + number of scores strictly greater than gold
        rank = int(1 + np.sum(row > gold_score))
        gold_ranks.append(rank)

        sorted_cols = np.argsort(-row)
        top1_col.append(int(sorted_cols[0]))
        top5_cols.append([int(x) for x in sorted_cols[:5]])

    return gold_ranks, top1_col, top5_cols


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--score_path", default="dataset/setting_a/11_ranker_v2/valid_scores.pt")
    parser.add_argument("--meta_path", default="dataset/setting_a/11_ranker_v2/score_dump_meta.json")
    parser.add_argument("--valid_tsv", default="dataset/setting_a/01_split/valid.tsv")
    parser.add_argument("--raw_indication_tsv", default="dataset/setting_a/00_raw_triples/primekg_indication_only.tsv")
    parser.add_argument("--entity2id_pkl", default="dataset/setting_a/04_drkgc_json/entity2id.pkl")
    parser.add_argument("--id2entity_pkl", default="dataset/setting_a/04_drkgc_json/id2entity.pkl")
    parser.add_argument("--out_dir", default="dataset/setting_a/17_structure_baselines")
    parser.add_argument("--report_path", default="reports/week8/day2_rgcn_baseline.md")
    args = parser.parse_args()

    score_path = Path(args.score_path)
    meta_path = Path(args.meta_path)
    valid_tsv = Path(args.valid_tsv)
    raw_indication_tsv = Path(args.raw_indication_tsv)
    entity2id_pkl = Path(args.entity2id_pkl)
    id2entity_pkl = Path(args.id2entity_pkl)
    out_dir = Path(args.out_dir)
    report_path = Path(args.report_path)

    out_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    entity2id = load_pickle(entity2id_pkl)
    id2entity = load_pickle(id2entity_pkl)

    valid_rows = read_tsv_triples(valid_tsv)
    if len(valid_rows) != 500:
        print(f"WARNING: valid rows detected = {len(valid_rows)} (expected 500)")

    raw_score_obj = torch.load(score_path, map_location="cpu")
    score_tensor = extract_score_tensor(raw_score_obj).float()

    if score_tensor.ndim != 2:
        raise ValueError(f"Score tensor must be 2D, got shape {tuple(score_tensor.shape)}")

    num_queries, num_cols = score_tensor.shape
    if num_queries != len(valid_rows):
        raise ValueError(
            f"Score rows and valid queries mismatch: score_rows={num_queries}, valid_rows={len(valid_rows)}"
        )

    meta = load_json(meta_path) if meta_path.exists() else {}
    universe_ids, universe_source = extract_universe_ids_from_meta(meta, num_cols)

    fallback_used = False
    fallback_missing_names = []
    if universe_ids is None:
        universe_ids, fallback_missing_names = fallback_drug_universe_ids(
            raw_indication_tsv=raw_indication_tsv,
            entity2id=entity2id,
            num_cols=num_cols,
        )
        universe_source = "fallback_from_raw_indication_heads_sorted_by_entity_id"
        fallback_used = True

    gold_ids = []
    for row in valid_rows:
        head_name = row["head"]
        if head_name not in entity2id:
            raise ValueError(f"Gold head not found in entity2id: {head_name}")
        gold_ids.append(int(entity2id[head_name]))

    gold_ranks, top1_cols, top5_cols = compute_ranks(score_tensor, gold_ids, universe_ids)

    top1_ids = [int(universe_ids[c]) for c in top1_cols]
    top1_names = [id2entity[x] for x in top1_ids]
    top1_counter = Counter(top1_names)

    metrics = {
        "method": "R-GCN",
        "protocol": "Setting A structure-only baseline",
        "source_score_path": str(score_path),
        "source_meta_path": str(meta_path),
        "universe_source": universe_source,
        "fallback_used": fallback_used,
        "num_valid_queries": int(num_queries),
        "drug_universe_size": int(num_cols),
        "mrr": round(float(np.mean(1.0 / np.array(gold_ranks))), 8),
        "hits1": round(float(np.mean(np.array(gold_ranks) <= 1)), 8),
        "hits3": round(float(np.mean(np.array(gold_ranks) <= 3)), 8),
        "hits10": round(float(np.mean(np.array(gold_ranks) <= 10)), 8),
        "top1_dominance_ratio": round(float(max(top1_counter.values()) / num_queries), 8),
        "unique_top1_count": int(len(top1_counter)),
        "warning": (
            "Fallback universe order was used; verify top1 names carefully."
            if fallback_used else ""
        ),
    }

    case_samples = []
    for i in range(min(10, num_queries)):
        top5_names = [id2entity[int(universe_ids[c])] for c in top5_cols[i]]
        case_samples.append({
            "idx": i,
            "query_disease": valid_rows[i]["tail"],
            "gold_drug": valid_rows[i]["head"],
            "gold_rank": int(gold_ranks[i]),
            "top1_pred": top1_names[i],
            "top5_pred": top5_names,
        })

    # save standardized outputs
    torch.save(score_tensor, out_dir / "rgcn_valid_scores.pt")
    save_json(out_dir / "rgcn_valid_metrics.json", metrics)
    save_json(out_dir / "rgcn_valid_case_samples.json", case_samples)

    with (out_dir / "rgcn_valid_top1_frequency.tsv").open("w", encoding="utf-8") as f:
        f.write("drug\tcount\tratio\n")
        for drug, count in top1_counter.most_common():
            ratio = count / num_queries
            f.write(f"{drug}\t{count}\t{ratio:.8f}\n")

    report_md = []
    report_md.append("# Day 2 R-GCN Structure Baseline")
    report_md.append("")
    report_md.append("## 1. Scope")
    report_md.append("- Clean evaluation of existing R-GCN structure scorer on Setting A")
    report_md.append("- Full drug-only universe")
    report_md.append("- Valid split only")
    report_md.append("")
    report_md.append("## 2. Source")
    report_md.append(f"- score_path: `{score_path}`")
    report_md.append(f"- meta_path: `{meta_path}`")
    report_md.append(f"- universe_source: `{universe_source}`")
    report_md.append(f"- fallback_used: `{fallback_used}`")
    report_md.append("")
    report_md.append("## 3. Main metrics")
    report_md.append(f"- MRR: {metrics['mrr']}")
    report_md.append(f"- Hits@1: {metrics['hits1']}")
    report_md.append(f"- Hits@3: {metrics['hits3']}")
    report_md.append(f"- Hits@10: {metrics['hits10']}")
    report_md.append("")
    report_md.append("## 4. Supporting analysis")
    report_md.append(f"- top1_dominance_ratio: {metrics['top1_dominance_ratio']}")
    report_md.append(f"- unique_top1_count: {metrics['unique_top1_count']}")
    report_md.append("")
    report_md.append("## 5. Output files")
    report_md.append(f"- `{out_dir / 'rgcn_valid_scores.pt'}`")
    report_md.append(f"- `{out_dir / 'rgcn_valid_metrics.json'}`")
    report_md.append(f"- `{out_dir / 'rgcn_valid_top1_frequency.tsv'}`")
    report_md.append(f"- `{out_dir / 'rgcn_valid_case_samples.json'}`")
    report_md.append("")
    if fallback_used:
        report_md.append("## 6. Warning")
        report_md.append("- Universe ids were reconstructed from raw indication heads.")
        report_md.append("- Re-check top1 names manually before freezing this row into table v0.")
        if fallback_missing_names:
            report_md.append(f"- Missing names during fallback mapping: {len(fallback_missing_names)}")
            report_md.append("")
    report_md.append("## 7. Conclusion")
    report_md.append("- R-GCN clean structure-only evaluation completed on valid split.")

    report_path.write_text("\n".join(report_md), encoding="utf-8")

    print("Saved:")
    print(f"- {out_dir / 'rgcn_valid_scores.pt'}")
    print(f"- {out_dir / 'rgcn_valid_metrics.json'}")
    print(f"- {out_dir / 'rgcn_valid_top1_frequency.tsv'}")
    print(f"- {out_dir / 'rgcn_valid_case_samples.json'}")
    print(f"- {report_path}")
    print()
    print("Main metrics:")
    print(json.dumps({
        "mrr": metrics["mrr"],
        "hits1": metrics["hits1"],
        "hits3": metrics["hits3"],
        "hits10": metrics["hits10"],
        "top1_dominance_ratio": metrics["top1_dominance_ratio"],
        "unique_top1_count": metrics["unique_top1_count"],
        "fallback_used": metrics["fallback_used"],
        "universe_source": metrics["universe_source"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()