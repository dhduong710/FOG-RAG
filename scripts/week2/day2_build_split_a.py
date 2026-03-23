from pathlib import Path
import pandas as pd
import json
import random
import hashlib

# =========================
# Config
# =========================
RAW_PATH = Path("dataset/setting_a/00_raw_triples/primekg_indication_only.tsv")
OUT_DIR = Path("dataset/setting_a/01_split")
REPORT_PATH = Path("reports/week2/day2_split_report.md")

TARGET_TRAIN = 8388
TARGET_VALID = 500
TARGET_TEST = 500

BASE_SEED = 2025
MAX_ATTEMPTS = 200


def sha256_file(path: Path) -> str:
    """
    Tính toán mã băm SHA-256 cho một file.

    Hàm này đọc file theo từng khối nhỏ (chunk) để tránh việc tiêu tốn 
    quá nhiều RAM (Out of Memory) khi xử lý các file có dung lượng lớn.

    Args:
        path (Path): Đường dẫn đến file cần tính mã băm. Có thể là 
                     đối tượng pathlib.Path hoặc chuỗi string.

    Returns:
        str: Chuỗi mã băm SHA-256 ở định dạng thập lục phân (hexadecimal) 
             gồm 64 ký tự.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_required_columns(df: pd.DataFrame):
    required = {"head", "relation", "tail"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")


def can_hold_out(row, head_count, tail_count) -> bool:
    h = row["head"]
    t = row["tail"]
    return head_count[h] > 1 and tail_count[t] > 1


def build_split_once(df: pd.DataFrame, seed: int):
    idxs = list(df.index)
    rng = random.Random(seed)
    rng.shuffle(idxs)

    head_count = df["head"].value_counts().to_dict()
    tail_count = df["tail"].value_counts().to_dict()

    remaining = set(df.index)
    test_ids = []
    valid_ids = []

    # Lấy test trước
    for idx in idxs:
        if len(test_ids) == TARGET_TEST:
            break
        if idx not in remaining:
            continue

        row = df.loc[idx]
        if can_hold_out(row, head_count, tail_count):
            test_ids.append(idx)
            remaining.remove(idx)
            head_count[row["head"]] -= 1
            tail_count[row["tail"]] -= 1

    if len(test_ids) != TARGET_TEST:
        return None

    # Lấy valid sau
    for idx in idxs:
        if len(valid_ids) == TARGET_VALID:
            break
        if idx not in remaining:
            continue

        row = df.loc[idx]
        if can_hold_out(row, head_count, tail_count):
            valid_ids.append(idx)
            remaining.remove(idx)
            head_count[row["head"]] -= 1
            tail_count[row["tail"]] -= 1

    if len(valid_ids) != TARGET_VALID:
        return None

    train_ids = sorted(list(remaining))

    train_df = df.loc[train_ids].reset_index(drop=True)
    valid_df = df.loc[valid_ids].reset_index(drop=True)
    test_df = df.loc[test_ids].reset_index(drop=True)

    return train_df, valid_df, test_df


def verify_split(train_df, valid_df, test_df):
    assert len(train_df) == TARGET_TRAIN, f"Train size != {TARGET_TRAIN}"
    assert len(valid_df) == TARGET_VALID, f"Valid size != {TARGET_VALID}"
    assert len(test_df) == TARGET_TEST, f"Test size != {TARGET_TEST}"

    train_set = set(map(tuple, train_df[["head", "relation", "tail"]].values.tolist()))
    valid_set = set(map(tuple, valid_df[["head", "relation", "tail"]].values.tolist()))
    test_set = set(map(tuple, test_df[["head", "relation", "tail"]].values.tolist()))

    assert train_set.isdisjoint(valid_set), "Train and valid overlap"
    assert train_set.isdisjoint(test_set), "Train and test overlap"
    assert valid_set.isdisjoint(test_set), "Valid and test overlap"

    train_heads = set(train_df["head"].tolist())
    train_tails = set(train_df["tail"].tolist())

    assert set(valid_df["head"]).issubset(train_heads), "Valid has unseen drug"
    assert set(test_df["head"]).issubset(train_heads), "Test has unseen drug"
    assert set(valid_df["tail"]).issubset(train_tails), "Valid has unseen disease"
    assert set(test_df["tail"]).issubset(train_tails), "Test has unseen disease"


def split_stats(df: pd.DataFrame):
    return {
        "num_triples": int(len(df)),
        "num_unique_drugs": int(df["head"].nunique()),
        "num_unique_diseases": int(df["tail"].nunique()),
        "relations": sorted(df["relation"].unique().tolist()),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(RAW_PATH, sep="\t")
    assert_required_columns(df)

    # Chuẩn hóa nhẹ
    df["head"] = df["head"].astype(str).str.strip()
    df["relation"] = df["relation"].astype(str).str.strip()
    df["tail"] = df["tail"].astype(str).str.strip()

    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    after = len(df)

    if after != 9388:
        print(f"[WARN] Expected 9388 triples, got {after}")

    if len(df) != (TARGET_TRAIN + TARGET_VALID + TARGET_TEST):
        raise ValueError(
            f"Total triples must be {TARGET_TRAIN + TARGET_VALID + TARGET_TEST}, got {len(df)}"
        )

    success = None
    used_seed = None

    for attempt in range(MAX_ATTEMPTS):
        seed = BASE_SEED + attempt
        result = build_split_once(df, seed)
        if result is None:
            continue

        train_df, valid_df, test_df = result
        try:
            verify_split(train_df, valid_df, test_df)
            success = (train_df, valid_df, test_df)
            used_seed = seed
            break
        except AssertionError:
            continue

    if success is None:
        raise RuntimeError("Could not build a valid split after multiple attempts.")

    train_df, valid_df, test_df = success

    train_path = OUT_DIR / "train.tsv"
    valid_path = OUT_DIR / "valid.tsv"
    test_path = OUT_DIR / "test.tsv"
    meta_path = OUT_DIR / "split_meta.json"

    train_df.to_csv(train_path, sep="\t", index=False)
    valid_df.to_csv(valid_path, sep="\t", index=False)
    test_df.to_csv(test_path, sep="\t", index=False)

    meta = {
        "source_file": str(RAW_PATH),
        "total_triples_before_dedup": int(before),
        "total_triples_after_dedup": int(after),
        "split_sizes": {
            "train": TARGET_TRAIN,
            "valid": TARGET_VALID,
            "test": TARGET_TEST,
        },
        "coverage_rule": "All drugs and diseases in valid/test must already appear in train.",
        "seed": used_seed,
        "base_seed": BASE_SEED,
        "max_attempts": MAX_ATTEMPTS,
        "train_stats": split_stats(train_df),
        "valid_stats": split_stats(valid_df),
        "test_stats": split_stats(test_df),
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    file_hashes = {
        "train.tsv": sha256_file(train_path),
        "valid.tsv": sha256_file(valid_path),
        "test.tsv": sha256_file(test_path),
        "split_meta.json": sha256_file(meta_path),
    }

    report = f"""# Week 2 - Day 2 Split A Report

