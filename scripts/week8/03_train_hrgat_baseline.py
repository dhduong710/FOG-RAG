#!/usr/bin/env python3
import argparse
import csv
import json
import math
import pickle
import random
from collections import Counter
from pathlib import Path

import dgl
from dgl.nn.functional import edge_softmax
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


def build_graph_tensors(graph_rows, entity2id, relation2id):
    src, dst, etypes = [], [], []
    skipped = 0
    for h, r, t in graph_rows:
        if h not in entity2id or t not in entity2id or r not in relation2id:
            skipped += 1
            continue
        src.append(int(entity2id[h]))
        dst.append(int(entity2id[t]))
        etypes.append(int(relation2id[r]))
    return src, dst, etypes, skipped


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


class HRGATLayer(nn.Module):
    def __init__(self, in_dim, out_dim, rel_dim, dropout=0.1, negative_slope=0.2):
        super().__init__()
        self.fc_node = nn.Linear(in_dim, out_dim, bias=False)
        self.fc_self = nn.Linear(in_dim, out_dim, bias=False)
        self.fc_rel = nn.Linear(rel_dim, out_dim, bias=False)
        self.attn = nn.Linear(out_dim * 3, 1, bias=False)
        self.dropout = nn.Dropout(dropout)
        self.negative_slope = negative_slope
        self.norm = nn.LayerNorm(out_dim)

    def forward(self, g, h, rel_embed, etypes):
        with g.local_scope():
            Wh = self.fc_node(h)
            Wr = self.fc_rel(rel_embed[etypes])

            g.ndata["Wh"] = Wh
            g.edata["Wr"] = Wr

            def edge_attention(edges):
                z = torch.cat([edges.src["Wh"], edges.dst["Wh"], edges.data["Wr"]], dim=-1)
                e = F.leaky_relu(self.attn(z), negative_slope=self.negative_slope)
                return {"e": e}

            g.apply_edges(edge_attention)
            g.edata["a"] = edge_softmax(g, g.edata["e"])

            def edge_message(edges):
                msg = edges.data["a"] * (edges.src["Wh"] + edges.data["Wr"])
                return {"m": self.dropout(msg)}

            g.update_all(edge_message, dgl.function.sum("m", "agg"))

            out = g.ndata["agg"] + self.fc_self(h)
            out = self.norm(out)
            out = F.elu(out)
            return out


class HRGATScorer(nn.Module):
    def __init__(
        self,
        num_nodes,
        num_relations,
        indication_rel_id,
        embedding_dim=128,
        hidden_dim=128,
        num_layers=2,
        dropout=0.1,
    ):
        super().__init__()
        self.num_nodes = num_nodes
        self.num_relations = num_relations
        self.indication_rel_id = indication_rel_id
        self.node_embed = nn.Embedding(num_nodes, embedding_dim)
        self.rel_embed = nn.Embedding(num_relations, embedding_dim)

        layers = []
        in_dim = embedding_dim
        for _ in range(num_layers):
            layers.append(HRGATLayer(in_dim, hidden_dim, embedding_dim, dropout=dropout))
            in_dim = hidden_dim
        self.layers = nn.ModuleList(layers)

        self.final_dropout = nn.Dropout(dropout)
        self.scorer_rel = nn.Parameter(torch.empty(hidden_dim))
        nn.init.xavier_uniform_(self.node_embed.weight)
        nn.init.xavier_uniform_(self.rel_embed.weight)
        nn.init.uniform_(self.scorer_rel, -0.1, 0.1)

    def encode(self, g, etypes):
        h = self.node_embed.weight
        rel = self.rel_embed.weight
        for layer in self.layers:
            h = layer(g, h, rel, etypes)
        return self.final_dropout(h)

    def score_pairs(self, node_repr, drug_ids, disease_ids):
        drug_vec = node_repr[drug_ids]
        disease_vec = node_repr[disease_ids]
        rel = self.scorer_rel.view(1, -1)
        return torch.sum(drug_vec * rel * disease_vec, dim=-1)

    def score_full_drug_universe(self, node_repr, disease_ids, drug_universe_ids):
        drug_repr = node_repr[drug_universe_ids]
        disease_repr = node_repr[disease_ids]
        rel = self.scorer_rel.view(1, 1, -1)
        return torch.sum(drug_repr.unsqueeze(0) * rel * disease_repr.unsqueeze(1), dim=-1)


def compute_probe_metrics(model, g, etypes, valid_queries, drug_universe_ids, id2entity, device, max_queries=None):
    model.eval()
    rows = valid_queries[:max_queries] if (max_queries is not None and max_queries > 0) else valid_queries

    with torch.no_grad():
        node_repr = model.encode(g, etypes)
        q_ids = torch.tensor([x["query_disease_id"] for x in rows], device=device, dtype=torch.long)
        scores = model.score_full_drug_universe(node_repr, q_ids, drug_universe_ids)
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


