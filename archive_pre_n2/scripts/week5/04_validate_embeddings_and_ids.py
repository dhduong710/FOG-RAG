#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import torch


def load_pickle(path: Path):
    with path.open("rb") as f:
        return pickle.load(f)


def save_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Validate exported entity embeddings against id maps.")
    parser.add_argument("--embedding_path", type=Path, default=Path("dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt"))
    parser.add_argument("--entity2id_path", type=Path, default=Path("dataset/setting_a/08_backbone_ready/entity2id.pkl"))
    parser.add_argument("--reference_embedding_path", type=Path, default=Path("dataset/setting_a/07_pilot_ready/mock_entity_embeddings.pt"))
    parser.add_argument("--report_path", type=Path, default=Path("reports/week5/day3_embedding_report.md"))
    return parser.parse_args()


def main():
    args = parse_args()

    entity2id = load_pickle(args.entity2id_path)
    emb = torch.load(args.embedding_path, map_location="cpu")

    if isinstance(emb, dict):
        raise TypeError(
            "Expected tensor from torch.load(embedding_path), but got dict. "
            "GraphEnhancer in your repo should receive a tensor-shaped embedding matrix."
        )

    assert isinstance(emb, torch.Tensor), f"Expected torch.Tensor, got {type(emb)}"
    assert emb.ndim == 2, f"Expected 2D embedding tensor, got shape {tuple(emb.shape)}"
    assert emb.shape[0] == len(entity2id), (
        f"Entity count mismatch: embedding rows={emb.shape[0]} vs len(entity2id)={len(entity2id)}"
    )

    nan_count = int(torch.isnan(emb).sum().item())
    inf_count = int(torch.isinf(emb).sum().item())
    zero_like = bool(torch.allclose(emb, torch.zeros_like(emb)))
    mean_abs = float(emb.abs().mean().item())
    std_val = float(emb.std().item())

    ref_note = "reference_embedding_not_found"
    ref_shape = None
    dim_match_ref = None

    if args.reference_embedding_path.exists():
        ref = torch.load(args.reference_embedding_path, map_location="cpu")
        if isinstance(ref, torch.Tensor) and ref.ndim == 2:
            ref_shape = tuple(ref.shape)
            dim_match_ref = (emb.shape[1] == ref.shape[1])
            ref_note = "reference_embedding_loaded"
        else:
            ref_note = "reference_embedding_exists_but_not_plain_2d_tensor"

    ok = (
        emb.shape[0] == len(entity2id)
        and nan_count == 0
        and inf_count == 0
        and not zero_like
    )

    report = f"""# Week 5 - Day 3 Embedding Report

## Input
- embedding_path: `{args.embedding_path}`
- entity2id_path: `{args.entity2id_path}`
- reference_embedding_path: `{args.reference_embedding_path}`

## Validation summary
- embedding_type: `{type(emb)}`
- embedding_shape: `{tuple(emb.shape)}`
- num_entities_from_entity2id: `{len(entity2id)}`
- entity_count_match: `{emb.shape[0] == len(entity2id)}`
- nan_count: `{nan_count}`
- inf_count: `{inf_count}`
- all_zero_like: `{zero_like}`
- mean_abs: `{mean_abs:.8f}`
- std: `{std_val:.8f}`

## Reference comparison
- reference_note: `{ref_note}`
- reference_shape: `{ref_shape}`
- embedding_dim_match_reference: `{dim_match_ref}`

## Judgment
- VALID_FOR_DAY4: `{ok}`

## Interpretation
This report checks only whether the exported entity embedding matrix is structurally valid
for week-5 day-4 server dry run. It does not claim that the embedding is already optimal.
"""

    save_text(args.report_path, report)

    print(report)
    if ok:
        print("\n[OK] Embedding validation passed.")
    else:
        print("\n[WARN] Embedding validation failed. Fix before day 4.")


if __name__ == "__main__":
    main()