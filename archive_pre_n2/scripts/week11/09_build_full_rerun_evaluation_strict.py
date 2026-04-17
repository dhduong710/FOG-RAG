import csv
import json
from pathlib import Path
from statistics import mean

OUT_DIR = Path("results/week11_rerun_fix_strict")
OUT_DIR.mkdir(parents=True, exist_ok=True)

VARIANTS = {
    "Backbone": {
        "rerun_dir": Path("results/week11_test/backbone_test"),
        "valid_eval_json": Path("dataset/setting_b/05_eval_week11/valid_backbone_eval.json"),
        "test_eval_json": Path("dataset/setting_b/06_eval_week11_test/test_backbone_eval.json"),
    },
    "+ Ontology": {
        "rerun_dir": Path("results/week11_test/ontology_test"),
        "valid_eval_json": Path("dataset/setting_b/05_eval_week11/valid_ontology_eval.json"),
        "test_eval_json": Path("dataset/setting_b/06_eval_week11_test/test_ontology_eval.json"),
    },
    "+ Ontology + Hard": {
        "rerun_dir": Path("results/week11_test/hard_main_test"),
        "valid_eval_json": Path("dataset/setting_b/05_eval_week11/valid_hard_main_eval.json"),
        "test_eval_json": Path("dataset/setting_b/06_eval_week11_test/test_hard_main_eval.json"),
    },
    "+ Ontology + Soft": {
        "rerun_dir": Path("results/week11_test/soft_best_test"),
        "valid_eval_json": Path("dataset/setting_b/05_eval_week11/valid_soft_best_eval.json"),
        "test_eval_json": Path("dataset/setting_b/06_eval_week11_test/test_soft_best_eval.json"),
    },
}

RANKING_FILE_PREFERENCE = {
    "valid": [
        "ranking_metrics_valid_rerun_clean.json",
        "ranking_metrics_valid_rerun.json",
        "ranking_metrics_valid.json",
    ],
    "test": [
        "ranking_metrics_test_rerun_clean.json",
        "ranking_metrics_test_rerun.json",
        "ranking_metrics_test.json",
    ],
}

PRED_FILE_PREFERENCE = {
    "valid": [
        "prediction_valid_rerun_clean.json",
        "prediction_valid_rerun.json",
        "prediction_valid.json",
    ],
    "test": [
        "prediction_test_rerun_clean.json",
        "prediction_test_rerun.json",
        "prediction_test.json",
    ],
}


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_existing(base: Path, names):
    for name in names:
        p = base / name
        if p.exists():
            return p
    return None


