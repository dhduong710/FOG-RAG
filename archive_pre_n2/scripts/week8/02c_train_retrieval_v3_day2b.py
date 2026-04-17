#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
import json
import pickle
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import Counter
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
    init_checkpoint_path: str
    train_top20_raw_json: str
    valid_top20_raw_json: str
    collapse_summary_path: str
    drug_bias_stats_path: str
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
    margin: float
    log_every_epochs: int
    valid_probe_size: int
    save_every_epochs: int
    raw_keep: int
    collapse_keep: int
    bias_keep: int
    random_fill: bool
    random_fill_max: int
    week7_v2_probe_recall20_target: float
    week7_v2_probe_top1_dominance_target: float


# ============================================================
# Utils
# ============================================================

def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_pickle(path: Path) -> Any:
    with path.open("rb") as f:
        return pickle.load(f)


def set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


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


def build_name_to_id_maps(entity2id, relation2id):
    id2entity = {v: k for k, v in entity2id.items()}
    id2relation = {v: k for k, v in relation2id.items()}
    return entity2id, id2entity, relation2id, id2relation


# ============================================================
# Data
# ============================================================

def load_graph(graph_path: Path, entity2id: Dict[str, int], relation2id: Dict[str, int]):
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


def load_query_triples(split_path: Path, entity2id, relation2id, target_relation: str):
    triples = read_tsv_triples(split_path)
    examples = []
    for h, r, t in triples:
        if r != target_relation:
            continue
        if h not in entity2id or t not in entity2id or r not in relation2id:
            continue
        examples.append({
            "drug_name": h,
            "drug_id": entity2id[h],
            "relation_name": r,
            "relation_id": relation2id[r],
            "disease_name": t,
            "disease_id": entity2id[t],
        })
    return examples


def build_drug_universe_from_splits(train_queries, valid_queries, test_queries):
    drug_ids = set()
    for ex in train_queries + valid_queries + test_queries:
        drug_ids.add(ex["drug_id"])
    return torch.tensor(sorted(drug_ids), dtype=torch.long)


def build_raw_map(raw_rows: List[Dict[str, Any]]) -> Dict[Tuple[int, int], Dict[str, Any]]:
    out = {}
    for row in raw_rows:
        out[(int(row["query_entity_id"]), int(row["gold_entity_id"]))] = row
    return out


# ============================================================
# Model
# ============================================================

class RGCNEncoder(nn.Module):
    def __init__(self, num_nodes, num_rels, embedding_dim, hidden_dim, num_layers, dropout):
        super().__init__()
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

    def forward(self, g, etypes):
        x = self.node_emb.weight
        for i, layer in enumerate(self.layers):
            x = layer(g, x, etypes)
            if i != len(self.layers) - 1:
                x = F.relu(x)
                x = self.dropout(x)
        return x


class RGCNCoarseRanker(nn.Module):
    def __init__(self, num_nodes, num_rels, embedding_dim, hidden_dim, num_layers, dropout):
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

    def encode(self, g, etypes):
        return self.encoder(g, etypes)

    def score_pairs(self, node_repr, drug_ids, relation_ids, disease_ids):
        drug_vec = node_repr[drug_ids]
        rel_vec = self.rel_emb(relation_ids)
        disease_vec = node_repr[disease_ids]
        return (drug_vec * rel_vec * disease_vec).sum(dim=-1)

    def score_candidates_for_query(self, node_repr, candidate_drug_ids, relation_id, disease_id):
        rel_ids = torch.full((candidate_drug_ids.size(0),), relation_id, dtype=torch.long, device=node_repr.device)
        disease_ids = torch.full((candidate_drug_ids.size(0),), disease_id, dtype=torch.long, device=node_repr.device)
        return self.score_pairs(node_repr, candidate_drug_ids, rel_ids, disease_ids)


# ============================================================
# Sampling
# ============================================================

