from pathlib import Path
import pandas as pd

SETTING_A_SPLIT_DIR = Path("dataset/setting_a/01_split")
SETTING_A_GRAPH_DIR = Path("dataset/setting_a/02_graph")
WEEK2_CONTRA_PATH = Path("dataset/setting_b/00_safety_labels/contraindication_edges_overlap.tsv")

OUT_DIR = Path("dataset/setting_b/01_annotations")
OUT_PATH = OUT_DIR / "contraindication_pairs.tsv"
CONFLICT_PATH = OUT_DIR / "contraindication_conflicts.tsv"
REPORT_PATH = Path("reports/week3/day1_contra_protocol_report.md")


def norm(x):
    return str(x).strip()


def read_indication_pairs():
    dfs = []
    for name in ["train.tsv", "valid.tsv", "test.tsv"]:
        path = SETTING_A_SPLIT_DIR / name
        df = pd.read_csv(path, sep="\t")
        df = df[["head", "relation", "tail"]].copy()
        df["head"] = df["head"].map(norm)
        df["tail"] = df["tail"].map(norm)
        df["split_source"] = name.replace(".tsv", "")
        dfs.append(df)

    # train_enriched có thể chứa nhiều relation, nên chỉ giữ indication nếu có
    train_graph_path = SETTING_A_GRAPH_DIR / "train_enriched_deg1000_final.tsv"
    if not train_graph_path.exists():
        train_graph_path = SETTING_A_GRAPH_DIR / "train_enriched.tsv"

    if train_graph_path.exists():
        gdf = pd.read_csv(train_graph_path, sep="\t")
        gdf = gdf[["head", "relation", "tail"]].copy()
        gdf["head"] = gdf["head"].map(norm)
        gdf["tail"] = gdf["tail"].map(norm)
        gdf = gdf[gdf["relation"].astype(str).str.strip().str.lower() == "indication"].copy()
        gdf["split_source"] = "train_enriched_indication"
        dfs.append(gdf)

    out = pd.concat(dfs, ignore_index=True)
    out["pair_key"] = out["head"] + "||" + out["tail"]
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    contra = pd.read_csv(WEEK2_CONTRA_PATH, sep="\t")
    contra = contra.rename(columns={"head": "drug", "tail": "disease"}).copy()

    contra["drug"] = contra["drug"].map(norm)
    contra["disease"] = contra["disease"].map(norm)
    contra["relation"] = "contraindication"
    contra["source_scope"] = "overlap_with_setting_a"
    contra = contra[["drug", "disease", "relation", "source_scope"]].drop_duplicates().reset_index(drop=True)

    indication_pairs = read_indication_pairs()
    indication_key_set = set(indication_pairs["pair_key"].tolist())

    contra["pair_key"] = contra["drug"] + "||" + contra["disease"]
    contra["conflict_flag"] = contra["pair_key"].map(lambda x: 1 if x in indication_key_set else 0)

    conflict_df = contra[contra["conflict_flag"] == 1].copy()

    save_df = contra[["drug", "disease", "relation", "source_scope", "conflict_flag"]].copy()
    save_df.to_csv(OUT_PATH, sep="\t", index=False)
    conflict_df.to_csv(CONFLICT_PATH, sep="\t", index=False)

    report = f"""# Day 1 Contraindication Protocol Report

## Input files
- week2 contraindication overlap: `{WEEK2_CONTRA_PATH}`
- setting A split: `{SETTING_A_SPLIT_DIR}`
- setting A train graph: `{SETTING_A_GRAPH_DIR}`

## Output files
- canonical contraindication pairs: `{OUT_PATH}`
- conflict-only subset: `{CONFLICT_PATH}`

## Summary
- total contraindication pairs: {len(save_df)}
- conflict pairs (also appear in indication): {len(conflict_df)}

## Policy
Conflict pairs are retained in the raw annotation table and marked with `conflict_flag = 1`.
No pair is silently deleted.
"""

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    print("Saved:", OUT_PATH)
    print("Saved:", CONFLICT_PATH)
    print("Saved:", REPORT_PATH)
    print("total_pairs =", len(save_df))
    print("conflict_pairs =", len(conflict_df))


if __name__ == "__main__":
    main()