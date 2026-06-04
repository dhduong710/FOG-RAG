from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


RAW_VALID = Path("dataset/setting_a/23_noinj_source/valid_top20_raw.json")
RAW_TEST = Path("dataset/setting_a/23_noinj_source/test_top20_raw.json")

ONTO_VALID = Path("dataset/setting_a/24_noinj_ontology/valid_top20_ontology_raw.json")
ONTO_TEST = Path("dataset/setting_a/24_noinj_ontology/test_top20_ontology_raw.json")

TYPE_MAP_TSV = Path("dataset/setting_b/01_annotations/type_map.tsv")
FALLBACK_TYPE_JSON = Path("dataset/setting_b/01_ontology/entity_name_to_type.json")

OUT_DIR = Path("results/week12B/ontology_pruning_audit")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_type_map() -> dict[str, str]:
    m = {}
    with TYPE_MAP_TSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            ent = row.get("entity")
            final_type = row.get("final_type")
            if ent:
                m[ent] = final_type
    return m


def load_fallback_type() -> dict[str, str]:
    with FALLBACK_TYPE_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_gold_type(gold: str, type_map: dict, fallback: dict) -> tuple[str | None, str]:
    if gold in type_map and type_map[gold]:
        return type_map[gold], "type_map"
    if gold in fallback and fallback[gold]:
        return fallback[gold], "fallback"
    return None, "missing"


def build_idx(data: list[dict]) -> dict[tuple[str, str], dict]:
    idx = {}
    for row in data:
        q = row.get("query_entity")
        g = row.get("gold_entity")
        if q is not None and g is not None:
            idx[(q, g)] = row
    return idx


def classify_case(raw_row: dict, onto_row: dict, gold_type: str | None, gold_type_source: str) -> dict:
    gold = raw_row["gold_entity"]
    raw_cand = raw_row.get("candidate_entities") or raw_row.get("rank_entities") or []
    onto_cand = onto_row.get("candidate_entities") or onto_row.get("rank_entities") or []

    raw_has_gold = gold in raw_cand
    onto_has_gold = gold in onto_cand

    if not raw_has_gold:
        reason = "not_a_pruning_case"
    elif onto_has_gold:
        reason = "gold_preserved"
    else:
        if gold_type is None:
            reason = "gold_missing_type"
        elif gold_type != "Drug":
            reason = "gold_wrong_type"
        else:
            fb = onto_row.get("ontology_fallback_used")
            # heuristic categories
            if fb is True:
                reason = "gold_not_recovered_by_fallback"
            else:
                reason = "gold_no_ontology_support"

    return {
        "query_entity": raw_row["query_entity"],
        "gold_entity": gold,
        "gold_type": gold_type,
        "gold_type_source": gold_type_source,
        "raw_candidate_size": len(raw_cand),
        "ontology_candidate_size": len(onto_cand),
        "raw_has_gold": raw_has_gold,
        "ontology_has_gold": onto_has_gold,
        "ontology_fallback_used": onto_row.get("ontology_fallback_used"),
        "reason": reason,
        "raw_top5": raw_cand[:5],
        "onto_top5": onto_cand[:5],
    }


def audit_split(raw_path: Path, onto_path: Path, type_map: dict, fallback: dict):
    raw = load_json(raw_path)
    onto = load_json(onto_path)

    raw_idx = build_idx(raw)
    onto_idx = build_idx(onto)

    results = []
    for key, raw_row in raw_idx.items():
        onto_row = onto_idx.get(key)
        if onto_row is None:
            continue

        gold = raw_row["gold_entity"]
        gold_type, gold_type_source = get_gold_type(gold, type_map, fallback)
        results.append(classify_case(raw_row, onto_row, gold_type, gold_type_source))

    return results


def summarize(rows: list[dict]) -> dict:
    total = len(rows)
    reason_counter = Counter(r["reason"] for r in rows)

    pruning_cases = [r for r in rows if r["raw_has_gold"] and not r["ontology_has_gold"]]
    raw_gold_cases = [r for r in rows if r["raw_has_gold"]]

    summary = {
        "num_rows": total,
        "num_raw_gold_cases": len(raw_gold_cases),
        "num_pruning_cases": len(pruning_cases),
        "pruning_rate_given_raw_gold": round(len(pruning_cases) / max(1, len(raw_gold_cases)), 6),
        "reason_counts": dict(reason_counter),
    }
    return summary


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    type_map = load_type_map()
    fallback = load_fallback_type()

    valid_rows = audit_split(RAW_VALID, ONTO_VALID, type_map, fallback)
    test_rows = audit_split(RAW_TEST, ONTO_TEST, type_map, fallback)

    valid_summary = summarize(valid_rows)
    test_summary = summarize(test_rows)

    valid_cases = [r for r in valid_rows if r["raw_has_gold"] and not r["ontology_has_gold"]][:50]
    test_cases = [r for r in test_rows if r["raw_has_gold"] and not r["ontology_has_gold"]][:50]

    with (OUT_DIR / "valid_gold_loss_audit.json").open("w", encoding="utf-8") as f:
        json.dump(valid_rows, f, indent=2, ensure_ascii=False)
    with (OUT_DIR / "test_gold_loss_audit.json").open("w", encoding="utf-8") as f:
        json.dump(test_rows, f, indent=2, ensure_ascii=False)
    with (OUT_DIR / "valid_gold_loss_summary.json").open("w", encoding="utf-8") as f:
        json.dump(valid_summary, f, indent=2, ensure_ascii=False)
    with (OUT_DIR / "test_gold_loss_summary.json").open("w", encoding="utf-8") as f:
        json.dump(test_summary, f, indent=2, ensure_ascii=False)
    with (OUT_DIR / "gold_loss_case_samples.json").open("w", encoding="utf-8") as f:
        json.dump({"valid": valid_cases, "test": test_cases}, f, indent=2, ensure_ascii=False)

    print("VALID SUMMARY")
    print(json.dumps(valid_summary, indent=2, ensure_ascii=False))
    print("-----")
    print("TEST SUMMARY")
    print(json.dumps(test_summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()