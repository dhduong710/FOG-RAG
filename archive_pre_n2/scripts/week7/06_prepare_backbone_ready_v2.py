#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 7 - Day 5
Build dataset/setting_a/12_backbone_ready_ranker_v2 from 11_ranker_v2 candidate artifacts.

Pipeline:
1. Load *_top20_drkgc_ready.json from Day 3
2. Convert them into ranked_input JSON expected by prompt_subgraph.py
3. Call prompt_subgraph.py to add prompt + subgraph and enforce exact leakage checks
4. Copy id maps and write manifest

This intentionally reuses the already-stable prompt_subgraph pipeline instead of
re-implementing subgraph retrieval logic.
"""

from __future__ import annotations

import argparse
import csv
import json
import pickle
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


# ============================================================
# Config
# ============================================================

@dataclass
class PrepareConfig:
    seed: int
    train_candidate_ready_json: str
    valid_candidate_ready_json: str
    test_candidate_ready_json: str
    train_graph_tsv: str
    train_split_tsv: str
    valid_split_tsv: str
    test_split_tsv: str
    entity2id_path: str
    id2entity_path: str
    relation2id_path: str
    id2relation_path: str
    tail_pred_lex: str
    head_pred_lex: str
    rules_path: str
    output_dir: str
    report_dir: str
    target_relation: str
    graph_size: int
    bkg: bool


# ============================================================
# Utilities
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


def load_pickle(path: Path) -> Any:
    with path.open("rb") as f:
        return pickle.load(f)


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


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


def ensure_noheader_tsv(src: Path, dst: Path) -> Dict[str, Any]:
    """
    Writes a headerless TSV copy.
    If the first row looks like a header (head/relation/tail or similar), drop it.
    """
    rows = []
    with src.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if not row:
                continue
            rows.append(row)

    dropped_header = False
    if rows:
        first = [x.strip().lower() for x in rows[0][:3]]
        if first in [
            ["head", "relation", "tail"],
            ["drug", "relation", "disease"],
            ["subject", "predicate", "object"],
        ]:
            rows = rows[1:]
            dropped_header = True

    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        for row in rows:
            writer.writerow(row[:3])

    return {
        "source": str(src),
        "saved": str(dst),
        "num_rows": len(rows),
        "dropped_header": dropped_header,
    }


# ============================================================
# Conversion
# ============================================================

def build_split_lookup(
    split_tsv: Path,
    entity2id: Dict[str, int],
    relation2id: Dict[str, int],
    target_relation: str,
) -> Dict[Tuple[int, int], Dict[str, Any]]:
    """
    Build lookup keyed by (query_entity_id, gold_entity_id) for head prediction:
      triple = (drug, indication, disease)
      query entity = disease
      gold entity = drug
    """
    triples = read_tsv_triples(split_tsv)
    lookup = {}
    for h, r, t in triples:
        if r != target_relation:
            continue
        if h not in entity2id or t not in entity2id or r not in relation2id:
            continue
        key = (entity2id[t], entity2id[h])  # (query_entity_id, gold_entity_id)
        lookup[key] = {
            "triple": [h, r, t],
            "triple_id": [entity2id[h], relation2id[r], entity2id[t]],
            "type": "predicted_head",
            "query_entity": t,
            "query_entity_id": entity2id[t],
            "gold_entity": h,
            "gold_entity_id": entity2id[h],
            "relation_name": r,
            "relation_id": relation2id[r],
        }
    return lookup


def convert_candidate_ready_to_ranked_input(
    candidate_ready_rows: List[Dict[str, Any]],
    split_lookup: Dict[Tuple[int, int], Dict[str, Any]],
) -> List[Dict[str, Any]]:
    out = []

    for row in candidate_ready_rows:
        key = (int(row["query_entity_id"]), int(row["gold_entity_id"]))
        if key not in split_lookup:
            raise KeyError(
                f"Cannot find split triple for key={key} "
                f"(query={row['query_entity']}, gold={row['gold_entity']})"
            )

        base = split_lookup[key]

        rank_entities = row["candidate_entities"]
        rank_entities_id = row["candidate_entity_ids"]

        if len(rank_entities) != 20 or len(rank_entities_id) != 20:
            raise ValueError(
                f"Candidate list length must be 20, got len(names)={len(rank_entities)}, "
                f"len(ids)={len(rank_entities_id)} for query={row['query_entity']}"
            )

        try:
            rank = rank_entities_id.index(base["gold_entity_id"]) + 1
        except ValueError:
            # This should not happen for drkgc_ready.
            raise ValueError(
                f"Gold entity id {base['gold_entity_id']} not found in drkgc_ready candidates "
                f"for query={base['query_entity']}"
            )

        item = {
            "triple": base["triple"],
            "triple_id": base["triple_id"],
            "type": base["type"],
            "query_entity": base["query_entity"],
            "query_entity_id": base["query_entity_id"],
            "rank_entities": rank_entities,
            "rank_entities_id": rank_entities_id,
            "rank": rank,
            "gold_entity": row["gold_entity"],
            "gold_entity_id": row["gold_entity_id"],
            "gold_in_topk_raw": row["gold_in_topk_raw"],
            "gold_in_topk_ready": row["gold_in_topk_ready"],
            "gold_injected": row["gold_injected"],
            "gold_rank_in_full_universe": row["gold_rank_in_full_universe"],
        }
        out.append(item)

    return out


# ============================================================
# Prompt-subgraph wrapper
# ============================================================

def run_prompt_subgraph(
    *,
    train_graph_noheader: Path,
    valid_raw_noheader: Path,
    test_raw_noheader: Path,
    train_ranked_input: Path,
    valid_ranked_input: Path,
    test_ranked_input: Path,
    train_saved_json: Path,
    valid_saved_json: Path,
    test_saved_json: Path,
    cfg: PrepareConfig,
    python_exe: str,
    log_path: Path,
) -> None:
    cmd = [
        python_exe,
        "prompt_subgraph.py",
        "--train_raw", str(train_graph_noheader),
        "--valid_raw", str(valid_raw_noheader),
        "--test_raw", str(test_raw_noheader),
        "--entity2id_path", cfg.entity2id_path,
        "--id2entity_path", cfg.id2entity_path,
        "--id2relation_path", cfg.id2relation_path,
        "--train_json_path", str(train_ranked_input),
        "--valid_json_path", str(valid_ranked_input),
        "--test_json_path", str(test_ranked_input),
        "--train_path_saved", str(train_saved_json),
        "--valid_path_saved", str(valid_saved_json),
        "--test_path_saved", str(test_saved_json),
        "--tail_pred_lex", cfg.tail_pred_lex,
        "--head_pred_lex", cfg.head_pred_lex,
        "--rules_path", cfg.rules_path,
        "--graph_size", str(cfg.graph_size),
    ]
    if cfg.bkg:
        cmd.append("--bkg")

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as f:
        proc = subprocess.run(
            cmd,
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    if proc.returncode != 0:
        raise RuntimeError(
            f"prompt_subgraph.py failed with return code {proc.returncode}. "
            f"See log: {log_path}"
        )


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        required=True,
        help="Path to configs/week7/backbone_ready_ranker_v2.yaml",
    )
    args = parser.parse_args()

    cfg_dict = load_yaml(Path(args.config))
    cfg = PrepareConfig(**cfg_dict)

    output_dir = Path(cfg.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_dir = Path(cfg.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    tmp_dir = output_dir / "_tmp_prompt_subgraph"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # Load mappings
    # --------------------------------------------------------
    entity2id = load_pickle(Path(cfg.entity2id_path))
    relation2id = load_pickle(Path(cfg.relation2id_path))

    if cfg.target_relation not in relation2id:
        raise ValueError(
            f"target_relation '{cfg.target_relation}' not found in relation2id: {sorted(relation2id.keys())}"
        )

    # --------------------------------------------------------
    # Load candidate-ready artifacts
    # --------------------------------------------------------
    train_ready = load_json(Path(cfg.train_candidate_ready_json))
    valid_ready = load_json(Path(cfg.valid_candidate_ready_json))
    test_ready = load_json(Path(cfg.test_candidate_ready_json))

    # --------------------------------------------------------
    # Build split lookups from raw split TSVs
    # --------------------------------------------------------
    train_lookup = build_split_lookup(
        Path(cfg.train_split_tsv), entity2id, relation2id, cfg.target_relation
    )
    valid_lookup = build_split_lookup(
        Path(cfg.valid_split_tsv), entity2id, relation2id, cfg.target_relation
    )
    test_lookup = build_split_lookup(
        Path(cfg.test_split_tsv), entity2id, relation2id, cfg.target_relation
    )

    # --------------------------------------------------------
    # Convert to ranked_input JSON for prompt_subgraph.py
    # --------------------------------------------------------
    train_ranked_input = convert_candidate_ready_to_ranked_input(train_ready, train_lookup)
    valid_ranked_input = convert_candidate_ready_to_ranked_input(valid_ready, valid_lookup)
    test_ranked_input = convert_candidate_ready_to_ranked_input(test_ready, test_lookup)

    train_ranked_input_path = tmp_dir / "train_ranked_input.json"
    valid_ranked_input_path = tmp_dir / "valid_ranked_input.json"
    test_ranked_input_path = tmp_dir / "test_ranked_input.json"

    save_json(train_ranked_input_path, train_ranked_input)
    save_json(valid_ranked_input_path, valid_ranked_input)
    save_json(test_ranked_input_path, test_ranked_input)

    # --------------------------------------------------------
    # Prepare headerless TSV copies
    # --------------------------------------------------------
    train_graph_noheader = tmp_dir / "train_graph_noheader.tsv"
    valid_raw_noheader = tmp_dir / "valid_raw_noheader.tsv"
    test_raw_noheader = tmp_dir / "test_raw_noheader.tsv"

    train_graph_info = ensure_noheader_tsv(Path(cfg.train_graph_tsv), train_graph_noheader)
    valid_raw_info = ensure_noheader_tsv(Path(cfg.valid_split_tsv), valid_raw_noheader)
    test_raw_info = ensure_noheader_tsv(Path(cfg.test_split_tsv), test_raw_noheader)

    # --------------------------------------------------------
    # Run prompt_subgraph.py
    # --------------------------------------------------------
    train_saved_json = output_dir / "train.json"
    valid_saved_json = output_dir / "valid.json"
    test_saved_json = output_dir / "test.json"

    prompt_log_path = report_dir / "day5_prepare_backbone_ready_v2.log"

    run_prompt_subgraph(
        train_graph_noheader=train_graph_noheader,
        valid_raw_noheader=valid_raw_noheader,
        test_raw_noheader=test_raw_noheader,
        train_ranked_input=train_ranked_input_path,
        valid_ranked_input=valid_ranked_input_path,
        test_ranked_input=test_ranked_input_path,
        train_saved_json=train_saved_json,
        valid_saved_json=valid_saved_json,
        test_saved_json=test_saved_json,
        cfg=cfg,
        python_exe=sys.executable,
        log_path=prompt_log_path,
    )

    # --------------------------------------------------------
    # Copy mapping files
    # --------------------------------------------------------
    copy_file(Path(cfg.entity2id_path), output_dir / "entity2id.pkl")
    copy_file(Path(cfg.id2entity_path), output_dir / "id2entity.pkl")
    copy_file(Path(cfg.relation2id_path), output_dir / "relation2id.pkl")
    copy_file(Path(cfg.id2relation_path), output_dir / "id2relation.pkl")

    # --------------------------------------------------------
    # Write manifest
    # --------------------------------------------------------
    manifest = {
        "week": 7,
        "day": 5,
        "goal": "Build backbone-ready v2 package from ranker_v2 candidate artifacts.",
        "config": asdict(cfg),
        "input_candidate_artifacts": {
            "train": cfg.train_candidate_ready_json,
            "valid": cfg.valid_candidate_ready_json,
            "test": cfg.test_candidate_ready_json,
        },
        "tmp_prompt_subgraph_inputs": {
            "train_ranked_input": str(train_ranked_input_path),
            "valid_ranked_input": str(valid_ranked_input_path),
            "test_ranked_input": str(test_ranked_input_path),
            "train_graph_noheader": str(train_graph_noheader),
            "valid_raw_noheader": str(valid_raw_noheader),
            "test_raw_noheader": str(test_raw_noheader),
        },
        "output_files": {
            "train_json": str(train_saved_json),
            "valid_json": str(valid_saved_json),
            "test_json": str(test_saved_json),
            "entity2id_pkl": str(output_dir / "entity2id.pkl"),
            "id2entity_pkl": str(output_dir / "id2entity.pkl"),
            "relation2id_pkl": str(output_dir / "relation2id.pkl"),
            "id2relation_pkl": str(output_dir / "id2relation.pkl"),
        },
        "prompt_subgraph_log": str(prompt_log_path),
        "headerless_tsv_info": {
            "train_graph": train_graph_info,
            "valid_raw": valid_raw_info,
            "test_raw": test_raw_info,
        },
        "important_note": "This packaging step intentionally reuses prompt_subgraph.py so that exact leakage checks remain consistent with the already stable pipeline.",
    }
    save_json(output_dir / "manifest.json", manifest)

    # --------------------------------------------------------
    # Write brief day5 markdown
    # --------------------------------------------------------
    day5_md = report_dir / "day5_backbone_ready_v2.md"
    with day5_md.open("w", encoding="utf-8") as f:
        f.write("# Day 5 — backbone-ready v2 packaging\n\n")
        f.write("## Scope\n\n")
        f.write("- Convert week7 drkgc-ready candidates into ranked_input JSON.\n")
        f.write("- Reuse prompt_subgraph.py to build final train/valid/test with prompt + subgraph.\n")
        f.write("- Preserve exact leakage checks in the same way as the stable earlier pipeline.\n\n")

        f.write("## Inputs\n\n")
        f.write(f"- train_candidate_ready_json: `{cfg.train_candidate_ready_json}`\n")
        f.write(f"- valid_candidate_ready_json: `{cfg.valid_candidate_ready_json}`\n")
        f.write(f"- test_candidate_ready_json: `{cfg.test_candidate_ready_json}`\n")
        f.write(f"- train_graph_tsv: `{cfg.train_graph_tsv}`\n")
        f.write(f"- valid_split_tsv: `{cfg.valid_split_tsv}`\n")
        f.write(f"- test_split_tsv: `{cfg.test_split_tsv}`\n")
        f.write(f"- graph_size: `{cfg.graph_size}`\n\n")

        f.write("## Outputs\n\n")
        f.write(f"- `{train_saved_json}`\n")
        f.write(f"- `{valid_saved_json}`\n")
        f.write(f"- `{test_saved_json}`\n")
        f.write(f"- `{output_dir / 'manifest.json'}`\n")
        f.write(f"- prompt_subgraph log: `{prompt_log_path}`\n\n")

        f.write("## Notes\n\n")
        f.write("- Day 5 is a packaging day only.\n")
        f.write("- Exact leakage validation is delegated to prompt_subgraph.py.\n")
        f.write("- Day 6 will decide whether candidate improvement transfers to valid reranker behavior.\n")

    print("Saved:")
    print(f"- {train_saved_json}")
    print(f"- {valid_saved_json}")
    print(f"- {test_saved_json}")
    print(f"- {output_dir / 'manifest.json'}")
    print(f"- {day5_md}")
    print(f"- {prompt_log_path}")


if __name__ == "__main__":
    main()