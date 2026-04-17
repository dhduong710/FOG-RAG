#!/usr/bin/env python3
import argparse
import csv
import json
import pickle
from collections import Counter
from pathlib import Path

import dgl
from dgl.nn.functional import edge_softmax
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


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

    def score_full_drug_universe(self, node_repr, disease_ids, drug_universe_ids):
        drug_repr = node_repr[drug_universe_ids]
        disease_repr = node_repr[disease_ids]
        rel = self.scorer_rel.view(1, 1, -1)
        return torch.sum(drug_repr.unsqueeze(0) * rel * disease_repr.unsqueeze(1), dim=-1)


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
        "method": "HRGAT",
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
    parser.add_argument("--checkpoint_path", default="results/week8/hrgat_baseline_full_v1/hrgat_checkpoint.pt")
    parser.add_argument("--meta_path", default="results/week8/hrgat_baseline_full_v1/hrgat_meta.json")
    parser.add_argument("--graph_path", default="dataset/setting_a/02_graph/train_enriched_deg1000_final.tsv")
    parser.add_argument("--valid_queries_path", default="dataset/setting_a/01_split/valid.tsv")
    parser.add_argument("--raw_indication_path", default="dataset/setting_a/00_raw_triples/primekg_indication_only.tsv")
    parser.add_argument("--entity2id_path", default="dataset/setting_a/04_drkgc_json/entity2id.pkl")
    parser.add_argument("--relation2id_path", default="dataset/setting_a/04_drkgc_json/relation2id.pkl")
    parser.add_argument("--id2entity_path", default="dataset/setting_a/04_drkgc_json/id2entity.pkl")
    parser.add_argument("--out_dir", default="dataset/setting_a/17_structure_baselines")
    parser.add_argument("--report_path", default="reports/week8/day4_hrgat_results.md")
    args = parser.parse_args()

    checkpoint_path = Path(args.checkpoint_path)
    meta_path = Path(args.meta_path)
    graph_path = Path(args.graph_path)
    valid_queries_path = Path(args.valid_queries_path)
    raw_indication_path = Path(args.raw_indication_path)
    entity2id_path = Path(args.entity2id_path)
    relation2id_path = Path(args.relation2id_path)
    id2entity_path = Path(args.id2entity_path)
    out_dir = Path(args.out_dir)
    report_path = Path(args.report_path)

    out_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    meta = json.load(open(meta_path, "r", encoding="utf-8"))
    entity2id = load_pickle(entity2id_path)
    relation2id = load_pickle(relation2id_path)
    id2entity = load_pickle(id2entity_path)

    graph_rows = read_tsv(graph_path)
    src, dst, etypes_list, skipped = build_graph_tensors(graph_rows, entity2id, relation2id)

    num_nodes = max(entity2id.values()) + 1
    num_rels = max(relation2id.values()) + 1
    indication_rel_id = int(relation2id["indication"])

    g = dgl.graph((src, dst), num_nodes=num_nodes)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    g = g.to(device)
    etypes = torch.tensor(etypes_list, dtype=torch.long, device=device)

    valid_queries = read_queries(valid_queries_path, entity2id)
    if len(valid_queries) != 500:
        print(f"WARNING: valid queries detected = {len(valid_queries)} (expected 500)")

    drug_universe_ids, _ = derive_drug_universe_ids(raw_indication_path, entity2id)

    model = HRGATScorer(
        num_nodes=num_nodes,
        num_relations=num_rels,
        indication_rel_id=indication_rel_id,
        embedding_dim=meta["embedding_dim"],
        hidden_dim=meta["hidden_dim"],
        num_layers=meta["num_layers"],
        dropout=meta["dropout"],
    ).to(device)

    ckpt = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    with torch.no_grad():
        node_repr = model.encode(g, etypes)
        q_ids = torch.tensor([x["query_disease_id"] for x in valid_queries], dtype=torch.long, device=device)
        scores = model.score_full_drug_universe(node_repr, q_ids, drug_universe_ids)

    metrics, top1_counter, case_samples = compute_metrics_and_cases(
        score_matrix=scores,
        valid_queries=valid_queries,
        drug_universe_ids=drug_universe_ids,
        id2entity=id2entity,
    )

    metrics["checkpoint_path"] = str(checkpoint_path)
    metrics["checkpoint_best_epoch"] = ckpt.get("best_epoch")
    metrics["meta_path"] = str(meta_path)
    metrics["graph_path"] = str(graph_path)
    metrics["valid_queries_path"] = str(valid_queries_path)
    metrics["device"] = str(device)
    metrics["skipped_graph_rows"] = skipped

    torch.save(scores.detach().cpu(), out_dir / "hrgat_valid_scores.pt")
    save_json(out_dir / "hrgat_valid_metrics.json", metrics)
    save_json(out_dir / "hrgat_valid_case_samples.json", case_samples)

    with (out_dir / "hrgat_valid_top1_frequency.tsv").open("w", encoding="utf-8") as f:
        f.write("drug\tcount\tratio\n")
        for drug, count in top1_counter.most_common():
            ratio = count / len(valid_queries)
            f.write(f"{drug}\t{count}\t{ratio:.8f}\n")

    report_md = []
    report_md.append("# Day 4 HRGAT Valid Results")
    report_md.append("")
    report_md.append("## 1. Scope")
    report_md.append("- Full valid evaluation for HRGAT structure-only baseline")
    report_md.append("- Same Setting A structure-only protocol as Day 2")
    report_md.append("")
    report_md.append("## 2. Sources")
    report_md.append(f"- checkpoint_path: `{checkpoint_path}`")
    report_md.append(f"- checkpoint_best_epoch: {ckpt.get('best_epoch')}")
    report_md.append(f"- meta_path: `{meta_path}`")
    report_md.append(f"- graph_path: `{graph_path}`")
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
    report_md.append(f"- `{out_dir / 'hrgat_valid_scores.pt'}`")
    report_md.append(f"- `{out_dir / 'hrgat_valid_metrics.json'}`")
    report_md.append(f"- `{out_dir / 'hrgat_valid_top1_frequency.tsv'}`")
    report_md.append(f"- `{out_dir / 'hrgat_valid_case_samples.json'}`")
    report_md.append("")
    report_md.append("## 6. Decision on baseline #3")
    report_md.append("- Preferred: ComplEx")
    report_md.append("- Fallback: TransE")
    report_md.append("")
    report_md.append("## 7. Conclusion")
    report_md.append("- HRGAT valid evaluation completed under clean structure-only protocol.")
    report_md.append("- If metrics and collapse profile are reasonable, move to ComplEx on Day 5.")

    report_path.write_text("\n".join(report_md), encoding="utf-8")

    print("Saved:")
    print(f"- {out_dir / 'hrgat_valid_scores.pt'}")
    print(f"- {out_dir / 'hrgat_valid_metrics.json'}")
    print(f"- {out_dir / 'hrgat_valid_top1_frequency.tsv'}")
    print(f"- {out_dir / 'hrgat_valid_case_samples.json'}")
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