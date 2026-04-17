from __future__ import annotations

import json
import pickle
import shutil
from pathlib import Path


ROOT = Path(".")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def load_pickle(path: Path):
    with path.open("rb") as f:
        return pickle.load(f)


def copy_if_exists(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def convert_split(ready_json_path: Path, relation2id: dict, relation_name: str = "indication"):
    data = load_json(ready_json_path)

    if relation_name not in relation2id:
        raise KeyError(f"Relation `{relation_name}` not found in relation2id.")

    relation_id = int(relation2id[relation_name])

    converted = []
    inject_count = 0

    for ex in data:
        cand_names = ex["candidate_entities"]
        cand_ids = ex["candidate_entity_ids"]

        if len(cand_names) != 20 or len(cand_ids) != 20:
            raise ValueError(
                f"{ready_json_path.name}: candidate length != 20 for query {ex.get('query_entity')}"
            )

        gold_id = int(ex["gold_entity_id"])
        gold_name = ex["gold_entity"]
        query_id = int(ex["query_entity_id"])
        query_name = ex["query_entity"]

        if gold_id in cand_ids:
            rank = cand_ids.index(gold_id) + 1
        else:
            rank = None

        injected = bool(ex.get("gold_injected", False))
        if injected:
            inject_count += 1

        out = {
            "triple": [gold_name, relation_name, query_name],
            "triple_id": [gold_id, relation_id, query_id],
            "type": "predicted_head",
            "query_entity": query_name,
            "query_entity_id": query_id,
            "rank_entities": cand_names,
            "rank_entities_id": cand_ids,
            "rank": rank,
            "gold_entity": gold_name,
            "gold_entity_id": gold_id,
            "gold_in_topk_raw": bool(ex.get("gold_in_topk_raw", False)),
            "gold_in_topk_ready": bool(ex.get("gold_in_topk_ready", True)),
            "gold_injected": injected,
            "gold_rank_in_full_universe": ex.get("gold_rank_in_full_universe"),
        }
        converted.append(out)

    return converted, inject_count


def main():
    src_base = ROOT / "dataset/setting_a/09_real_coarse_ranker"
    dst_base = ROOT / "dataset/setting_a/10_backbone_ready_real"
    interm = dst_base / "intermediate"

    relation2id_path = ROOT / "dataset/setting_a/04_drkgc_json/relation2id.pkl"
    entity2id_path = ROOT / "dataset/setting_a/04_drkgc_json/entity2id.pkl"
    id2entity_path = ROOT / "dataset/setting_a/04_drkgc_json/id2entity.pkl"
    id2relation_path = ROOT / "dataset/setting_a/04_drkgc_json/id2relation.pkl"

    relation2id = load_pickle(relation2id_path)

    split_inputs = {
        "train": src_base / "train_top20_drkgc_ready.json",
        "valid": src_base / "valid_top20_drkgc_ready.json",
        "test": src_base / "test_top20_drkgc_ready.json",
    }

    split_outputs = {
        "train": interm / "train_ranked_input.json",
        "valid": interm / "valid_ranked_input.json",
        "test": interm / "test_ranked_input.json",
    }

    split_meta = {}

    for split, src_path in split_inputs.items():
        converted, inject_count = convert_split(src_path, relation2id, relation_name="indication")
        save_json(split_outputs[split], converted)

        split_meta[split] = {
            "source_ready_json": str(src_path),
            "ranked_input_json": str(split_outputs[split]),
            "num_queries": len(converted),
            "inject_count": inject_count,
            "inject_ratio": round(inject_count / len(converted), 6) if converted else 0.0,
        }

    copy_if_exists(entity2id_path, dst_base / "entity2id.pkl")
    copy_if_exists(id2entity_path, dst_base / "id2entity.pkl")
    copy_if_exists(relation2id_path, dst_base / "relation2id.pkl")
    copy_if_exists(id2relation_path, dst_base / "id2relation.pkl")

    manifest = {
        "week": 6,
        "day": 4,
        "goal": "Rebuild backbone-ready package from real-ranked candidate artifacts.",
        "source_candidate_dir": str(src_base),
        "destination_dir": str(dst_base),
        "relation_name": "indication",
        "intermediate_ranked_inputs": split_meta,
    }

    save_json(dst_base / "backbone_ready_real_manifest.json", manifest)

    print("=" * 80)
    print("Prepared ranked inputs:")
    for split in ["train", "valid", "test"]:
        print("-", split_outputs[split])
    print("Saved manifest:", dst_base / "backbone_ready_real_manifest.json")
    print("=" * 80)


if __name__ == "__main__":
    main()