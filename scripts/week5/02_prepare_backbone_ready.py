from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(
        description="Prepare full Setting-A backbone-ready JSON for week-5."
    )

    parser.add_argument(
        "--input_dir",
        type=Path,
        default=Path("dataset/setting_a/04_drkgc_json"),
        help="Directory containing train_mock_ranked.json / valid_mock_ranked.json / test_mock_ranked.json",
    )
    parser.add_argument(
        "--split_dir",
        type=Path,
        default=Path("dataset/setting_a/01_split"),
        help="Directory containing train.tsv / valid.tsv / test.tsv",
    )
    parser.add_argument(
        "--graph_path",
        type=Path,
        default=None,
        help=(
            "Retrieval graph TSV. If not set, script prefers "
            "dataset/setting_a/02_graph/train_enriched_deg1000_final.tsv, "
            "then falls back to dataset/setting_a/02_graph/train_enriched.tsv."
        ),
    )
    parser.add_argument(
        "--map_dir",
        type=Path,
        default=Path("dataset/setting_a/04_drkgc_json"),
        help="Directory containing entity2id.pkl / id2entity.pkl / relation2id.pkl / id2relation.pkl",
    )
    parser.add_argument(
        "--lexicon_dir",
        type=Path,
        default=Path("dataset/setting_a/05_prompt_subgraph_subset"),
        help="Directory containing head_prediction_lexicon.json / tail_prediction_lexicon.json / rules.json",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=Path("dataset/setting_a/08_backbone_ready"),
        help="Output directory for full train.json / valid.json / test.json",
    )
    parser.add_argument(
        "--report_path",
        type=Path,
        default=Path("reports/week5/day2_backbone_ready_report.md"),
        help="Markdown report path",
    )
    parser.add_argument(
        "--graph_size",
        type=int,
        default=100,
        help="Tau / subgraph size for prompt_subgraph.py",
    )
    parser.add_argument(
        "--python_exec",
        type=str,
        default=sys.executable,
        help="Python executable used to call prompt_subgraph.py",
    )
    parser.add_argument(
        "--bkg",
        action="store_true",
        help="Use biomedical prompt template. Recommended for PrimeKG.",
    )
    return parser.parse_args()


