#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 25 Day 6: Build sensitivity / robustness paper assets.

Inputs:
- results/week25/rule_sensitivity/rule_sensitivity_e2e_summary.json
- results/week25/template_sensitivity/template_sensitivity_e2e_summary.json
- results/week25/noise_robustness/noise_robustness_summary.json

Outputs:
- results/week25/paper_assets/rule_sensitivity_table_latex.tex
- results/week25/paper_assets/template_sensitivity_table_latex.tex
- results/week25/paper_assets/noise_robustness_table_latex.tex
- results/week25/paper_assets/week25_sensitivity_paragraph.md
- results/week25/paper_assets/week25_limitation_paragraph.md
- reports/week25/day6_sensitivity_paper_assets.md
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]

RULE_JSON = ROOT / "results" / "week25" / "rule_sensitivity" / "rule_sensitivity_e2e_summary.json"
TEMPLATE_JSON = ROOT / "results" / "week25" / "template_sensitivity" / "template_sensitivity_e2e_summary.json"
NOISE_JSON = ROOT / "results" / "week25" / "noise_robustness" / "noise_robustness_summary.json"

OUT_DIR = ROOT / "results" / "week25" / "paper_assets"
REPORT_DIR = ROOT / "reports" / "week25"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fmt(x: Any, nd: int = 4) -> str:
    if x is None:
        return "--"
    if isinstance(x, int):
        return str(x)
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x)


def fmt_delta(x: Any, nd: int = 4) -> str:
    if x is None:
        return "--"
    try:
        v = float(x)
        if abs(v) < 0.00005:
            return "0.0000"
        return f"{v:+.{nd}f}"
    except Exception:
        return str(x)


def pct_reduction(old: float, new: float) -> float:
    return 100.0 * (old - new) / old if old else 0.0


