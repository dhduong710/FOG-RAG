#!/usr/bin/env python3
import argparse
import csv
import json
import pickle
import random
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


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


def build_triple_ids(rows, entity2id, relation2id):
    triples = []
    skipped = 0
    for h, r, t in rows:
        if h not in entity2id or t not in entity2id or r not in relation2id:
            skipped += 1
            continue
        triples.append((int(entity2id[h]), int(relation2id[r]), int(entity2id[t])))
    return triples, skipped


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

        nn.init.xavier_uniform_(self.ent_re.weight)
        nn.init.xavier_uniform_(self.ent_im.weight)
        nn.init.xavier_uniform_(self.rel_re.weight)
        nn.init.xavier_uniform_(self.rel_im.weight)

    def score_triples(self, h_idx, r_idx, t_idx):
        h_re = self.ent_re(h_idx)
        h_im = self.ent_im(h_idx)
        r_re = self.rel_re(r_idx)
        r_im = self.rel_im(r_idx)
        t_re = self.ent_re(t_idx)
        t_im = self.ent_im(t_idx)

        h_re = self.dropout(h_re)
        h_im = self.dropout(h_im)
        r_re = self.dropout(r_re)
        r_im = self.dropout(r_im)
        t_re = self.dropout(t_re)
        t_im = self.dropout(t_im)

        score = torch.sum(
            h_re * r_re * t_re
            + h_re * r_im * t_im
            + h_im * r_re * t_im
            - h_im * r_im * t_re,
            dim=-1
        )
        return score

    def score_head_candidates(self, relation_id, tail_ids, candidate_head_ids):
        """
        relation_id: int
        tail_ids: [B]
        candidate_head_ids: [U]
        return: [B, U]
        """
        h_re = self.ent_re(candidate_head_ids)  # [U, D]
        h_im = self.ent_im(candidate_head_ids)  # [U, D]

        r_re = self.rel_re(torch.tensor([relation_id], device=tail_ids.device)).squeeze(0)  # [D]
        r_im = self.rel_im(torch.tensor([relation_id], device=tail_ids.device)).squeeze(0)  # [D]

        t_re = self.ent_re(tail_ids)  # [B, D]
        t_im = self.ent_im(tail_ids)  # [B, D]

        # score = sum(h_re*(r_re*t_re + r_im*t_im) + h_im*(r_re*t_im - r_im*t_re))
        coef_re = t_re * r_re.unsqueeze(0) + t_im * r_im.unsqueeze(0)   # [B, D]
        coef_im = t_im * r_re.unsqueeze(0) - t_re * r_im.unsqueeze(0)   # [B, D]

        scores = coef_re @ h_re.T + coef_im @ h_im.T  # [B, U]
        return scores


def compute_probe_metrics(model, valid_queries, indication_rel_id, drug_universe_ids, id2entity, device, max_queries=None):
    model.eval()
    rows = valid_queries[:max_queries] if (max_queries is not None and max_queries > 0) else valid_queries
    with torch.no_grad():
        tail_ids = torch.tensor([x["query_disease_id"] for x in rows], dtype=torch.long, device=device)
        cand_ids = torch.tensor(drug_universe_ids, dtype=torch.long, device=device)
        scores = model.score_head_candidates(indication_rel_id, tail_ids, cand_ids)
        scores_np = scores.detach().cpu().numpy()

    col_of_drug = {int(eid): idx for idx, eid in enumerate(drug_universe_ids)}
    ranks = []
    top1_names = []

    for i, ex in enumerate(rows):
        gold_id = int(ex["gold_drug_id"])
        gold_col = col_of_drug[gold_id]
        row = scores_np[i]
        gold_score = row[gold_col]
        rank = int(1 + np.sum(row > gold_score))
        ranks.append(rank)

        top1_col = int(np.argmax(row))
        top1_id = int(drug_universe_ids[top1_col])
        top1_names.append(id2entity[top1_id])

    cnt = Counter(top1_names)
    return {
        "probe_mrr": round(float(np.mean(1.0 / np.array(ranks))), 8),
        "probe_hits10": round(float(np.mean(np.array(ranks) <= 10)), 8),
        "probe_top1_dominance_ratio": round(float(max(cnt.values()) / len(rows)), 8),
        "probe_unique_top1_count": int(len(cnt)),
    }


