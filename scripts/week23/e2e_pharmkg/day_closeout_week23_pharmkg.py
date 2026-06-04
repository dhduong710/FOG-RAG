import json
from pathlib import Path
from statistics import mean


REPORT_DIR = Path("reports/week23")
RESULT_DIR = Path("results/week23")
E2E_SAFE = Path("results/week23/e2e_pharmkg/reviewer_safe/e2e_pharmkg_reviewer_safe_summary.json")
MODEL_COMPARE = Path("results/week23/e2e_pharmkg_model_compare/reviewer_safe/model_compare_reviewer_safe_summary.json")
READY_ROOT = Path("dataset/setting_c_pharmkg/13_e2e_infer_ready")


def load_json(path: Path):
    if not path.exists():
        print(f"[WARN] Missing: {path}")
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def fmt(x, n=6):
    if x is None:
        return "NA"
    if isinstance(x, int):
        return str(x)
    return f"{float(x):.{n}f}"


def get_row(rows, split, row_name):
    for r in rows:
        if r.get("split") == split and r.get("row_name") == row_name:
            return r
    return None


def md_table(headers, rows):
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(lines)


def ready_subgraph_summary(row_name):
    out = {}
    for split in ["valid", "test"]:
        path = READY_ROOT / row_name / f"{split}.json"
        rows = load_json(path)
        if rows is None:
            continue
        sizes = [len(r.get("subgraph", [])) for r in rows]
        out[split] = {
            "num_rows": len(rows),
            "avg_subgraph_size": mean(sizes),
            "min_subgraph_size": min(sizes),
            "max_subgraph_size": max(sizes),
            "gold_at20": mean([1.0 if int(r["rank"]) <= 20 else 0.0 for r in rows]),
            "rank21_count": sum(1 for r in rows if int(r["rank"]) > 20),
        }
    return out


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    e2e_rows = load_json(E2E_SAFE) or []
    model_rows = load_json(MODEL_COMPARE) or []

    # Add Llama-3.2-3B rows into model comparison style for unified model table.
    llama32_rows = []
    for r in e2e_rows:
        rr = dict(r)
        rr["model_tag"] = "llama3_2_3b"
        llama32_rows.append(rr)

    all_model_rows = llama32_rows + model_rows

    # Deduplicate if script is re-run and model compare already includes llama3_2_3b somehow.
    seen = set()
    dedup_model_rows = []
    for r in all_model_rows:
        key = (r.get("model_tag"), r.get("split"), r.get("row_name"))
        if key not in seen:
            seen.add(key)
            dedup_model_rows.append(r)
    all_model_rows = dedup_model_rows

    subgraph = {
        row_name: ready_subgraph_summary(row_name)
        for row_name in ["backbone_raw", "soft_support_raw", "fuzzy_retrieval_main"]
    }

    # Week 23 candidate-level fixed results from completed PharmKG transfer.
    candidate_level = [
        {
            "row_name": "backbone_raw",
            "valid_gold_at20": 0.070,
            "valid_mrr_at20": 0.017846471743,
            "valid_h10": 0.034,
            "test_gold_at20": 0.092,
            "test_mrr_at20": 0.020480769841,
            "test_h10": 0.046,
            "avg_subgraph_size": 100,
            "note": "R-GCN raw top-20 source.",
        },
        {
            "row_name": "hard_support_raw",
            "valid_gold_at20": 0.070,
            "valid_mrr_at20": 0.017846471743,
            "valid_h10": 0.034,
            "test_gold_at20": 0.092,
            "test_mrr_at20": 0.020480769841,
            "test_h10": 0.046,
            "avg_subgraph_size": 100,
            "note": "Negative control; support features saturated and same as backbone.",
        },
        {
            "row_name": "soft_support_raw",
            "valid_gold_at20": 0.070,
            "valid_mrr_at20": 0.021307588490,
            "valid_h10": 0.054,
            "test_gold_at20": 0.092,
            "test_mrr_at20": 0.028159018759,
            "test_h10": 0.068,
            "avg_subgraph_size": 100,
            "note": "Soft support b050; no pruning and no gold injection.",
        },
        {
            "row_name": "fuzzy_retrieval_main",
            "valid_gold_at20": 0.070,
            "valid_mrr_at20": 0.021307588490,
            "valid_h10": 0.054,
            "test_gold_at20": 0.092,
            "test_mrr_at20": 0.028159018759,
            "test_h10": 0.068,
            "avg_subgraph_size": 55,
            "note": "Preserves soft ranking and compresses evidence subgraph.",
        },
    ]

    # Best model on test fuzzy.
    test_fuzzy_rows = [
        r for r in all_model_rows
        if r.get("split") == "test" and r.get("row_name") == "fuzzy_retrieval_main"
    ]
    best_test_fuzzy = None
    if test_fuzzy_rows:
        best_test_fuzzy = max(test_fuzzy_rows, key=lambda r: r.get("reviewer_safe_mrr_at20", -1))

    summary = {
        "decision": "WEEK23_PHARMKG_TRANSFER_CLOSEOUT_COMPLETE",
        "dataset": "PharmKG therapeutic-association proxy task",
        "target_relation": "T",
        "target_relation_normalized": "therapeutic_association_proxy",
        "candidate_universe": "drug_only_from_train_T_heads",
        "protocol": {
            "top_k": 20,
            "valid_test_gold_injection": False,
            "rank_absent_sentinel": 21,
            "reviewer_safe_rr": "1/rank if rank <= 20 else 0",
        },
        "candidate_level_results": candidate_level,
        "llama32_e2e_results": e2e_rows,
        "model_comparison_results": all_model_rows,
        "subgraph_summary": subgraph,
        "best_test_fuzzy_model": best_test_fuzzy,
        "paper_stance": {
            "role": "secondary transfer dataset",
            "main_claim": (
                "Soft support improves PharmKG top-20 ranking without valid/test gold injection; "
                "fuzzy retrieval preserves this gain while reducing the evidence subgraph from 100 to 55 triples."
            ),
            "e2e_claim": (
                "Across base LLMs, soft/fuzzy rows consistently improve reviewer-safe E2E MRR over backbone, "
                "but absolute E2E remains limited by candidate bottleneck and invalid free-form generation."
            ),
            "do_not_claim": [
                "Do not call relation T clinical indication.",
                "Do not claim Gold@20 improvement.",
                "Do not claim full-universe PharmKG KGC superiority.",
                "Do not claim fuzzy retrieval reduces shortcut rate on PharmKG.",
            ],
        },
    }

    save_json(summary, RESULT_DIR / "week23_pharmkg_closeout_summary.json")

    lines = []
    lines.append("# Week 23 Closeout — PharmKG Transfer and E2E Evaluation")
    lines.append("")
    lines.append("## 1. Decision")
    lines.append("")
    lines.append("**WEEK23_PHARMKG_TRANSFER_CLOSEOUT_COMPLETE**")
    lines.append("")
    lines.append("Week 23 successfully completed the PharmKG transfer study for FOG-RAG. The dataset is used as a secondary transfer benchmark, not as the primary dataset. The relation `T` is reported as `therapeutic_association_proxy`, not as clinical indication.")
    lines.append("")
    lines.append("## 2. Protocol")
    lines.append("")
    lines.append("- Task: `(? , T, disease)` head prediction.")
    lines.append("- Missing entity: drug/chemical.")
    lines.append("- Relation name for paper: `therapeutic_association_proxy`.")
    lines.append("- Candidate size: top-20.")
    lines.append("- Valid/test gold injection: **false**.")
    lines.append("- Reviewer-safe metric: `RR = 1/rank` if `rank <= 20`, otherwise `0`.")
    lines.append("- Rank-absent sentinel: `21`.")
    lines.append("")
    lines.append("## 3. Candidate-level transfer results")
    lines.append("")
    candidate_table_rows = []
    for r in candidate_level:
        candidate_table_rows.append([
            r["row_name"],
            f"{r['valid_gold_at20']:.3f}",
            f"{r['valid_mrr_at20']:.6f}",
            f"{r['valid_h10']:.3f}",
            f"{r['test_gold_at20']:.3f}",
            f"{r['test_mrr_at20']:.6f}",
            f"{r['test_h10']:.3f}",
            r["avg_subgraph_size"],
            r["note"],
        ])
    lines.append(md_table(
        ["Row", "Valid Gold@20", "Valid MRR@20", "Valid H@10", "Test Gold@20", "Test MRR@20", "Test H@10", "Avg subgraph", "Note"],
        candidate_table_rows,
    ))
    lines.append("")
    lines.append("**Interpretation.** `soft_support_raw` improves MRR@20 over `backbone_raw` on both valid and test without changing Gold@20. `fuzzy_retrieval_main` preserves the soft-support ranking and reduces the evidence subgraph from 100 to 55 triples.")
    lines.append("")
    lines.append("## 4. Llama-3.2-3B E2E reviewer-safe results")
    lines.append("")
    e2e_table_rows = []
    for split in ["valid", "test"]:
        for row_name in ["backbone_raw", "soft_support_raw", "fuzzy_retrieval_main"]:
            r = get_row(e2e_rows, split, row_name)
            if r is None:
                continue
            e2e_table_rows.append([
                split,
                row_name,
                f"{r['gold_at20']:.3f}",
                f"{r['candidate_mrr_at20']:.6f}",
                f"{r['reviewer_safe_mrr_at20']:.6f}",
                f"{r['reviewer_safe_hits1_at20']:.3f}",
                f"{r['reviewer_safe_hits3_at20']:.3f}",
                f"{r['reviewer_safe_hits10_at20']:.3f}",
                f"{r['pred_in_candidate_rate']:.3f}",
                f"{r['invalid_prediction_rate']:.3f}",
                r["rank21_count"],
            ])
    lines.append(md_table(
        ["Split", "Row", "Gold@20", "Cand MRR", "E2E MRR", "H@1", "H@3", "H@10", "Pred-in-cand", "Invalid", "Rank21"],
        e2e_table_rows,
    ))
    lines.append("")
    lines.append("**Interpretation.** On the locked test split, Llama-3.2-3B improves from `0.015575` E2E MRR@20 on `backbone_raw` to `0.020587` on `soft_support_raw` and `0.020971` on `fuzzy_retrieval_main`.")
    lines.append("")
    lines.append("## 5. Base LLM model comparison")
    lines.append("")
    model_table_rows = []
    for model in sorted(set(r.get("model_tag", "unknown") for r in all_model_rows)):
        for split in ["valid", "test"]:
            for row_name in ["backbone_raw", "soft_support_raw", "fuzzy_retrieval_main"]:
                rows = [
                    r for r in all_model_rows
                    if r.get("model_tag") == model and r.get("split") == split and r.get("row_name") == row_name
                ]
                if not rows:
                    continue
                r = rows[0]
                model_table_rows.append([
                    model,
                    split,
                    row_name,
                    f"{r['gold_at20']:.3f}",
                    f"{r['candidate_mrr_at20']:.6f}",
                    f"{r['reviewer_safe_mrr_at20']:.6f}",
                    f"{r['reviewer_safe_hits1_at20']:.3f}",
                    f"{r['reviewer_safe_hits3_at20']:.3f}",
                    f"{r['reviewer_safe_hits10_at20']:.3f}",
                    f"{r['pred_in_candidate_rate']:.3f}",
                    f"{r['invalid_prediction_rate']:.3f}",
                ])
    lines.append(md_table(
        ["Model", "Split", "Row", "Gold@20", "Cand MRR", "E2E MRR", "H@1", "H@3", "H@10", "Pred-in-cand", "Invalid"],
        model_table_rows,
    ))
    lines.append("")
    if best_test_fuzzy:
        lines.append(
            f"**Best test fuzzy model:** `{best_test_fuzzy['model_tag']}` with E2E MRR@20 = "
            f"`{best_test_fuzzy['reviewer_safe_mrr_at20']:.6f}`."
        )
    lines.append("")
    lines.append("**Interpretation.** Larger or biomedical-specific base LLMs did not necessarily improve E2E generation. Several 7B/8B base models produced repeated strings or candidate-list fragments, resulting in high invalid prediction rates. This supports reporting Llama-3.2-3B as the primary PharmKG E2E model and treating the other base models as diagnostic comparisons.")
    lines.append("")
    lines.append("## 6. Paper-ready statement")
    lines.append("")
    lines.append("> On the PharmKG therapeutic-association proxy task, soft support improves reviewer-safe top-20 ranking without valid/test gold injection. On the locked test split, candidate-level MRR@20 improves from 0.0205 to 0.0282, while fuzzy retrieval preserves this gain and reduces the retrieved evidence subgraph from 100 to 55 triples. In E2E LLM evaluation with Llama-3.2-3B, FOG-RAG improves reviewer-safe MRR@20 from 0.0156 to 0.0210. Additional base LLM comparisons show the same direction of improvement but also reveal a generation-format limitation: larger or biomedical-specific base LLMs often produce invalid candidate-list fragments rather than a single entity.")
    lines.append("")
    lines.append("## 7. What not to claim")
    lines.append("")
    lines.append("- Do **not** call PharmKG relation `T` a clinical indication relation.")
    lines.append("- Do **not** claim Gold@20 or candidate recall improvement.")
    lines.append("- Do **not** claim full-universe PharmKG KGC superiority.")
    lines.append("- Do **not** claim fuzzy retrieval reduces shortcut rate on PharmKG.")
    lines.append("- Do **not** use raw `infer.py` MRR as paper metric; use reviewer-safe MRR only.")
    lines.append("")
    lines.append("## 8. Final Week 23 status")
    lines.append("")
    lines.append("Week 23 is closed. PharmKG is ready to be used as a secondary transfer dataset in the paper. The main paper story remains PrimeKG Setting A, while PharmKG supports transferability and highlights remaining E2E generation limitations.")

    report_path = REPORT_DIR / "week23_pharmkg_closeout.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote JSON: {RESULT_DIR / 'week23_pharmkg_closeout_summary.json'}")
    print(f"[OK] wrote report: {report_path}")
    print("")
    print("Decision: WEEK23_PHARMKG_TRANSFER_CLOSEOUT_COMPLETE")


if __name__ == "__main__":
    main()