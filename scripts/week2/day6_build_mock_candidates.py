from pathlib import Path
import pandas as pd
import pickle
import json
import random
import hashlib

SPLIT_DIR = Path("dataset/setting_a/01_split")
MAP_DIR = Path("dataset/setting_a/04_drkgc_json")
CAND_DIR = Path("dataset/setting_a/03_candidates")
OUT_JSON_DIR = Path("dataset/setting_a/04_drkgc_json")
REPORT_PATH = Path("reports/week2/day6_mock_coarse_ranker_report.md")

K = 20
BASE_SEED = 2025


def load_pickle(path: Path):
    with open(path, "rb") as f:
        return pickle.load(f)


def save_json(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def norm_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["head"] = out["head"].astype(str).str.strip()
    out["relation"] = out["relation"].astype(str).str.strip()
    out["tail"] = out["tail"].astype(str).str.strip()
    return out.drop_duplicates().reset_index(drop=True)


def stable_seed(*parts) -> int:
    """
    Tạo ra một random seed (hạt giống ngẫu nhiên) cố định và duy nhất 
    dựa trên các tham số đầu vào.
    
    Args:
        *parts: Chấp nhận vô số tham số (tên kịch bản, tỷ lệ chia, ID...).
                Ví dụ: stable_seed("Train_split", 0.8)
                
    Returns:
        int: Một số nguyên ổn định dùng để đưa vào các hàm set_seed()
             của random, numpy, hay PyTorch.
    """
    text = "||".join(str(x) for x in parts)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16) + BASE_SEED


def build_mock_candidate_list(gold_drug: str, drug_universe: list, disease: str, k: int):
    assert gold_drug in drug_universe, f"Gold drug not in universe: {gold_drug}"

    negatives = [d for d in drug_universe if d != gold_drug]

    rng = random.Random(stable_seed(gold_drug, disease, k))
    rng.shuffle(negatives)

    picked_negatives = negatives[: max(0, k - 1)]
    candidates = [gold_drug] + picked_negatives

    # rank của gold trong mock candidate list luôn là 1
    gold_rank = 1

    assert len(candidates) <= k
    assert candidates[0] == gold_drug
    assert len(set(candidates)) == len(candidates)

    return candidates, gold_rank


def build_candidate_records(df: pd.DataFrame, entity2id: dict, relation2id: dict, drug_universe: list, k: int):
    records = []
    drkgc_ready = []

    for _, row in df.iterrows():
        gold = row["head"]
        rel = row["relation"]
        disease = row["tail"]

        candidates, gold_rank = build_mock_candidate_list(gold, drug_universe, disease, k)

        record = {
            "triple": [gold, rel, disease],
            "type": "predicted_head",
            "query_entity": disease,
            "gold_entity": gold,
            "candidate_entities": candidates,
            "candidate_entity_ids": [entity2id[x] for x in candidates],
            "gold_rank_in_candidates": gold_rank,
            "k": len(candidates),
            "candidate_type": "drug",
            "mock_ranker": True
        }
        records.append(record)

        drkgc_item = {
            "triple": [gold, rel, disease],
            "triple_id": [
                entity2id[gold],
                relation2id[rel],
                entity2id[disease]
            ],
            "type": "predicted_head",
            "query_entity": disease,
            "query_entity_id": entity2id[disease],
            "rank_entities": candidates,
            "rank_entities_id": [entity2id[x] for x in candidates],
            "rank": gold_rank
        }
        drkgc_ready.append(drkgc_item)

    return records, drkgc_ready


def sanity_check(records, drkgc_ready, entity2id, k):
    assert len(records) == len(drkgc_ready) and len(records) > 0

    for i in range(min(20, len(records))):
        r = records[i]
        j = drkgc_ready[i]

        assert r["type"] == "predicted_head"
        assert r["candidate_type"] == "drug"
        assert r["gold_entity"] == r["candidate_entities"][0]
        assert r["gold_rank_in_candidates"] == 1
        assert len(r["candidate_entities"]) <= k
        assert len(set(r["candidate_entities"])) == len(r["candidate_entities"])

        assert j["type"] == "predicted_head"
        assert j["query_entity"] == r["query_entity"]
        assert j["rank_entities"][0] == r["gold_entity"]
        assert j["rank"] == 1
        assert len(j["rank_entities"]) == len(j["rank_entities_id"])

        for ent, ent_id in zip(j["rank_entities"], j["rank_entities_id"]):
            assert entity2id[ent] == ent_id


