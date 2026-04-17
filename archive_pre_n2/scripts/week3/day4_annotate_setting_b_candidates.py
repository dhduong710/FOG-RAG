from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


BASE_A = Path("dataset/setting_a")
BASE_B = Path("dataset/setting_b")

CAND_DIR = BASE_A / "03_candidates"
ANNOT_DIR = BASE_B / "01_annotations"
OUT_DIR = BASE_B / "02_eval_ready"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TYPE_MAP_PATH = ANNOT_DIR / "type_map.tsv"
CONTRA_PATH = ANNOT_DIR / "contraindication_pairs.tsv"
CONFLICT_PATH = ANNOT_DIR / "contraindication_conflicts.tsv"

VALID_IN = CAND_DIR / "valid_mock_candidates.json"
TEST_IN = CAND_DIR / "test_mock_candidates.json"

VALID_OUT = OUT_DIR / "valid_b_annotations.json"
TEST_OUT = OUT_DIR / "test_b_annotations.json"

REPORT_PATH = Path("reports/week3/day4_setting_b_annotation_report.md")
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)


def norm(x):
    return str(x).strip()


def read_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_type_map():
    df = pd.read_csv(TYPE_MAP_PATH, sep="\t")
    type_col = "final_type" if "final_type" in df.columns else "type"
    return {norm(r["entity"]): norm(r[type_col]) for _, r in df.iterrows()}


def load_pair_set(path: Path, pair_type: str):
    if not path.exists():
        return set()

    df = pd.read_csv(path, sep="\t")
    out = set()

    if {"drug", "disease"}.issubset(df.columns):
        for _, r in df.iterrows():
            out.add((norm(r["drug"]), norm(r["disease"])))
    elif {"head", "tail"}.issubset(df.columns):
        for _, r in df.iterrows():
            out.add((norm(r["head"]), norm(r["tail"])))
    else:
        raise ValueError(f"Unsupported columns in {pair_type}: {path}")

    return out


def annotate_split(in_path: Path, out_path: Path, type_map, contra_pairs, conflict_pairs):
    data = read_json(in_path)

    annotated = []
    all_candidates_have_type = True
    non_drug_candidates = 0
    gold_missing_annotation = 0
    contra_positive_samples = 0

    for ex in data:
        query_disease = norm(ex.get("query_entity"))
        gold_drug = norm(ex.get("gold_entity"))
        candidate_drugs = [norm(x) for x in ex.get("candidate_entities", [])]

        candidate_types = []
        contra_flags = []
        conflict_flags = []

        for drug in candidate_drugs:
            t = type_map.get(drug)
            if t is None:
                t = "MISSING"
                all_candidates_have_type = False
            candidate_types.append(t)

            if t != "Drug":
                non_drug_candidates += 1

            contra_flags.append(1 if (drug, query_disease) in contra_pairs else 0)
            conflict_flags.append(1 if (drug, query_disease) in conflict_pairs else 0)

        gold_type = type_map.get(gold_drug, "MISSING")
        gold_is_contra = 1 if (gold_drug, query_disease) in contra_pairs else 0
        gold_conflict_flag = 1 if (gold_drug, query_disease) in conflict_pairs else 0

        if gold_type == "MISSING":
            gold_missing_annotation += 1

        has_any_contra_candidate = int(any(contra_flags))
        if has_any_contra_candidate:
            contra_positive_samples += 1

        annotated.append({
            "query_disease": query_disease,
            "gold_drug": gold_drug,
            "setting_a_relation": "indication",
            "candidate_drugs": candidate_drugs,
            "candidate_types": candidate_types,
            "contra_flags": contra_flags,
            "conflict_flags": conflict_flags,
            "gold_type": gold_type,
            "gold_is_contraindicated": gold_is_contra,
            "gold_conflict_flag": gold_conflict_flag,
            "has_any_contra_candidate": has_any_contra_candidate
        })

    write_json(out_path, annotated)

    return {
        "num_samples": len(annotated),
        "all_candidates_have_type": all_candidates_have_type,
        "non_drug_candidates": non_drug_candidates,
        "gold_missing_annotation": gold_missing_annotation,
        "contra_positive_samples": contra_positive_samples,
    }


def main():
    type_map = load_type_map()
    contra_pairs = load_pair_set(CONTRA_PATH, "contra")
    conflict_pairs = load_pair_set(CONFLICT_PATH, "conflict") if CONFLICT_PATH.exists() else set()

    valid_stats = annotate_split(VALID_IN, VALID_OUT, type_map, contra_pairs, conflict_pairs)
    test_stats = annotate_split(TEST_IN, TEST_OUT, type_map, contra_pairs, conflict_pairs)

    lines = [
        "# Day 4 Setting B Annotation Report",
        "",
        "## Output files",
        f"- {VALID_OUT}",
        f"- {TEST_OUT}",
        "",
        "## Valid stats",
    ]
    for k, v in valid_stats.items():
        lines.append(f"- {k}: {v}")

    lines += ["", "## Test stats"]
    for k, v in test_stats.items():
        lines.append(f"- {k}: {v}")

    lines += [
        "",
        "## Final checks",
        f"- valid/test sample count preserved: {valid_stats['num_samples']} / {test_stats['num_samples']}",
        f"- candidate type failures: {valid_stats['non_drug_candidates'] + test_stats['non_drug_candidates']}",
        f"- gold missing annotation: {valid_stats['gold_missing_annotation'] + test_stats['gold_missing_annotation']}",
        "",
        "## Required checklist",
        "- every candidate has type",
        "- contra_flags length matches candidate list",
        "- no non-Drug candidate remains",
        "- every gold drug has annotation",
        "- Setting B sample count matches Setting A candidate files",
    ]

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Saved:", VALID_OUT)
    print("Saved:", TEST_OUT)
    print("Saved:", REPORT_PATH)
    print("valid_stats =", valid_stats)
    print("test_stats =", test_stats)


if __name__ == "__main__":
    main()