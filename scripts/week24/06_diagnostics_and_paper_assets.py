from __future__ import annotations

import json
import re
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Tuple


ROOT = Path(".").resolve()

FROZEN_VALID = ROOT / "results/week24/frozen_decode_test/primekg_e2e_final_table_valid.json"
FROZEN_TEST = ROOT / "results/week24/frozen_decode_test/primekg_e2e_final_table_test.json"

MODEL_SUMMARY = ROOT / "results/week24/model_compare/model_compare_reviewer_safe_summary.json"
MODEL_BEST = ROOT / "results/week24/model_compare/model_compare_best_model.json"
MODEL_ROOT = ROOT / "results/week24/model_compare"

READY_ROOT = ROOT / "dataset/setting_a/29_n2_e2e_infer_ready"

DIAG_DIR = ROOT / "results/week24/diagnostics"
ASSET_DIR = ROOT / "results/week24/paper_assets"
REPORT_MD = ROOT / "reports/week24/day6_e2e_diagnostics_and_paper_assets.md"

OUT_FAILURE = DIAG_DIR / "primekg_e2e_failure_analysis.json"
OUT_BUCKETS = DIAG_DIR / "primekg_generation_error_buckets.json"
OUT_CASES = DIAG_DIR / "primekg_case_samples.json"
OUT_INTERPRETATION = DIAG_DIR / "primekg_e2e_paper_interpretation.json"

OUT_E2E_TEX = ASSET_DIR / "primekg_e2e_table_latex.tex"
OUT_MODEL_TEX = ASSET_DIR / "primekg_model_compare_table_latex.tex"
OUT_RESULT_PARA = ASSET_DIR / "primekg_e2e_result_paragraph.md"
OUT_LIMIT_PARA = ASSET_DIR / "primekg_e2e_limitation_paragraph.md"
OUT_MODEL_PARA = ASSET_DIR / "primekg_model_compare_paragraph.md"

PRIMARY_MODEL = "llama3_2_3b"
METRIC_MODEL_CANDIDATES = ["llama3_8b", "medllama3_8b"]

ROWS = ["backbone_raw", "soft_support_raw", "retrieval_main"]
K = 20


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def latex_escape(x: Any) -> str:
    s = str(x)
    repl = {
        "\\": r"\textbackslash{}",
        "_": r"\_",
        "%": r"\%",
        "&": r"\&",
        "#": r"\#",
        "$": r"\$",
        "{": r"\{",
        "}": r"\}",
    }
    for a, b in repl.items():
        s = s.replace(a, b)
    return s


def norm_strict(x: Any) -> str:
    return str(x).strip()


def norm_loose(x: Any) -> str:
    x = "" if x is None else str(x)
    if "Answer:" in x:
        x = x.split("Answer:")[-1]
    x = x.strip()
    x = x.splitlines()[0].strip() if x.splitlines() else x
    x = x.strip().strip("'").strip('"').strip("`")
    x = re.sub(r"\s+", " ", x)
    return x.strip(" .,:;").lower()


def get_target(row: Dict[str, Any]) -> str:
    if "target" in row:
        return norm_strict(row["target"])
    if "output" in row:
        return norm_strict(row["output"])
    raise KeyError("Missing target/output")


def get_candidates(row: Dict[str, Any]) -> List[str]:
    return [norm_strict(x) for x in row["rank_entities"][:K]]


def gold_rank(row: Dict[str, Any]) -> Tuple[int, bool]:
    target = get_target(row)
    candidates = get_candidates(row)
    if target in candidates:
        return candidates.index(target) + 1, True
    return K + 1, False


def adjusted_rank(row: Dict[str, Any]) -> Tuple[int, bool]:
    target = get_target(row)
    pred = norm_strict(row.get("pred", ""))
    candidates = get_candidates(row)
    gr, present = gold_rank(row)

    if not present:
        return K + 1, False

    if pred == target:
        return 1, True

    ar = gr
    if pred not in set(candidates):
        ar += 1
    else:
        pred_pos = candidates.index(pred) + 1
        if pred_pos >= gr:
            ar += 1

    return min(ar, K + 1), True


