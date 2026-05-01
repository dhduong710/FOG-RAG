from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(".").resolve()

OUT_JSON = ROOT / "results/week24/week24_closeout.json"
OUT_DECISION = ROOT / "results/week24/week24_go_decision.json"
OUT_MD = ROOT / "reports/week24/week24_closeout.md"

PRIMEKG_E2E_TEST = ROOT / "results/week24/frozen_decode_test/primekg_e2e_final_table_test.json"
PRIMEKG_MODEL_BEST = ROOT / "results/week24/model_compare/model_compare_best_model.json"
PRIMEKG_INTERPRET = ROOT / "results/week24/diagnostics/primekg_e2e_paper_interpretation.json"
PRIMEKG_FAILURE = ROOT / "results/week24/diagnostics/primekg_e2e_failure_analysis.json"

PHARMKG_TEST = ROOT / "results/week24/pharmkg_frozen_model_compare/pharmkg_model_compare_table_test.json"
PHARMKG_BEST = ROOT / "results/week24/pharmkg_frozen_model_compare/pharmkg_model_compare_best_model.json"
PHARMKG_RESULT_PARA = ROOT / "results/week24/pharmkg_frozen_model_compare/paper_assets/pharmkg_result_paragraph.md"
PHARMKG_LIMIT_PARA = ROOT / "results/week24/pharmkg_frozen_model_compare/paper_assets/pharmkg_limitation_paragraph.md"


def load_json(path: Path, required: bool = True) -> Any:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Missing required file: {path}")
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: Path, required: bool = True) -> str:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Missing required file: {path}")
        return ""
    return path.read_text(encoding="utf-8").strip()


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def get_row(rows: List[Dict[str, Any]], row_name: str, model_tag: str | None = None) -> Dict[str, Any]:
    for r in rows:
        if r.get("row_name") == row_name and (model_tag is None or r.get("model_tag") == model_tag):
            return r
    raise KeyError(f"Missing row={row_name}, model={model_tag}")


def fmt(x: float, n: int = 6) -> str:
    return f"{float(x):.{n}f}"