def sample_query_specific_mixed_negatives(
    *,
    ex: Dict[str, Any],
    raw_map: Dict[Tuple[int, int], Dict[str, Any]],
    collapse_ids: List[int],
    bias_ids: List[int],
    drug_universe_ids: torch.Tensor,
    raw_keep: int,
    collapse_keep: int,
    bias_keep: int,
    num_negatives: int,
    random_fill: bool,
    random_fill_max: int,
    rng: random.Random,
) -> Tuple[List[int], Dict[str, Any]]:
    gold_id = int(ex["drug_id"])
    key = (int(ex["disease_id"]), int(ex["drug_id"]))
    raw_row = raw_map[key]

    selected: List[int] = []
    selected_set = set()

    # A. query-specific raw top non-gold
    raw_take = 0
    for nid in raw_row["candidate_entity_ids"]:
        nid = int(nid)
        if nid == gold_id or nid in selected_set:
            continue
        selected.append(nid)
        selected_set.add(nid)
        raw_take += 1
        if raw_take >= raw_keep:
            break

    # B. collapse drugs
    collapse_take = 0
    for nid in collapse_ids:
        nid = int(nid)
        if nid == gold_id or nid in selected_set:
            continue
        selected.append(nid)
        selected_set.add(nid)
        collapse_take += 1
        if collapse_take >= collapse_keep:
            break

    # C. bias-heavy drugs
    bias_take = 0
    for nid in bias_ids:
        nid = int(nid)
        if nid == gold_id or nid in selected_set:
            continue
        selected.append(nid)
        selected_set.add(nid)
        bias_take += 1
        if bias_take >= bias_keep:
            break

    # D. tiny random fill only if truly needed
    random_take = 0
    if random_fill and len(selected) < num_negatives:
        universe = drug_universe_ids.tolist()
        rng.shuffle(universe)
        for nid in universe:
            nid = int(nid)
            if nid == gold_id or nid in selected_set:
                continue
            selected.append(nid)
            selected_set.add(nid)
            random_take += 1
            if len(selected) >= num_negatives or random_take >= random_fill_max:
                break

    # E. fallback if still short: continue with leftover universe
    if len(selected) < num_negatives:
        universe = drug_universe_ids.tolist()
        for nid in universe:
            nid = int(nid)
            if nid == gold_id or nid in selected_set:
                continue
            selected.append(nid)
            selected_set.add(nid)
            if len(selected) >= num_negatives:
                break

    selected = selected[:num_negatives]
    if len(selected) < num_negatives:
        raise ValueError(
            f"Cannot fill enough negatives for query={ex['disease_name']} gold={ex['drug_name']}. "
            f"len(selected)={len(selected)} expected={num_negatives}"
        )

    debug = {
        "query_entity": ex["disease_name"],
        "query_entity_id": ex["disease_id"],
        "gold_entity": ex["drug_name"],
        "gold_entity_id": ex["drug_id"],
        "num_selected": len(selected),
        "raw_take": raw_take,
        "collapse_take": collapse_take,
        "bias_take": bias_take,
        "random_take": random_take,
        "first10_negative_ids": selected[:10],
    }
    return selected, debug


def pairwise_margin_loss(pos_scores, neg_scores, margin):
    pos_expand = pos_scores.unsqueeze(1).expand_as(neg_scores)
    return F.relu(margin - pos_expand + neg_scores).mean()


def compute_score_stats(pos_scores, neg_scores):
    gap = pos_scores.unsqueeze(1) - neg_scores
    return {
        "pos_score_mean": float(pos_scores.mean().item()),
        "pos_score_std": float(pos_scores.std().item()) if pos_scores.numel() > 1 else 0.0,
        "neg_score_mean": float(neg_scores.mean().item()),
        "neg_score_std": float(neg_scores.std().item()) if neg_scores.numel() > 1 else 0.0,
        "score_gap_mean": float(gap.mean().item()),
        "score_gap_std": float(gap.std().item()) if gap.numel() > 1 else 0.0,
    }


@torch.no_grad()
def run_valid_probe(model, g, etypes, valid_queries, drug_universe_ids, valid_probe_size, device, seed):
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

    cand_ids = drug_universe_ids.to(device)

    for ex in probe_examples:
        scores = model.score_candidates_for_query(
            node_repr=node_repr,
            candidate_drug_ids=cand_ids,
            relation_id=ex["relation_id"],
            disease_id=ex["disease_id"],
        )
        _, top_idx = torch.topk(scores, k=min(20, cand_ids.size(0)), largest=True, sorted=True)
        top_ids = cand_ids[top_idx].detach().cpu().tolist()

        if ex["drug_id"] in top_ids:
            recall20 += 1
        if top_ids and top_ids[0] == ex["drug_id"]:
            top1_hit += 1
        if top_ids:
            top1_counter[top_ids[0]] += 1

    n = len(probe_examples)
    most_common = top1_counter.most_common(20)
    top1_dom = (most_common[0][1] / n) if most_common else 0.0

    return {
        "num_probe_queries": n,
        "recall20": recall20 / n if n else 0.0,
        "top1_hit_ratio": top1_hit / n if n else 0.0,
        "unique_top1_count": len(top1_counter),
        "top1_dominance_ratio": top1_dom,
        "top1_counter": dict(top1_counter),
    }