def is_list_fragment(pred: str, candidates: List[str]) -> bool:
    p = str(pred)
    if len(p) > 120:
        return True
    if p.count(",") >= 2:
        return True
    if p.count("'") >= 4:
        return True
    if "####" in p:
        return True

    loose = norm_loose(p)
    hits = 0
    for c in candidates:
        cn = norm_loose(c)
        if cn and cn in loose:
            hits += 1

    return hits >= 3


def category(row: Dict[str, Any]) -> str:
    pred = norm_strict(row.get("pred", ""))
    target = get_target(row)
    candidates = get_candidates(row)

    if pred == "":
        return "empty_prediction"
    if pred == target:
        return "exact_target"
    if pred in set(candidates):
        if candidates and pred == candidates[0]:
            return "top1_copy"
        return "other_candidate"
    if is_list_fragment(pred, candidates):
        return "candidate_list_fragment"
    return "invalid_other"


def compact_case(row: Dict[str, Any], idx: int) -> Dict[str, Any]:
    gr, present = gold_rank(row)
    ar, _ = adjusted_rank(row)
    pred = norm_strict(row.get("pred", ""))
    return {
        "row_index": row.get("row_index", idx),
        "query_entity": row.get("query_entity"),
        "target": get_target(row),
        "pred": pred,
        "gold_rank": gr,
        "gold_present": bool(present),
        "adjusted_rank": ar,
        "category": category(row),
        "top5": row.get("rank_entities", [])[:5],
    }


def load_prediction(model_tag: str, split: str, row_name: str) -> List[Dict[str, Any]]:
    path = MODEL_ROOT / model_tag / "predictions" / f"prediction_{split}_{row_name}.json"
    obj = load_json(path)
    rows = obj["prediction"]
    if len(rows) != 500:
        raise RuntimeError(f"{path} has {len(rows)} rows, expected 500")
    return rows


def get_model_row(summary_rows: List[Dict[str, Any]], model: str, split: str, row: str) -> Dict[str, Any]:
    matches = [
        r for r in summary_rows
        if r["model_tag"] == model and r["split"] == split and r["row_name"] == row
    ]
    if not matches:
        raise KeyError(f"Missing model row {model}/{split}/{row}")
    return matches[0]


def get_frozen_row(rows: List[Dict[str, Any]], row_name: str) -> Dict[str, Any]:
    matches = [r for r in rows if r["row_name"] == row_name]
    if not matches:
        raise KeyError(row_name)
    return matches[0]


def build_failure_buckets(model_tag: str, split: str, row_name: str, max_cases: int = 10) -> Dict[str, Any]:
    rows = load_prediction(model_tag, split, row_name)

    buckets = {
        "raw_bottleneck_failure": [],
        "candidate_present_but_generation_fail": [],
        "exact_target_success": [],
        "top1_copy": [],
        "other_candidate": [],
        "invalid_generation": [],
        "candidate_list_fragment": [],
    }

    counts = {k: 0 for k in buckets}

    for i, row in enumerate(rows):
        gr, present = gold_rank(row)
        ar, _ = adjusted_rank(row)
        cat = category(row)
        case = compact_case(row, i)

        if not present:
            counts["raw_bottleneck_failure"] += 1
            if len(buckets["raw_bottleneck_failure"]) < max_cases:
                buckets["raw_bottleneck_failure"].append(case)

        if present and ar > gr:
            counts["candidate_present_but_generation_fail"] += 1
            if len(buckets["candidate_present_but_generation_fail"]) < max_cases:
                buckets["candidate_present_but_generation_fail"].append(case)

        if cat == "exact_target":
            counts["exact_target_success"] += 1
            if len(buckets["exact_target_success"]) < max_cases:
                buckets["exact_target_success"].append(case)

        if cat == "top1_copy":
            counts["top1_copy"] += 1
            if len(buckets["top1_copy"]) < max_cases:
                buckets["top1_copy"].append(case)

        if cat == "other_candidate":
            counts["other_candidate"] += 1
            if len(buckets["other_candidate"]) < max_cases:
                buckets["other_candidate"].append(case)

        if cat in {"invalid_other", "empty_prediction"}:
            counts["invalid_generation"] += 1
            if len(buckets["invalid_generation"]) < max_cases:
                buckets["invalid_generation"].append(case)

        if cat == "candidate_list_fragment":
            counts["candidate_list_fragment"] += 1
            if len(buckets["candidate_list_fragment"]) < max_cases:
                buckets["candidate_list_fragment"].append(case)

    rates = {k + "_rate": round(v / len(rows), 8) for k, v in counts.items()}

    return {
        "model_tag": model_tag,
        "split": split,
        "row_name": row_name,
        "num_rows": len(rows),
        "counts": counts,
        "rates": rates,
        "cases": buckets,
    }


