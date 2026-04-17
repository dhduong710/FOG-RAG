#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 7 - Day 2
Train a more stable R-GCN coarse ranker v2 for Setting A.

Main design goals:
- keep R-GCN as the main path
- keep graph source / relation / drug-only universe fixed
- improve optimization stability
- log score statistics to detect score collapse

Outputs:
- dataset/setting_a/11_ranker_v2/rgcn_ranker_v2_checkpoint.pt
- dataset/setting_a/11_ranker_v2/ranker_v2_train_log.jsonl
- dataset/setting_a/11_ranker_v2/ranker_v2_meta.json
- reports/week7/day2_score_stats.json
- reports/week7/day2_top1_probe.tsv
- reports/week7/day2_ranker_v2_train.md
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import pickle
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple, Any, Optional

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


def append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def safe_div(a: float, b: float) -> float:
    return float(a) / float(b) if b else 0.0


def read_tsv_triples(path: Path) -> List[Tuple[str, str, str]]:
    """
    Read TSV triples with 3 columns and no header.
    """
    triples = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if not row:
                continue
            if len(row) < 3:
                continue
            h, r, t = row[0].strip(), row[1].strip(), row[2].strip()
            if h == "" or r == "" or t == "":
                continue
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

    src_ids = []
    dst_ids = []
    rel_ids = []

    skipped = 0
    for h, r, t in triples:
        if h not in entity2id or t not in entity2id or r not in relation2id:
            skipped += 1
            continue
        src_ids.append(entity2id[h])
        dst_ids.append(entity2id[t])
        rel_ids.append(relation2id[r])

    num_nodes = len(entity2id)
    num_edges = len(src_ids)

    g = dgl.graph((src_ids, dst_ids), num_nodes=num_nodes)
    etypes = torch.tensor(rel_ids, dtype=torch.long)

    return g, etypes, num_nodes, skipped


def load_query_triples(
    split_path: Path,
    entity2id: Dict[str, int],
    relation2id: Dict[str, int],
    target_relation: str,
) -> List[Dict[str, Any]]:
    """
    Setting A split rows are expected as:
      head(drug)    relation(indication)    tail(disease)

    For head prediction (?, indication, disease),
    the query is the disease, and the gold answer is the drug.
    """
    triples = read_tsv_triples(split_path)
    examples = []

    skipped = 0
    for h, r, t in triples:
        if r != target_relation:
            continue
        if h not in entity2id or t not in entity2id or r not in relation2id:
            skipped += 1
            continue
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
    drug_ids = sorted(drug_ids)
    return torch.tensor(drug_ids, dtype=torch.long)


# ============================================================
# Model
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
        assert num_layers >= 1, "num_layers must be >= 1"

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
    """
    Score for head prediction:
      score(drug, indication, disease) = <z_drug * r_indication, z_disease>
    DistMult-like score with learned relation embedding.
    """
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

    def score_pairs(
        self,
        node_repr: torch.Tensor,
        drug_ids: torch.Tensor,
        relation_ids: torch.Tensor,
        disease_ids: torch.Tensor,
    ) -> torch.Tensor:
        drug_vec = node_repr[drug_ids]            # [B, H] or [N, H]
        rel_vec = self.rel_emb(relation_ids)      # [B, H] or [N, H]
        disease_vec = node_repr[disease_ids]      # [B, H] or [N, H]
        return (drug_vec * rel_vec * disease_vec).sum(dim=-1)

    def score_candidates_for_query(
        self,
        node_repr: torch.Tensor,
        candidate_drug_ids: torch.Tensor,  # [Nc]
        relation_id: int,
        disease_id: int,
    ) -> torch.Tensor:
        rel_ids = torch.full(
            (candidate_drug_ids.size(0),),
            fill_value=relation_id,
            dtype=torch.long,
            device=node_repr.device,
        )
        disease_ids = torch.full(
            (candidate_drug_ids.size(0),),
            fill_value=disease_id,
            dtype=torch.long,
            device=node_repr.device,
        )
        return self.score_pairs(node_repr, candidate_drug_ids, rel_ids, disease_ids)


