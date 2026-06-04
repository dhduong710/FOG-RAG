#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import pickle
from pathlib import Path

import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import dgl
from dgl.nn import RelGraphConv


def load_pickle(path: Path):
    with path.open("rb") as f:
        return pickle.load(f)


def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Train/export first real R-GCN entity embeddings for week 5.")
    parser.add_argument("--graph_path", type=Path, default=Path("dataset/setting_a/02_graph/train_enriched_deg1000_final.tsv"))
    parser.add_argument("--entity2id_path", type=Path, default=Path("dataset/setting_a/04_drkgc_json/entity2id.pkl"))
    parser.add_argument("--relation2id_path", type=Path, default=Path("dataset/setting_a/04_drkgc_json/relation2id.pkl"))
    parser.add_argument("--output_embedding_path", type=Path, default=Path("dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt"))
    parser.add_argument("--output_meta_path", type=Path, default=Path("results/week5/rgcn_setting_a/export_meta.json"))

    parser.add_argument("--embedding_dim", type=int, default=256)
    parser.add_argument("--num_layers", type=int, default=2)
    parser.add_argument("--dropout", type=float, default=0.1)

    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--learning_rate", type=float, default=1e-2)
    parser.add_argument("--weight_decay", type=float, default=1e-5)
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--device", type=str, default="auto", choices=["auto", "cpu", "cuda"])

    return parser.parse_args()


def set_seed(seed: int):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class RGCNLinkPredictor(nn.Module):
    def __init__(self, num_nodes: int, num_rels: int, emb_dim: int, num_layers: int, dropout: float):
        super().__init__()
        self.node_embed = nn.Embedding(num_nodes, emb_dim)
        self.rel_embed = nn.Embedding(num_rels, emb_dim)

        layers = []
        for _ in range(num_layers):
            layers.append(
                RelGraphConv(
                    in_feat=emb_dim,
                    out_feat=emb_dim,
                    num_rels=num_rels,
                    regularizer="basis",
                    num_bases=min(num_rels, 4),
                    self_loop=True,
                    dropout=dropout,
                )
            )
        self.layers = nn.ModuleList(layers)
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.xavier_uniform_(self.node_embed.weight)
        nn.init.xavier_uniform_(self.rel_embed.weight)

    def encode(self, g, etypes):
        h = self.node_embed.weight
        for i, layer in enumerate(self.layers):
            h = layer(g, h, etypes)
            if i != len(self.layers) - 1:
                h = F.relu(h)
        return h

    def score(self, node_emb, heads, rels, tails):
        h = node_emb[heads]
        r = self.rel_embed(rels)
        t = node_emb[tails]
        return torch.sum(h * r * t, dim=-1)


def build_graph_and_triples(graph_df: pd.DataFrame, entity2id: dict, relation2id: dict, device: torch.device):
    heads = torch.tensor([entity2id[h] for h in graph_df["head"].tolist()], dtype=torch.long, device=device)
    rels = torch.tensor([relation2id[r] for r in graph_df["relation"].tolist()], dtype=torch.long, device=device)
    tails = torch.tensor([entity2id[t] for t in graph_df["tail"].tolist()], dtype=torch.long, device=device)

    g = dgl.graph((heads, tails), num_nodes=len(entity2id), device=device)
    g.edata["etype"] = rels

    triples = torch.stack([heads, rels, tails], dim=1)
    return g, triples, rels


def make_negative_samples(pos_triples: torch.Tensor, num_nodes: int):
    neg = pos_triples.clone()
    corrupt_head_mask = torch.rand(len(pos_triples), device=pos_triples.device) < 0.5
    random_nodes = torch.randint(low=0, high=num_nodes, size=(len(pos_triples),), device=pos_triples.device)

    neg[corrupt_head_mask, 0] = random_nodes[corrupt_head_mask]
    neg[~corrupt_head_mask, 2] = random_nodes[~corrupt_head_mask]
    return neg


