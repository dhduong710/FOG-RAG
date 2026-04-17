from __future__ import annotations

import json
from pathlib import Path
from collections import Counter

import torch


ROOT = Path(".")


def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def load_scores(path: Path):
    return torch.load(path, map_location="cpu")


def rank_of_gold(scores_row, candidate_ids, gold_id):
    # rank bắt đầu từ 1, descending score
    sorted_idx = torch.argsort(scores_row, descending=True)
    ranked_ids = candidate_ids[sorted_idx]
    pos = (ranked_ids == gold_id).nonzero(as_tuple=False)
    if len(pos) == 0:
        return None
    return int(pos[0].item()) + 1


def build_split(split_name: str, obj: dict, k: int = 20):
    scores = obj["scores"]
    query_names = obj["query_entity_names"]
    query_ids = obj["query_entity_ids"]
    gold_names = obj["gold_entity_names"]
    gold_ids = obj["gold_entity_ids"]
    cand_names = obj["candidate_entity_names"]
    cand_ids = obj["candidate_entity_ids"]

    raw_examples = []
    ready_examples = []

    recall_count = 0
    top1_hit_count = 0
    inject_count = 0
    rank_counter = Counter()

    for i in range(scores.shape[0]):
        row = scores[i]
        topk_idx = torch.argsort(row, descending=True)[:k]

        topk_names = [cand_names[j] for j in topk_idx.tolist()]
        topk_ids = [int(cand_ids[j]) for j in topk_idx.tolist()]

        gold_name = gold_names[i]
        gold_id = int(gold_ids[i])
        query_name = query_names[i]
        query_id = int(query_ids[i])

        raw_rank = rank_of_gold(row, cand_ids, gold_id)
        if raw_rank is not None:
            rank_counter[raw_rank] += 1

        if gold_id in topk_ids:
            recall_count += 1

        if len(topk_ids) > 0 and topk_ids[0] == gold_id:
            top1_hit_count += 1

        raw_ex = {
            "split": split_name,
            "query_entity": query_name,
            "query_entity_id": query_id,
            "gold_entity": gold_name,
            "gold_entity_id": gold_id,
            "candidate_entities": topk_names,
            "candidate_entity_ids": topk_ids,
            "gold_rank_in_full_universe": raw_rank,
            "gold_in_topk_raw": gold_id in topk_ids,
        }
        raw_examples.append(raw_ex)

        ready_names = list(topk_names)
        ready_ids = list(topk_ids)
        injected = False

        if gold_id not in ready_ids:
            injected = True
            inject_count += 1
            # thay candidate cuối cùng bằng gold
            if len(ready_ids) >= k:
                ready_ids[-1] = gold_id
                ready_names[-1] = gold_name
            else:
                ready_ids.append(gold_id)
                ready_names.append(gold_name)

        ready_ex = {
            "split": split_name,
            "query_entity": query_name,
            "query_entity_id": query_id,
            "gold_entity": gold_name,
            "gold_entity_id": gold_id,
            "candidate_entities": ready_names,
            "candidate_entity_ids": ready_ids,
            "gold_rank_in_full_universe": raw_rank,
            "gold_in_topk_raw": gold_id in topk_ids,
            "gold_in_topk_ready": gold_id in ready_ids,
            "gold_injected": injected,
        }
        ready_examples.append(ready_ex)

    report = {
        "split": split_name,
        "num_queries": len(raw_examples),
        "k": k,
        "recall_at_k_raw": round(recall_count / len(raw_examples), 6),
        "top1_hit_ratio_raw": round(top1_hit_count / len(raw_examples), 6),
        "inject_count_ready": inject_count,
        "inject_ratio_ready": round(inject_count / len(raw_examples), 6),
        "rank_distribution_raw_top50": {
            str(rank): count
            for rank, count in sorted(rank_counter.items())
            if rank <= 50
        },
    }

    return raw_examples, ready_examples, report


def main():
    base = ROOT / "dataset/setting_a/09_real_coarse_ranker"

    split_files = {
        "train": base / "train_scores.pt",
        "valid": base / "valid_scores.pt",
        "test": base / "test_scores.pt",
    }

    all_reports = {}

    for split_name, score_path in split_files.items():
        obj = load_scores(score_path)

        raw_examples, ready_examples, report = build_split(split_name, obj, k=20)
        all_reports[split_name] = report

        save_json(base / f"{split_name}_top20_raw.json", raw_examples)
        save_json(base / f"{split_name}_top20_drkgc_ready.json", ready_examples)

    summary = {
        "week": 6,
        "day": 3,
        "goal": "Build real candidate JSON and analyze candidate retrieval quality.",
        "splits": all_reports,
        "important_note": (
            "top20_raw is for candidate retrieval quality; "
            "top20_drkgc_ready is for reranking pipeline and may include gold injection."
        ),
    }

    save_json(base / "candidate_recall_report.json", summary)

    print("=" * 80)
    print("Saved:")
    for split in ["train", "valid", "test"]:
        print("-", base / f"{split}_top20_raw.json")
        print("-", base / f"{split}_top20_drkgc_ready.json")
    print("-", base / "candidate_recall_report.json")
    print("=" * 80)

    for split, rep in all_reports.items():
        print(f"[{split}] recall@20_raw={rep['recall_at_k_raw']}, "
              f"top1_raw={rep['top1_hit_ratio_raw']}, "
              f"inject_ratio_ready={rep['inject_ratio_ready']}")\
              
if __name__ == "__main__":
    main()