from __future__ import annotations

import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("dataset/setting_a/21_ranker_rescue")
TARGET_DIR = Path("dataset/setting_a/23_noinj_source")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def summarize_raw(data: list[dict]) -> dict:
    n = len(data)
    recall_at_20_raw = sum(int(x.get("gold_in_topk_raw", False)) for x in data) / n if n else 0.0
    unique_top1_count = None
    top1_dominance_ratio = None

    # compatible with your candidate_report conventions if raw rows keep candidate_entities
    top1_list = []
    for x in data:
        cand = x.get("candidate_entities") or x.get("rank_entities") or []
        if cand:
            top1_list.append(cand[0])

    if top1_list:
        from collections import Counter
        c = Counter(top1_list)
        unique_top1_count = len(c)
        top1_dominance_ratio = max(c.values()) / len(top1_list)

    return {
        "num_queries": n,
        "recall_at_20_raw": round(recall_at_20_raw, 6),
        "unique_top1_count_raw": unique_top1_count,
        "top1_dominance_ratio_raw": round(top1_dominance_ratio, 6) if top1_dominance_ratio is not None else None,
    }


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    required = [
        SOURCE_DIR / "valid_top20_raw.json",
        SOURCE_DIR / "test_top20_raw.json",
        SOURCE_DIR / "candidate_report.json",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing raw source files:\n" + "\n".join(missing))

    for name in ["valid_top20_raw.json", "test_top20_raw.json"]:
        shutil.copy2(SOURCE_DIR / name, TARGET_DIR / name)

    valid = load_json(TARGET_DIR / "valid_top20_raw.json")
    test = load_json(TARGET_DIR / "test_top20_raw.json")

    manifest = {
        "source_dir": str(SOURCE_DIR),
        "target_dir": str(TARGET_DIR),
        "copied_files": [
            "valid_top20_raw.json",
            "test_top20_raw.json"
        ],
        "valid_summary": summarize_raw(valid),
        "test_summary": summarize_raw(test),
        "important_note": "This frozen source is the official raw/no-injection source of truth for Week 12B."
    }

    manifest_path = TARGET_DIR / "raw_source_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"Saved manifest to: {manifest_path}")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()