def retrieval_cleaner_graph_analysis(split: str = "test") -> Dict[str, Any]:
    soft = load_json(READY_ROOT / "soft_support_raw" / f"{split}.json")
    retr = load_json(READY_ROOT / "retrieval_main" / f"{split}.json")

    if len(soft) != len(retr):
        raise RuntimeError("soft/retr row length mismatch")

    same_candidate_order = 0
    same_rank = 0
    smaller_graph = 0
    same_rank_cleaner = 0
    reductions = []
    cases = []

    for i, (s, r) in enumerate(zip(soft, retr)):
        same_order = s["rank_entities_id"] == r["rank_entities_id"]
        same_candidate_order += int(same_order)

        s_rank = int(s["rank"])
        r_rank = int(r["rank"])
        same_r = s_rank == r_rank
        same_rank += int(same_r)

        s_size = len(s.get("subgraph", []))
        r_size = len(r.get("subgraph", []))
        reduction = s_size - r_size
        reductions.append(reduction)

        is_smaller = r_size < s_size
        smaller_graph += int(is_smaller)

        if same_r and is_smaller:
            same_rank_cleaner += 1
            if len(cases) < 10:
                cases.append({
                    "row_index": r.get("row_index", i),
                    "query_entity": r.get("query_entity"),
                    "gold_entity": r.get("gold_entity"),
                    "rank": r_rank,
                    "soft_subgraph_size": s_size,
                    "retrieval_subgraph_size": r_size,
                    "subgraph_reduction": reduction,
                    "top5": r.get("rank_entities", [])[:5],
                })

    n = len(soft)
    return {
        "split": split,
        "num_rows": n,
        "same_candidate_order_rate": round(same_candidate_order / n, 8),
        "same_rank_rate": round(same_rank / n, 8),
        "retrieval_smaller_graph_rate": round(smaller_graph / n, 8),
        "same_rank_cleaner_graph_count": same_rank_cleaner,
        "same_rank_cleaner_graph_rate": round(same_rank_cleaner / n, 8),
        "avg_subgraph_reduction": round(mean(reductions), 8),
        "min_subgraph_reduction": min(reductions),
        "max_subgraph_reduction": max(reductions),
        "cases": cases,
    }


def make_e2e_latex(test_rows: List[Dict[str, Any]]) -> str:
    display = {
        "backbone_raw": "Backbone raw",
        "soft_support_raw": "Soft support",
        "retrieval_main": "FOG-RAG retrieval",
    }

    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(r"\centering")
    lines.append(r"\small")
    lines.append(r"\begin{tabular}{lrrrrrr}")
    lines.append(r"\hline")
    lines.append(r"Row & Gold@20 & Cand. MRR & E2E MRR & H@3 & H@10 & Avg. graph \\")
    lines.append(r"\hline")
    for row_name in ROWS:
        r = get_frozen_row(test_rows, row_name)
        lines.append(
            f"{latex_escape(display[row_name])} & "
            f"{r['gold_at20']:.3f} & "
            f"{r['candidate_mrr_at20']:.6f} & "
            f"{r['reviewer_safe_e2e_mrr_at20']:.6f} & "
            f"{r['reviewer_safe_e2e_hits3_at20']:.3f} & "
            f"{r['reviewer_safe_e2e_hits10_at20']:.3f} & "
            f"{r['avg_subgraph_size']:.2f} \\\\"
        )
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    lines.append(r"\caption{PrimeKG reviewer-safe end-to-end results with the primary Llama-3.2-3B base model.}")
    lines.append(r"\label{tab:primekg-e2e}")
    lines.append(r"\end{table}")
    return "\n".join(lines) + "\n"