def main():
    args = parse_args()
    set_seed(args.seed)

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    print("=" * 80)
    print("Week 5 Day 3 - Train / Export R-GCN Entity Embeddings")
    print("=" * 80)
    print("graph_path           :", args.graph_path)
    print("entity2id_path       :", args.entity2id_path)
    print("relation2id_path     :", args.relation2id_path)
    print("output_embedding_path:", args.output_embedding_path)
    print("output_meta_path     :", args.output_meta_path)
    print("device               :", device)
    print("=" * 80)

    entity2id = load_pickle(args.entity2id_path)
    relation2id = load_pickle(args.relation2id_path)

    graph_df = pd.read_csv(args.graph_path, sep="\t")
    graph_df["head"] = graph_df["head"].astype(str).str.strip()
    graph_df["relation"] = graph_df["relation"].astype(str).str.strip()
    graph_df["tail"] = graph_df["tail"].astype(str).str.strip()

    # Keep only rows whose entities/relations are mapped
    before_rows = len(graph_df)
    graph_df = graph_df[
        graph_df["head"].isin(entity2id)
        & graph_df["tail"].isin(entity2id)
        & graph_df["relation"].isin(relation2id)
    ].drop_duplicates().reset_index(drop=True)
    after_rows = len(graph_df)

    print(f"Filtered graph rows: {before_rows} -> {after_rows}")

    g, triples, etypes = build_graph_and_triples(graph_df, entity2id, relation2id, device)

    model = RGCNLinkPredictor(
        num_nodes=len(entity2id),
        num_rels=len(relation2id),
        emb_dim=args.embedding_dim,
        num_layers=args.num_layers,
        dropout=args.dropout,
    ).to(device)

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )

    num_nodes = len(entity2id)
    best_loss = float("inf")
    loss_history = []

    for epoch in range(1, args.epochs + 1):
        model.train()
        optimizer.zero_grad()

        node_emb = model.encode(g, etypes)
        pos_scores = model.score(node_emb, triples[:, 0], triples[:, 1], triples[:, 2])

        neg_triples = make_negative_samples(triples, num_nodes)
        neg_scores = model.score(node_emb, neg_triples[:, 0], neg_triples[:, 1], neg_triples[:, 2])

        pos_labels = torch.ones_like(pos_scores)
        neg_labels = torch.zeros_like(neg_scores)

        loss_pos = F.binary_cross_entropy_with_logits(pos_scores, pos_labels)
        loss_neg = F.binary_cross_entropy_with_logits(neg_scores, neg_labels)
        loss = loss_pos + loss_neg

        loss.backward()
        optimizer.step()

        loss_value = float(loss.item())
        loss_history.append(loss_value)
        best_loss = min(best_loss, loss_value)

        print(f"[Epoch {epoch:02d}/{args.epochs}] loss={loss_value:.6f}")

    model.eval()
    with torch.no_grad():
        final_node_emb = model.encode(g, etypes).detach().cpu()

    args.output_embedding_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(final_node_emb, args.output_embedding_path)

    export_meta = {
        "graph_path": str(args.graph_path),
        "entity2id_path": str(args.entity2id_path),
        "relation2id_path": str(args.relation2id_path),
        "num_entities": len(entity2id),
        "num_relations": len(relation2id),
        "num_graph_triples_used": len(graph_df),
        "embedding_dim": int(final_node_emb.shape[1]),
        "num_layers": args.num_layers,
        "dropout": args.dropout,
        "epochs": args.epochs,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "seed": args.seed,
        "device": str(device),
        "loss_history": loss_history,
        "best_loss": best_loss,
        "output_embedding_path": str(args.output_embedding_path),
        "note": "First real R-GCN entity embedding export for week-5 backbone run.",
    }
    save_json(args.output_meta_path, export_meta)

    print("\nSaved:")
    print(" -", args.output_embedding_path)
    print(" -", args.output_meta_path)
    print("\nFinal embedding shape:", tuple(final_node_emb.shape))
    print("Done.")


if __name__ == "__main__":
    main()