# ============================================================
# Training / probing
# ============================================================

def sample_negative_drugs(
    batch_gold_drug_ids: torch.Tensor,     # [B]
    drug_universe_ids: torch.Tensor,       # [Nd]
    num_negatives: int,
    device: torch.device,
) -> torch.Tensor:
    """
    Sample negatives from drug-only universe.
    Shape: [B, K]
    """
    nd = drug_universe_ids.size(0)
    bsz = batch_gold_drug_ids.size(0)

    idx = torch.randint(0, nd, (bsz, num_negatives), device=device)
    neg_ids = drug_universe_ids.to(device)[idx]  # [B, K]

    # Avoid sampling the gold drug itself.
    gold_expand = batch_gold_drug_ids.unsqueeze(1).expand_as(neg_ids)
    clash_mask = neg_ids.eq(gold_expand)

    max_resample_rounds = 10
    rounds = 0
    while clash_mask.any() and rounds < max_resample_rounds:
        num_clash = clash_mask.sum().item()
        resample_idx = torch.randint(0, nd, (num_clash,), device=device)
        neg_ids[clash_mask] = drug_universe_ids.to(device)[resample_idx]
        clash_mask = neg_ids.eq(gold_expand)
        rounds += 1

    return neg_ids


def pairwise_margin_loss(
    pos_scores: torch.Tensor,  # [B]
    neg_scores: torch.Tensor,  # [B, K]
    margin: float,
) -> torch.Tensor:
    pos_expand = pos_scores.unsqueeze(1).expand_as(neg_scores)
    return F.relu(margin - pos_expand + neg_scores).mean()


@torch.no_grad()
def run_valid_probe(
    model: RGCNCoarseRanker,
    g: dgl.DGLGraph,
    etypes: torch.Tensor,
    valid_queries: List[Dict[str, Any]],
    drug_universe_ids: torch.Tensor,
    valid_probe_size: int,
    device: torch.device,
    seed: int,
) -> Dict[str, Any]:
    model.eval()
    node_repr = model.encode(g, etypes)

    rng = random.Random(seed)
    if valid_probe_size <= 0 or valid_probe_size >= len(valid_queries):
        probe_examples = valid_queries
    else:
        probe_examples = rng.sample(valid_queries, valid_probe_size)

    recall20 = 0
    top1_hit = 0
    top1_counter = Counter()
    examples_for_table = []

    cand_ids = drug_universe_ids.to(device)

    for ex in probe_examples:
        disease_id = ex["disease_id"]
        gold_drug_id = ex["drug_id"]
        relation_id = ex["relation_id"]

        scores = model.score_candidates_for_query(
            node_repr=node_repr,
            candidate_drug_ids=cand_ids,
            relation_id=relation_id,
            disease_id=disease_id,
        )

        topk = min(20, cand_ids.size(0))
        top_scores, top_idx = torch.topk(scores, k=topk, dim=0, largest=True, sorted=True)
        top_drug_ids = cand_ids[top_idx].detach().cpu().tolist()

        if gold_drug_id in top_drug_ids:
            recall20 += 1
        if top_drug_ids and top_drug_ids[0] == gold_drug_id:
            top1_hit += 1

        if top_drug_ids:
            top1_counter[top_drug_ids[0]] += 1

        examples_for_table.append(
            {
                "query_disease": ex["disease_name"],
                "gold_drug": ex["drug_name"],
                "top1_drug_id": top_drug_ids[0] if top_drug_ids else None,
            }
        )

    n = len(probe_examples)
    most_common_top1 = top1_counter.most_common(20)
    top1_dominance_ratio = safe_div(most_common_top1[0][1], n) if most_common_top1 else 0.0

    return {
        "num_probe_queries": n,
        "recall20": safe_div(recall20, n),
        "top1_hit_ratio": safe_div(top1_hit, n),
        "unique_top1_count": len(top1_counter),
        "top1_dominance_ratio": top1_dominance_ratio,
        "top1_counter": dict(top1_counter),
        "top1_examples": examples_for_table[:50],
    }