def make_model_latex(summary_rows: List[Dict[str, Any]]) -> str:
    rows = [
        r for r in summary_rows
        if r["split"] == "test" and r["row_name"] == "retrieval_main"
    ]
    rows = sorted(rows, key=lambda x: x["model_tag"])

    display = {
        "llama3_2_3b": "Llama-3.2-3B",
        "llama3_8b": "Llama-3-8B",
        "medllama3_8b": "MedLlama-3-8B",
    }

    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(r"\centering")
    lines.append(r"\small")
    lines.append(r"\begin{tabular}{lrrrrr}")
    lines.append(r"\hline")
    lines.append(r"Base LLM & E2E MRR & H@10 & Pred-in-cand. & Invalid & Top1-copy \\")
    lines.append(r"\hline")
    for r in rows:
        lines.append(
            f"{latex_escape(display.get(r['model_tag'], r['model_tag']))} & "
            f"{r['reviewer_safe_e2e_mrr_at20']:.6f} & "
            f"{r['reviewer_safe_e2e_hits10_at20']:.3f} & "
            f"{r['pred_in_candidate_rate']:.3f} & "
            f"{r['invalid_prediction_rate']:.3f} & "
            f"{r['top1_copy_rate']:.3f} \\\\"
        )
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    lines.append(r"\caption{PrimeKG base-LLM comparison on the FOG-RAG retrieval row. Higher MRR for 8B models is accompanied by a top-1-copy collapse.}")
    lines.append(r"\label{tab:primekg-model-comparison}")
    lines.append(r"\end{table}")
    return "\n".join(lines) + "\n"


