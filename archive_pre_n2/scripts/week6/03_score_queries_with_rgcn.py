from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import pandas as pd
import torch


def load_pickle(path: Path):
    with path.open("rb") as f:
        return pickle.load(f)


def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Week 6 Day 2 - score Setting-A queries with trained R-GCN coarse ranker.")
    parser.add_argument(
        "--checkpoint_path",
        type=Path,
        default=Path("dataset/setting_a/09_real_coarse_ranker/rgcn_ranker_checkpoint.pt"),
    )
    parser.add_argument(
        "--entity2id_path",
        type=Path,
        default=Path("dataset/setting_a/04_drkgc_json/entity2id.pkl"),
    )
    parser.add_argument(
        "--relation2id_path",
        type=Path,
        default=Path("dataset/setting_a/04_drkgc_json/relation2id.pkl"),
    )
    parser.add_argument(
        "--train_split_path",
        type=Path,
        default=Path("dataset/setting_a/01_split/train.tsv"),
    )
    parser.add_argument(
        "--valid_split_path",
        type=Path,
        default=Path("dataset/setting_a/01_split/valid.tsv"),
    )
    parser.add_argument(
        "--test_split_path",
        type=Path,
        default=Path("dataset/setting_a/01_split/test.tsv"),
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=Path("dataset/setting_a/09_real_coarse_ranker"),
    )
    parser.add_argument(
        "--relation_name",
        type=str,
        default="indication",
    )
    return parser.parse_args()


def load_split(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t")
    df["head"] = df["head"].astype(str).str.strip()
    df["relation"] = df["relation"].astype(str).str.strip()
    df["tail"] = df["tail"].astype(str).str.strip()
    return df


def score_split(
    split_name: str,
    split_df: pd.DataFrame,
    node_emb: torch.Tensor,
    rel_emb: torch.Tensor,
    relation_id: int,
    drug_names: list[str],
    drug_ids: list[int],
    entity2id: dict,
    output_path: Path,
):
    query_disease_names = split_df["tail"].tolist()
    gold_drug_names = split_df["head"].tolist()

    query_ids = torch.tensor([entity2id[x] for x in query_disease_names], dtype=torch.long)
    gold_ids = torch.tensor([entity2id[x] for x in gold_drug_names], dtype=torch.long)
    drug_ids_t = torch.tensor(drug_ids, dtype=torch.long)

    disease_emb = node_emb[query_ids]                                # [N, D]
    relation_vec = rel_emb[relation_id].unsqueeze(0)                 # [1, D]
    query_vec = disease_emb * relation_vec                           # [N, D]
    drug_emb = node_emb[drug_ids_t]                                  # [M, D]

    scores = torch.matmul(query_vec, drug_emb.T)                     # [N, M]

    payload = {
        "split": split_name,
        "relation_name": "indication",
        "query_entity_names": query_disease_names,
        "query_entity_ids": query_ids,
        "gold_entity_names": gold_drug_names,
        "gold_entity_ids": gold_ids,
        "candidate_entity_names": drug_names,
        "candidate_entity_ids": drug_ids_t,
        "scores": scores,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(payload, output_path)

    top1_idx = torch.argmax(scores, dim=1)
    top1_ids = drug_ids_t[top1_idx]
    top1_hit_ratio = float((top1_ids == gold_ids).float().mean().item())

    meta = {
        "split": split_name,
        "num_queries": int(scores.shape[0]),
        "drug_universe_size": int(scores.shape[1]),
        "score_tensor_shape": list(scores.shape),
        "top1_hit_ratio_raw": round(top1_hit_ratio, 6),
        "output_path": str(output_path),
    }
    return meta


def main():
    args = parse_args()

    entity2id = load_pickle(args.entity2id_path)
    relation2id = load_pickle(args.relation2id_path)

    checkpoint = torch.load(args.checkpoint_path, map_location="cpu")
    node_emb = checkpoint["node_embeddings"]
    rel_emb = checkpoint["relation_embeddings"]

    if args.relation_name not in relation2id:
        raise KeyError(f"Relation `{args.relation_name}` not found in relation2id.")
    relation_id = relation2id[args.relation_name]

    drug_names = checkpoint["drug_universe_names"]
    drug_ids = checkpoint["drug_universe_ids"]

    train_df = load_split(args.train_split_path)
    valid_df = load_split(args.valid_split_path)
    test_df = load_split(args.test_split_path)

    train_meta = score_split(
        "train",
        train_df,
        node_emb,
        rel_emb,
        relation_id,
        drug_names,
        drug_ids,
        entity2id,
        args.output_dir / "train_scores.pt",
    )
    valid_meta = score_split(
        "valid",
        valid_df,
        node_emb,
        rel_emb,
        relation_id,
        drug_names,
        drug_ids,
        entity2id,
        args.output_dir / "valid_scores.pt",
    )
    test_meta = score_split(
        "test",
        test_df,
        node_emb,
        rel_emb,
        relation_id,
        drug_names,
        drug_ids,
        entity2id,
        args.output_dir / "test_scores.pt",
    )

    dump_meta = {
        "week": 6,
        "day": 2,
        "goal": "Dump real coarse-ranker scores for train/valid/test.",
        "checkpoint_path": str(args.checkpoint_path),
        "relation_name": args.relation_name,
        "relation_id": int(relation_id),
        "drug_universe_size": len(drug_ids),
        "splits": {
            "train": train_meta,
            "valid": valid_meta,
            "test": test_meta,
        },
        "note": "These are raw score dumps. Day 3 will convert them into top20_raw and top20_drkgc_ready artifacts.",
    }
    save_json(args.output_dir / "score_dump_meta.json", dump_meta)

    print("=" * 80)
    print("Saved raw score dumps:")
    print(" -", args.output_dir / "train_scores.pt")
    print(" -", args.output_dir / "valid_scores.pt")
    print(" -", args.output_dir / "test_scores.pt")
    print(" -", args.output_dir / "score_dump_meta.json")
    print("=" * 80)


if __name__ == "__main__":
    main()