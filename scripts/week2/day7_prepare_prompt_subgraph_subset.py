from pathlib import Path
import pandas as pd
import json
import random

TRAIN_GRAPH_PATH = Path("dataset/setting_a/02_graph/train_enriched.tsv")
VALID_RAW_PATH = Path("dataset/setting_a/01_split/valid.tsv")
TEST_RAW_PATH = Path("dataset/setting_a/01_split/test.tsv")

TRAIN_JSON_PATH = Path("dataset/setting_a/04_drkgc_json/train_mock_ranked.json")
VALID_JSON_PATH = Path("dataset/setting_a/04_drkgc_json/valid_mock_ranked.json")
TEST_JSON_PATH = Path("dataset/setting_a/04_drkgc_json/test_mock_ranked.json")

OUT_DIR = Path("dataset/setting_a/05_prompt_subgraph_subset")
REPORT_PATH = Path("reports/week2/day7_prompt_subgraph_report.md")

SUBSET_N = 20
SEED = 2025


def norm_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["head"] = out["head"].astype(str).str.strip()
    out["relation"] = out["relation"].astype(str).str.strip()
    out["tail"] = out["tail"].astype(str).str.strip()
    return out.drop_duplicates().reset_index(drop=True)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def sample_json_records(records, n, seed):
    rng = random.Random(seed)
    idxs = list(range(len(records)))
    rng.shuffle(idxs)
    idxs = sorted(idxs[:n])
    return [records[i] for i in idxs]


def triple_key_from_json(item):
    t = item["triple"]
    return (str(t[0]).strip(), str(t[1]).strip(), str(t[2]).strip())


def subset_raw_from_json(raw_df: pd.DataFrame, json_records):
    keep = {triple_key_from_json(x) for x in json_records}
    mask = raw_df.apply(
        lambda r: (r["head"], r["relation"], r["tail"]) in keep,
        axis=1
    )
    out = raw_df[mask].copy().reset_index(drop=True)
    return out


def write_noheader_tsv(df: pd.DataFrame, path: Path):
    df[["head", "relation", "tail"]].to_csv(path, sep="\t", index=False, header=False)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    train_graph_df = norm_df(pd.read_csv(TRAIN_GRAPH_PATH, sep="\t"))
    valid_raw_df = norm_df(pd.read_csv(VALID_RAW_PATH, sep="\t"))
    test_raw_df = norm_df(pd.read_csv(TEST_RAW_PATH, sep="\t"))

    train_json = load_json(TRAIN_JSON_PATH)
    valid_json = load_json(VALID_JSON_PATH)
    test_json = load_json(TEST_JSON_PATH)

    train_20 = sample_json_records(train_json, SUBSET_N, SEED)
    valid_20 = sample_json_records(valid_json, SUBSET_N, SEED)
    test_20 = sample_json_records(test_json, SUBSET_N, SEED)

    valid_20_raw = subset_raw_from_json(valid_raw_df, valid_20)
    test_20_raw = subset_raw_from_json(test_raw_df, test_20)

    assert len(train_20) == SUBSET_N
    assert len(valid_20) == SUBSET_N
    assert len(test_20) == SUBSET_N
    assert len(valid_20_raw) == SUBSET_N
    assert len(test_20_raw) == SUBSET_N

    # raw no-header files for prompt_subgraph.py
    write_noheader_tsv(train_graph_df, OUT_DIR / "train_enriched_noheader.tsv")
    write_noheader_tsv(valid_20_raw, OUT_DIR / "valid_20_raw_noheader.tsv")
    write_noheader_tsv(test_20_raw, OUT_DIR / "test_20_raw_noheader.tsv")

    # subset json inputs
    save_json(train_20, OUT_DIR / "train_20_input.json")
    save_json(valid_20, OUT_DIR / "valid_20_input.json")
    save_json(test_20, OUT_DIR / "test_20_input.json")

    # Minimal biomedical lexicons
    head_pred_lex = {
        "indication": "What drug is indicated for {}?",
        "contraindication": "What drug is contraindicated for {}?"
    }
    tail_pred_lex = {
        "indication": "What disease can be treated with {}?",
        "contraindication": "What disease is contraindicated for {}?"
    }

    save_json(head_pred_lex, OUT_DIR / "head_prediction_lexicon.json")
    save_json(tail_pred_lex, OUT_DIR / "tail_prediction_lexicon.json")

    # Minimal rule file for indication head prediction:
    # disease --associated_with--> gene --target--> drug
    # disease --associated_with--> gene --ppi--> gene --target--> drug
    rules = {
        "indication": [
            ["associated_with", "target"],
            ["associated_with", "ppi", "target"]
        ]
    }
    save_json(rules, OUT_DIR / "rules.json")

    report = f"""# Week 2 - Day 7 Report

## Part A - Prepare prompt_subgraph subset
- subset_n: {SUBSET_N}
- seed: {SEED}
- source_train_graph: `{TRAIN_GRAPH_PATH}`
- source_valid_raw: `{VALID_RAW_PATH}`
- source_test_raw: `{TEST_RAW_PATH}`
- source_train_json: `{TRAIN_JSON_PATH}`
- source_valid_json: `{VALID_JSON_PATH}`
- source_test_json: `{TEST_JSON_PATH}`

## Prepared files
- `{OUT_DIR / 'train_enriched_noheader.tsv'}`
- `{OUT_DIR / 'valid_20_raw_noheader.tsv'}`
- `{OUT_DIR / 'test_20_raw_noheader.tsv'}`
- `{OUT_DIR / 'train_20_input.json'}`
- `{OUT_DIR / 'valid_20_input.json'}`
- `{OUT_DIR / 'test_20_input.json'}`
- `{OUT_DIR / 'head_prediction_lexicon.json'}`
- `{OUT_DIR / 'tail_prediction_lexicon.json'}`
- `{OUT_DIR / 'rules.json'}`

## Notes
- train raw for graph building uses full enriched train graph.
- valid/test raw are 20-sample subsets.
- input raw TSV files are exported WITHOUT header for compatibility with prompt_subgraph.py.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")

    print("Done.")
    print(f"train_20: {len(train_20)}")
    print(f"valid_20: {len(valid_20)}")
    print(f"test_20: {len(test_20)}")
    print(f"valid_20_raw: {len(valid_20_raw)}")
    print(f"test_20_raw: {len(test_20_raw)}")
    print(f"Saved: {OUT_DIR}")
    print(f"Saved: {REPORT_PATH}")


if __name__ == "__main__":
    main()