def md_table_primekg(rows: List[Dict[str, Any]]) -> str:
    lines = []
    lines.append("| Row | Gold@20 | Cand MRR | E2E MRR | H@3 | H@10 | Pred-in-cand | Invalid | Top1-copy | Avg graph |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row_name in ["backbone_raw", "soft_support_raw", "retrieval_main"]:
        r = get_row(rows, row_name)
        lines.append(
            f"| {row_name} | {r['gold_at20']:.3f} | {r['candidate_mrr_at20']:.6f} | "
            f"{r['reviewer_safe_e2e_mrr_at20']:.6f} | "
            f"{r['reviewer_safe_e2e_hits3_at20']:.3f} | "
            f"{r['reviewer_safe_e2e_hits10_at20']:.3f} | "
            f"{r['pred_in_candidate_rate']:.3f} | "
            f"{r['invalid_prediction_rate']:.3f} | "
            f"{r['top1_copy_rate']:.3f} | "
            f"{r['avg_subgraph_size']:.2f} |"
        )
    return "\n".join(lines)


def md_table_pharmkg(rows: List[Dict[str, Any]]) -> str:
    primary = [r for r in rows if r["model_tag"] == "llama3_2_3b"]
    lines = []
    lines.append("| Row | Gold@20 | Cand MRR | E2E MRR | H@3 | H@10 | Pred-in-cand | Invalid | List-frag | Avg graph |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row_name in ["backbone_raw", "soft_support_raw", "fuzzy_retrieval_main"]:
        r = get_row(primary, row_name)
        lines.append(
            f"| {row_name} | {r['gold_at20']:.3f} | {r['candidate_mrr_at20']:.6f} | "
            f"{r['reviewer_safe_e2e_mrr_at20']:.6f} | "
            f"{r['reviewer_safe_e2e_hits3_at20']:.3f} | "
            f"{r['reviewer_safe_e2e_hits10_at20']:.3f} | "
            f"{r['pred_in_candidate_rate']:.3f} | "
            f"{r['invalid_prediction_rate']:.3f} | "
            f"{r['candidate_list_fragment_rate']:.3f} | "
            f"{r['avg_subgraph_size']:.2f} |"
        )
    return "\n".join(lines)


def main() -> None:
    primekg_test = load_json(PRIMEKG_E2E_TEST)
    primekg_best = load_json(PRIMEKG_MODEL_BEST)
    primekg_interpret = load_json(PRIMEKG_INTERPRET)
    primekg_failure = load_json(PRIMEKG_FAILURE)

    pharmkg_test = load_json(PHARMKG_TEST)
    pharmkg_best = load_json(PHARMKG_BEST)
    pharmkg_result_para = load_text(PHARMKG_RESULT_PARA)
    pharmkg_limit_para = load_text(PHARMKG_LIMIT_PARA)

    prime_b = get_row(primekg_test, "backbone_raw")
    prime_s = get_row(primekg_test, "soft_support_raw")
    prime_r = get_row(primekg_test, "retrieval_main")

    pharm_b = get_row([r for r in pharmkg_test if r["model_tag"] == "llama3_2_3b"], "backbone_raw")
    pharm_s = get_row([r for r in pharmkg_test if r["model_tag"] == "llama3_2_3b"], "soft_support_raw")
    pharm_f = get_row([r for r in pharmkg_test if r["model_tag"] == "llama3_2_3b"], "fuzzy_retrieval_main")

    decision = {
        "decision": "GO_PAPER_E2E_WITH_LIMITATION",
        "reason": (
            "PrimeKG E2E and PharmKG transfer both show reviewer-safe FOG-RAG improvements over the "
            "DrKGC-style raw backbone, and fuzzy retrieval preserves the soft-support gains while reducing "
            "subgraph size. However, unconstrained generation and top-1-copy behavior remain important limitations."
        ),
        "primary_dataset": "PrimeKG Setting A",
        "secondary_dataset": "PharmKG therapeutic_association_proxy",
        "primary_e2e_model": "llama3_2_3b",
        "main_primekg_row": "retrieval_main",
        "main_pharmkg_row": "fuzzy_retrieval_main",
        "paper_positioning": {
            "PrimeKG": "main result",
            "PharmKG": "secondary transfer evidence",
            "model_comparison": "diagnostic, with Top1-copy reported",
        },
        "week25_recommendation": {
            "theme": "sensitivity and robustness experiments",
            "experiments": [
                "Rule sensitivity: hard-coded rules vs no-rules vs random-rule negative control",
                "Question-template sensitivity for indication prompts",
                "Small noise robustness if time permits",
            ],
            "goal": "supporting evidence, not a new novelty claim",
        },
    }

    closeout = {
        "decision": decision,
        "primekg_final": {
            "backbone_raw": prime_b,
            "soft_support_raw": prime_s,
            "retrieval_main": prime_r,
            "delta_retrieval_minus_backbone_e2e": round(
                prime_r["reviewer_safe_e2e_mrr_at20"] - prime_b["reviewer_safe_e2e_mrr_at20"], 8
            ),
            "delta_retrieval_minus_soft_e2e": round(
                prime_r["reviewer_safe_e2e_mrr_at20"] - prime_s["reviewer_safe_e2e_mrr_at20"], 8
            ),
            "subgraph_reduction_soft_to_retrieval": round(
                prime_s["avg_subgraph_size"] - prime_r["avg_subgraph_size"], 8
            ),
        },
        "primekg_model_comparison": {
            "metric_best_model": primekg_best["best_test_retrieval_main"]["model_tag"],
            "primary_e2e_model": primekg_interpret["primary_e2e_model"],
            "diagnostic_top1_copy_models": primekg_interpret.get("diagnostic_top1_copy_models", []),
            "trend_checks": primekg_best["trend_checks_by_model"],
        },
        "primekg_diagnostics": {
            "primary_failure_buckets": primekg_failure["primary_failure_buckets_summary"],
            "retrieval_cleaner_graph_analysis": primekg_failure["retrieval_cleaner_graph_analysis"]["test"],
        },
        "pharmkg_final": {
            "backbone_raw": pharm_b,
            "soft_support_raw": pharm_s,
            "fuzzy_retrieval_main": pharm_f,
            "delta_fuzzy_minus_backbone_e2e": round(
                pharm_f["reviewer_safe_e2e_mrr_at20"] - pharm_b["reviewer_safe_e2e_mrr_at20"], 8
            ),
            "delta_fuzzy_minus_soft_e2e": round(
                pharm_f["reviewer_safe_e2e_mrr_at20"] - pharm_s["reviewer_safe_e2e_mrr_at20"], 8
            ),
            "subgraph_reduction_soft_to_fuzzy": round(
                pharm_s["avg_subgraph_size"] - pharm_f["avg_subgraph_size"], 8
            ),
        },
        "pharmkg_model_comparison": {
            "primary_e2e_model": pharmkg_best["primary_e2e_model"],
            "metric_best_test_fuzzy": pharmkg_best["metric_best_test_fuzzy"]["model_tag"],
            "trend_checks": pharmkg_best["trend_checks_by_model"],
        },
        "paper_assets": {
            "primekg_e2e_table": "results/week24/paper_assets/primekg_e2e_table_latex.tex",
            "primekg_model_table": "results/week24/paper_assets/primekg_model_compare_table_latex.tex",
            "pharmkg_e2e_table": "results/week24/pharmkg_frozen_model_compare/paper_assets/pharmkg_e2e_table_latex.tex",
            "pharmkg_model_table": "results/week24/pharmkg_frozen_model_compare/paper_assets/pharmkg_model_compare_table_latex.tex",
        },
    }

    save_json(OUT_JSON, closeout)
    save_json(OUT_DECISION, decision)

    lines = []
    lines.append("# Week 24 Closeout — PrimeKG and PharmKG E2E Finalization")
    lines.append("")
    lines.append("## Final decision")
    lines.append("")
    lines.append("**GO_PAPER_E2E_WITH_LIMITATION**")
    lines.append("")
    lines.append(decision["reason"])
    lines.append("")
    lines.append("## 1. PrimeKG final E2E result")
    lines.append("")
    lines.append("Primary E2E model: **Llama-3.2-3B**")
    lines.append("")
    lines.append(md_table_primekg(primekg_test))
    lines.append("")
    lines.append(
        f"PrimeKG locked-test E2E MRR improves from `{prime_b['reviewer_safe_e2e_mrr_at20']:.6f}` "
        f"on `backbone_raw` to `{prime_r['reviewer_safe_e2e_mrr_at20']:.6f}` on `retrieval_main`. "
        f"The retrieved evidence graph is reduced from `{prime_s['avg_subgraph_size']:.2f}` to "
        f"`{prime_r['avg_subgraph_size']:.2f}` triples."
    )
    lines.append("")
    lines.append("## 2. PrimeKG model-comparison interpretation")
    lines.append("")
    lines.append(f"- Metric-best model: `{primekg_best['best_test_retrieval_main']['model_tag']}`")
    lines.append(f"- Primary paper E2E model: `{primekg_interpret['primary_e2e_model']}`")
    lines.append("- Larger 8B models are diagnostic because they reach candidate-ceiling behavior through top-1-copy.")
    lines.append("- Model comparison tables must include `Top1-copy`.")
    lines.append("")
    lines.append("## 3. PrimeKG retrieval diagnostics")
    lines.append("")
    cleaner = primekg_failure["retrieval_cleaner_graph_analysis"]["test"]
    lines.append(f"- Same candidate order rate: `{cleaner['same_candidate_order_rate']}`")
    lines.append(f"- Same rank cleaner graph count: `{cleaner['same_rank_cleaner_graph_count']}` / 500")
    lines.append(f"- Average subgraph reduction: `{cleaner['avg_subgraph_reduction']}` triples")
    lines.append("")
    lines.append("## 4. PharmKG secondary transfer result")
    lines.append("")
    lines.append("Primary E2E model: **Llama-3.2-3B**")
    lines.append("")
    lines.append(md_table_pharmkg(pharmkg_test))
    lines.append("")
    lines.append(pharmkg_result_para)
    lines.append("")
    lines.append("## 5. PharmKG limitation")
    lines.append("")
    lines.append(pharmkg_limit_para)
    lines.append("")
    lines.append("## 6. What to claim")
    lines.append("")
    lines.append("- FOG-RAG improves reviewer-safe E2E MRR over the DrKGC-style raw backbone on PrimeKG.")
    lines.append("- Soft support provides the main ranking gain.")
    lines.append("- Fuzzy retrieval preserves the soft-support gain while substantially reducing subgraph size.")
    lines.append("- PharmKG supports transferability under a stricter secondary benchmark.")
    lines.append("- Larger/base biomedical models need diagnostics because top-1-copy and invalid generation can distort interpretation.")
    lines.append("")
    lines.append("## 7. What not to claim")
    lines.append("")
    lines.append("- Do not claim FOG-RAG improves Gold@20.")
    lines.append("- Do not claim full-universe PharmKG superiority.")
    lines.append("- Do not call PharmKG relation `T` a clinical indication label.")
    lines.append("- Do not select Llama-3-8B as the main E2E model solely because adjusted MRR is highest.")
    lines.append("- Do not use raw `infer.py` MRR in the paper.")
    lines.append("")
    lines.append("## 8. Week 25 recommendation")
    lines.append("")
    lines.append("Week 25 should be a sensitivity/robustness week, not a new novelty week:")
    lines.append("")
    lines.append("1. **Rule sensitivity**: hard-coded rules vs no-rules vs random-rule negative control.")
    lines.append("2. **Question-template sensitivity**: indication prompt variants.")
    lines.append("3. **Small noise robustness**: perturb candidate order/support scores/subgraph edges lightly if time permits.")
    lines.append("")
    lines.append("Expected Week 25 output: robustness table + appendix-ready sensitivity paragraph.")
    lines.append("")
    lines.append("## 9. Next action")
    lines.append("")
    lines.append("Proceed to Week 25 only after saving this closeout and backing up Week 24 results.")

    write_text(OUT_MD, "\n".join(lines) + "\n")

    print("decision = GO_PAPER_E2E_WITH_LIMITATION")
    print(f"wrote closeout_json = {OUT_JSON}")
    print(f"wrote go_decision = {OUT_DECISION}")
    print(f"wrote report = {OUT_MD}")
    print("")
    print("PrimeKG retrieval_main E2E =", prime_r["reviewer_safe_e2e_mrr_at20"])
    print("PrimeKG retrieval_main avg_graph =", prime_r["avg_subgraph_size"])
    print("PharmKG fuzzy_retrieval_main E2E =", pharm_f["reviewer_safe_e2e_mrr_at20"])
    print("PharmKG fuzzy_retrieval_main avg_graph =", pharm_f["avg_subgraph_size"])
    print("")
    print("Week25 recommended experiments:")
    for x in decision["week25_recommendation"]["experiments"]:
        print("-", x)


if __name__ == "__main__":
    main()