def write_top1_probe_tsv(path: Path, probe: Dict[str, Any], id2entity: Dict[int, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(probe["top1_counter"].items(), key=lambda x: (-x[1], x[0]))
    with path.open("w", encoding="utf-8") as f:
        f.write("drug_id\tdrug_name\tcount\n")
        for drug_id, count in rows:
            f.write(f"{drug_id}\t{id2entity.get(int(drug_id), f'<UNK:{drug_id}>')}\t{count}\n")


def write_markdown_report(
    path: Path,
    cfg: TrainConfig,
    best_epoch: int,
    best_probe: Dict[str, Any],
    best_stats: Dict[str, Any],
    stopped_early: bool,
    sampled_neg_summary: Dict[str, Any],
    train_log_tail: List[Dict[str, Any]],
):
    lines = []
    lines.append("# Week8 / retrieval-v3 Day 2b — ranker_v3 warm-start training")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Warm-start from ranker_v2 instead of training from scratch.")
    lines.append("- Use query-specific mixed negatives with small global quotas.")
    lines.append("- Keep retrieval signal while reducing collapse.")
    lines.append("")

    lines.append("## Config")
    lines.append("")
    lines.append(f"- init_checkpoint_path = `{cfg.init_checkpoint_path}`")
    lines.append(f"- learning_rate = `{cfg.learning_rate}`")
    lines.append(f"- batch_size = `{cfg.batch_size}`")
    lines.append(f"- num_negatives = `{cfg.num_negatives}`")
    lines.append(f"- raw_keep = `{cfg.raw_keep}`")
    lines.append(f"- collapse_keep = `{cfg.collapse_keep}`")
    lines.append(f"- bias_keep = `{cfg.bias_keep}`")
    lines.append(f"- random_fill = `{cfg.random_fill}`")
    lines.append(f"- random_fill_max = `{cfg.random_fill_max}`")
    lines.append("")

    lines.append("## Best checkpoint")
    lines.append("")
    lines.append(f"- best_epoch = `{best_epoch}`")
    lines.append(f"- valid_probe_recall20 = `{best_probe.get('recall20')}`")
    lines.append(f"- valid_probe_top1_hit_ratio = `{best_probe.get('top1_hit_ratio')}`")
    lines.append(f"- valid_probe_unique_top1_count = `{best_probe.get('unique_top1_count')}`")
    lines.append(f"- valid_probe_top1_dominance_ratio = `{best_probe.get('top1_dominance_ratio')}`")
    lines.append(f"- pos_score_mean = `{best_stats.get('pos_score_mean')}`")
    lines.append(f"- neg_score_mean = `{best_stats.get('neg_score_mean')}`")
    lines.append(f"- score_gap_mean = `{best_stats.get('score_gap_mean')}`")
    lines.append(f"- stopped_early = `{stopped_early}`")
    lines.append("")

    lines.append("## Target reference from week7-v2")
    lines.append("")
    lines.append(f"- week7_v2_probe_recall20_target = `{cfg.week7_v2_probe_recall20_target}`")
    lines.append(f"- week7_v2_probe_top1_dominance_target = `{cfg.week7_v2_probe_top1_dominance_target}`")
    lines.append("")

    lines.append("## Sampled negative summary")
    lines.append("")
    for k, v in sampled_neg_summary.items():
        lines.append(f"- {k} = `{v}`")
    lines.append("")

    lines.append("## Last logged rows")
    lines.append("")
    for row in train_log_tail:
        lines.append(f"- `{json.dumps(row, ensure_ascii=False)}`")
    lines.append("")

    lines.append("## Conclusion")
    lines.append("")
    lines.append("- This run is acceptable only if it preserves a meaningful recall20 probe while reducing top1 dominance versus week7-v2.")
    lines.append("- Day 3 should start only if the tradeoff is clearly better than the failed Day 2 scratch run.")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to configs/week8/retrieval_v3_day2b.yaml")
    args = parser.parse_args()

    cfg = TrainConfig(**load_yaml(Path(args.config)))
    set_seed(cfg.seed)
    rng = random.Random(cfg.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    output_dir = Path(cfg.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir = Path(cfg.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    train_log_path = output_dir / "ranker_v3_day2b_train_log.jsonl"
    ckpt_path = output_dir / "rgcn_ranker_v3_day2b_checkpoint.pt"
    meta_path = output_dir / "ranker_v3_day2b_meta.json"
    sampled_train_neg_path = output_dir / "sampled_train_negatives_day2b.json"
    score_stats_path = report_dir / "day2b_ranker_v3_score_stats.json"
    top1_probe_tsv_path = report_dir / "day2b_ranker_v3_top1_probe.tsv"
    day2_md_path = report_dir / "day2b_ranker_v3_train.md"

    if train_log_path.exists():
        train_log_path.unlink()

    entity2id = load_pickle(Path(cfg.entity2id_path))
    relation2id = load_pickle(Path(cfg.relation2id_path))
    entity2id, id2entity, relation2id, _ = build_name_to_id_maps(entity2id, relation2id)

    if cfg.target_relation not in relation2id:
        raise ValueError(f"target_relation '{cfg.target_relation}' not found")
    target_relation_id = relation2id[cfg.target_relation]

    g, etypes, num_nodes, skipped_graph_rows = load_graph(Path(cfg.graph_path), entity2id, relation2id)
    g = g.to(device)
    etypes = etypes.to(device)

    train_queries = load_query_triples(Path(cfg.train_queries_path), entity2id, relation2id, cfg.target_relation)
    valid_queries = load_query_triples(Path(cfg.valid_queries_path), entity2id, relation2id, cfg.target_relation)
    test_queries = load_query_triples(Path(cfg.test_queries_path), entity2id, relation2id, cfg.target_relation)

    drug_universe_ids = build_drug_universe_from_splits(train_queries, valid_queries, test_queries)
    if cfg.candidate_universe != "drug_only":
        raise ValueError("This script only supports candidate_universe='drug_only'.")

    train_raw = load_json(Path(cfg.train_top20_raw_json))
    valid_raw = load_json(Path(cfg.valid_top20_raw_json))
    train_raw_map = build_raw_map(train_raw)
    valid_raw_map = build_raw_map(valid_raw)

    collapse_summary = load_json(Path(cfg.collapse_summary_path))
    drug_bias_stats = load_json(Path(cfg.drug_bias_stats_path))

    collapse_ids = [int(x["drug_id"]) for x in collapse_summary["collapse_summary"]["collapse_drugs"][:cfg.collapse_keep]]
    bias_ids = [int(x["drug_id"]) for x in drug_bias_stats["bias_table_sorted"][:cfg.bias_keep]]

    model = RGCNCoarseRanker(
        num_nodes=num_nodes,
        num_rels=len(relation2id),
        embedding_dim=cfg.embedding_dim,
        hidden_dim=cfg.hidden_dim,
        num_layers=cfg.num_rgcn_layers,
        dropout=cfg.dropout,
    ).to(device)

    # warm-start from ranker_v2
    init_ckpt = torch.load(cfg.init_checkpoint_path, map_location="cpu")
    state_dict = init_ckpt["model_state_dict"]
    model.load_state_dict(state_dict, strict=True)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
    )

    num_train = len(train_queries)
    global_step = 0
    best_epoch = -1
    best_probe = None
    best_stats = None
    best_score = -1e18
    bad_epochs = 0
    stopped_early = False

    sampled_train_examples_debug = []

    def composite_probe_score(probe, avg_epoch_loss):
        return (
            1000.0 * probe["recall20"]
            - 10.0 * probe["top1_dominance_ratio"]
            + 1.5 * probe["unique_top1_count"]
            + 50.0 * probe["top1_hit_ratio"]
            - 0.05 * avg_epoch_loss
        )

    for epoch in range(1, cfg.num_epochs + 1):
        model.train()

        perm = torch.randperm(num_train, device="cpu")
        epoch_loss_sum = 0.0
        epoch_pos_scores = []
        epoch_neg_scores = []
        epoch_grad_norms = []

        for start in range(0, num_train, cfg.batch_size):
            global_step += 1
            end = min(start + cfg.batch_size, num_train)
            batch_idx = perm[start:end].tolist()
            batch_examples = [train_queries[i] for i in batch_idx]

            all_neg_ids = []
            batch_debug_rows = []
            for ex in batch_examples:
                negs, dbg = sample_query_specific_mixed_negatives(
                    ex=ex,
                    raw_map=train_raw_map,
                    collapse_ids=collapse_ids,
                    bias_ids=bias_ids,
                    drug_universe_ids=drug_universe_ids,
                    raw_keep=cfg.raw_keep,
                    collapse_keep=cfg.collapse_keep,
                    bias_keep=cfg.bias_keep,
                    num_negatives=cfg.num_negatives,
                    random_fill=cfg.random_fill,
                    random_fill_max=cfg.random_fill_max,
                    rng=rng,
                )
                all_neg_ids.append(negs)
                batch_debug_rows.append(dbg)

            if len(sampled_train_examples_debug) < 20:
                sampled_train_examples_debug.extend(batch_debug_rows[: max(0, 20 - len(sampled_train_examples_debug))])

            neg_ids = torch.tensor(all_neg_ids, dtype=torch.long, device=device)
            batch_drugs = torch.tensor([ex["drug_id"] for ex in batch_examples], dtype=torch.long, device=device)
            batch_rels = torch.tensor([ex["relation_id"] for ex in batch_examples], dtype=torch.long, device=device)
            batch_diseases = torch.tensor([ex["disease_id"] for ex in batch_examples], dtype=torch.long, device=device)

            optimizer.zero_grad(set_to_none=True)

            node_repr = model.encode(g, etypes)

            pos_scores = model.score_pairs(node_repr, batch_drugs, batch_rels, batch_diseases)

            B, K = neg_ids.shape
            neg_rel_ids = batch_rels.unsqueeze(1).expand(B, K).reshape(-1)
            neg_disease_ids = batch_diseases.unsqueeze(1).expand(B, K).reshape(-1)
            neg_scores = model.score_pairs(
                node_repr,
                neg_ids.reshape(-1),
                neg_rel_ids,
                neg_disease_ids,
            ).reshape(B, K)

            loss = pairwise_margin_loss(pos_scores, neg_scores, cfg.margin)
            loss.backward()

            grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip_norm)
            optimizer.step()

            epoch_loss_sum += float(loss.item()) * B
            epoch_pos_scores.append(pos_scores.detach().cpu())
            epoch_neg_scores.append(neg_scores.detach().cpu())
            epoch_grad_norms.append(float(grad_norm.item()) if hasattr(grad_norm, "item") else float(grad_norm))

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
            seed=cfg.seed + epoch,
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

        if bad_epochs >= cfg.early_stop_patience:
            stopped_early = True
            print(f"[INFO] Early stopping at epoch {epoch}")
            break

    if best_probe is None or best_stats is None:
        raise RuntimeError("Training ended without best checkpoint.")

    sampled_train_neg_summary = {
        "num_saved_debug_rows": len(sampled_train_examples_debug),
        "raw_keep": cfg.raw_keep,
        "collapse_keep": cfg.collapse_keep,
        "bias_keep": cfg.bias_keep,
        "num_negatives": cfg.num_negatives,
        "random_fill_max": cfg.random_fill_max,
    }

    save_json(sampled_train_neg_path, {
        "summary": sampled_train_neg_summary,
        "rows": sampled_train_examples_debug,
    })
    save_json(score_stats_path, {
        "best_epoch": best_epoch,
        "best_probe": best_probe,
        "best_stats": best_stats,
    })
    write_top1_probe_tsv(top1_probe_tsv_path, best_probe, id2entity)

    log_rows = []
    with train_log_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                log_rows.append(json.loads(line))
    train_log_tail = log_rows[-10:]

    write_markdown_report(
        path=day2_md_path,
        cfg=cfg,
        best_epoch=best_epoch,
        best_probe=best_probe,
        best_stats=best_stats,
        stopped_early=stopped_early,
        sampled_neg_summary=sampled_train_neg_summary,
        train_log_tail=train_log_tail,
    )

    save_json(meta_path, {
        "week": 8,
        "stage": "retrieval_v3",
        "day": "2b",
        "goal": "Warm-start ranker_v3 with query-specific mixed negatives to reduce collapse without losing retrieval signal.",
        "config": asdict(cfg),
        "num_nodes": num_nodes,
        "num_relations": len(relation2id),
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
        "important_note": "This run warm-starts from ranker_v2; only proceed to Day 3 if probe retains meaningful recall20 while reducing top1 dominance.",
    })

    print("Saved:")
    print("-", ckpt_path)
    print("-", train_log_path)
    print("-", meta_path)
    print("-", sampled_train_neg_path)
    print("-", score_stats_path)
    print("-", top1_probe_tsv_path)
    print("-", day2_md_path)


if __name__ == "__main__":
    main()