def compute_score_stats(
    pos_scores: torch.Tensor,
    neg_scores: torch.Tensor,
) -> Dict[str, float]:
    gap = pos_scores.unsqueeze(1) - neg_scores
    return {
        "pos_score_mean": float(pos_scores.mean().item()),
        "pos_score_std": float(pos_scores.std().item()) if pos_scores.numel() > 1 else 0.0,
        "neg_score_mean": float(neg_scores.mean().item()),
        "neg_score_std": float(neg_scores.std().item()) if neg_scores.numel() > 1 else 0.0,
        "score_gap_mean": float(gap.mean().item()),
        "score_gap_std": float(gap.std().item()) if gap.numel() > 1 else 0.0,
    }


# ============================================================
# Report writers
# ============================================================

def write_top1_probe_tsv(
    path: Path,
    probe: Dict[str, Any],
    id2entity: Dict[int, str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(
        probe["top1_counter"].items(),
        key=lambda x: (-x[1], x[0]),
    )
    with path.open("w", encoding="utf-8") as f:
        f.write("drug_id\tdrug_name\tcount\n")
        for drug_id, count in rows:
            drug_name = id2entity.get(int(drug_id), f"<UNK:{drug_id}>")
            f.write(f"{drug_id}\t{drug_name}\t{count}\n")


def write_day2_markdown_report(
    report_path: Path,
    cfg: TrainConfig,
    train_log_tail: List[Dict[str, Any]],
    best_epoch: int,
    best_probe: Dict[str, Any],
    best_stats: Dict[str, Any],
    stopped_early: bool,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    def fmt(x: Optional[float]) -> str:
        if x is None:
            return "N/A"
        if isinstance(x, float):
            return f"{x:.6f}"
        return str(x)

    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Day 2 — Ranker v2 training\n\n")
        f.write("## Scope\n\n")
        f.write("- Train a more stable R-GCN coarse ranker v2 for Setting A.\n")
        f.write("- Keep graph source, relation, and drug-only candidate universe fixed.\n")
        f.write("- Improve optimization stability and score discrimination.\n\n")

        f.write("## Config decisions\n\n")
        f.write(f"- graph source: `{cfg.graph_path}`\n")
        f.write(f"- relation: `{cfg.target_relation}`\n")
        f.write(f"- candidate universe: `{cfg.candidate_universe}`\n")
        f.write(f"- learning rate: `{cfg.learning_rate}`\n")
        f.write(f"- batch size: `{cfg.batch_size}`\n")
        f.write(f"- negatives per query: `{cfg.num_negatives}`\n")
        f.write(f"- grad clip norm: `{cfg.grad_clip_norm}`\n")
        f.write(f"- seed: `{cfg.seed}`\n\n")

        f.write("## Best checkpoint summary\n\n")
        f.write(f"- best_epoch = `{best_epoch}`\n")
        f.write(f"- valid_probe_recall20 = `{fmt(best_probe.get('recall20'))}`\n")
        f.write(f"- valid_probe_top1_hit_ratio = `{fmt(best_probe.get('top1_hit_ratio'))}`\n")
        f.write(f"- valid_probe_unique_top1_count = `{best_probe.get('unique_top1_count')}`\n")
        f.write(f"- valid_probe_top1_dominance_ratio = `{fmt(best_probe.get('top1_dominance_ratio'))}`\n")
        f.write(f"- pos_score_mean = `{fmt(best_stats.get('pos_score_mean'))}`\n")
        f.write(f"- neg_score_mean = `{fmt(best_stats.get('neg_score_mean'))}`\n")
        f.write(f"- score_gap_mean = `{fmt(best_stats.get('score_gap_mean'))}`\n")
        f.write(f"- stopped_early = `{stopped_early}`\n\n")

        f.write("## Last logged rows\n\n")
        for row in train_log_tail:
            f.write(f"- `{json.dumps(row, ensure_ascii=False)}`\n")

        f.write("\n## Conclusion\n\n")
        f.write("- Check whether train loss is cleaner than week 6.\n")
        f.write("- Check whether pos_score_mean is above neg_score_mean.\n")
        f.write("- Check whether top1 dominance on valid probe is lower than the collapsed week-6 pattern.\n")
        f.write("- If the checkpoint is stable and score stats are sensible, move to Day 3 to build candidate artifacts.\n")


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        required=True,
        help="Path to configs/week7/rgcn_ranker_v2.yaml",
    )
    args = parser.parse_args()

    cfg_dict = load_yaml(Path(args.config))
    cfg = TrainConfig(**cfg_dict)

    set_seed(cfg.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    output_dir = Path(cfg.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_dir = Path(cfg.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    train_log_path = output_dir / "ranker_v2_train_log.jsonl"
    ckpt_path = output_dir / "rgcn_ranker_v2_checkpoint.pt"
    meta_path = output_dir / "ranker_v2_meta.json"

    day2_score_stats_path = report_dir / "day2_score_stats.json"
    day2_top1_probe_path = report_dir / "day2_top1_probe.tsv"
    day2_md_path = report_dir / "day2_ranker_v2_train.md"

    # Reset old log if rerunning.
    if train_log_path.exists():
        train_log_path.unlink()

    # -------------------------------
    # Load mappings
    # -------------------------------
    entity2id = load_pickle(Path(cfg.entity2id_path))
    relation2id = load_pickle(Path(cfg.relation2id_path))
    entity2id, id2entity, relation2id, id2relation = build_name_to_id_maps(entity2id, relation2id)

    if cfg.target_relation not in relation2id:
        raise ValueError(
            f"target_relation '{cfg.target_relation}' not found in relation2id. "
            f"Available relations: {sorted(list(relation2id.keys()))}"
        )

    # -------------------------------
    # Load graph and queries
    # -------------------------------
    g, etypes, num_nodes, skipped_graph_rows = load_graph(
        graph_path=Path(cfg.graph_path),
        entity2id=entity2id,
        relation2id=relation2id,
    )
    g = g.to(device)
    etypes = etypes.to(device)

    train_queries = load_query_triples(
        Path(cfg.train_queries_path), entity2id, relation2id, cfg.target_relation
    )
    valid_queries = load_query_triples(
        Path(cfg.valid_queries_path), entity2id, relation2id, cfg.target_relation
    )
    test_queries = load_query_triples(
        Path(cfg.test_queries_path), entity2id, relation2id, cfg.target_relation
    )

    drug_universe_ids = build_drug_universe_from_splits(train_queries, valid_queries, test_queries)

    if cfg.candidate_universe != "drug_only":
        raise ValueError("This script currently supports candidate_universe='drug_only' only.")

    num_rels = len(relation2id)

    # -------------------------------
    # Build model
    # -------------------------------
    model = RGCNCoarseRanker(
        num_nodes=num_nodes,
        num_rels=num_rels,
        embedding_dim=cfg.embedding_dim,
        hidden_dim=cfg.hidden_dim,
        num_layers=cfg.num_rgcn_layers,
        dropout=cfg.dropout,
    ).to(device)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
    )

    # -------------------------------
    # Prepare train tensors
    # -------------------------------
    train_drug_ids = torch.tensor([ex["drug_id"] for ex in train_queries], dtype=torch.long, device=device)
    train_rel_ids = torch.tensor([ex["relation_id"] for ex in train_queries], dtype=torch.long, device=device)
    train_disease_ids = torch.tensor([ex["disease_id"] for ex in train_queries], dtype=torch.long, device=device)

    num_train = len(train_queries)
    global_step = 0
    best_epoch = -1
    best_probe = None
    best_stats = None
    best_score = -1e18
    bad_epochs = 0
    stopped_early = False

    # For tie-breaking, we prefer:
    #   higher recall20, then lower top1 dominance, then lower loss
    def composite_probe_score(probe: Dict[str, Any], loss_val: float) -> float:
        return (
            1000.0 * probe["recall20"]
            - 10.0 * probe["top1_dominance_ratio"]
            - 0.1 * loss_val
        )

    # -------------------------------
    # Training
    # -------------------------------
    for epoch in range(1, cfg.num_epochs + 1):
        model.train()

        # shuffle indices
        perm = torch.randperm(num_train, device=device)

        epoch_loss_sum = 0.0
        epoch_pos_scores = []
        epoch_neg_scores = []
        epoch_grad_norms = []

        for start in range(0, num_train, cfg.batch_size):
            global_step += 1
            end = min(start + cfg.batch_size, num_train)
            idx = perm[start:end]

            batch_drugs = train_drug_ids[idx]
            batch_rels = train_rel_ids[idx]
            batch_diseases = train_disease_ids[idx]

            neg_drugs = sample_negative_drugs(
                batch_gold_drug_ids=batch_drugs,
                drug_universe_ids=drug_universe_ids,
                num_negatives=cfg.num_negatives,
                device=device,
            )

            optimizer.zero_grad(set_to_none=True)

            node_repr = model.encode(g, etypes)

            pos_scores = model.score_pairs(
                node_repr=node_repr,
                drug_ids=batch_drugs,
                relation_ids=batch_rels,
                disease_ids=batch_diseases,
            )  # [B]

            # negative scores
            # neg_drugs: [B, K]
            B, K = neg_drugs.shape
            neg_rel_ids = batch_rels.unsqueeze(1).expand(B, K).reshape(-1)
            neg_disease_ids = batch_diseases.unsqueeze(1).expand(B, K).reshape(-1)
            neg_scores = model.score_pairs(
                node_repr=node_repr,
                drug_ids=neg_drugs.reshape(-1),
                relation_ids=neg_rel_ids,
                disease_ids=neg_disease_ids,
            ).reshape(B, K)

            loss = pairwise_margin_loss(
                pos_scores=pos_scores,
                neg_scores=neg_scores,
                margin=cfg.margin,
            )
            loss.backward()

            grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip_norm)
            optimizer.step()

            epoch_loss_sum += float(loss.item()) * B
            epoch_pos_scores.append(pos_scores.detach().cpu())
            epoch_neg_scores.append(neg_scores.detach().cpu())
            epoch_grad_norms.append(
                float(grad_norm.item()) if hasattr(grad_norm, "item") else float(grad_norm)
            )

        avg_epoch_loss = epoch_loss_sum / max(1, num_train)
        all_pos = torch.cat(epoch_pos_scores, dim=0)
        all_neg = torch.cat(epoch_neg_scores, dim=0)
        stats = compute_score_stats(all_pos, all_neg)
        avg_grad_norm = sum(epoch_grad_norms) / max(1, len(epoch_grad_norms))

        probe = run_valid_probe(
            model=model,
            g=g,
            etypes=etypes,
            valid_queries=valid_queries,
            drug_universe_ids=drug_universe_ids,
            valid_probe_size=cfg.valid_probe_size,
            device=device,
            seed=cfg.seed + epoch,  # small variation across epochs
        )

        log_row = {
            "epoch": epoch,
            "global_step": global_step,
            "avg_epoch_loss": avg_epoch_loss,
            "avg_grad_norm": avg_grad_norm,
            **stats,
            "valid_probe_recall20": probe["recall20"],
            "valid_probe_top1_hit_ratio": probe["top1_hit_ratio"],
            "valid_probe_unique_top1_count": probe["unique_top1_count"],
            "valid_probe_top1_dominance_ratio": probe["top1_dominance_ratio"],
        }
        append_jsonl(train_log_path, log_row)
        print(json.dumps(log_row, ensure_ascii=False))

        current_score = composite_probe_score(probe, avg_epoch_loss)
        if current_score > best_score:
            best_score = current_score
            best_epoch = epoch
            best_probe = probe
            best_stats = {
                "epoch": epoch,
                "avg_epoch_loss": avg_epoch_loss,
                "avg_grad_norm": avg_grad_norm,
                **stats,
            }
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "config": asdict(cfg),
                    "best_epoch": best_epoch,
                    "best_score": best_score,
                    "best_probe": best_probe,
                    "best_stats": best_stats,
                },
                ckpt_path,
            )
            bad_epochs = 0
        else:
            bad_epochs += 1

        if cfg.save_every_epochs > 0 and epoch % cfg.save_every_epochs == 0:
            # optional rolling meta save
            save_json(
                meta_path,
                {
                    "week": 7,
                    "day": 2,
                    "goal": "Train a more stable R-GCN coarse ranker v2.",
                    "config": asdict(cfg),
                    "device": str(device),
                    "num_nodes": num_nodes,
                    "num_relations": num_rels,
                    "num_train_queries": len(train_queries),
                    "num_valid_queries": len(valid_queries),
                    "num_test_queries": len(test_queries),
                    "drug_universe_size": int(drug_universe_ids.numel()),
                    "skipped_graph_rows": skipped_graph_rows,
                    "latest_epoch": epoch,
                    "best_epoch": best_epoch,
                    "best_score": best_score,
                    "best_probe": best_probe,
                    "best_stats": best_stats,
                    "checkpoint_path": str(ckpt_path),
                },
            )

        if bad_epochs >= cfg.early_stop_patience:
            stopped_early = True
            print(f"[INFO] Early stopping at epoch {epoch} (patience={cfg.early_stop_patience}).")
            break

    # -------------------------------
    # Final writes
    # -------------------------------
    if best_probe is None or best_stats is None:
        raise RuntimeError("Training finished without saving any checkpoint.")

    save_json(
        day2_score_stats_path,
        {
            "best_epoch": best_epoch,
            "best_probe": best_probe,
            "best_stats": best_stats,
        },
    )

    write_top1_probe_tsv(day2_top1_probe_path, best_probe, id2entity)

    # tail of log
    log_rows = []
    with train_log_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                log_rows.append(json.loads(line))
    train_log_tail = log_rows[-10:]

    write_day2_markdown_report(
        report_path=day2_md_path,
        cfg=cfg,
        train_log_tail=train_log_tail,
        best_epoch=best_epoch,
        best_probe=best_probe,
        best_stats=best_stats,
        stopped_early=stopped_early,
    )

    save_json(
        meta_path,
        {
            "week": 7,
            "day": 2,
            "goal": "Train a more stable R-GCN coarse ranker v2.",
            "config": asdict(cfg),
            "device": str(device),
            "num_nodes": num_nodes,
            "num_relations": num_rels,
            "num_train_queries": len(train_queries),
            "num_valid_queries": len(valid_queries),
            "num_test_queries": len(test_queries),
            "drug_universe_size": int(drug_universe_ids.numel()),
            "skipped_graph_rows": skipped_graph_rows,
            "best_epoch": best_epoch,
            "best_score": best_score,
            "best_probe": best_probe,
            "best_stats": best_stats,
            "stopped_early": stopped_early,
            "checkpoint_path": str(ckpt_path),
            "important_note": "Day 2 optimizes stability and score discrimination only; Day 3 is responsible for true candidate retrieval evaluation.",
        },
    )

    print("\nSaved:")
    print(f"- {ckpt_path}")
    print(f"- {train_log_path}")
    print(f"- {meta_path}")
    print(f"- {day2_score_stats_path}")
    print(f"- {day2_top1_probe_path}")
    print(f"- {day2_md_path}")


if __name__ == "__main__":
    main()