def norm_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["head"] = out["head"].astype(str).str.strip()
    out["relation"] = out["relation"].astype(str).str.strip()
    out["tail"] = out["tail"].astype(str).str.strip()
    return out.drop_duplicates().reset_index(drop=True)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def write_noheader_tsv(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df[["head", "relation", "tail"]].to_csv(path, sep="\t", index=False, header=False)


def count_exact_leaks(data: Iterable[dict]) -> int:
    leak = 0
    for item in data:
        gold = tuple(item["triple_id"])
        if any(tuple(x) == gold for x in item.get("subgraph", [])):
            leak += 1
    return leak


def summarize_ready_json(data: List[dict]) -> dict:
    required_keys = {
        "input",
        "output",
        "query_entity_id",
        "rank_entities_id",
        "subgraph",
        "triple",
        "triple_id",
        "type",
        "query_entity",
        "rank_entities",
        "rank",
    }

    missing_key_count = 0
    empty_subgraph_count = 0
    bad_subgraph_type_count = 0
    gold_in_candidate_count = 0
    candidate_lens = []

    for ex in data:
        if not required_keys.issubset(ex.keys()):
            missing_key_count += 1
            continue

        subg = ex.get("subgraph", [])
        if not isinstance(subg, list):
            bad_subgraph_type_count += 1
        if len(subg) == 0:
            empty_subgraph_count += 1

        gid = ex["triple_id"][0]
        cids = ex["rank_entities_id"]
        candidate_lens.append(len(cids))
        if gid in cids:
            gold_in_candidate_count += 1

    return {
        "num_samples": len(data),
        "missing_key_count": missing_key_count,
        "empty_subgraph_count": empty_subgraph_count,
        "bad_subgraph_type_count": bad_subgraph_type_count,
        "gold_in_candidate_count": gold_in_candidate_count,
        "candidate_len_min": min(candidate_lens) if candidate_lens else 0,
        "candidate_len_max": max(candidate_lens) if candidate_lens else 0,
    }


def choose_graph_path(user_path: Path | None) -> Path:
    if user_path is not None:
        return user_path

    candidates = [
        Path("dataset/setting_a/02_graph/train_enriched_deg1000_final.tsv"),
        Path("dataset/setting_a/02_graph/train_enriched.tsv"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "Cannot find retrieval graph. Expected one of: "
        "dataset/setting_a/02_graph/train_enriched_deg1000_final.tsv or train_enriched.tsv"
    )


def ensure_exists(paths: List[Path]):
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required files:\n- " + "\n- ".join(missing))


def main():
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    os_cwd = repo_root

    graph_path = choose_graph_path(args.graph_path)

    train_input_path = args.input_dir / "train_mock_ranked.json"
    valid_input_path = args.input_dir / "valid_mock_ranked.json"
    test_input_path = args.input_dir / "test_mock_ranked.json"

    train_split_path = args.split_dir / "train.tsv"
    valid_split_path = args.split_dir / "valid.tsv"
    test_split_path = args.split_dir / "test.tsv"

    entity2id_path = args.map_dir / "entity2id.pkl"
    id2entity_path = args.map_dir / "id2entity.pkl"
    relation2id_path = args.map_dir / "relation2id.pkl"
    id2relation_path = args.map_dir / "id2relation.pkl"

    head_lex_path = args.lexicon_dir / "head_prediction_lexicon.json"
    tail_lex_path = args.lexicon_dir / "tail_prediction_lexicon.json"
    rules_path = args.lexicon_dir / "rules.json"

    ensure_exists(
        [
            train_input_path,
            valid_input_path,
            test_input_path,
            train_split_path,
            valid_split_path,
            test_split_path,
            graph_path,
            entity2id_path,
            id2entity_path,
            relation2id_path,
            id2relation_path,
            head_lex_path,
            tail_lex_path,
            rules_path,
        ]
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.report_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_dir = args.output_dir / "_tmp_prompt_subgraph"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # 1) load full ranked inputs
    train_input = load_json(train_input_path)
    valid_input = load_json(valid_input_path)
    test_input = load_json(test_input_path)

    # 2) load raw split tables + graph
    train_split_df = norm_df(pd.read_csv(train_split_path, sep="\t"))
    valid_split_df = norm_df(pd.read_csv(valid_split_path, sep="\t"))
    test_split_df = norm_df(pd.read_csv(test_split_path, sep="\t"))
    graph_df = norm_df(pd.read_csv(graph_path, sep="\t"))

    assert len(train_input) == 8388, f"Expected 8388 train inputs, got {len(train_input)}"
    assert len(valid_input) == 500, f"Expected 500 valid inputs, got {len(valid_input)}"
    assert len(test_input) == 500, f"Expected 500 test inputs, got {len(test_input)}"

    # 3) export temp files for prompt_subgraph.py
    train_graph_noheader_path = tmp_dir / "train_graph_noheader.tsv"
    valid_raw_noheader_path = tmp_dir / "valid_raw_noheader.tsv"
    test_raw_noheader_path = tmp_dir / "test_raw_noheader.tsv"

    train_json_tmp = tmp_dir / "train_input.json"
    valid_json_tmp = tmp_dir / "valid_input.json"
    test_json_tmp = tmp_dir / "test_input.json"

    write_noheader_tsv(graph_df, train_graph_noheader_path)
    write_noheader_tsv(valid_split_df, valid_raw_noheader_path)
    write_noheader_tsv(test_split_df, test_raw_noheader_path)

    save_json(train_input, train_json_tmp)
    save_json(valid_input, valid_json_tmp)
    save_json(test_input, test_json_tmp)

    # 4) call prompt_subgraph.py
    out_train = args.output_dir / "train.json"
    out_valid = args.output_dir / "valid.json"
    out_test = args.output_dir / "test.json"

    cmd = [
        args.python_exec,
        "prompt_subgraph.py",
        "--train_raw",
        str(train_graph_noheader_path),
        "--valid_raw",
        str(valid_raw_noheader_path),
        "--test_raw",
        str(test_raw_noheader_path),
        "--entity2id_path",
        str(entity2id_path),
        "--id2entity_path",
        str(id2entity_path),
        "--id2relation_path",
        str(id2relation_path),
        "--train_json_path",
        str(train_json_tmp),
        "--valid_json_path",
        str(valid_json_tmp),
        "--test_json_path",
        str(test_json_tmp),
        "--train_path_saved",
        str(out_train),
        "--valid_path_saved",
        str(out_valid),
        "--test_path_saved",
        str(out_test),
        "--tail_pred_lex",
        str(tail_lex_path),
        "--head_pred_lex",
        str(head_lex_path),
        "--rules_path",
        str(rules_path),
        "--graph_size",
        str(args.graph_size),
    ]
    if args.bkg:
        cmd.append("--bkg")

    print("Running prompt_subgraph.py ...")
    print(" ".join(cmd))
    subprocess.run(cmd, cwd=os_cwd, check=True)

    # 5) copy maps into 08_backbone_ready
    shutil.copy2(entity2id_path, args.output_dir / "entity2id.pkl")
    shutil.copy2(id2entity_path, args.output_dir / "id2entity.pkl")
    shutil.copy2(relation2id_path, args.output_dir / "relation2id.pkl")
    shutil.copy2(id2relation_path, args.output_dir / "id2relation.pkl")

    # 6) post-run sanity checks
    ensure_exists([
        out_train, out_valid, out_test,
        args.output_dir / "entity2id.pkl",
        args.output_dir / "id2entity.pkl",
        args.output_dir / "relation2id.pkl",
        args.output_dir / "id2relation.pkl",
    ])

    train_ready = load_json(out_train)
    valid_ready = load_json(out_valid)
    test_ready = load_json(out_test)

    assert len(train_ready) == 8388, f"train ready count mismatch: {len(train_ready)}"
    assert len(valid_ready) == 500, f"valid ready count mismatch: {len(valid_ready)}"
    assert len(test_ready) == 500, f"test ready count mismatch: {len(test_ready)}"

    valid_leak = count_exact_leaks(valid_ready)
    test_leak = count_exact_leaks(test_ready)

    train_summary = summarize_ready_json(train_ready)
    valid_summary = summarize_ready_json(valid_ready)
    test_summary = summarize_ready_json(test_ready)

    assert valid_leak == 0, f"Validation leakage detected after prompt_subgraph: {valid_leak}"
    assert test_leak == 0, f"Test leakage detected after prompt_subgraph: {test_leak}"
    assert train_summary["missing_key_count"] == 0, "Missing keys in train.json"
    assert valid_summary["missing_key_count"] == 0, "Missing keys in valid.json"
    assert test_summary["missing_key_count"] == 0, "Missing keys in test.json"

    manifest = {
        "graph_path_used": str(graph_path),
        "graph_size": args.graph_size,
        "bkg": bool(args.bkg),
        "train_count": len(train_ready),
        "valid_count": len(valid_ready),
        "test_count": len(test_ready),
        "train_summary": train_summary,
        "valid_summary": valid_summary,
        "test_summary": test_summary,
        "valid_exact_leak_count": valid_leak,
        "test_exact_leak_count": test_leak,
        "output_train": str(out_train),
        "output_valid": str(out_valid),
        "output_test": str(out_test),
        "entity2id": str(args.output_dir / "entity2id.pkl"),
        "id2entity": str(args.output_dir / "id2entity.pkl"),
        "relation2id": str(args.output_dir / "relation2id.pkl"),
        "id2relation": str(args.output_dir / "id2relation.pkl"),
        "note": "Week-5 full Setting-A backbone-ready package generated from full mock-ranked JSON + prompt_subgraph.py",
    }
    save_json(manifest, args.output_dir / "backbone_ready_manifest.json")

    report = f"""# Week 5 - Day 2 Backbone Ready Report

## Goal
Build full Setting-A prompt/subgraph-ready JSON for week-5 backbone reproduction.

## Inputs
- input_dir: `{args.input_dir}`
- split_dir: `{args.split_dir}`
- graph_path_used: `{graph_path}`
- map_dir: `{args.map_dir}`
- lexicon_dir: `{args.lexicon_dir}`
- graph_size: {args.graph_size}
- biomedical_prompt: {bool(args.bkg)}

## Full Input Counts
- train_input_count: {len(train_input)}
- valid_input_count: {len(valid_input)}
- test_input_count: {len(test_input)}

## Outputs
- `{out_train}`
- `{out_valid}`
- `{out_test}`
- `{args.output_dir / 'entity2id.pkl'}`
- `{args.output_dir / 'id2entity.pkl'}`
- `{args.output_dir / 'relation2id.pkl'}`
- `{args.output_dir / 'id2relation.pkl'}`
- `{args.output_dir / 'backbone_ready_manifest.json'}`

## Sanity Summary
### train.json
- num_samples: {train_summary["num_samples"]}
- missing_key_count: {train_summary["missing_key_count"]}
- empty_subgraph_count: {train_summary["empty_subgraph_count"]}
- gold_in_candidate_count: {train_summary["gold_in_candidate_count"]}
- candidate_len_min: {train_summary["candidate_len_min"]}
- candidate_len_max: {train_summary["candidate_len_max"]}

### valid.json
- num_samples: {valid_summary["num_samples"]}
- missing_key_count: {valid_summary["missing_key_count"]}
- empty_subgraph_count: {valid_summary["empty_subgraph_count"]}
- gold_in_candidate_count: {valid_summary["gold_in_candidate_count"]}
- valid_exact_leak_count: {valid_leak}
- candidate_len_min: {valid_summary["candidate_len_min"]}
- candidate_len_max: {valid_summary["candidate_len_max"]}

### test.json
- num_samples: {test_summary["num_samples"]}
- missing_key_count: {test_summary["missing_key_count"]}
- empty_subgraph_count: {test_summary["empty_subgraph_count"]}
- gold_in_candidate_count: {test_summary["gold_in_candidate_count"]}
- test_exact_leak_count: {test_leak}
- candidate_len_min: {test_summary["candidate_len_min"]}
- candidate_len_max: {test_summary["candidate_len_max"]}

## Judgment
READY for week-5 day-3 embedding export if all assertions passed.
"""
    args.report_path.write_text(report, encoding="utf-8")

    print("Done.")
    print(f"Saved: {out_train}")
    print(f"Saved: {out_valid}")
    print(f"Saved: {out_test}")
    print(f"Saved: {args.output_dir / 'backbone_ready_manifest.json'}")
    print(f"Saved: {args.report_path}")


if __name__ == "__main__":
    main()