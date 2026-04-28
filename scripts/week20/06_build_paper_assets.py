from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(".").resolve()

# Inputs
W19_MAIN = ROOT / "results/week19/test_main_table.json"
W19_ABL = ROOT / "results/week19/test_ablation.json"
W19_CASES = ROOT / "results/week19/test_case_shortlist.json"
W19_GO = ROOT / "results/week19/week19_go_decision.json"

W20_E2E_MAIN = ROOT / "results/week20/e2e_main_table.json"
W20_E2E_ABL = ROOT / "results/week20/e2e_ablation.json"

# Optional predictions for richer case pack
PRED_BACKBONE = ROOT / "results/week20/prediction_test_backbone_raw_e2e.json"
PRED_SOFT = ROOT / "results/week20/prediction_test_soft_support_raw_e2e.json"
PRED_RETR = ROOT / "results/week20/prediction_test_retrieval_main_e2e.json"

OUT_DIR = ROOT / "results/week20/paper_assets"
TABLES_MANIFEST = ROOT / "results/week20/paper_tables_manifest.json"
FIGURES_MANIFEST = ROOT / "results/week20/paper_figures_manifest.json"
CASE_PACK = ROOT / "results/week20/paper_case_pack.json"
SNIPPETS_MD = ROOT / "results/week20/paper_interpretation_snippets.md"
REPORT_MD = ROOT / "reports/week20/day6_figures_cases_assets.md"


def load_json(path: Path, required: bool = True) -> Any:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Missing required file: {path}")
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


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


def fmt(x: Any) -> str:
    if isinstance(x, float):
        return f"{x:.6f}"
    return str(x)


