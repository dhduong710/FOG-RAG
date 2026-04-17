from pathlib import Path
import pandas as pd
import pickle
import json

TRAIN_GRAPH_PATH = Path("dataset/setting_a/02_graph/train_enriched.tsv")
TRAIN_SPLIT_PATH = Path("dataset/setting_a/01_split/train.tsv")
VALID_SPLIT_PATH = Path("dataset/setting_a/01_split/valid.tsv")
TEST_SPLIT_PATH = Path("dataset/setting_a/01_split/test.tsv")

OUT_DIR = Path("dataset/setting_a/04_drkgc_json")
REPORT_PATH = Path("reports/week2/day5_id_maps_and_skeleton_report.md")


def save_pickle(obj, path: Path):
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def save_json(obj, path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def norm_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["head"] = out["head"].astype(str).str.strip()
    out["relation"] = out["relation"].astype(str).str.strip()
    out["tail"] = out["tail"].astype(str).str.strip()
    return out.drop_duplicates().reset_index(drop=True)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    train_graph_df = norm_df(pd.read_csv(TRAIN_GRAPH_PATH, sep="\t"))
    train_df = norm_df(pd.read_csv(TRAIN_SPLIT_PATH, sep="\t"))
    valid_df = norm_df(pd.read_csv(VALID_SPLIT_PATH, sep="\t"))
    test_df = norm_df(pd.read_csv(TEST_SPLIT_PATH, sep="\t"))

    # Entity universe:
    # ưu tiên graph train enriched, nhưng vẫn union thêm split để assert coverage rõ ràng
    entity_names = sorted(
        set(train_graph_df["head"]) |
        set(train_graph_df["tail"]) |
        set(valid_df["head"]) |
        set(valid_df["tail"]) |
        set(test_df["head"]) |
        set(test_df["tail"])
    )

    # Relation universe cho Setting A graph
    relation_names = sorted(set(train_graph_df["relation"]))

    entity2id = {name: idx for idx, name in enumerate(entity_names)}
    id2entity = {idx: name for name, idx in entity2id.items()}

    relation2id = {name: idx for idx, name in enumerate(relation_names)}
    id2relation = {idx: name for name, idx in relation2id.items()}

    # Sanity
    assert "indication" in relation2id, "Missing indication relation in relation map."

    split_entities = (
        set(train_df["head"]) | set(train_df["tail"]) |
        set(valid_df["head"]) | set(valid_df["tail"]) |
        set(test_df["head"]) | set(test_df["tail"])
    )
    missing = sorted([e for e in split_entities if e not in entity2id])
    assert len(missing) == 0, f"Missing entities in entity2id: {missing[:20]}"

    # Save pkl
    save_pickle(entity2id, OUT_DIR / "entity2id.pkl")
    save_pickle(id2entity, OUT_DIR / "id2entity.pkl")
    save_pickle(relation2id, OUT_DIR / "relation2id.pkl")
    save_pickle(id2relation, OUT_DIR / "id2relation.pkl")

    # Save json mirrors for readability
    save_json(entity2id, OUT_DIR / "entity2id.json")
    save_json(id2entity, OUT_DIR / "id2entity.json")
    save_json(relation2id, OUT_DIR / "relation2id.json")
    save_json(id2relation, OUT_DIR / "id2relation.json")

    report_lines = []
    if REPORT_PATH.exists():
        report_lines.append(REPORT_PATH.read_text(encoding="utf-8").rstrip())
        report_lines.append("")

    report_lines.append("# Week 2 - Day 5 Report")
    report_lines.append("")
    report_lines.append("## Part A - ID maps")
    report_lines.append(f"- source train graph: `{TRAIN_GRAPH_PATH}`")
    report_lines.append(f"- num_entities: {len(entity2id)}")
    report_lines.append(f"- num_relations: {len(relation2id)}")
    report_lines.append(f"- relation_names: {sorted(relation2id.keys())}")
    report_lines.append(f"- split_entity_coverage_ok: {len(missing) == 0}")
    report_lines.append("")
    report_lines.append("## Output files")
    report_lines.append(f"- `{OUT_DIR / 'entity2id.pkl'}`")
    report_lines.append(f"- `{OUT_DIR / 'id2entity.pkl'}`")
    report_lines.append(f"- `{OUT_DIR / 'relation2id.pkl'}`")
    report_lines.append(f"- `{OUT_DIR / 'id2relation.pkl'}`")
    report_lines.append("")

    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")

    print("Done.")
    print(f"num_entities: {len(entity2id)}")
    print(f"num_relations: {len(relation2id)}")
    print(f"relations: {sorted(relation2id.keys())}")
    print(f"Saved maps to: {OUT_DIR}")


if __name__ == "__main__":
    main()