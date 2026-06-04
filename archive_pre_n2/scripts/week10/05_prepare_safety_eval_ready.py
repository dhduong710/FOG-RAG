#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import pickle
import shutil
from pathlib import Path

import networkx as nx
import pandas as pd
from tqdm import tqdm

from prompt_subgraph import add_prompt, subgraph_func, count_exact_leaks


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def load_pickle(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def load_rules_json(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # rules.json may have string keys and relation names/ids
    processed = {}
    for k, v in raw.items():
        try:
            key = int(k)
        except Exception:
            key = k
        # keep as list of tuples/lists
        processed[key] = v
    return processed


def build_graph(graph_tsv, entity2id, relation2id):
    df = pd.read_csv(graph_tsv, sep='\t', header=None, skiprows=1)
    # graph file is expected to be text triples: head relation tail
    df[0] = df[0].map(entity2id)
    df[1] = df[1].map(relation2id)
    df[2] = df[2].map(entity2id)

    if df[[0, 1, 2]].isnull().any().any():
        bad = df[df[[0, 1, 2]].isnull().any(axis=1)]
        raise ValueError(f"Graph mapping has NaN rows. Example:\n{bad.head()}")

    G = nx.MultiDiGraph()
    for _, row in df.iterrows():
        h, r, t = int(row[0]), int(row[1]), int(row[2])
        G.add_edge(h, t, relation=r)
    return G


def detect_cand_field(row):
    if "candidate_entities" in row:
        return "candidate_entities"
    if "rank_entities" in row:
        return "rank_entities"
    raise KeyError("Cannot detect candidate field")


def detect_cand_id_field(row):
    if "candidate_entity_ids" in row:
        return "candidate_entity_ids"
    if "rank_entities_id" in row:
        return "rank_entities_id"
    raise KeyError("Cannot detect candidate id field")


def convert_variant_rows_to_backbone_rows(rows, relation2id):
    converted = []

    for row in rows:
        out = dict(row)

        cand_field = detect_cand_field(row)
        cand_id_field = detect_cand_id_field(row)

        # normalize candidate fields to DrKGC expected names
        out["rank_entities"] = list(row[cand_field])
        out["rank_entities_id"] = list(row[cand_id_field])

        # normalize prediction type
        if "type" not in out or not out["type"]:
            out["type"] = "predicted_head"

        # recover relation name
        relation_name = (
            out.get("setting_a_relation")
            or out.get("relation")
            or "indication"
        )

        if relation_name not in relation2id:
            raise KeyError(
                f"Relation '{relation_name}' not found in relation2id. "
                f"Available keys example: {list(relation2id.keys())[:10]}"
            )

        # reconstruct triple / triple_id if missing
        if "triple" not in out:
            if out["type"] == "predicted_head":
                # (?, relation, disease) => gold is head drug
                out["triple"] = [
                    out["gold_entity"],
                    relation_name,
                    out["query_entity"],
                ]
            elif out["type"] == "predicted_tail":
                out["triple"] = [
                    out["query_entity"],
                    relation_name,
                    out["gold_entity"],
                ]
            else:
                raise ValueError(f"Unsupported prediction type: {out['type']}")

        if "triple_id" not in out:
            rel_id = relation2id[relation_name]
            if out["type"] == "predicted_head":
                out["triple_id"] = [
                    int(out["gold_entity_id"]),
                    int(rel_id),
                    int(out["query_entity_id"]),
                ]
            elif out["type"] == "predicted_tail":
                out["triple_id"] = [
                    int(out["query_entity_id"]),
                    int(rel_id),
                    int(out["gold_entity_id"]),
                ]

        # recompute rank against normalized rank_entities
        gold = out.get("gold_entity")
        if gold in out["rank_entities"]:
            out["rank"] = out["rank_entities"].index(gold) + 1
        else:
            out["rank"] = len(out["rank_entities"]) + 1

        converted.append(out)

    return converted


def build_prompts_and_subgraphs(
    rows,
    head_pred_lex_path,
    tail_pred_lex_path,
    graph_tsv,
    entity2id_path,
    relation2id_path,
    rules_path,
    graph_size=100,
    bkg=True,
):
    relation_questions_A_to_B = load_json(tail_pred_lex_path)
    relation_questions_B_to_A = load_json(head_pred_lex_path)

    entity2id = load_pickle(entity2id_path)
    relation2id = load_pickle(relation2id_path)
    rules = load_rules_json(rules_path)

    G = build_graph(graph_tsv, entity2id, relation2id)

    rows = convert_variant_rows_to_backbone_rows(rows, relation2id)

    # build prompt + output
    for row in rows:
        add_prompt(
            raw=row,
            relation_questions_A_to_B=relation_questions_A_to_B,
            relation_questions_B_to_A=relation_questions_B_to_A,
            bkg=bkg,
        )

    # build subgraph
    subgraphs = subgraph_func(rows, graph_size=graph_size, G=G, rules=rules)
    for row, sg in zip(rows, subgraphs):
        row["subgraph"] = sg

    leak_count = count_exact_leaks(rows)
    return rows, leak_count


def copy_base_package(base_dir, out_dir):
    base_dir = Path(base_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    must_copy = [
        "train.json",
        "test.json",
        "entity2id.pkl",
        "id2entity.pkl",
        "relation2id.pkl",
        "id2relation.pkl",
    ]
    for name in must_copy:
        src = base_dir / name
        dst = out_dir / name
        if not src.exists():
            raise FileNotFoundError(f"Missing required base file: {src}")
        shutil.copyfile(src, dst)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant_json", required=True)
    parser.add_argument("--base_eval_ready_dir", default="dataset/setting_a/18_ontology_only_eval_ready")
    parser.add_argument("--out_dir", required=True)
    parser.add_argument("--graph_tsv", default="dataset/setting_a/02_graph/train_enriched_deg1000_final.tsv")
    parser.add_argument("--head_pred_lex", default="dataset/setting_a/05_prompt_subgraph_subset/head_prediction_lexicon.json")
    parser.add_argument("--tail_pred_lex", default="dataset/setting_a/05_prompt_subgraph_subset/tail_prediction_lexicon.json")
    parser.add_argument("--rules_json", default="dataset/setting_a/05_prompt_subgraph_subset/rules.json")
    parser.add_argument("--entity2id_path", default="dataset/setting_a/18_ontology_only_eval_ready/entity2id.pkl")
    parser.add_argument("--relation2id_path", default="dataset/setting_a/18_ontology_only_eval_ready/relation2id.pkl")
    parser.add_argument("--graph_size", type=int, default=100)
    parser.add_argument("--bkg", action="store_true")
    args = parser.parse_args()

    rows = load_json(args.variant_json)

    prepared_rows, leak_count = build_prompts_and_subgraphs(
        rows=rows,
        head_pred_lex_path=args.head_pred_lex,
        tail_pred_lex_path=args.tail_pred_lex,
        graph_tsv=args.graph_tsv,
        entity2id_path=args.entity2id_path,
        relation2id_path=args.relation2id_path,
        rules_path=args.rules_json,
        graph_size=args.graph_size,
        bkg=args.bkg,
    )

    copy_base_package(args.base_eval_ready_dir, args.out_dir)
    save_json(prepared_rows, Path(args.out_dir) / "valid.json")

    manifest = {
        "variant_json": args.variant_json,
        "base_eval_ready_dir": args.base_eval_ready_dir,
        "out_dir": args.out_dir,
        "graph_tsv": args.graph_tsv,
        "head_pred_lex": args.head_pred_lex,
        "tail_pred_lex": args.tail_pred_lex,
        "rules_json": args.rules_json,
        "graph_size": args.graph_size,
        "bkg": args.bkg,
        "num_valid_rows": len(prepared_rows),
        "exact_leak_count": leak_count,
    }
    save_json(manifest, Path(args.out_dir) / "prep_manifest.json")

    print(f"Saved eval-ready package to: {args.out_dir}")
    print(f"num_valid_rows = {len(prepared_rows)}")
    print(f"exact_leak_count = {leak_count}")


if __name__ == "__main__":
    main()