def write_latex_table(path: Path, rows: List[Dict[str, Any]], caption: str, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("% Empty table\n", encoding="utf-8")
        return

    cols = list(rows[0].keys())
    colspec = "l" * len(cols)

    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(r"\centering")
    lines.append(r"\small")
    lines.append(rf"\begin{{tabular}}{{{colspec}}}")
    lines.append(r"\hline")
    lines.append(" & ".join(latex_escape(c) for c in cols) + r" \\")
    lines.append(r"\hline")
    for row in rows:
        lines.append(" & ".join(latex_escape(fmt(row[c])) for c in cols) + r" \\")
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    lines.append(rf"\caption{{{latex_escape(caption)}}}")
    lines.append(rf"\label{{{latex_escape(label)}}}")
    lines.append(r"\end{table}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def get_prediction_map(pred_obj: Any) -> Dict[int, Dict[str, Any]]:
    if pred_obj is None:
        return {}
    rows = pred_obj.get("prediction", [])
    return {i: row for i, row in enumerate(rows)}


def add_e2e_prediction_fields(case: Dict[str, Any], pred_maps: Dict[str, Dict[int, Dict[str, Any]]]) -> Dict[str, Any]:
    out = dict(case)
    idx = int(case.get("row_index", -1))
    if idx < 0:
        return out

    out["e2e_predictions"] = {}
    for name, mp in pred_maps.items():
        row = mp.get(idx)
        if row is None:
            continue
        out["e2e_predictions"][name] = {
            "target": row.get("target", row.get("output")),
            "pred": row.get("pred"),
            "pred_rank": row.get("pred_rank"),
            "rank": row.get("rank"),
            "top5": row.get("rank_entities", [])[:5],
        }
    return out


def extract_w19_locked_rows(w19_main: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for r in w19_main.get("main_rows", []):
        rows.append({
            "row": r.get("row_name"),
            "gold_present": r.get("gold_present_rate"),
            "mrr_at20": r.get("mrr_at20"),
            "hits1": r.get("hits1_at20"),
            "hits3": r.get("hits3_at20"),
            "hits10": r.get("hits10_at20"),
            "avg_gold_rank": r.get("avg_gold_rank"),
        })
    return rows


def extract_w20_e2e_rows(w20_main: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for r in w20_main.get("main_rows", []):
        c = r["candidate_ceiling_reviewer_safe"]
        e = r["e2e_generation_reviewer_safe"]
        g = r["graph_package"]
        rows.append({
            "row": r["row_name"],
            "candidate_mrr": c.get("mrr_at20"),
            "candidate_h1": c.get("hits1_at20"),
            "candidate_h3": c.get("hits3_at20"),
            "candidate_h10": c.get("hits10_at20"),
            "e2e_mrr": e.get("mrr_at20"),
            "e2e_h1": e.get("hits1_at20"),
            "e2e_h3": e.get("hits3_at20"),
            "e2e_h10": e.get("hits10_at20"),
            "exact_gen": e.get("exact_generated_rate"),
            "pred_in_candidates": e.get("pred_in_candidate_rate"),
            "avg_subgraph_size": g.get("avg_subgraph_size"),
        })
    return rows


def extract_graph_rows(w20_main: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for r in w20_main.get("main_rows", []):
        g = r["graph_package"]
        rows.append({
            "row": r["row_name"],
            "avg_subgraph_size": g.get("avg_subgraph_size"),
            "min_subgraph_size": g.get("min_subgraph_size"),
            "max_subgraph_size": g.get("max_subgraph_size"),
            "coverage": g.get("avg_candidate_coverage_preserved_rate", ""),
            "direct_shortcut_rate": g.get("avg_direct_shortcut_path_rate", ""),
            "source_variant": ",".join(g.get("selected_source_variant_set", [])) if "selected_source_variant_set" in g else "",
        })
    return rows


def extract_ablation_rows(w20_ablation: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []

    def add_block(comparison: str, layer: str, block: Dict[str, Any]):
        rows.append({
            "comparison": comparison,
            "layer": layer,
            "delta_mrr": block.get("delta_mrr_at20", ""),
            "delta_h1": block.get("delta_hits1_at20", ""),
            "delta_h3": block.get("delta_hits3_at20", ""),
            "delta_h10": block.get("delta_hits10_at20", ""),
            "delta_h20": block.get("delta_hits20_at20", ""),
        })

    add_block(
        "soft_support_raw - backbone_raw",
        "candidate_ceiling",
        w20_ablation["soft_minus_backbone"]["candidate_ceiling"],
    )
    add_block(
        "soft_support_raw - backbone_raw",
        "e2e_generation",
        w20_ablation["soft_minus_backbone"]["e2e_generation"],
    )
    add_block(
        "retrieval_main - soft_support_raw",
        "candidate_ceiling",
        w20_ablation["retrieval_minus_soft"]["candidate_ceiling"],
    )
    add_block(
        "retrieval_main - soft_support_raw",
        "e2e_generation",
        w20_ablation["retrieval_minus_soft"]["e2e_generation"],
    )
    add_block(
        "retrieval_main - backbone_raw",
        "candidate_ceiling",
        w20_ablation["retrieval_minus_backbone"]["candidate_ceiling"],
    )
    add_block(
        "retrieval_main - backbone_raw",
        "e2e_generation",
        w20_ablation["retrieval_minus_backbone"]["e2e_generation"],
    )
    return rows


def choose_cases(w19_cases: Dict[str, Any], w19_go: Dict[str, Any] | None, pred_maps: Dict[str, Dict[int, Dict[str, Any]]]) -> Dict[str, Any]:
    if w19_go and "recommended_case_packs" in w19_go:
        main_cases = w19_go["recommended_case_packs"].get("main_paper", {})
        appendix_cases = w19_go["recommended_case_packs"].get("appendix", {})
    else:
        sl = w19_cases.get("shortlist", {})
        main_cases = {
            "backbone_to_retrieval_improved": sl.get("backbone_to_retrieval_improved", [])[:3],
            "ontology_failure_retrieval_success": sl.get("ontology_failure_retrieval_success", [])[:3],
            "same_rank_cleaner_graph": [
                x for x in sl.get("same_rank_cleaner_graph", [])
                if x.get("retrieval_gold_present") and int(x.get("retrieval_gold_rank", 21)) <= 10
            ][:3],
        }
        if len(main_cases["same_rank_cleaner_graph"]) == 0:
            main_cases["same_rank_cleaner_graph"] = sl.get("same_rank_cleaner_graph", [])[:3]

        appendix_cases = {
            "same_rank_cleaner_graph_extra": sl.get("same_rank_cleaner_graph", [])[3:8],
            "encoder_appendix_deferred": sl.get("encoder_appendix_deferred", []),
        }

    enriched_main = {}
    for bucket, cases in main_cases.items():
        enriched_main[bucket] = [add_e2e_prediction_fields(c, pred_maps) for c in cases]

    enriched_appendix = {}
    for bucket, cases in appendix_cases.items():
        if isinstance(cases, list):
            enriched_appendix[bucket] = [add_e2e_prediction_fields(c, pred_maps) for c in cases]
        else:
            enriched_appendix[bucket] = cases

    return {
        "main_paper": enriched_main,
        "appendix": enriched_appendix,
    }


def build_snippets(
    w20_main: Dict[str, Any],
    w20_ablation: Dict[str, Any],
    case_pack: Dict[str, Any],
) -> str:
    rows = {r["row_name"]: r for r in w20_main["main_rows"]}
    b = rows["backbone_raw"]
    s = rows["soft_support_raw"]
    r = rows["soft_support_fuzzy_retrieval_main"]

    b_e2e = b["e2e_generation_reviewer_safe"]
    s_e2e = s["e2e_generation_reviewer_safe"]
    r_e2e = r["e2e_generation_reviewer_safe"]
    r_graph = r["graph_package"]

    soft_delta = w20_ablation["soft_minus_backbone"]
    retr_delta = w20_ablation["retrieval_minus_soft"]

    lines = []
    lines.append("# Paper interpretation snippets")
    lines.append("")
    lines.append("## Main result wording")
    lines.append("")
    lines.append(
        "Soft-support re-ranking provides the main candidate-level improvement over the raw backbone. "
        f"On the reviewer-safe E2E evaluation, soft_support_raw improves MRR@20 from "
        f"{b_e2e['mrr_at20']} to {s_e2e['mrr_at20']}, with Hits@3 increasing from "
        f"{b_e2e['hits3_at20']} to {s_e2e['hits3_at20']} and Hits@10 from "
        f"{b_e2e['hits10_at20']} to {s_e2e['hits10_at20']}."
    )
    lines.append("")
    lines.append(
        "The confidence-aware retrieval stage preserves the soft-support ranking and E2E behavior "
        "while producing a substantially smaller evidence package. "
        f"The retrieval-main row obtains E2E MRR@20={r_e2e['mrr_at20']} and reduces the average "
        f"subgraph size to {r_graph['avg_subgraph_size']} triples, with candidate coverage preserved at "
        f"{r_graph.get('avg_candidate_coverage_preserved_rate')}."
    )
    lines.append("")
    lines.append("## Ablation wording")
    lines.append("")
    lines.append(
        f"Compared with the raw backbone, soft support improves candidate-ceiling MRR@20 by "
        f"{soft_delta['candidate_ceiling']['delta_mrr_at20']} and E2E MRR@20 by "
        f"{soft_delta['e2e_generation']['delta_mrr_at20']}."
    )
    lines.append("")
    lines.append(
        f"Compared with soft support, retrieval main changes candidate-ceiling MRR@20 by "
        f"{retr_delta['candidate_ceiling']['delta_mrr_at20']} and E2E MRR@20 by "
        f"{retr_delta['e2e_generation']['delta_mrr_at20']}, while reducing average subgraph size by "
        f"{retr_delta['graph_package']['delta_avg_subgraph_size']} triples."
    )
    lines.append("")
    lines.append("## Limitation wording")
    lines.append("")
    lines.append(
        "The E2E Hits@1 remains weak because the frozen LLM adapter often generates a plausible "
        "candidate rather than the exact gold entity string, even when the gold entity is ranked first "
        "in the candidate list. We therefore report both candidate-ceiling and generation-adjusted "
        "reviewer-safe metrics."
    )
    lines.append("")
    lines.append("## Recommended main-paper case buckets")
    lines.append("")
    for bucket, cases in case_pack["main_paper"].items():
        lines.append(f"### {bucket}")
        for c in cases:
            lines.append(
                f"- row={c.get('row_index')} | query={c.get('query_entity')} | gold={c.get('gold_entity')} | "
                f"backbone_rank={c.get('backbone_gold_rank')} | soft_rank={c.get('soft_gold_rank')} | "
                f"retrieval_rank={c.get('retrieval_gold_rank')} | subgraph_shrink={c.get('subgraph_shrink')} | "
                f"shortcut_reduction={c.get('direct_shortcut_reduction')}"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    w19_main = load_json(W19_MAIN)
    w19_ablation = load_json(W19_ABL, required=False)
    w19_cases = load_json(W19_CASES)
    w19_go = load_json(W19_GO, required=False)

    w20_main = load_json(W20_E2E_MAIN)
    w20_ablation = load_json(W20_E2E_ABL)

    pred_maps = {
        "backbone_raw": get_prediction_map(load_json(PRED_BACKBONE, required=False)),
        "soft_support_raw": get_prediction_map(load_json(PRED_SOFT, required=False)),
        "retrieval_main": get_prediction_map(load_json(PRED_RETR, required=False)),
    }

    locked_rows = extract_w19_locked_rows(w19_main)
    e2e_rows = extract_w20_e2e_rows(w20_main)
    graph_rows = extract_graph_rows(w20_main)
    ablation_rows = extract_ablation_rows(w20_ablation)

    table_paths = {
        "locked_test_csv": OUT_DIR / "table1_locked_test_main.csv",
        "locked_test_tex": OUT_DIR / "table1_locked_test_main.tex",
        "e2e_csv": OUT_DIR / "table2_e2e_confirmation.csv",
        "e2e_tex": OUT_DIR / "table2_e2e_confirmation.tex",
        "ablation_csv": OUT_DIR / "table3_e2e_ablation.csv",
        "ablation_tex": OUT_DIR / "table3_e2e_ablation.tex",
        "graph_csv": OUT_DIR / "table4_graph_package.csv",
        "graph_tex": OUT_DIR / "table4_graph_package.tex",
    }

    write_csv(table_paths["locked_test_csv"], locked_rows)
    write_latex_table(
        table_paths["locked_test_tex"],
        locked_rows,
        "Locked-test reviewer-safe ranking results.",
        "tab:locked-test-ranking",
    )

    write_csv(table_paths["e2e_csv"], e2e_rows)
    write_latex_table(
        table_paths["e2e_tex"],
        e2e_rows,
        "End-to-end reviewer-safe confirmation results.",
        "tab:e2e-confirmation",
    )

    write_csv(table_paths["ablation_csv"], ablation_rows)
    write_latex_table(
        table_paths["ablation_tex"],
        ablation_rows,
        "Reviewer-safe ablation deltas.",
        "tab:e2e-ablation",
    )

    write_csv(table_paths["graph_csv"], graph_rows)
    write_latex_table(
        table_paths["graph_tex"],
        graph_rows,
        "Evidence graph package diagnostics.",
        "tab:graph-package",
    )

    case_pack = choose_cases(w19_cases, w19_go, pred_maps)
    save_json(CASE_PACK, {
        "week": 20,
        "stage": "paper_case_pack",
        "status": "BUILT",
        "source": {
            "week19_case_shortlist": str(W19_CASES),
            "week19_go_decision": str(W19_GO) if W19_GO.exists() else None,
            "week20_predictions_used_if_available": True,
        },
        "case_pack": case_pack,
    })

    snippets = build_snippets(w20_main, w20_ablation, case_pack)
    SNIPPETS_MD.write_text(snippets, encoding="utf-8")

    figures_manifest = {
        "week": 20,
        "stage": "paper_figures_manifest",
        "status": "BUILT",
        "figures": [
            {
                "figure_id": "fig1_pipeline",
                "title": "FOG-RAG / Novelty 2 pipeline overview",
                "purpose": "Show raw no-injection candidates, soft support scoring, confidence-aware retrieval, and E2E confirmation.",
                "source_files": [
                    "results/week19/week19_go_decision.json",
                    "results/week20/e2e_main_table.json",
                ],
                "recommended_type": "diagram",
                "paper_location": "Method",
            },
            {
                "figure_id": "fig2_candidate_vs_e2e_mrr",
                "title": "Candidate-ceiling versus E2E reviewer-safe MRR@20",
                "purpose": "Show that soft support improves over backbone and retrieval preserves performance.",
                "source_file": str(table_paths["e2e_csv"]),
                "recommended_type": "bar_chart",
                "paper_location": "Experiments",
            },
            {
                "figure_id": "fig3_subgraph_size_reduction",
                "title": "Evidence subgraph size reduction",
                "purpose": "Show retrieval_main reduces average subgraph size while preserving candidate coverage.",
                "source_file": str(table_paths["graph_csv"]),
                "recommended_type": "bar_chart",
                "paper_location": "Ablation",
            },
            {
                "figure_id": "fig4_case_study",
                "title": "Representative case study",
                "purpose": "Show one improvement or cleaner-graph case with candidate ranks and evidence diagnostics.",
                "source_file": str(CASE_PACK),
                "recommended_type": "case_study_panel",
                "paper_location": "Qualitative Analysis",
            },
        ],
    }
    save_json(FIGURES_MANIFEST, figures_manifest)

    tables_manifest = {
        "week": 20,
        "stage": "paper_tables_manifest",
        "status": "BUILT",
        "tables": {
            "locked_test_main": {
                "csv": str(table_paths["locked_test_csv"]),
                "latex": str(table_paths["locked_test_tex"]),
                "source": str(W19_MAIN),
            },
            "e2e_confirmation": {
                "csv": str(table_paths["e2e_csv"]),
                "latex": str(table_paths["e2e_tex"]),
                "source": str(W20_E2E_MAIN),
            },
            "e2e_ablation": {
                "csv": str(table_paths["ablation_csv"]),
                "latex": str(table_paths["ablation_tex"]),
                "source": str(W20_E2E_ABL),
            },
            "graph_package": {
                "csv": str(table_paths["graph_csv"]),
                "latex": str(table_paths["graph_tex"]),
                "source": str(W20_E2E_MAIN),
            },
        },
        "paper_facing_decision": {
            "main_row": w20_main.get("provisional_main_row"),
            "decision_note": w20_main.get("decision_note"),
            "known_limitation": w20_ablation.get("interpretation", {}).get("known_limitation"),
        },
    }
    save_json(TABLES_MANIFEST, tables_manifest)

    report_lines = []
    report_lines.append("# Day 6 — Paper-ready tables, figures, and case assets")
    report_lines.append("")
    report_lines.append("- status: **BUILT**")
    report_lines.append("")
    report_lines.append("## 1. Tables")
    for k, v in tables_manifest["tables"].items():
        report_lines.append(f"- {k}: CSV=`{v['csv']}`, LaTeX=`{v['latex']}`")
    report_lines.append("")
    report_lines.append("## 2. Figures")
    for fig in figures_manifest["figures"]:
        report_lines.append(f"- {fig['figure_id']}: {fig['title']} | type=`{fig['recommended_type']}`")
    report_lines.append("")
    report_lines.append("## 3. Case pack")
    for bucket, cases in case_pack["main_paper"].items():
        report_lines.append(f"- main_paper/{bucket}: `{len(cases)}` cases")
    for bucket, cases in case_pack["appendix"].items():
        if isinstance(cases, list):
            report_lines.append(f"- appendix/{bucket}: `{len(cases)}` cases")
    report_lines.append("")
    report_lines.append("## 4. Paper-facing decision")
    report_lines.append(f"- main_row: `{tables_manifest['paper_facing_decision']['main_row']}`")
    report_lines.append(f"- decision_note: {tables_manifest['paper_facing_decision']['decision_note']}")
    report_lines.append("")
    report_lines.append("## 5. Day-6 conclusion")
    report_lines.append(
        "Paper-ready tables, figure manifest, case pack, and interpretation snippets have been generated. "
        "Day 7 should close Week 20 and decide whether to move to full paper writing or run a small robustness package."
    )
    REPORT_MD.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "tables_manifest": tables_manifest,
        "figures_manifest": figures_manifest,
        "case_pack_summary": {
            "main_paper_buckets": {k: len(v) for k, v in case_pack["main_paper"].items()},
            "appendix_buckets": {
                k: len(v) if isinstance(v, list) else "non_list"
                for k, v in case_pack["appendix"].items()
            },
        },
        "outputs": {
            "paper_tables_manifest": str(TABLES_MANIFEST),
            "paper_figures_manifest": str(FIGURES_MANIFEST),
            "paper_case_pack": str(CASE_PACK),
            "paper_interpretation_snippets": str(SNIPPETS_MD),
            "report": str(REPORT_MD),
        },
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