def latex_escape(s: Any) -> str:
    text = "" if s is None else str(s)
    replacements = {
        "\\": r"\textbackslash{}",
        "_": r"\_",
        "%": r"\%",
        "&": r"\&",
        "$": r"\$",
        "#": r"\#",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def md_table(headers: List[str], rows: List[List[Any]]) -> str:
    def esc(x: Any) -> str:
        return ("" if x is None else str(x)).replace("|", "\\|").replace("\n", " ")

    lines = []
    lines.append("| " + " | ".join(esc(h) for h in headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(esc(x) for x in row) + " |")
    return "\n".join(lines)


def get_split_rows(summary: Dict[str, Any], split: str) -> List[Dict[str, Any]]:
    return [s for s in summary["summaries"] if s["split"] == split]


def by_variant(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {r["variant"]: r for r in rows}


def build_rule_latex(rule: Dict[str, Any]) -> str:
    rows = get_split_rows(rule, "test")
    order = ["main_rules", "no_rules", "random_rules"]

    display = {
        "main_rules": "Main rules",
        "no_rules": "No rules",
        "random_rules": "Random rules",
    }

    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(r"\centering")
    lines.append(r"\small")
    lines.append(r"\caption{Rule-sensitivity analysis on the locked PrimeKG test split. All variants use the same candidate set; changes mainly affect the graph evidence package.}")
    lines.append(r"\label{tab:rule-sensitivity}")
    lines.append(r"\begin{tabular}{lcccccc}")
    lines.append(r"\toprule")
    lines.append(r"Variant & Gold@20 & Cand. MRR & E2E MRR & H@10 & Invalid & Avg. graph \\")
    lines.append(r"\midrule")

    m = by_variant(rows)
    for v in order:
        s = m[v]
        lines.append(
            f"{latex_escape(display[v])} & "
            f"{fmt(s['gold_at20'], 3)} & "
            f"{fmt(s['candidate_mrr_at20'], 4)} & "
            f"{fmt(s['e2e_mrr_at20'], 4)} & "
            f"{fmt(s['e2e_hits10_at20'], 3)} & "
            f"{fmt(s['invalid_rate'], 3)} & "
            f"{fmt(s['avg_graph_size'], 2)} \\\\"
        )

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    lines.append("")
    return "\n".join(lines)


def build_template_latex(template: Dict[str, Any]) -> str:
    rows = get_split_rows(template, "test")
    order = ["T0_canonical", "T1_treatment", "T2_medication", "T3_association_neutral"]

    display = {
        "T0_canonical": "Canonical",
        "T1_treatment": "Treatment",
        "T2_medication": "Medication",
        "T3_association_neutral": "Association-neutral",
    }

    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(r"\centering")
    lines.append(r"\small")
    lines.append(r"\caption{Question-template sensitivity on the locked PrimeKG test split. Only the wording of the question is changed; candidates and subgraphs are fixed.}")
    lines.append(r"\label{tab:template-sensitivity}")
    lines.append(r"\begin{tabular}{lcccccc}")
    lines.append(r"\toprule")
    lines.append(r"Template & Cand. MRR & E2E MRR & H@10 & Invalid & Pred. change & $\Delta$MRR \\")
    lines.append(r"\midrule")

    m = by_variant(rows)
    for v in order:
        s = m[v]
        lines.append(
            f"{latex_escape(display[v])} & "
            f"{fmt(s['candidate_mrr_at20'], 4)} & "
            f"{fmt(s['e2e_mrr_at20'], 4)} & "
            f"{fmt(s['e2e_hits10_at20'], 3)} & "
            f"{fmt(s['invalid_rate'], 3)} & "
            f"{fmt(s['prediction_change_rate_vs_T0'], 3)} & "
            f"{fmt_delta(s['delta_e2e_mrr_at20_vs_T0'], 4)} \\\\"
        )

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    lines.append("")
    return "\n".join(lines)


def build_noise_latex(noise: Dict[str, Any]) -> str:
    rows = get_split_rows(noise, "test")
    order = [
        "N0_no_noise",
        "N1_support_score_noise_seed1",
        "N2_support_score_noise_seed2",
        "N3_support_score_noise_seed3",
        "N4_subgraph_edge_dropout_5_seed1",
        "N5_subgraph_edge_dropout_5_seed2",
        "N6_subgraph_edge_dropout_5_seed3",
    ]

    display = {
        "N0_no_noise": "No noise",
        "N1_support_score_noise_seed1": "Score noise s1",
        "N2_support_score_noise_seed2": "Score noise s2",
        "N3_support_score_noise_seed3": "Score noise s3",
        "N4_subgraph_edge_dropout_5_seed1": "Edge drop s1",
        "N5_subgraph_edge_dropout_5_seed2": "Edge drop s2",
        "N6_subgraph_edge_dropout_5_seed3": "Edge drop s3",
    }

    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(r"\centering")
    lines.append(r"\small")
    lines.append(r"\caption{Small-noise robustness on the locked PrimeKG test split. Score-noise variants perturb support scores before re-ranking, while edge-drop variants remove approximately 5\% of selected subgraph edges.}")
    lines.append(r"\label{tab:noise-robustness}")
    lines.append(r"\begin{tabular}{lcccccc}")
    lines.append(r"\toprule")
    lines.append(r"Variant & MRR@20 & H@10 & Same top1 & Rank change & Avg. graph & $\Delta$MRR \\")
    lines.append(r"\midrule")

    m = by_variant(rows)
    for v in order:
        s = m[v]
        lines.append(
            f"{latex_escape(display[v])} & "
            f"{fmt(s['candidate_mrr_at20'], 4)} & "
            f"{fmt(s['hits10_at20'], 3)} & "
            f"{fmt(s['same_top1_rate_vs_N0'], 3)} & "
            f"{fmt(s['rank_change_rate_vs_N0'], 3)} & "
            f"{fmt(s['avg_subgraph_size'], 2)} & "
            f"{fmt_delta(s['delta_candidate_mrr_at20_vs_N0'], 4)} \\\\"
        )

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    lines.append("")
    return "\n".join(lines)


def build_paragraphs(rule: Dict[str, Any], template: Dict[str, Any], noise: Dict[str, Any]) -> Dict[str, str]:
    rule_test = by_variant(get_split_rows(rule, "test"))
    template_test = by_variant(get_split_rows(template, "test"))
    noise_test = by_variant(get_split_rows(noise, "test"))

    main_rule = rule_test["main_rules"]
    no_rule = rule_test["no_rules"]
    random_rule = rule_test["random_rules"]

    t0 = template_test["T0_canonical"]
    t1 = template_test["T1_treatment"]
    t2 = template_test["T2_medication"]
    t3 = template_test["T3_association_neutral"]

    n0 = noise_test["N0_no_noise"]
    n1 = noise_test["N1_support_score_noise_seed1"]
    n2 = noise_test["N2_support_score_noise_seed2"]
    n3 = noise_test["N3_support_score_noise_seed3"]
    n4 = noise_test["N4_subgraph_edge_dropout_5_seed1"]

    no_rule_graph_reduction = pct_reduction(no_rule["avg_graph_size"], main_rule["avg_graph_size"])
    edge_drop_graph_reduction = pct_reduction(n0["avg_subgraph_size"], n4["avg_subgraph_size"])

    support_noise_avg_mrr = (n1["candidate_mrr_at20"] + n2["candidate_mrr_at20"] + n3["candidate_mrr_at20"]) / 3.0
    support_noise_avg_delta = support_noise_avg_mrr - n0["candidate_mrr_at20"]
    support_noise_avg_same_top1 = (n1["same_top1_rate_vs_N0"] + n2["same_top1_rate_vs_N0"] + n3["same_top1_rate_vs_N0"]) / 3.0
    support_noise_avg_rank_change = (n1["rank_change_rate_vs_N0"] + n2["rank_change_rate_vs_N0"] + n3["rank_change_rate_vs_N0"]) / 3.0

    template_mrrs = [
        t0["e2e_mrr_at20"],
        t1["e2e_mrr_at20"],
        t2["e2e_mrr_at20"],
        t3["e2e_mrr_at20"],
    ]
    template_range = max(template_mrrs) - min(template_mrrs)

    sensitivity = f"""## Week 25 sensitivity paragraph

We further conducted sensitivity analyses on the locked PrimeKG Setting A evaluation using the frozen Llama-3.2-3B decoding configuration. First, rule-package sensitivity shows that the main confidence-aware retrieval package achieves essentially the same E2E MRR@20 as the larger no-rule/source-graph variant ({fmt(main_rule['e2e_mrr_at20'], 6)} vs. {fmt(no_rule['e2e_mrr_at20'], 6)}), while reducing the average subgraph size from {fmt(no_rule['avg_graph_size'], 2)} to {fmt(main_rule['avg_graph_size'], 2)} triples ({fmt(no_rule_graph_reduction, 1)}\\% reduction). The random-rule negative control also produces a nearly identical E2E score ({fmt(random_rule['e2e_mrr_at20'], 6)}), suggesting that, under the candidate-constrained setting, the main ranking gain is primarily driven by soft candidate support rather than brittle dependence on a single hand-coded rule package. Second, question-template sensitivity is minimal: canonical, treatment, medication, and association-neutral prompts produce E2E MRR@20 values within {fmt(template_range, 6)} of each other on the locked test split. This indicates that the main result is not an artifact of one prompt wording, although the canonical indication prompt remains the main setting because it best matches the PrimeKG task definition. Third, light subgraph-edge dropout preserves candidate-level MRR@20 ({fmt(n0['candidate_mrr_at20'], 6)} to {fmt(n4['candidate_mrr_at20'], 6)}) while reducing the average graph from {fmt(n0['avg_subgraph_size'], 2)} to {fmt(n4['avg_subgraph_size'], 2)} triples, suggesting that the selected fuzzy evidence package is not fragile to minor edge loss.
"""

    limitation = f"""## Week 25 limitation paragraph

The small-noise study also reveals an important limitation. When Gaussian perturbations are added directly to support scores before re-ranking, MRR@20 drops from {fmt(n0['candidate_mrr_at20'], 6)} to an average of {fmt(support_noise_avg_mrr, 6)} across three seeds (average delta {fmt_delta(support_noise_avg_delta, 6)}). The same-top1 rate is only {fmt(support_noise_avg_same_top1, 3)}, with a rank-change rate of {fmt(support_noise_avg_rank_change, 3)}. Therefore, FOG-RAG should not be overclaimed as robust to arbitrary support-score perturbations. Instead, the result suggests that soft-support scoring is effective but remains sensitive near close score ties, motivating future calibration of support-score margins and uncertainty-aware re-ranking. In contrast, the graph package itself is stable under light edge dropout, so the main limitation lies more in support-score calibration than in fuzzy subgraph selection.
"""

    return {
        "sensitivity": sensitivity.strip() + "\n",
        "limitation": limitation.strip() + "\n",
    }


def write_report(
    rule: Dict[str, Any],
    template: Dict[str, Any],
    noise: Dict[str, Any],
    paragraphs: Dict[str, str],
    outputs: Dict[str, Path],
    path: Path,
) -> None:
    lines = []
    lines.append("# Week 25 Day 6 — Sensitivity Paper Assets\n")
    lines.append(f"- Decision: **WEEK25_SENSITIVITY_PAPER_ASSETS_READY**")
    lines.append(f"- Created at: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append("")

    lines.append("## Outputs\n")
    for name, p in outputs.items():
        lines.append(f"- `{name}`: `{rel(p)}`")
    lines.append("")

    rule_test = get_split_rows(rule, "test")
    template_test = get_split_rows(template, "test")
    noise_test = get_split_rows(noise, "test")

    lines.append("## Rule sensitivity test table\n")
    lines.append(md_table(
        ["Variant", "Gold@20", "CandMRR", "E2E MRR", "H@10", "Invalid", "AvgGraph"],
        [
            [
                s["variant"],
                s["gold_at20"],
                s["candidate_mrr_at20"],
                s["e2e_mrr_at20"],
                s["e2e_hits10_at20"],
                s["invalid_rate"],
                s["avg_graph_size"],
            ]
            for s in rule_test
        ],
    ))
    lines.append("")

    lines.append("## Template sensitivity test table\n")
    lines.append(md_table(
        ["Variant", "E2E MRR", "H@10", "Invalid", "PredChange", "DeltaMRR"],
        [
            [
                s["variant"],
                s["e2e_mrr_at20"],
                s["e2e_hits10_at20"],
                s["invalid_rate"],
                s["prediction_change_rate_vs_T0"],
                s["delta_e2e_mrr_at20_vs_T0"],
            ]
            for s in template_test
        ],
    ))
    lines.append("")

    lines.append("## Noise robustness test table\n")
    lines.append(md_table(
        ["Variant", "MRR@20", "H@10", "SameTop1", "RankChange", "AvgGraph", "DeltaMRR"],
        [
            [
                s["variant"],
                s["candidate_mrr_at20"],
                s["hits10_at20"],
                s["same_top1_rate_vs_N0"],
                s["rank_change_rate_vs_N0"],
                s["avg_subgraph_size"],
                s["delta_candidate_mrr_at20_vs_N0"],
            ]
            for s in noise_test
        ],
    ))
    lines.append("")

    lines.append("## Paper paragraph\n")
    lines.append(paragraphs["sensitivity"])
    lines.append("")

    lines.append("## Limitation paragraph\n")
    lines.append(paragraphs["limitation"])
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    missing = [p for p in [RULE_JSON, TEMPLATE_JSON, NOISE_JSON] if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs: " + ", ".join(rel(p) for p in missing))

    rule = load_json(RULE_JSON)
    template = load_json(TEMPLATE_JSON)
    noise = load_json(NOISE_JSON)

    required_decisions = {
        "rule": "RULE_SENSITIVITY_TEST_E2E_READY",
        "template": "QUESTION_TEMPLATE_SENSITIVITY_READY",
        "noise": "NOISE_ROBUSTNESS_READY",
    }

    if rule.get("decision") != required_decisions["rule"]:
        raise RuntimeError(f"Bad rule decision: {rule.get('decision')}")
    if template.get("decision") != required_decisions["template"]:
        raise RuntimeError(f"Bad template decision: {template.get('decision')}")
    if noise.get("decision") != required_decisions["noise"]:
        raise RuntimeError(f"Bad noise decision: {noise.get('decision')}")

    rule_tex = build_rule_latex(rule)
    template_tex = build_template_latex(template)
    noise_tex = build_noise_latex(noise)
    paragraphs = build_paragraphs(rule, template, noise)

    outputs = {
        "rule_sensitivity_table_latex": OUT_DIR / "rule_sensitivity_table_latex.tex",
        "template_sensitivity_table_latex": OUT_DIR / "template_sensitivity_table_latex.tex",
        "noise_robustness_table_latex": OUT_DIR / "noise_robustness_table_latex.tex",
        "week25_sensitivity_paragraph": OUT_DIR / "week25_sensitivity_paragraph.md",
        "week25_limitation_paragraph": OUT_DIR / "week25_limitation_paragraph.md",
        "day6_report": REPORT_DIR / "day6_sensitivity_paper_assets.md",
    }

    write_text(rule_tex, outputs["rule_sensitivity_table_latex"])
    write_text(template_tex, outputs["template_sensitivity_table_latex"])
    write_text(noise_tex, outputs["noise_robustness_table_latex"])
    write_text(paragraphs["sensitivity"], outputs["week25_sensitivity_paragraph"])
    write_text(paragraphs["limitation"], outputs["week25_limitation_paragraph"])

    write_report(rule, template, noise, paragraphs, outputs, outputs["day6_report"])

    summary = {
        "week": 25,
        "day": 6,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "decision": "WEEK25_SENSITIVITY_PAPER_ASSETS_READY",
        "inputs": {
            "rule": rel(RULE_JSON),
            "template": rel(TEMPLATE_JSON),
            "noise": rel(NOISE_JSON),
        },
        "outputs": {k: rel(v) for k, v in outputs.items()},
        "notes": [
            "Use the sensitivity paragraph in the appendix or robustness section.",
            "Use the limitation paragraph to avoid overclaiming support-score robustness.",
            "Tables are appendix-ready but may need resizing depending on final paper format.",
        ],
    }

    summary_path = OUT_DIR / "week25_paper_assets_summary.json"
    write_text(json.dumps(summary, indent=2, ensure_ascii=False), summary_path)

    print("=" * 100)
    print("decision =", summary["decision"])
    print("summary_json =", rel(summary_path))
    for name, p in outputs.items():
        print(f"{name} = {rel(p)}")
    print("=" * 100)


if __name__ == "__main__":
    main()