## Goal
Lock a fixed Setting A split for PrimeKG indication benchmark.

## Source
- Raw file: {RAW_PATH}

## Split sizes
- train: {len(train_df)}
- valid: {len(valid_df)}
- test: {len(test_df)}

## Coverage rule
- All drugs and diseases appearing in valid/test must also appear in train.

## Seed
- base_seed: {BASE_SEED}
- used_seed: {used_seed}

## Train stats
- unique drugs: {train_df["head"].nunique()}
- unique diseases: {train_df["tail"].nunique()}

## Valid stats
- unique drugs: {valid_df["head"].nunique()}
- unique diseases: {valid_df["tail"].nunique()}

## Test stats
- unique drugs: {test_df["head"].nunique()}
- unique diseases: {test_df["tail"].nunique()}

## Output files
- {train_path}
- {valid_path}
- {test_path}
- {meta_path}

## SHA256
- train.tsv: {file_hashes["train.tsv"]}
- valid.tsv: {file_hashes["valid.tsv"]}
- test.tsv: {file_hashes["test.tsv"]}
- split_meta.json: {file_hashes["split_meta.json"]}

## Notes
- This split is now the locked Setting A split.
- Do not change this split in later weeks.
"""

    REPORT_PATH.write_text(report, encoding="utf-8")

    print("Done.")
    print(f"Used seed: {used_seed}")
    print(f"Train: {len(train_df)}")
    print(f"Valid: {len(valid_df)}")
    print(f"Test : {len(test_df)}")
    print(f"Saved: {train_path}")
    print(f"Saved: {valid_path}")
    print(f"Saved: {test_path}")
    print(f"Saved: {meta_path}")
    print(f"Saved: {REPORT_PATH}")


if __name__ == "__main__":
    main()