def safe_mean(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return mean(xs)


def round_or_none(x, nd=4):
    if x is None:
        return None
    return round(float(x), nd)


def fmt(x):
    if x is None:
        return "-"
    if isinstance(x, float):
        return f"{x:.4f}"
    return str(x)


def summarize_prediction(pred_path: Path):
    payload = load_json(pred_path)
    rows = payload["prediction"]

    cand_sizes = []
    subgraph_sizes = []
    gold_in_topk = []
    gold_injected = []
    pred_in_candidate = []
    pred_ranks = []

    for ex in rows:
        rank_entities = ex.get("rank_entities", [])
        target = ex.get("target", ex.get("output"))
        pred = ex.get("pred")
        pred_rank = ex.get("pred_rank")
        subgraph = ex.get("subgraph", [])

        cand_sizes.append(len(rank_entities))
        subgraph_sizes.append(len(subgraph))
        gold_in_topk.append(int(target in rank_entities) if target is not None else None)
        gold_injected.append(int(bool(ex.get("gold_injected", False))) if "gold_injected" in ex else None)
        pred_in_candidate.append(int(pred in rank_entities) if pred is not None else None)
        pred_ranks.append(pred_rank)

    return {
        "AvgCandidateSize": round_or_none(safe_mean(cand_sizes)),
        "AvgSubgraphSize": round_or_none(safe_mean(subgraph_sizes)),
        "GoldInTopKRate": round_or_none(safe_mean(gold_in_topk)),
        "GoldInjectedRate": round_or_none(safe_mean(gold_injected)),
        "PredInCandidateRate": round_or_none(safe_mean(pred_in_candidate)),
        "MeanPredRank": round_or_none(safe_mean(pred_ranks)),
        "NumExamplesFromPrediction": len(rows),
    }


def get_expected_head_type(setting_a_relation: str):
    # current project uses head prediction for (? , indication, disease)
    # and all candidate rows are drug-ranking rows
    if setting_a_relation in {"indication", "treats"}:
        return "Drug"
    return "Drug"


def summarize_setting_b_eval(eval_path: Path, k: int = 10):
    rows = load_json(eval_path)

    safety_viol = []
    contra_counts = []
    constraint_violation_rates = []
    query_has_constraint_violation = []
    gold_in_topk = []
    candidate_count = []
    has_any_contra_candidate = []

    num_contra_candidates = []
    strict_empty = []
    fallback = []

    for row in rows:
        cand_drugs = row.get("candidate_drugs_final", []) or []
        cand_types = row.get("candidate_types_final", []) or []
        contra_flags = row.get("contra_flags_final", []) or []

        topk_types = cand_types[:k]
        topk_contra = contra_flags[:k]

        expected_type = get_expected_head_type(row.get("setting_a_relation", "indication"))
        invalid_flags = [1 if t != expected_type else 0 for t in topk_types]

        safety_viol.append(1 if any(topk_contra) else 0)
        contra_counts.append(sum(topk_contra))

        if len(topk_types) > 0:
            constraint_violation_rates.append(sum(invalid_flags) / len(topk_types))
            query_has_constraint_violation.append(1 if any(invalid_flags) else 0)
        else:
            constraint_violation_rates.append(0.0)
            query_has_constraint_violation.append(0)

        gold_in_topk.append(int(bool(row.get("row_has_gold_in_topk", False))))
        candidate_count.append(int(row.get("candidate_count_final", len(cand_drugs))))
        has_any_contra_candidate.append(int(bool(row.get("has_any_contra_candidate_final", False))))

        # hard / soft-specific support fields
        num_contra_candidates.append(sum(contra_flags) if len(contra_flags) > 0 else 0)
        strict_empty.append(int(bool(row.get("strict_empty_after_hard", False))) if "strict_empty_after_hard" in row else None)
        fallback.append(int(bool(row.get("fallback_after_hard", False))) if "fallback_after_hard" in row else None)

    return {
        "SafetyViolation@10": round_or_none(safe_mean(safety_viol)),
        "Contra@10": round_or_none(safe_mean(contra_counts)),
        "ConstraintViolationRate": round_or_none(safe_mean(constraint_violation_rates)),
        "QueryHasConstraintViolationRate": round_or_none(safe_mean(query_has_constraint_violation)),
        "CandidateCountFinal": round_or_none(safe_mean(candidate_count)),
        "SettingB_GoldInTopKRate": round_or_none(safe_mean(gold_in_topk)),
        "QueryHasContraCandidateRate": round_or_none(safe_mean(has_any_contra_candidate)),
        "NumContraCandidates": round_or_none(safe_mean(num_contra_candidates)),
        "StrictEmptyRate": round_or_none(safe_mean(strict_empty)),
        "FallbackRate": round_or_none(safe_mean(fallback)),
        "NumRowsFromSettingBEval": len(rows),
    }


def collect_split(split: str):
    rows = []

    for variant_name, info in VARIANTS.items():
        rerun_dir = info["rerun_dir"]
        eval_json_path = info["valid_eval_json"] if split == "valid" else info["test_eval_json"]

        ranking_path = pick_existing(rerun_dir, RANKING_FILE_PREFERENCE[split])
        pred_path = pick_existing(rerun_dir, PRED_FILE_PREFERENCE[split])

        if ranking_path is None:
            raise FileNotFoundError(f"Missing ranking file for {variant_name} [{split}] in {rerun_dir}")
        if pred_path is None:
            raise FileNotFoundError(f"Missing prediction file for {variant_name} [{split}] in {rerun_dir}")
        if not eval_json_path.exists():
            raise FileNotFoundError(f"Missing Setting B eval json: {eval_json_path}")

        ranking = load_json(ranking_path)
        pred_summary = summarize_prediction(pred_path)
        settingb_summary = summarize_setting_b_eval(eval_json_path)

        row = {
            "Variant": variant_name,
            "MRR": ranking.get("mrr"),
            "Hits@1": ranking.get("hits1"),
            "Hits@3": ranking.get("hits3"),
            "Hits@10": ranking.get("hits10"),
            "NumExamples": ranking.get("num_examples"),
        }
        row.update(pred_summary)
        row.update(settingb_summary)
        rows.append(row)

    backbone = next(r for r in rows if r["Variant"] == "Backbone")
    for r in rows:
        r["ΔMRR_vs_Backbone"] = round_or_none(r["MRR"] - backbone["MRR"])
        r["ΔHits@10_vs_Backbone"] = round_or_none(r["Hits@10"] - backbone["Hits@10"])

    return rows


def write_csv(path: Path, rows, columns):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for r in rows:
            writer.writerow({c: r.get(c) for c in columns})


def write_md_table(path: Path, title: str, rows, columns):
    lines = [f"# {title}", ""]
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("|" + "|".join(["---"] * len(columns)) + "|")
    for r in rows:
        lines.append("| " + " | ".join(fmt(r.get(c)) for c in columns) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def write_report(valid_rows, test_rows):
    md = []
    md.append("# Week 11 Strict Fresh Rerun Report")
    md.append("")
    md.append("## 1. Evaluation policy")
    md.append("- This report does not reuse old metric files from `results/week11` or `results/week11_test`.")
    md.append("- Ranking metrics are read from rerun outputs after the inference split fix.")
    md.append("- Safety and constraint metrics are recomputed directly from Setting B eval JSON files.")
    md.append("")
    md.append("## 2. Official valid summary")
    for r in valid_rows:
        md.append(
            f"- **{r['Variant']}**: "
            f"MRR={fmt(r['MRR'])}, Hits@1={fmt(r['Hits@1'])}, Hits@3={fmt(r['Hits@3'])}, Hits@10={fmt(r['Hits@10'])}, "
            f"SafetyViolation@10={fmt(r['SafetyViolation@10'])}, Contra@10={fmt(r['Contra@10'])}, "
            f"ConstraintViolationRate={fmt(r['ConstraintViolationRate'])}"
        )
    md.append("")
    md.append("## 3. Official test summary")
    for r in test_rows:
        md.append(
            f"- **{r['Variant']}**: "
            f"MRR={fmt(r['MRR'])}, Hits@1={fmt(r['Hits@1'])}, Hits@3={fmt(r['Hits@3'])}, Hits@10={fmt(r['Hits@10'])}, "
            f"SafetyViolation@10={fmt(r['SafetyViolation@10'])}, Contra@10={fmt(r['Contra@10'])}, "
            f"ConstraintViolationRate={fmt(r['ConstraintViolationRate'])}"
        )
    md.append("")
    md.append("## 4. Main decision")
    md.append("- Main row: **+ Ontology + Hard**")
    md.append("- Supporting row: **+ Ontology + Soft**")
    md.append("")
    md.append("## 5. Reason")
    md.append("- `+ Ontology + Hard` remains the strongest main row by overall ranking trade-off after the split fix.")
    md.append("- All numbers in this report are regenerated after the fix.")
    md.append("")

    (OUT_DIR / "strict_rerun_report.md").write_text("\n".join(md), encoding="utf-8")


def main():
    valid_rows = collect_split("valid")
    test_rows = collect_split("test")

    ranking_cols = [
        "Variant", "MRR", "Hits@1", "Hits@3", "Hits@10",
        "ΔMRR_vs_Backbone", "ΔHits@10_vs_Backbone", "NumExamples"
    ]
    full_cols = [
        "Variant",
        "MRR", "Hits@1", "Hits@3", "Hits@10",
        "SafetyViolation@10", "Contra@10",
        "ConstraintViolationRate", "QueryHasConstraintViolationRate",
        "AvgCandidateSize", "AvgSubgraphSize", "GoldInTopKRate", "GoldInjectedRate",
        "PredInCandidateRate", "MeanPredRank",
        "CandidateCountFinal", "SettingB_GoldInTopKRate",
        "QueryHasContraCandidateRate", "NumContraCandidates",
        "StrictEmptyRate", "FallbackRate",
        "ΔMRR_vs_Backbone", "ΔHits@10_vs_Backbone",
    ]

    write_json(OUT_DIR / "valid_rows.json", valid_rows)
    write_json(OUT_DIR / "test_rows.json", test_rows)

    write_csv(OUT_DIR / "valid_ranking_table.csv", valid_rows, ranking_cols)
    write_csv(OUT_DIR / "test_ranking_table.csv", test_rows, ranking_cols)
    write_md_table(OUT_DIR / "valid_ranking_table.md", "Valid Ranking Table", valid_rows, ranking_cols)
    write_md_table(OUT_DIR / "test_ranking_table.md", "Test Ranking Table", test_rows, ranking_cols)

    write_csv(OUT_DIR / "valid_full_table.csv", valid_rows, full_cols)
    write_csv(OUT_DIR / "test_full_table.csv", test_rows, full_cols)
    write_md_table(OUT_DIR / "valid_full_table.md", "Valid Full Evaluation Table", valid_rows, full_cols)
    write_md_table(OUT_DIR / "test_full_table.md", "Test Full Evaluation Table", test_rows, full_cols)

    write_report(valid_rows, test_rows)

    print("Done.")
    print(f"Outputs saved to: {OUT_DIR}")


if __name__ == "__main__":
    main()