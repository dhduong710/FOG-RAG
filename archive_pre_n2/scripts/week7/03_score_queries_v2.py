#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 7 - Day 3
Score full train/valid/test queries using the best ranker_v2 checkpoint.

Outputs:
- dataset/setting_a/11_ranker_v2/train_scores.pt
- dataset/setting_a/11_ranker_v2/valid_scores.pt
- dataset/setting_a/11_ranker_v2/test_scores.pt
- dataset/setting_a/11_ranker_v2/score_dump_meta.json
"""

from __future__ import annotations

import argparse
import csv
import json
import pickle
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import dgl
import torch
import torch.nn as nn
import torch.nn.functional as F
import yaml
from dgl.nn import RelGraphConv


# ============================================================
# Config
# ============================================================

@dataclass
class TrainConfig:
    seed: int
    graph_path: str
    train_queries_path: str
    valid_queries_path: str
    test_queries_path: str
    entity2id_path: str
    id2entity_path: str
    relation2id_path: str
    id2relation_path: str
    output_dir: str
    report_dir: str
    target_relation: str
    candidate_universe: str
    learning_rate: float
    weight_decay: float
    num_epochs: int
    early_stop_patience: int
    batch_size: int
    num_negatives: int
    grad_clip_norm: float
    embedding_dim: int
    hidden_dim: int
    num_rgcn_layers: int
    dropout: float
    log_every_epochs: int
    valid_probe_size: int
    save_every_epochs: int
    margin: float


# ============================================================
# Utilities
# ============================================================

def set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def load_pickle(path: Path) -> Any:
    with path.open("rb") as f:
        return pickle.load(f)


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def read_tsv_triples(path: Path) -> List[Tuple[str, str, str]]:
    triples = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if not row or len(row) < 3:
                continue
            h, r, t = row[0].strip(), row[1].strip(), row[2].strip()
            if h and r and t:
                triples.append((h, r, t))
    return triples


def build_name_to_id_maps(
    entity2id: Dict[str, int],
    relation2id: Dict[str, int],
) -> Tuple[Dict[str, int], Dict[int, str], Dict[str, int], Dict[int, str]]:
    id2entity = {v: k for k, v in entity2id.items()}
    id2relation = {v: k for k, v in relation2id.items()}
    return entity2id, id2entity, relation2id, id2relation


# ============================================================
# Data loading
# ============================================================

def load_graph(
    graph_path: Path,
    entity2id: Dict[str, int],
    relation2id: Dict[str, int],
) -> Tuple[dgl.DGLGraph, torch.Tensor, int, int]:
    triples = read_tsv_triples(graph_path)

    src_ids, dst_ids, rel_ids = [], [], []
    skipped = 0
    for h, r, t in triples:
        if h not in entity2id or t not in entity2id or r not in relation2id:
            skipped += 1
            continue
        src_ids.append(entity2id[h])
        dst_ids.append(entity2id[t])
        rel_ids.append(relation2id[r])

    g = dgl.graph((src_ids, dst_ids), num_nodes=len(entity2id))
    etypes = torch.tensor(rel_ids, dtype=torch.long)
    return g, etypes, len(entity2id), skipped


def load_query_triples(
    split_path: Path,
    entity2id: Dict[str, int],
    relation2id: Dict[str, int],
    target_relation: str,
) -> List[Dict[str, Any]]:
    triples = read_tsv_triples(split_path)
    examples = []

    for h, r, t in triples:
        if r != target_relation:
            continue
        if h not in entity2id or t not in entity2id or r not in relation2id:
            continue

        # head prediction (?, indication, disease)
        examples.append(
            {
                "drug_name": h,
                "drug_id": entity2id[h],
                "relation_name": r,
                "relation_id": relation2id[r],
                "disease_name": t,
                "disease_id": entity2id[t],
            }
        )
    return examples


def build_drug_universe_from_splits(
    train_queries: List[Dict[str, Any]],
    valid_queries: List[Dict[str, Any]],
    test_queries: List[Dict[str, Any]],
) -> torch.Tensor:
    drug_ids = set()
    for ex in train_queries:
        drug_ids.add(ex["drug_id"])
    for ex in valid_queries:
        drug_ids.add(ex["drug_id"])
    for ex in test_queries:
        drug_ids.add(ex["drug_id"])
    return torch.tensor(sorted(drug_ids), dtype=torch.long)


# ============================================================
# Model (same architecture as Day 2)
# ============================================================

class RGCNEncoder(nn.Module):
    def __init__(
        self,
        num_nodes: int,
        num_rels: int,
        embedding_dim: int,
        hidden_dim: int,
        num_layers: int,
        dropout: float,
    ):
        super().__init__()
        assert num_layers >= 1

        self.node_emb = nn.Embedding(num_nodes, embedding_dim)
        nn.init.xavier_uniform_(self.node_emb.weight)

        self.dropout = nn.Dropout(dropout)
        self.layers = nn.ModuleList()

        if num_layers == 1:
            self.layers.append(RelGraphConv(embedding_dim, hidden_dim, num_rels))
        else:
            self.layers.append(RelGraphConv(embedding_dim, hidden_dim, num_rels))
            for _ in range(num_layers - 2):
                self.layers.append(RelGraphConv(hidden_dim, hidden_dim, num_rels))
            self.layers.append(RelGraphConv(hidden_dim, hidden_dim, num_rels))

    def forward(self, g: dgl.DGLGraph, etypes: torch.Tensor) -> torch.Tensor:
        x = self.node_emb.weight
        for i, layer in enumerate(self.layers):
            x = layer(g, x, etypes)
            if i != len(self.layers) - 1:
                x = F.relu(x)
                x = self.dropout(x)
        return x


class RGCNCoarseRanker(nn.Module):
    def __init__(
        self,
        num_nodes: int,
        num_rels: int,
        embedding_dim: int,
        hidden_dim: int,
        num_layers: int,
        dropout: float,
    ):
        super().__init__()
        self.encoder = RGCNEncoder(
            num_nodes=num_nodes,
            num_rels=num_rels,
            embedding_dim=embedding_dim,
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            dropout=dropout,
        )
        self.rel_emb = nn.Embedding(num_rels, hidden_dim)
        nn.init.xavier_uniform_(self.rel_emb.weight)

    def encode(self, g: dgl.DGLGraph, etypes: torch.Tensor) -> torch.Tensor:
        return self.encoder(g, etypes)

    def score_all_candidates_for_query_batch(
        self,
        node_repr: torch.Tensor,             # [N, H]
        candidate_drug_ids: torch.Tensor,    # [Nc]
        relation_id: int,                    # scalar
        disease_ids: torch.Tensor,           # [B]
    ) -> torch.Tensor:
        """
        Returns scores of shape [B, Nc].
        DistMult-like:
          score(drug, relation, disease) = sum(z_drug * r * z_disease)
        """
        drug_vec = node_repr[candidate_drug_ids]  # [Nc, H]
        rel_vec = self.rel_emb(
            torch.full((1,), relation_id, dtype=torch.long, device=node_repr.device)
        )[0]  # [H]
        disease_vec = node_repr[disease_ids]      # [B, H]

        # [Nc, H]
        drug_rel = drug_vec * rel_vec.unsqueeze(0)

        # [B, H] x [H, Nc] -> [B, Nc]
        scores = disease_vec @ drug_rel.t()
        return scores


# ============================================================
# Scoring
# ============================================================

@torch.no_grad()
def score_split(
    model: RGCNCoarseRanker,
    g: dgl.DGLGraph,
    etypes: torch.Tensor,
    split_name: str,
    queries: List[Dict[str, Any]],
    drug_universe_ids: torch.Tensor,
    relation_id: int,
    id2entity: Dict[int, str],
    device: torch.device,
    query_batch_size: int = 256,
) -> Dict[str, Any]:
    model.eval()
    node_repr = model.encode(g, etypes)

    cand_ids = drug_universe_ids.to(device)

    query_entity_ids = torch.tensor([ex["disease_id"] for ex in queries], dtype=torch.long)
    gold_entity_ids = torch.tensor([ex["drug_id"] for ex in queries], dtype=torch.long)
    relation_ids = torch.tensor([ex["relation_id"] for ex in queries], dtype=torch.long)

    query_entity_names = [ex["disease_name"] for ex in queries]
    gold_entity_names = [ex["drug_name"] for ex in queries]

    all_scores = []

    for start in range(0, len(queries), query_batch_size):
        end = min(start + query_batch_size, len(queries))
        disease_ids_batch = query_entity_ids[start:end].to(device)

        scores = model.score_all_candidates_for_query_batch(
            node_repr=node_repr,
            candidate_drug_ids=cand_ids,
            relation_id=relation_id,
            disease_ids=disease_ids_batch,
        )  # [B, Nc]

        all_scores.append(scores.detach().cpu().to(torch.float16))

    score_matrix = torch.cat(all_scores, dim=0)  # [num_queries, Nc]

    payload = {
        "split": split_name,
        "relation_name": id2entity.get(relation_id, None),  # not used; harmless
        "target_relation_id": relation_id,
        "candidate_universe_entity_ids": drug_universe_ids.clone().cpu(),
        "candidate_universe_entity_names": [id2entity[int(x)] for x in drug_universe_ids.tolist()],
        "query_entity_ids": query_entity_ids,
        "query_entity_names": query_entity_names,
        "gold_entity_ids": gold_entity_ids,
        "gold_entity_names": gold_entity_names,
        "relation_ids": relation_ids,
        "scores": score_matrix,
    }
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to configs/week7/rgcn_ranker_v2.yaml")
    parser.add_argument(
        "--checkpoint-path",
        default=None,
        help="Optional explicit checkpoint path. If not given, read from ranker_v2_meta.json.",
    )
    parser.add_argument("--query-batch-size", type=int, default=256)
    args = parser.parse_args()

    cfg_dict = load_yaml(Path(args.config))
    cfg = TrainConfig(**cfg_dict)
    set_seed(cfg.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    output_dir = Path(cfg.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    meta_path = output_dir / "ranker_v2_meta.json"
    if args.checkpoint_path is not None:
        checkpoint_path = Path(args.checkpoint_path)
    else:
        if not meta_path.exists():
            raise FileNotFoundError(
                f"Cannot find {meta_path}. Either run Day 2 first or pass --checkpoint-path explicitly."
            )
        meta = json.load(open(meta_path, "r", encoding="utf-8"))
        checkpoint_path = Path(meta["checkpoint_path"])

    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    # Load mappings
    entity2id = load_pickle(Path(cfg.entity2id_path))
    relation2id = load_pickle(Path(cfg.relation2id_path))
    entity2id, id2entity, relation2id, id2relation = build_name_to_id_maps(entity2id, relation2id)

    if cfg.target_relation not in relation2id:
        raise ValueError(
            f"target_relation '{cfg.target_relation}' not found in relation2id: {sorted(relation2id.keys())}"
        )
    target_relation_id = relation2id[cfg.target_relation]

    # Load graph and splits
    g, etypes, num_nodes, skipped_graph_rows = load_graph(
        Path(cfg.graph_path), entity2id, relation2id
    )
    g = g.to(device)
    etypes = etypes.to(device)

    train_queries = load_query_triples(Path(cfg.train_queries_path), entity2id, relation2id, cfg.target_relation)
    valid_queries = load_query_triples(Path(cfg.valid_queries_path), entity2id, relation2id, cfg.target_relation)
    test_queries = load_query_triples(Path(cfg.test_queries_path), entity2id, relation2id, cfg.target_relation)

    drug_universe_ids = build_drug_universe_from_splits(train_queries, valid_queries, test_queries)

    # Build model and load checkpoint
    model = RGCNCoarseRanker(
        num_nodes=num_nodes,
        num_rels=len(relation2id),
        embedding_dim=cfg.embedding_dim,
        hidden_dim=cfg.hidden_dim,
        num_layers=cfg.num_rgcn_layers,
        dropout=cfg.dropout,
    ).to(device)

    ckpt = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(ckpt["model_state_dict"], strict=True)
    model.eval()

    # Score all splits
    train_dump = score_split(
        model=model,
        g=g,
        etypes=etypes,
        split_name="train",
        queries=train_queries,
        drug_universe_ids=drug_universe_ids,
        relation_id=target_relation_id,
        id2entity=id2entity,
        device=device,
        query_batch_size=args.query_batch_size,
    )
    valid_dump = score_split(
        model=model,
        g=g,
        etypes=etypes,
        split_name="valid",
        queries=valid_queries,
        drug_universe_ids=drug_universe_ids,
        relation_id=target_relation_id,
        id2entity=id2entity,
        device=device,
        query_batch_size=args.query_batch_size,
    )
    test_dump = score_split(
        model=model,
        g=g,
        etypes=etypes,
        split_name="test",
        queries=test_queries,
        drug_universe_ids=drug_universe_ids,
        relation_id=target_relation_id,
        id2entity=id2entity,
        device=device,
        query_batch_size=args.query_batch_size,
    )

    train_scores_path = output_dir / "train_scores.pt"
    valid_scores_path = output_dir / "valid_scores.pt"
    test_scores_path = output_dir / "test_scores.pt"

    torch.save(train_dump, train_scores_path)
    torch.save(valid_dump, valid_scores_path)
    torch.save(test_dump, test_scores_path)

    save_json(
        output_dir / "score_dump_meta.json",
        {
            "week": 7,
            "day": 3,
            "goal": "Score full train/valid/test with ranker_v2 best checkpoint.",
            "config": asdict(cfg),
            "device": str(device),
            "checkpoint_path": str(checkpoint_path),
            "best_epoch_from_checkpoint": ckpt.get("best_epoch"),
            "drug_universe_size": int(drug_universe_ids.numel()),
            "num_nodes": num_nodes,
            "num_relations": len(relation2id),
            "skipped_graph_rows": skipped_graph_rows,
            "train_num_queries": len(train_queries),
            "valid_num_queries": len(valid_queries),
            "test_num_queries": len(test_queries),
            "score_dtype": "float16",
            "query_batch_size": args.query_batch_size,
        },
    )

    print("Saved:")
    print(f"- {train_scores_path}")
    print(f"- {valid_scores_path}")
    print(f"- {test_scores_path}")
    print(f"- {output_dir / 'score_dump_meta.json'}")


if __name__ == "__main__":
    main()