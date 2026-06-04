from pathlib import Path
import pandas as pd
import pickle
import json

SPLIT_DIR = Path("dataset/setting_a/01_split")
MAP_DIR = Path("dataset/setting_a/04_drkgc_json")
OUT_DIR = Path("dataset/setting_a/04_drkgc_json")
REPORT_PATH = Path("reports/week2/day5_id_maps_and_skeleton_report.md")


def load_pickle(path: Path):
    with open(path, "rb") as f:
        return pickle.load(f)


def save_json(obj, path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def norm_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["head"] = out["head"].astype(str).str.strip()
    out["relation"] = out["relation"].astype(str).str.strip()
    out["tail"] = out["tail"].astype(str).str.strip()
    return out.drop_duplicates().reset_index(drop=True)


def build_samples(df: pd.DataFrame, entity2id: dict, relation2id: dict):
    samples = []

    for _, row in df.iterrows():
        head = row["head"]
        rel = row["relation"]
        tail = row["tail"]

        # task (? , indication, disease) => predicted_head
        sample = {
            "triple": [head, rel, tail],
            "triple_id": [
                entity2id[head],
                relation2id[rel],
                entity2id[tail]
            ],
            "type": "predicted_head",
            "query_entity": tail,
            "query_entity_id": entity2id[tail],

            # Placeholder tạm thời cho ngày 5.
            # Ngày 6 sẽ thay bằng mock coarse ranker top-K.
            "rank_entities": [head],
            "rank_entities_id": [entity2id[head]],
            "rank": 1
        }
        samples.append(sample)

    return samples


def sanity_check(samples):
    required_fields = {
        "triple",
        "triple_id",
        "type",
        "query_entity",
        "query_entity_id",
        "rank_entities",
        "rank_entities_id",
        "rank",
    }

    assert len(samples) > 0, "Empty skeleton samples."

    for i, sample in enumerate(samples[:10]):
        missing = required_fields - set(sample.keys())
        assert not missing, f"Sample {i} missing fields: {missing}"
        assert sample["type"] == "predicted_head"
        assert len(sample["triple"]) == 3
        assert len(sample["triple_id"]) == 3
        assert len(sample["rank_entities"]) == len(sample["rank_entities_id"])
        assert sample["rank"] == 1


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    entity2id = load_pickle(MAP_DIR / "entity2id.pkl")
    relation2id = load_pickle(MAP_DIR / "relation2id.pkl")

    train_df = norm_df(pd.read_csv(SPLIT_DIR / "train.tsv", sep="\t"))
    valid_df = norm_df(pd.read_csv(SPLIT_DIR / "valid.tsv", sep="\t"))
    test_df = norm_df(pd.read_csv(SPLIT_DIR / "test.tsv", sep="\t"))

    train_samples = build_samples(train_df, entity2id, relation2id)
    valid_samples = build_samples(valid_df, entity2id, relation2id)
    test_samples = build_samples(test_df, entity2id, relation2id)

    sanity_check(train_samples)
    sanity_check(valid_samples)
    sanity_check(test_samples)

    save_json(train_samples, OUT_DIR / "train_skeleton.json")
    save_json(valid_samples, OUT_DIR / "valid_skeleton.json")
    save_json(test_samples, OUT_DIR / "test_skeleton.json")

    report_lines = []
    if REPORT_PATH.exists():
        report_lines.append(REPORT_PATH.read_text(encoding="utf-8").rstrip())
        report_lines.append("")

    report_lines.append("## Part B - JSON skeleton")
    report_lines.append(f"- train_skeleton_samples: {len(train_samples)}")
    report_lines.append(f"- valid_skeleton_samples: {len(valid_samples)}")
    report_lines.append(f"- test_skeleton_samples: {len(test_samples)}")
    report_lines.append("- sample_type: predicted_head")
    report_lines.append("- query_entity_role: disease")
    report_lines.append("- placeholder_ranking: gold-only list, to be replaced on Day 6")
    report_lines.append("")
    report_lines.append("## Output files")
    report_lines.append(f"- `{OUT_DIR / 'train_skeleton.json'}`")
    report_lines.append(f"- `{OUT_DIR / 'valid_skeleton.json'}`")
    report_lines.append(f"- `{OUT_DIR / 'test_skeleton.json'}`")
    report_lines.append("")

    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")

    print("Done.")
    print(f"train_skeleton: {len(train_samples)}")
    print(f"valid_skeleton: {len(valid_samples)}")
    print(f"test_skeleton: {len(test_samples)}")
    print(f"Saved skeletons to: {OUT_DIR}")


if __name__ == "__main__":
    main()