def main() -> None:
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)

    frozen_valid = load_json(FROZEN_VALID)
    frozen_test = load_json(FROZEN_TEST)
    model_summary_obj = load_json(MODEL_SUMMARY)
    model_summary_rows = model_summary_obj["summary_rows"]
    model_best = load_json(MODEL_BEST)

    # Main rows for primary Llama-3.2-3B
    primary_test = {
        row_name: get_frozen_row(frozen_test, row_name)
        for row_name in ROWS
    }

    # Model-comparison retrieval rows
    retrieval_test_rows = [
        r for r in model_summary_rows
        if r["split"] == "test" and r["row_name"] == "retrieval_main"
    ]

    metric_best = max(
        retrieval_test_rows,
        key=lambda x: x["reviewer_safe_e2e_mrr_at20"],
    )

    top1_collapsed = [
        r["model_tag"]
        for r in retrieval_test_rows
        if r["top1_copy_rate"] >= 0.90
    ]

    stable_primary = get_model_row(model_summary_rows, PRIMARY_MODEL, "test", "retrieval_main")

    model_selection = {
        "metric_best_model": metric_best["model_tag"],
        "metric_best_e2e_mrr_at20": metric_best["reviewer_safe_e2e_mrr_at20"],
        "primary_e2e_model": PRIMARY_MODEL,
        "primary_e2e_mrr_at20": stable_primary["reviewer_safe_e2e_mrr_at20"],
        "diagnostic_top1_copy_models": top1_collapsed,
        "selection_rationale": (
            "Llama-3-8B and MedLlama-3-8B reach candidate-ceiling MRR by copying the top-ranked "
            "candidate almost always. Llama-3.2-3B is kept as the primary E2E model because it avoids "
            "this degenerate top-1-copy behavior while preserving the FOG-RAG improvement trend."
        ),
    }

    # Failure buckets
    buckets = {
        "primary_model_test_retrieval_main": build_failure_buckets(PRIMARY_MODEL, "test", "retrieval_main"),
        "metric_best_model_test_retrieval_main": build_failure_buckets(metric_best["model_tag"], "test", "retrieval_main"),
        "llama3_8b_test_retrieval_main": build_failure_buckets("llama3_8b", "test", "retrieval_main"),
        "medllama3_8b_test_retrieval_main": build_failure_buckets("medllama3_8b", "test", "retrieval_main"),
    }

    cleaner = {
        "valid": retrieval_cleaner_graph_analysis("valid"),
        "test": retrieval_cleaner_graph_analysis("test"),
    }

    failure_analysis = {
        "decision": "PRIMEKG_E2E_DIAGNOSTICS_BUILT",
        "primary_model": PRIMARY_MODEL,
        "main_row": "retrieval_main",
        "primary_test_metrics": stable_primary,
        "model_selection": model_selection,
        "retrieval_cleaner_graph_analysis": cleaner,
        "primary_failure_buckets_summary": {
            "counts": buckets["primary_model_test_retrieval_main"]["counts"],
            "rates": buckets["primary_model_test_retrieval_main"]["rates"],
        },
        "metric_best_failure_buckets_summary": {
            "model_tag": metric_best["model_tag"],
            "counts": buckets["metric_best_model_test_retrieval_main"]["counts"],
            "rates": buckets["metric_best_model_test_retrieval_main"]["rates"],
        },
    }

    interpretation = {
        "decision": "PRIMEKG_E2E_PAPER_ASSETS_READY",
        "paper_main_row": "soft_support_fuzzy_retrieval_main",
        "primary_e2e_model": PRIMARY_MODEL,
        "metric_best_model": metric_best["model_tag"],
        "main_claim": (
            "On PrimeKG Setting A, soft support provides the main ranking gain over the raw DrKGC-style "
            "backbone, while fuzzy retrieval preserves the gain and substantially reduces the retrieved "
            "evidence subgraph."
        ),
        "e2e_claim": (
            f"With Llama-3.2-3B, FOG-RAG retrieval improves locked-test reviewer-safe E2E MRR@20 from "
            f"{primary_test['backbone_raw']['reviewer_safe_e2e_mrr_at20']:.6f} to "
            f"{primary_test['retrieval_main']['reviewer_safe_e2e_mrr_at20']:.6f}, while reducing the "
            f"average graph size from {primary_test['soft_support_raw']['avg_subgraph_size']:.2f} to "
            f"{primary_test['retrieval_main']['avg_subgraph_size']:.2f} triples."
        ),
        "model_comparison_claim": (
            "Larger 8B base models achieve higher adjusted E2E MRR but collapse into copying the first "
            "candidate, so they are reported as diagnostic candidate-order-following runs rather than "
            "the primary generative E2E result."
        ),
        "limitations": [
            "Raw top-20 candidate bottleneck remains the dominant limitation.",
            "E2E Hits@1 remains weak for the primary Llama-3.2-3B model.",
            "Some larger base models can inflate adjusted E2E MRR by copying top-1 candidates.",
            "Raw infer.py metrics should not be used for paper-facing reporting.",
        ],
        "do_not_claim": [
            "Do not claim FOG-RAG improves Gold@20.",
            "Do not claim Llama-3-8B reasoning is better solely from E2E MRR.",
            "Do not hide top1-copy rates in model comparison.",
            "Do not use instruct models as the main protocol.",
        ],
    }

    save_json(OUT_FAILURE, failure_analysis)
    save_json(OUT_BUCKETS, buckets)
    save_json(OUT_CASES, {
        "primary_model_cases": buckets["primary_model_test_retrieval_main"]["cases"],
        "metric_best_model_cases": buckets["metric_best_model_test_retrieval_main"]["cases"],
        "retrieval_cleaner_graph_cases": cleaner["test"]["cases"],
    })
    save_json(OUT_INTERPRETATION, interpretation)

    e2e_tex = make_e2e_latex(frozen_test)
    model_tex = make_model_latex(model_summary_rows)

    write_text(OUT_E2E_TEX, e2e_tex)
    write_text(OUT_MODEL_TEX, model_tex)

    result_para = (
        "On the locked PrimeKG test split, soft-support re-ranking improves the reviewer-safe "
        f"candidate MRR@20 from {primary_test['backbone_raw']['candidate_mrr_at20']:.6f} to "
        f"{primary_test['soft_support_raw']['candidate_mrr_at20']:.6f}. In end-to-end generation with "
        f"Llama-3.2-3B, the raw backbone obtains MRR@20={primary_test['backbone_raw']['reviewer_safe_e2e_mrr_at20']:.6f}, "
        f"while soft support reaches {primary_test['soft_support_raw']['reviewer_safe_e2e_mrr_at20']:.6f}. "
        f"The FOG-RAG retrieval row preserves this E2E performance "
        f"({primary_test['retrieval_main']['reviewer_safe_e2e_mrr_at20']:.6f}) while reducing the average "
        f"evidence subgraph from {primary_test['soft_support_raw']['avg_subgraph_size']:.2f} to "
        f"{primary_test['retrieval_main']['avg_subgraph_size']:.2f} triples."
    )

    limit_para = (
        "The main remaining limitation is not the fuzzy retrieval stage but the upstream candidate and "
        "generation bottleneck. Gold entities are absent from the top-20 list in many queries, and even "
        "when the gold is present, the base LLM may generate a plausible but incorrect candidate. "
        "In model comparison, Llama-3-8B and MedLlama-3-8B reach candidate-ceiling MRR by copying the "
        "top-ranked candidate almost always, which motivates reporting top1-copy diagnostics alongside "
        "reviewer-safe E2E metrics."
    )

    model_para = (
        "Model comparison shows that larger base LLMs do not necessarily provide better biomedical "
        "reasoning in this constrained generation setup. Llama-3-8B and MedLlama-3-8B obtain the highest "
        f"test retrieval-main adjusted MRR@20 ({metric_best['reviewer_safe_e2e_mrr_at20']:.6f}), but their "
        "top1-copy rate is 1.0 on the main row. Therefore, we treat them as diagnostic candidate-order-"
        "following runs and keep Llama-3.2-3B as the primary E2E model."
    )

    write_text(OUT_RESULT_PARA, result_para + "\n")
    write_text(OUT_LIMIT_PARA, limit_para + "\n")
    write_text(OUT_MODEL_PARA, model_para + "\n")

    # Markdown report
    lines = []
    lines.append("# Week 24 Day 6  PrimeKG E2E Diagnostics and Paper Assets")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append("**PRIMEKG_E2E_PAPER_ASSETS_READY**")
    lines.append("")
    lines.append("## Model-selection interpretation")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(model_selection, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## Primary E2E result")
    lines.append("")
    lines.append("| Row | Gold@20 | Cand MRR | E2E MRR | H@3 | H@10 | Pred-in-cand | Invalid | Top1-copy | Avg graph |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row_name in ROWS:
        r = primary_test[row_name]
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
    lines.append("")
    lines.append("## Retrieval cleaner-graph diagnostics")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(cleaner, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## Failure bucket summary")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(failure_analysis["primary_failure_buckets_summary"], ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## Paper result paragraph")
    lines.append("")
    lines.append(result_para)
    lines.append("")
    lines.append("## Limitation paragraph")
    lines.append("")
    lines.append(limit_para)
    lines.append("")
    lines.append("## Model comparison paragraph")
    lines.append("")
    lines.append(model_para)
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    for p in [
        OUT_FAILURE,
        OUT_BUCKETS,
        OUT_CASES,
        OUT_INTERPRETATION,
        OUT_E2E_TEX,
        OUT_MODEL_TEX,
        OUT_RESULT_PARA,
        OUT_LIMIT_PARA,
        OUT_MODEL_PARA,
    ]:
        lines.append(f"- `{p}`")

    write_text(REPORT_MD, "\n".join(lines) + "\n")

    print("decision = PRIMEKG_E2E_PAPER_ASSETS_READY")
    print(f"wrote failure = {OUT_FAILURE}")
    print(f"wrote buckets = {OUT_BUCKETS}")
    print(f"wrote cases = {OUT_CASES}")
    print(f"wrote interpretation = {OUT_INTERPRETATION}")
    print(f"wrote e2e latex = {OUT_E2E_TEX}")
    print(f"wrote model latex = {OUT_MODEL_TEX}")
    print(f"wrote result paragraph = {OUT_RESULT_PARA}")
    print(f"wrote limitation paragraph = {OUT_LIMIT_PARA}")
    print(f"wrote model paragraph = {OUT_MODEL_PARA}")
    print(f"wrote report = {REPORT_MD}")
    print("")
    print("model_selection =", json.dumps(model_selection, ensure_ascii=False, indent=2))
    print("")
    print("primary_failure_counts =", failure_analysis["primary_failure_buckets_summary"]["counts"])
    print("retrieval_cleaner_test =", json.dumps(cleaner["test"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()