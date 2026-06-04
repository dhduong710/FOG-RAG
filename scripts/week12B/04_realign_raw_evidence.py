from __future__ import annotations

import json
import pickle
from pathlib import Path

from prompt_subgraph import add_prompt, count_exact_leaks


RAW_TRAIN = Path("dataset/setting_a/21_ranker_rescue/train_top20_raw.json")
RAW_VALID = Path("dataset/setting_a/23_noinj_source/valid_top20_raw.json")
RAW_TEST = Path("dataset/setting_a/23_noinj_source/test_top20_raw.json")

OLD_TRAIN_EVI = Path("dataset/setting_a/12_backbone_ready_ranker_v2/train.json")
OLD_VALID_EVI = Path("dataset/setting_a/12_backbone_ready_ranker_v2/valid.json")
OLD_TEST_EVI = Path("dataset/setting_a/12_backbone_ready_ranker_v2/test.json")

HEAD_LEX = Path("dataset/setting_a/05_prompt_subgraph_subset/head_prediction_lexicon.json")
TAIL_LEX = Path("dataset/setting_a/05_prompt_subgraph_subset/tail_prediction_lexicon.json")
REL2ID = Path("dataset/setting_a/04_drkgc_json/relation2id.pkl")

OUT_DIR = Path("dataset/setting_a/24b_noinj_evidence")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj):
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def load_pickle(path: Path):
    with path.open("rb") as f:
        return pickle.load(f)


def normalize_raw_row(raw_row: dict, relation2id: dict) -> dict:
    gold_entity = raw_row["gold_entity"]
    gold_entity_id = raw_row["gold_entity_id"]
    query_entity = raw_row["query_entity"]
    query_entity_id = raw_row["query_entity_id"]
    cand_names = raw_row["candidate_entities"]
    cand_ids = raw_row["candidate_entity_ids"]

    if gold_entity in cand_names:
        rank = cand_names.index(gold_entity) + 1
    else:
        rank = len(cand_names) + 1

    row = {
        "triple": [gold_entity, "indication", query_entity],
        "triple_id": [gold_entity_id, relation2id["indication"], query_entity_id],
        "type": "predicted_head",
        "query_entity": query_entity,
        "query_entity_id": query_entity_id,
        "rank_entities": cand_names,
        "rank_entities_id": cand_ids,
        "rank": rank,
        "gold_entity": gold_entity,
        "gold_entity_id": gold_entity_id,
        "gold_in_topk_raw": raw_row.get("gold_in_topk_raw", gold_entity in cand_names),
        "gold_rank_in_full_universe": raw_row.get("gold_rank_in_full_universe"),
        "split": raw_row.get("split"),
    }
    return row


def build_evidence_index(evidence_rows: list[dict]) -> dict:
    idx = {}
    for row in evidence_rows:
        query = row.get("query_entity")
        gold = row.get("output", row.get("gold_entity"))
        if query is None or gold is None:
            continue
        idx[(query, gold)] = row
    return idx


def rebuild_split(raw_rows: list[dict], evidence_index: dict, rel_q_a2b: dict, rel_q_b2a: dict, relation2id: dict):
    rebuilt = []
    missing = []
    for raw in raw_rows:
        base = normalize_raw_row(raw, relation2id)
        key = (base["query_entity"], base["gold_entity"])
        ev = evidence_index.get(key)

        if ev is None:
            missing.append({"query_entity": base["query_entity"], "gold_entity": base["gold_entity"]})
            continue

        # Copy subgraph from aligned evidence row
        base["subgraph"] = ev.get("subgraph", [])

        # Regenerate prompt from RAW candidate list, not from old evidence row
        add_prompt(base, rel_q_a2b, rel_q_b2a, bkg=True)

        rebuilt.append(base)

    return rebuilt, missing


def summarize_alignment(raw_rows, rebuilt_rows):
    n_raw = len(raw_rows)
    n_rebuilt = len(rebuilt_rows)
    same_query = 0
    same_gold = 0
    same_rank_entities = 0

    for raw, reb in zip(raw_rows[:n_rebuilt], rebuilt_rows):
        if raw["query_entity"] == reb["query_entity"]:
            same_query += 1
        if raw["gold_entity"] == reb["gold_entity"]:
            same_gold += 1
        raw_cand = raw["candidate_entities"]
        reb_cand = reb["rank_entities"]
        if raw_cand == reb_cand:
            same_rank_entities += 1

    return {
        "num_raw_rows": n_raw,
        "num_rebuilt_rows": n_rebuilt,
        "same_query_rate_zip": round(same_query / max(1, n_rebuilt), 6),
        "same_gold_rate_zip": round(same_gold / max(1, n_rebuilt), 6),
        "same_candidate_list_rate_zip": round(same_rank_entities / max(1, n_rebuilt), 6),
        "exact_leak_count": count_exact_leaks(rebuilt_rows),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    relation2id = load_pickle(REL2ID)
    rel_q_a2b = load_json(TAIL_LEX)
    rel_q_b2a = load_json(HEAD_LEX)

    raw_train = load_json(RAW_TRAIN)
    raw_valid = load_json(RAW_VALID)
    raw_test = load_json(RAW_TEST)

    evi_train = load_json(OLD_TRAIN_EVI)
    evi_valid = load_json(OLD_VALID_EVI)
    evi_test = load_json(OLD_TEST_EVI)

    idx_train = build_evidence_index(evi_train)
    idx_valid = build_evidence_index(evi_valid)
    idx_test = build_evidence_index(evi_test)

    train_rebuilt, train_missing = rebuild_split(raw_train, idx_train, rel_q_a2b, rel_q_b2a, relation2id)
    valid_rebuilt, valid_missing = rebuild_split(raw_valid, idx_valid, rel_q_a2b, rel_q_b2a, relation2id)
    test_rebuilt, test_missing = rebuild_split(raw_test, idx_test, rel_q_a2b, rel_q_b2a, relation2id)

    save_json(OUT_DIR / "train_aligned_evidence.json", train_rebuilt)
    save_json(OUT_DIR / "valid_aligned_evidence.json", valid_rebuilt)
    save_json(OUT_DIR / "test_aligned_evidence.json", test_rebuilt)

    manifest = {
        "source": {
            "raw_train": str(RAW_TRAIN),
            "raw_valid": str(RAW_VALID),
            "raw_test": str(RAW_TEST),
            "old_train_evidence": str(OLD_TRAIN_EVI),
            "old_valid_evidence": str(OLD_VALID_EVI),
            "old_test_evidence": str(OLD_TEST_EVI),
        },
        "alignment_key": "(query_entity, gold_entity/output)",
        "train_summary": summarize_alignment(raw_train, train_rebuilt),
        "valid_summary": summarize_alignment(raw_valid, valid_rebuilt),
        "test_summary": summarize_alignment(raw_test, test_rebuilt),
        "missing": {
            "train_missing_count": len(train_missing),
            "valid_missing_count": len(valid_missing),
            "test_missing_count": len(test_missing),
            "valid_missing_samples": valid_missing[:10],
            "test_missing_samples": test_missing[:10],
        },
        "important_note": "Prompts were regenerated from raw candidate lists; subgraphs were copied from matched evidence rows keyed by (query_entity, gold_entity)."
    }

    save_json(OUT_DIR / "alignment_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()   