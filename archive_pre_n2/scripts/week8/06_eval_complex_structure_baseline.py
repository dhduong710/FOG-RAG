#!/usr/bin/env python3
import argparse
import csv
import json
import pickle
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn


def load_pickle(path: Path):
    with path.open("rb") as f:
        return pickle.load(f)


def save_json(path: Path, obj):
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def read_tsv(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        raw_rows = list(reader)

    if not raw_rows:
        return rows

    start = 1 if raw_rows[0][:3] == ["head", "relation", "tail"] else 0
    for row in raw_rows[start:]:
        if len(row) < 3:
            continue
        rows.append((row[0], row[1], row[2]))
    return rows


def read_queries(split_tsv: Path, entity2id: dict):
    rows = read_tsv(split_tsv)
    queries = []
    for h, r, t in rows:
        if h not in entity2id or t not in entity2id:
            continue
        queries.append({
            "gold_drug": h,
            "relation": r,
            "query_disease": t,
            "gold_drug_id": int(entity2id[h]),
            "query_disease_id": int(entity2id[t]),
        })
    return queries


def derive_drug_universe_ids(raw_indication_tsv: Path, entity2id: dict):
    rows = read_tsv(raw_indication_tsv)
    drug_names = sorted({h for h, _, _ in rows})
    drug_ids = [int(entity2id[name]) for name in drug_names if name in entity2id]
    return sorted(drug_ids), drug_names


class ComplExModel(nn.Module):
    def __init__(self, num_entities, num_relations, embedding_dim=200, dropout=0.1):
        super().__init__()
        self.ent_re = nn.Embedding(num_entities, embedding_dim)
        self.ent_im = nn.Embedding(num_entities, embedding_dim)
        self.rel_re = nn.Embedding(num_relations, embedding_dim)
        self.rel_im = nn.Embedding(num_relations, embedding_dim)
        self.dropout = nn.Dropout(dropout)

    def score_head_candidates(self, relation_id, tail_ids, candidate_head_ids):
        h_re = self.ent_re(candidate_head_ids)  # [U, D]
        h_im = self.ent_im(candidate_head_ids)  # [U, D]

        r_re = self.rel_re(torch.tensor([relation_id], device=tail_ids.device)).squeeze(0)  # [D]
        r_im = self.rel_im(torch.tensor([relation_id], device=tail_ids.device)).squeeze(0)  # [D]

        t_re = self.ent_re(tail_ids)  # [B, D]
        t_im = self.ent_im(tail_ids)  # [B, D]

        coef_re = t_re * r_re.unsqueeze(0) + t_im * r_im.unsqueeze(0)
        coef_im = t_im * r_re.unsqueeze(0) - t_re * r_im.unsqueeze(0)

        scores = coef_re @ h_re.T + coef_im @ h_im.T
        return scores


def compute_metrics_and_cases(score_matrix, valid_queries, drug_universe_ids, id2entity):
    score_np = score_matrix.detach().cpu().numpy()
    col_of_drug = {int(eid): idx for idx, eid in enumerate(drug_universe_ids)}

    ranks = []
    top1_names = []
    case_samples = []

    for i, ex in enumerate(valid_queries):
        row = score_np[i]
        gold_id = int(ex["gold_drug_id"])
        gold_col = col_of_drug[gold_id]
        gold_score = row[gold_col]

        rank = int(1 + np.sum(row > gold_score))
        ranks.append(rank)

        sorted_cols = np.argsort(-row)
        top1_col = int(sorted_cols[0])
        top1_id = int(drug_universe_ids[top1_col])
        top1_name = id2entity[top1_id]
        top1_names.append(top1_name)

        if i < 10:
            top5 = [id2entity[int(drug_universe_ids[c])] for c in sorted_cols[:5]]
            case_samples.append({
                "idx": i,
                "query_disease": ex["query_disease"],
                "gold_drug": ex["gold_drug"],
                "gold_rank": rank,
                "top1_pred": top1_name,
                "top5_pred": top5,
            })

    cnt = Counter(top1_names)
    metrics = {
        "method": "ComplEx",
        "protocol": "Setting A structure-only baseline",
        "num_valid_queries": len(valid_queries),
        "drug_universe_size": len(drug_universe_ids),
        "mrr": round(float(np.mean(1.0 / np.array(ranks))), 8),
        "hits1": round(float(np.mean(np.array(ranks) <= 1)), 8),
        "hits3": round(float(np.mean(np.array(ranks) <= 3)), 8),
        "hits10": round(float(np.mean(np.array(ranks) <= 10)), 8),
        "top1_dominance_ratio": round(float(max(cnt.values()) / len(valid_queries)), 8),
        "unique_top1_count": int(len(cnt)),
    }
    return metrics, cnt, case_samples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint_path", default="results/week8/complex_baseline_full_v1/complex_checkpoint.pt")
    parser.add_argument("--meta_path", default="results/week8/complex_baseline_full_v1/complex_meta.json")
    parser.add_argument("--valid_queries_path", default="dataset/setting_a/01_split/valid.tsv")
    parser.add_argument("--raw_indication_path", default="dataset/setting_a/00_raw_triples/primekg_indication_only.tsv")
    parser.add_argument("--entity2id_path", default="dataset/setting_a/04_drkgc_json/entity2id.pkl")
    parser.add_argument("--id2entity_path", default="dataset/setting_a/04_drkgc_json/id2entity.pkl")
    parser.add_argument("--out_dir", default="dataset/setting_a/17_structure_baselines")
    parser.add_argument("--report_path", default="reports/week8/day5_complex_or_transe.md")
    args = parser.parse_args()

    checkpoint_path = Path(args.checkpoint_path)
    meta_path = Path(args.meta_path)
    valid_queries_path = Path(args.valid_queries_path)
    raw_indication_path = Path(args.raw_indication_path)
    entity2id_path = Path(args.entity2id_path)
    id2entity_path = Path(args.id2entity_path)
    out_dir = Path(args.out_dir)
    report_path = Path(args.report_path)

    out_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    meta = json.load(open(meta_path, "r", encoding="utf-8"))
    entity2id = load_pickle(entity2id_path)
    id2entity = load_pickle(id2entity_path)

    valid_queries = read_queries(valid_queries_path, entity2id)
    drug_universe_ids, _ = derive_drug_universe_ids(raw_indication_path, entity2id)

    num_entities = meta["num_entities"]
    num_relations = meta["num_relations"]
    indication_rel_id = meta["indication_rel_id"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = ComplExModel(
        num_entities=num_entities,
        num_relations=num_relations,
        embedding_dim=meta["embedding_dim"],
        dropout=meta["dropout"],
    ).to(device)

    ckpt = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    with torch.no_grad():
        tail_ids = torch.tensor([x["query_disease_id"] for x in valid_queries], dtype=torch.long, device=device)
        cand_ids = torch.tensor(drug_universe_ids, dtype=torch.long, device=device)
        scores = model.score_head_candidates(indication_rel_id, tail_ids, cand_ids)

    metrics, top1_counter, case_samples = compute_metrics_and_cases(
        score_matrix=scores,
        valid_queries=valid_queries,
        drug_universe_ids=drug_universe_ids,
        id2entity=id2entity,
    )

    metrics["checkpoint_path"] = str(checkpoint_path)
    metrics["checkpoint_best_epoch"] = ckpt.get("best_epoch")
    metrics["meta_path"] = str(meta_path)
    metrics["valid_queries_path"] = str(valid_queries_path)
    metrics["device"] = str(device)

    torch.save(scores.detach().cpu(), out_dir / "complex_valid_scores.pt")
    save_json(out_dir / "complex_valid_metrics.json", metrics)
    save_json(out_dir / "complex_valid_case_samples.json", case_samples)

    with (out_dir / "complex_valid_top1_frequency.tsv").open("w", encoding="utf-8") as f:
        f.write("drug\tcount\tratio\n")
        for drug, count in top1_counter.most_common():
            ratio = count / len(valid_queries)
            f.write(f"{drug}\t{count}\t{ratio:.8f}\n")

    report_md = []
    report_md.append("# Day 5 ComplEx / TransE")
    report_md.append("")
    report_md.append("## 1. Scope")
    report_md.append("- Train and evaluate ComplEx structure-only baseline")
    report_md.append("- Keep the same Setting A structure-only protocol")
    report_md.append("")
    report_md.append("## 2. ComplEx sources")
    report_md.append(f"- checkpoint_path: `{checkpoint_path}`")
    report_md.append(f"- checkpoint_best_epoch: {ckpt.get('best_epoch')}")
    report_md.append(f"- meta_path: `{meta_path}`")
    report_md.append("")
    report_md.append("## 3. ComplEx main metrics")
    report_md.append(f"- MRR: {metrics['mrr']}")
    report_md.append(f"- Hits@1: {metrics['hits1']}")
    report_md.append(f"- Hits@3: {metrics['hits3']}")
    report_md.append(f"- Hits@10: {metrics['hits10']}")
    report_md.append("")
    report_md.append("## 4. Supporting analysis")
    report_md.append(f"- top1_dominance_ratio: {metrics['top1_dominance_ratio']}")
    report_md.append(f"- unique_top1_count: {metrics['unique_top1_count']}")
    report_md.append("")
    report_md.append("## 5. Current decision")
    report_md.append("- ComplEx is the preferred baseline #3.")
    report_md.append("- TransE remains optional if there is still enough time after table v0 is stable.")
    report_md.append("")
    report_md.append("## 6. Output files")
    report_md.append(f"- `{out_dir / 'complex_valid_scores.pt'}`")
    report_md.append(f"- `{out_dir / 'complex_valid_metrics.json'}`")
    report_md.append(f"- `{out_dir / 'complex_valid_top1_frequency.tsv'}`")
    report_md.append(f"- `{out_dir / 'complex_valid_case_samples.json'}`")

    report_path.write_text("\n".join(report_md), encoding="utf-8")

    print("Saved:")
    print(f"- {out_dir / 'complex_valid_scores.pt'}")
    print(f"- {out_dir / 'complex_valid_metrics.json'}")
    print(f"- {out_dir / 'complex_valid_top1_frequency.tsv'}")
    print(f"- {out_dir / 'complex_valid_case_samples.json'}")
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
        "checkpoint_best_epoch": metrics["checkpoint_best_epoch"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()