def main():
    CAND_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    entity2id = load_pickle(MAP_DIR / "entity2id.pkl")
    relation2id = load_pickle(MAP_DIR / "relation2id.pkl")

    train_df = norm_df(pd.read_csv(SPLIT_DIR / "train.tsv", sep="\t"))
    valid_df = norm_df(pd.read_csv(SPLIT_DIR / "valid.tsv", sep="\t"))
    test_df = norm_df(pd.read_csv(SPLIT_DIR / "test.tsv", sep="\t"))

    # Drug universe lấy từ train split để giữ consistency với split A
    drug_universe = sorted(train_df["head"].unique().tolist())

    train_records, train_drkgc = build_candidate_records(train_df, entity2id, relation2id, drug_universe, K)
    valid_records, valid_drkgc = build_candidate_records(valid_df, entity2id, relation2id, drug_universe, K)
    test_records, test_drkgc = build_candidate_records(test_df, entity2id, relation2id, drug_universe, K)

    sanity_check(train_records, train_drkgc, entity2id, K)
    sanity_check(valid_records, valid_drkgc, entity2id, K)
    sanity_check(test_records, test_drkgc, entity2id, K)

    save_json(train_records, CAND_DIR / "train_mock_candidates.json")
    save_json(valid_records, CAND_DIR / "valid_mock_candidates.json")
    save_json(test_records, CAND_DIR / "test_mock_candidates.json")

    save_json(train_drkgc, OUT_JSON_DIR / "train_mock_ranked.json")
    save_json(valid_drkgc, OUT_JSON_DIR / "valid_mock_ranked.json")
    save_json(test_drkgc, OUT_JSON_DIR / "test_mock_ranked.json")

    candidate_meta = {
        "k": K,
        "base_seed": BASE_SEED,
        "candidate_type": "drug",
        "gold_included": True,
        "ranking_policy": "gold-first + deterministic shuffled train-drug negatives",
        "drug_universe_size": len(drug_universe),
        "drug_universe_source": str(SPLIT_DIR / "train.tsv"),
        "mock_ranker": True
    }
    save_json(candidate_meta, CAND_DIR / "candidate_meta.json")

    report = f"""# Week 2 - Day 6 Report

## Goal
Build a deterministic type-safe mock coarse ranker and replace gold-only placeholder ranking.

## Candidate policy
- K: {K}
- candidate_type: drug
- gold_included: True
- ranking_policy: gold-first + deterministic shuffled negatives
- drug_universe_source: `{SPLIT_DIR / 'train.tsv'}`
- drug_universe_size: {len(drug_universe)}

## Split outputs
- train samples: {len(train_records)}
- valid samples: {len(valid_records)}
- test samples: {len(test_records)}

## Output files
- `{CAND_DIR / 'train_mock_candidates.json'}`
- `{CAND_DIR / 'valid_mock_candidates.json'}`
- `{CAND_DIR / 'test_mock_candidates.json'}`
- `{CAND_DIR / 'candidate_meta.json'}`
- `{OUT_JSON_DIR / 'train_mock_ranked.json'}`
- `{OUT_JSON_DIR / 'valid_mock_ranked.json'}`
- `{OUT_JSON_DIR / 'test_mock_ranked.json'}`

## Notes
- This is NOT a learned ranker.
- This is a schema- and pipeline-locking mock coarse ranker.
- Gold is always placed at rank 1 for deterministic sanity checking.
"""

    REPORT_PATH.write_text(report, encoding="utf-8")

    print("Done.")
    print(f"drug_universe_size: {len(drug_universe)}")
    print(f"train: {len(train_records)}")
    print(f"valid: {len(valid_records)}")
    print(f"test: {len(test_records)}")
    print(f"K: {K}")
    print(f"Saved: {CAND_DIR}")
    print(f"Saved: {OUT_JSON_DIR}")
    print(f"Saved: {REPORT_PATH}")


if __name__ == "__main__":
    main()