def train_one_epoch(model, g, etypes, train_queries, drug_universe_ids, optimizer, device, batch_size, num_negatives, margin):
    model.train()
    random.shuffle(train_queries)
    losses = []

    drug_universe = torch.tensor(drug_universe_ids, dtype=torch.long, device=device)

    for start in range(0, len(train_queries), batch_size):
        batch = train_queries[start:start + batch_size]
        q_ids = torch.tensor([x["query_disease_id"] for x in batch], dtype=torch.long, device=device)
        pos_ids = torch.tensor([x["gold_drug_id"] for x in batch], dtype=torch.long, device=device)

        node_repr = model.encode(g, etypes)
        pos_scores = model.score_pairs(node_repr, pos_ids, q_ids)

        neg_sample_idx = torch.randint(0, len(drug_universe_ids), (len(batch), num_negatives), device=device)
        neg_ids = drug_universe[neg_sample_idx]
        neg_ids = torch.where(
            neg_ids == pos_ids.unsqueeze(1),
            drug_universe[(neg_sample_idx + 1) % len(drug_universe_ids)],
            neg_ids,
        )

        flat_q = q_ids.unsqueeze(1).expand(-1, num_negatives).reshape(-1)
        flat_neg = neg_ids.reshape(-1)
        neg_scores = model.score_pairs(node_repr, flat_neg, flat_q).reshape(len(batch), num_negatives)

        loss = F.relu(margin - pos_scores.unsqueeze(1) + neg_scores).mean()

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        losses.append(float(loss.item()))

    return {
        "train_loss": round(float(np.mean(losses)), 8) if losses else None,
        "num_batches": math.ceil(len(train_queries) / batch_size),
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
    parser.add_argument("--out_dir", default="results/week8/hrgat_baseline")
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--embedding_dim", type=int, default=128)
    parser.add_argument("--hidden_dim", type=int, default=128)
    parser.add_argument("--num_layers", type=int, default=2)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--learning_rate", type=float, default=3e-4)
    parser.add_argument("--weight_decay", type=float, default=1e-4)
    parser.add_argument("--num_epochs", type=int, default=20)
    parser.add_argument("--batch_size", type=int, default=256)
    parser.add_argument("--num_negatives", type=int, default=32)
    parser.add_argument("--margin", type=float, default=1.0)
    parser.add_argument("--valid_probe_size", type=int, default=256)
    parser.add_argument("--early_stop", type=int, default=6)
    parser.add_argument("--max_train_queries", type=int, default=0)
    parser.add_argument("--max_valid_queries", type=int, default=0)
    args = parser.parse_args()

    set_seed(args.seed)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "hrgat_train_log.jsonl"
    ckpt_path = out_dir / "hrgat_checkpoint.pt"
    meta_path = out_dir / "hrgat_meta.json"

    entity2id = load_pickle(Path(args.entity2id_path))
    relation2id = load_pickle(Path(args.relation2id_path))
    id2entity = load_pickle(Path(args.id2entity_path))
    indication_rel_id = int(relation2id["indication"])

    graph_rows = read_tsv(Path(args.graph_path))
    src, dst, etypes_list, skipped = build_graph_tensors(graph_rows, entity2id, relation2id)

    num_nodes = max(entity2id.values()) + 1
    num_rels = max(relation2id.values()) + 1

    g = dgl.graph((src, dst), num_nodes=num_nodes)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    g = g.to(device)
    etypes = torch.tensor(etypes_list, dtype=torch.long, device=device)

    train_queries = read_queries(Path(args.train_queries_path), entity2id)
    valid_queries = read_queries(Path(args.valid_queries_path), entity2id)

    if args.max_train_queries > 0:
        train_queries = train_queries[:args.max_train_queries]
    if args.max_valid_queries > 0:
        valid_queries = valid_queries[:args.max_valid_queries]

    drug_universe_ids, _ = derive_drug_universe_ids(Path(args.raw_indication_path), entity2id)

    model = HRGATScorer(
        num_nodes=num_nodes,
        num_relations=num_rels,
        indication_rel_id=indication_rel_id,
        embedding_dim=args.embedding_dim,
        hidden_dim=args.hidden_dim,
        num_layers=args.num_layers,
        dropout=args.dropout,
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)

    meta = {
        "method": "HRGAT",
        "goal": "Minimal structure-only HRGAT baseline for Setting A valid-first table v0",
        "seed": args.seed,
        "graph_path": args.graph_path,
        "train_queries_path": args.train_queries_path,
        "valid_queries_path": args.valid_queries_path,
        "raw_indication_path": args.raw_indication_path,
        "num_nodes": num_nodes,
        "num_relations": num_rels,
        "skipped_graph_rows": skipped,
        "drug_universe_size": len(drug_universe_ids),
        "train_num_queries": len(train_queries),
        "valid_num_queries": len(valid_queries),
        "embedding_dim": args.embedding_dim,
        "hidden_dim": args.hidden_dim,
        "num_layers": args.num_layers,
        "dropout": args.dropout,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "batch_size": args.batch_size,
        "num_negatives": args.num_negatives,
        "margin": args.margin,
        "valid_probe_size": args.valid_probe_size,
        "device": str(device),
    }
    save_json(meta_path, meta)

    best_key = None
    best_state = None
    bad_epochs = 0

    for epoch in range(1, args.num_epochs + 1):
        train_stats = train_one_epoch(
            model=model,
            g=g,
            etypes=etypes,
            train_queries=train_queries,
            drug_universe_ids=drug_universe_ids,
            optimizer=optimizer,
            device=device,
            batch_size=args.batch_size,
            num_negatives=args.num_negatives,
            margin=args.margin,
        )

        probe_metrics = compute_probe_metrics(
            model=model,
            g=g,
            etypes=etypes,
            valid_queries=valid_queries,
            drug_universe_ids=drug_universe_ids,
            id2entity=id2entity,
            device=device,
            max_queries=args.valid_probe_size if args.valid_probe_size > 0 else None,
        )

        row = {"epoch": epoch, **train_stats, **probe_metrics}
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

        print(json.dumps(row, ensure_ascii=False))

        key = (probe_metrics["probe_hits10"], probe_metrics["probe_mrr"], -probe_metrics["probe_top1_dominance_ratio"])
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