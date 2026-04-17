import json
import random
from pathlib import Path

SEED = 2025
TRAIN_RATIO = 0.10
VALID_TARGET = 100
TEST_TARGET = 100

INPUT_DIR = Path("dataset/setting_a/04_drkgc_json")
OUTPUT_DIR = Path("dataset/setting_a/06_pilot_subset")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_PATH = INPUT_DIR / "train_mock_ranked.json"
VALID_PATH = INPUT_DIR / "valid_mock_ranked.json"
TEST_PATH  = INPUT_DIR / "test_mock_ranked.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def gold_id(ex):
    return ex["triple_id"][0]


def gold_name(ex):
    return ex["triple"][0]


def query_id(ex):
    return ex["query_entity_id"]


def query_name(ex):
    return ex["query_entity"]


def candidate_ids(ex):
    return ex["rank_entities_id"]


def candidate_names(ex):
    return ex["rank_entities"]


def valid_format(ex):
    required = [
        "triple", "triple_id", "type",
        "query_entity", "query_entity_id",
        "rank_entities", "rank_entities_id", "rank"
    ]
    for k in required:
        if k not in ex:
            return False
    if len(ex["triple"]) != 3:
        return False
    if len(ex["triple_id"]) != 3:
        return False
    if not isinstance(ex["rank_entities"], list):
        return False
    if not isinstance(ex["rank_entities_id"], list):
        return False
    return True


def build_pilot_entity_universe(samples):
    ent_ids = set()
    for ex in samples:
        ent_ids.add(query_id(ex))
        ent_ids.add(gold_id(ex))
    return ent_ids


def filter_eval_pool(samples, pilot_entity_ids):
    kept = []
    for ex in samples:
        if not valid_format(ex):
            continue
        qid = query_id(ex)
        gid = gold_id(ex)
        cids = candidate_ids(ex)

        if qid not in pilot_entity_ids:
            continue
        if gid not in pilot_entity_ids:
            continue
        if gid not in cids:
            continue
        if len(cids) == 0:
            continue

        kept.append(ex)
    return kept


def summarize(samples):
    bad_format = 0
    gold_in_candidate_count = 0
    unique_queries = set()
    unique_golds = set()
    candidate_lens = []

    for ex in samples:
        if not valid_format(ex):
            bad_format += 1
            continue

        q = query_id(ex)
        g = gold_id(ex)
        cids = candidate_ids(ex)

        unique_queries.add(q)
        unique_golds.add(g)
        candidate_lens.append(len(cids))

        if g in cids:
            gold_in_candidate_count += 1

    return {
        "num_samples": len(samples),
        "num_unique_query_entities": len(unique_queries),
        "num_unique_gold_entities": len(unique_golds),
        "gold_in_candidate_count": gold_in_candidate_count,
        "bad_format_count": bad_format,
        "candidate_len_min": min(candidate_lens) if candidate_lens else 0,
        "candidate_len_max": max(candidate_lens) if candidate_lens else 0,
    }


def main():
    rng = random.Random(SEED)

    train = load_json(TRAIN_PATH)
    valid = load_json(VALID_PATH)
    test = load_json(TEST_PATH)

    train_shuf = train[:]
    rng.shuffle(train_shuf)

    n_train = max(1, round(len(train_shuf) * TRAIN_RATIO))
    train_pilot = train_shuf[:n_train]

    pilot_entity_ids = build_pilot_entity_universe(train_pilot)

    valid_pool = filter_eval_pool(valid, pilot_entity_ids)
    test_pool = filter_eval_pool(test, pilot_entity_ids)

    rng.shuffle(valid_pool)
    rng.shuffle(test_pool)

    valid_pilot = valid_pool[:VALID_TARGET]
    test_pilot = test_pool[:TEST_TARGET]

    save_json(train_pilot, OUTPUT_DIR / "train_pilot_input.json")
    save_json(valid_pilot, OUTPUT_DIR / "valid_pilot_input.json")
    save_json(test_pilot, OUTPUT_DIR / "test_pilot_input.json")

    meta = {
        "seed": SEED,
        "train_ratio": TRAIN_RATIO,
        "valid_target": VALID_TARGET,
        "test_target": TEST_TARGET,
        "source_train": str(TRAIN_PATH),
        "source_valid": str(VALID_PATH),
        "source_test": str(TEST_PATH),
        "train_summary": summarize(train_pilot),
        "valid_summary": summarize(valid_pilot),
        "test_summary": summarize(test_pilot),
        "valid_pool_before_truncation": len(valid_pool),
        "test_pool_before_truncation": len(test_pool),
    }
    save_json(meta, OUTPUT_DIR / "pilot_subset_meta.json")

    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()