def train_one_epoch(model, triples, optimizer, num_entities, device, batch_size, num_negatives):
    model.train()
    random.shuffle(triples)
    losses = []

    for start in range(0, len(triples), batch_size):
        batch = triples[start:start + batch_size]
        h = torch.tensor([x[0] for x in batch], dtype=torch.long, device=device)
        r = torch.tensor([x[1] for x in batch], dtype=torch.long, device=device)
        t = torch.tensor([x[2] for x in batch], dtype=torch.long, device=device)

        pos_scores = model.score_triples(h, r, t)

        neg_heads = h.unsqueeze(1).repeat(1, num_negatives)
        neg_rels = r.unsqueeze(1).repeat(1, num_negatives)
        neg_tails = t.unsqueeze(1).repeat(1, num_negatives)

        corrupt_head_mask = torch.rand((len(batch), num_negatives), device=device) < 0.5
        random_entities = torch.randint(0, num_entities, (len(batch), num_negatives), device=device)

        neg_heads = torch.where(corrupt_head_mask, random_entities, neg_heads)
        neg_tails = torch.where(~corrupt_head_mask, random_entities, neg_tails)

        neg_scores = model.score_triples(
            neg_heads.reshape(-1),
            neg_rels.reshape(-1),
            neg_tails.reshape(-1),
        ).reshape(len(batch), num_negatives)

        pos_loss = F.softplus(-pos_scores).mean()
        neg_loss = F.softplus(neg_scores).mean()
        loss = pos_loss + neg_loss

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        losses.append(float(loss.item()))

    return {
        "train_loss": round(float(np.mean(losses)), 8) if losses else None,
        "num_batches": int(np.ceil(len(triples) / batch_size)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph_path", default="dataset/setting_a/02_graph/train_enriched_deg1000_final.tsv")
    parser.add_argument("--train_queries_path", default="dataset/setting_a/01_split/train.tsv")
    parser.add_argument("--valid_queries_path", default="dataset/setting_a/01_split/valid.tsv")
    parser.add_argument("--raw_indication_path", default="dataset/setting_a/00_raw_triples/primekg_indication_only.tsv")
    parser.add_argument("--entity2id_path", default="dataset/setting_a/04_drkgc_json/entity2id.pkl")
    parser.add_argument("--relation2id_path", default="dataset/setting_a/04_drkgc_json/relation2id.pkl")
    parser.add_argument("--id2entity_path", default="dataset/setting_a/04_drkgc_json/id2entity.pkl")
    parser.add_argument("--out_dir", default="results/week8/complex_baseline_full_v1")
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--embedding_dim", type=int, default=200)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--learning_rate", type=float, default=1e-3)
    parser.add_argument("--weight_decay", type=float, default=1e-6)
    parser.add_argument("--num_epochs", type=int, default=40)
    parser.add_argument("--batch_size", type=int, default=1024)
    parser.add_argument("--num_negatives", type=int, default=16)
    parser.add_argument("--valid_probe_size", type=int, default=256)
    parser.add_argument("--early_stop", type=int, default=8)
    parser.add_argument("--max_train_queries", type=int, default=0)
    parser.add_argument("--max_valid_queries", type=int, default=0)
    args = parser.parse_args()

    set_seed(args.seed)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "complex_train_log.jsonl"
    ckpt_path = out_dir / "complex_checkpoint.pt"
    meta_path = out_dir / "complex_meta.json"

    entity2id = load_pickle(Path(args.entity2id_path))
    relation2id = load_pickle(Path(args.relation2id_path))
    id2entity = load_pickle(Path(args.id2entity_path))

    graph_rows = read_tsv(Path(args.graph_path))
    graph_triples, skipped = build_triple_ids(graph_rows, entity2id, relation2id)

    train_queries = read_queries(Path(args.train_queries_path), entity2id)
    valid_queries = read_queries(Path(args.valid_queries_path), entity2id)

    if args.max_train_queries > 0:
        train_queries = train_queries[:args.max_train_queries]
    if args.max_valid_queries > 0:
        valid_queries = valid_queries[:args.max_valid_queries]

    drug_universe_ids, _ = derive_drug_universe_ids(Path(args.raw_indication_path), entity2id)

    num_entities = max(entity2id.values()) + 1
    num_relations = max(relation2id.values()) + 1
    indication_rel_id = int(relation2id["indication"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ComplExModel(
        num_entities=num_entities,
        num_relations=num_relations,
        embedding_dim=args.embedding_dim,
        dropout=args.dropout,
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)

    meta = {
        "method": "ComplEx",
        "goal": "Minimal structure-only ComplEx baseline for Setting A valid-first table v0",
        "seed": args.seed,
        "graph_path": args.graph_path,
        "train_queries_path": args.train_queries_path,
        "valid_queries_path": args.valid_queries_path,
        "raw_indication_path": args.raw_indication_path,
        "num_entities": num_entities,
        "num_relations": num_relations,
        "skipped_graph_rows": skipped,
        "drug_universe_size": len(drug_universe_ids),
        "graph_num_triples": len(graph_triples),
        "train_num_queries": len(train_queries),
        "valid_num_queries": len(valid_queries),
        "embedding_dim": args.embedding_dim,
        "dropout": args.dropout,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "batch_size": args.batch_size,
        "num_negatives": args.num_negatives,
        "valid_probe_size": args.valid_probe_size,
        "device": str(device),
        "indication_rel_id": indication_rel_id,
    }
    save_json(meta_path, meta)

    best_key = None
    best_state = None
    bad_epochs = 0

    for epoch in range(1, args.num_epochs + 1):
        train_stats = train_one_epoch(
            model=model,
            triples=graph_triples,
            optimizer=optimizer,
            num_entities=num_entities,
            device=device,
            batch_size=args.batch_size,
            num_negatives=args.num_negatives,
        )

        probe_metrics = compute_probe_metrics(
            model=model,
            valid_queries=valid_queries,
            indication_rel_id=indication_rel_id,
            drug_universe_ids=drug_universe_ids,
            id2entity=id2entity,
            device=device,
            max_queries=args.valid_probe_size if args.valid_probe_size > 0 else None,
        )

        row = {"epoch": epoch, **train_stats, **probe_metrics}
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

        print(json.dumps(row, ensure_ascii=False))

        key = (
            probe_metrics["probe_hits10"],
            probe_metrics["probe_mrr"],
            -probe_metrics["probe_top1_dominance_ratio"],
        )
        improved = best_key is None or key > best_key
        if improved:
            best_key = key
            bad_epochs = 0
            best_state = {
                "model_state_dict": model.state_dict(),
                "best_epoch": epoch,
                "best_key": best_key,
                "meta": meta,
            }
            torch.save(best_state, ckpt_path)
        else:
            bad_epochs += 1

        if bad_epochs >= args.early_stop:
            print(f"Early stop triggered at epoch {epoch}.")
            break

    meta["checkpoint_path"] = str(ckpt_path)
    meta["train_log_path"] = str(log_path)
    meta["best_epoch"] = best_state["best_epoch"] if best_state is not None else None
    meta["best_key"] = best_key
    save_json(meta_path, meta)

    print("Saved:")
    print(f"- {ckpt_path}")
    print(f"- {log_path}")
    print(f"- {meta_path}")


if __name__ == "__main__":
    main()