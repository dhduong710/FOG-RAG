#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 25 Day 7: Write Week 25 closeout.

This script summarizes:
- Day 1 protocol audit
- Day 2/3 rule sensitivity
- Day 4 template sensitivity
- Day 5 noise robustness
- Day 6 paper assets

It does not run new experiments.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = ROOT / "results" / "week25"
REPORTS_DIR = ROOT / "reports" / "week25"

PROTOCOL_JSON = RESULTS_DIR / "protocol" / "week25_sensitivity_protocol.json"
RULE_JSON = RESULTS_DIR / "rule_sensitivity" / "rule_sensitivity_e2e_summary.json"
TEMPLATE_JSON = RESULTS_DIR / "template_sensitivity" / "template_sensitivity_e2e_summary.json"
NOISE_JSON = RESULTS_DIR / "noise_robustness" / "noise_robustness_summary.json"
PAPER_ASSETS_JSON = RESULTS_DIR / "paper_assets" / "week25_paper_assets_summary.json"

OUT_CLOSEOUT_JSON = RESULTS_DIR / "week25_closeout.json"
OUT_GO_JSON = RESULTS_DIR / "week25_go_decision.json"
OUT_DAY7_MD = REPORTS_DIR / "day7_week25_closeout.md"
OUT_CLOSEOUT_MD = REPORTS_DIR / "week25_closeout.md"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def write_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fmt(x: Any, nd: int = 6) -> str:
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x)


def fmt4(x: Any) -> str:
    return fmt(x, 4)


def pct_reduction(old: float, new: float) -> float:
    return 100.0 * (old - new) / old if old else 0.0


def get_split_rows(summary: Dict[str, Any], split: str) -> List[Dict[str, Any]]:
    return [s for s in summary["summaries"] if s["split"] == split]


def by_variant(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {r["variant"]: r for r in rows}


def md_table(headers: List[str], rows: List[List[Any]]) -> str:
    def esc(x: Any) -> str:
        return ("" if x is None else str(x)).replace("|", "\\|").replace("\n", " ")

    lines = []
    lines.append("| " + " | ".join(esc(h) for h in headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(esc(x) for x in row) + " |")
    return "\n".join(lines)


def check_inputs() -> List[str]:
    missing = []
    for p in [PROTOCOL_JSON, RULE_JSON, TEMPLATE_JSON, NOISE_JSON, PAPER_ASSETS_JSON]:
        if not p.exists():
            missing.append(rel(p))
    return missing


def build_closeout(
    protocol: Dict[str, Any],
    rule: Dict[str, Any],
    template: Dict[str, Any],
    noise: Dict[str, Any],
    paper_assets: Dict[str, Any],
) -> Dict[str, Any]:
    rule_test = by_variant(get_split_rows(rule, "test"))
    rule_valid = by_variant(get_split_rows(rule, "valid"))

    template_test = by_variant(get_split_rows(template, "test"))
    template_valid = by_variant(get_split_rows(template, "valid"))

    noise_test = by_variant(get_split_rows(noise, "test"))
    noise_valid = by_variant(get_split_rows(noise, "valid"))

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
    n5 = noise_test["N5_subgraph_edge_dropout_5_seed2"]
    n6 = noise_test["N6_subgraph_edge_dropout_5_seed3"]

    support_noise_avg_mrr = (
        n1["candidate_mrr_at20"] + n2["candidate_mrr_at20"] + n3["candidate_mrr_at20"]
    ) / 3.0
    support_noise_avg_delta = support_noise_avg_mrr - n0["candidate_mrr_at20"]

    template_mrrs = [
        t0["e2e_mrr_at20"],
        t1["e2e_mrr_at20"],
        t2["e2e_mrr_at20"],
        t3["e2e_mrr_at20"],
    ]

    closeout = {
        "week": 25,
        "title": "Sensitivity and Robustness for FOG-RAG",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "decision": "GO_WEEK25_SENSITIVITY_APPENDIX_READY",
        "scope": {
            "main_role": "appendix sensitivity and robustness evidence",
            "not_a_new_novelty": True,
            "does_not_replace_week24_main_results": True,
            "primary_dataset": "PrimeKG Setting A",
            "primary_model": "Llama-3.2-3B",
            "frozen_decoding": "cfg01_mnt16_rp100_ng0",
            "metric_policy": "reviewer-safe RR@20; RR=1/rank if rank<=20 else 0",
            "gold_injection": False,
            "test_tuning": False,
        },
        "input_decisions": {
            "day1_protocol": protocol.get("decision"),
            "day3_rule_sensitivity": rule.get("decision"),
            "day4_template_sensitivity": template.get("decision"),
            "day5_noise_robustness": noise.get("decision"),
            "day6_paper_assets": paper_assets.get("decision"),
        },
        "rule_sensitivity": {
            "decision": "RULE_SENSITIVITY_TEST_E2E_READY",
            "test_main_rules": {
                "gold_at20": main_rule["gold_at20"],
                "candidate_mrr_at20": main_rule["candidate_mrr_at20"],
                "e2e_mrr_at20": main_rule["e2e_mrr_at20"],
                "e2e_hits10_at20": main_rule["e2e_hits10_at20"],
                "invalid_rate": main_rule["invalid_rate"],
                "avg_graph_size": main_rule["avg_graph_size"],
            },
            "test_no_rules": {
                "e2e_mrr_at20": no_rule["e2e_mrr_at20"],
                "invalid_rate": no_rule["invalid_rate"],
                "avg_graph_size": no_rule["avg_graph_size"],
                "delta_e2e_mrr_vs_main": no_rule["delta_e2e_mrr_at20_vs_main"],
                "delta_avg_graph_vs_main": no_rule["delta_avg_graph_size_vs_main"],
            },
            "test_random_rules": {
                "e2e_mrr_at20": random_rule["e2e_mrr_at20"],
                "invalid_rate": random_rule["invalid_rate"],
                "avg_graph_size": random_rule["avg_graph_size"],
                "delta_e2e_mrr_vs_main": random_rule["delta_e2e_mrr_at20_vs_main"],
            },
            "interpretation": [
                "Candidate metrics are identical across rule variants by construction.",
                "No-rules gives nearly identical E2E MRR but uses a much larger graph and has higher invalid rate.",
                "Random-rules is nearly identical in E2E MRR, showing that candidate ordering dominates under the constrained prompt.",
                "Main claim should emphasize graph efficiency and output validity, not superiority over random-rules.",
            ],
        },
        "template_sensitivity": {
            "decision": "QUESTION_TEMPLATE_SENSITIVITY_READY",
            "test_e2e_mrr_range": max(template_mrrs) - min(template_mrrs),
            "test_rows": {
                "T0_canonical": {
                    "e2e_mrr_at20": t0["e2e_mrr_at20"],
                    "invalid_rate": t0["invalid_rate"],
                    "prediction_change_rate_vs_T0": t0["prediction_change_rate_vs_T0"],
                },
                "T1_treatment": {
                    "e2e_mrr_at20": t1["e2e_mrr_at20"],
                    "invalid_rate": t1["invalid_rate"],
                    "prediction_change_rate_vs_T0": t1["prediction_change_rate_vs_T0"],
                },
                "T2_medication": {
                    "e2e_mrr_at20": t2["e2e_mrr_at20"],
                    "invalid_rate": t2["invalid_rate"],
                    "prediction_change_rate_vs_T0": t2["prediction_change_rate_vs_T0"],
                },
                "T3_association_neutral": {
                    "e2e_mrr_at20": t3["e2e_mrr_at20"],
                    "invalid_rate": t3["invalid_rate"],
                    "prediction_change_rate_vs_T0": t3["prediction_change_rate_vs_T0"],
                },
            },
            "interpretation": [
                "Template wording has negligible impact on reviewer-safe E2E MRR.",
                "Prediction strings change in a small subset of cases, but rank metrics remain essentially unchanged.",
                "Canonical indication prompt should remain the main prompt because it best matches the task definition.",
            ],
        },
        "noise_robustness": {
            "decision": "NOISE_ROBUSTNESS_READY",
            "test_no_noise": {
                "candidate_mrr_at20": n0["candidate_mrr_at20"],
                "hits10_at20": n0["hits10_at20"],
                "avg_graph_size": n0["avg_subgraph_size"],
                "candidate_coverage_rate": n0["candidate_coverage_rate"],
            },
            "support_score_noise": {
                "seed1_mrr": n1["candidate_mrr_at20"],
                "seed2_mrr": n2["candidate_mrr_at20"],
                "seed3_mrr": n3["candidate_mrr_at20"],
                "avg_mrr": round(support_noise_avg_mrr, 6),
                "avg_delta_vs_no_noise": round(support_noise_avg_delta, 6),
                "seed1_same_top1": n1["same_top1_rate_vs_N0"],
                "seed2_same_top1": n2["same_top1_rate_vs_N0"],
                "seed3_same_top1": n3["same_top1_rate_vs_N0"],
                "interpretation": "support-score perturbation substantially changes candidate ordering; report as limitation",
            },
            "edge_dropout_5": {
                "seed1_mrr": n4["candidate_mrr_at20"],
                "seed2_mrr": n5["candidate_mrr_at20"],
                "seed3_mrr": n6["candidate_mrr_at20"],
                "avg_graph_size_seed1": n4["avg_subgraph_size"],
                "avg_graph_size_seed2": n5["avg_subgraph_size"],
                "avg_graph_size_seed3": n6["avg_subgraph_size"],
                "candidate_coverage_seed1": n4["candidate_coverage_rate"],
                "graph_reduction_percent_seed1": round(
                    pct_reduction(n0["avg_subgraph_size"], n4["avg_subgraph_size"]), 3
                ),
                "interpretation": "light edge dropout preserves ranking and coverage; fuzzy subgraph is not fragile to minor edge loss",
            },
        },
        "paper_positioning": {
            "recommended_section": "Appendix or robustness/sensitivity subsection",
            "main_claim_supported": [
                "Soft support remains the main source of ranking gain from previous weeks.",
                "Fuzzy retrieval preserves ranking while reducing graph size.",
                "Week 25 shows the result is not an artifact of one prompt wording.",
                "Week 25 shows the graph package is stable under light edge dropout.",
            ],
            "limitations_to_state": [
                "Rule sensitivity does not show a strong E2E advantage of main rules over random rules under fixed candidates.",
                "Candidate ordering dominates E2E behavior in the constrained-prompt setting.",
                "Support-score perturbation exposes sensitivity near close score ties.",
                "Future work should calibrate support-score margins and uncertainty-aware re-ranking.",
            ],
            "do_not_claim": [
                "Do not claim Week 25 introduces a third novelty.",
                "Do not claim random-rules is worse if metrics are essentially tied.",
                "Do not claim robustness to support-score noise.",
                "Do not replace Week 24 main results.",
            ],
        },
        "paper_assets": paper_assets.get("outputs", {}),
        "final_outputs": {
            "week25_closeout_json": rel(OUT_CLOSEOUT_JSON),
            "week25_go_decision_json": rel(OUT_GO_JSON),
            "day7_closeout_md": rel(OUT_DAY7_MD),
            "week25_closeout_md": rel(OUT_CLOSEOUT_MD),
        },
    }

    return closeout


def build_go_decision(closeout: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "week": 25,
        "created_at": closeout["created_at"],
        "decision": closeout["decision"],
        "go_for_paper_update": True,
        "go_for_appendix_tables": True,
        "go_for_week26": True,
        "recommended_next_step": "Update the paper draft with Week 25 appendix tables, sensitivity paragraph, and limitation paragraph.",
        "main_result_status": "Week 24 main results remain frozen.",
        "week25_status": "Appendix-ready sensitivity and robustness evidence.",
        "must_include_limitations": [
            "Support-score perturbation is not robust.",
            "Rule variants are E2E-tied under fixed candidate ordering.",
            "Candidate ordering dominates LLM output under constrained prompts.",
        ],
    }


def build_markdown(closeout: Dict[str, Any]) -> str:
    rule = closeout["rule_sensitivity"]
    template = closeout["template_sensitivity"]
    noise = closeout["noise_robustness"]

    lines = []

    lines.append("# Week 25 Closeout — Sensitivity and Robustness for FOG-RAG\n")
    lines.append(f"- Decision: **{closeout['decision']}**")
    lines.append(f"- Created at: `{closeout['created_at']}`")
    lines.append("- Role: **appendix sensitivity / robustness evidence**")
    lines.append("- Main result status: **Week 24 remains frozen**")
    lines.append("- Primary model: **Llama-3.2-3B**")
    lines.append("- Frozen decoding: **cfg01_mnt16_rp100_ng0**")
    lines.append("- Metric: **reviewer-safe RR@20**")
    lines.append("")

    lines.append("## 1. What Week 25 answered\n")
    lines.append("Week 25 addressed three reviewer-facing questions:")
    lines.append("")
    lines.append("1. Does FOG-RAG depend too strongly on a single rule package?")
    lines.append("2. Is the E2E result sensitive to question wording?")
    lines.append("3. Is the retrieval/ranking stage robust to small support-score or graph perturbations?")
    lines.append("")

    lines.append("## 2. Rule sensitivity\n")
    lines.append(md_table(
        ["Variant", "Gold@20", "Cand MRR", "E2E MRR", "H@10", "Invalid", "Avg graph"],
        [
            [
                "main_rules",
                rule["test_main_rules"]["gold_at20"],
                rule["test_main_rules"]["candidate_mrr_at20"],
                rule["test_main_rules"]["e2e_mrr_at20"],
                rule["test_main_rules"]["e2e_hits10_at20"],
                rule["test_main_rules"]["invalid_rate"],
                rule["test_main_rules"]["avg_graph_size"],
            ],
            [
                "no_rules",
                rule["test_main_rules"]["gold_at20"],
                rule["test_main_rules"]["candidate_mrr_at20"],
                rule["test_no_rules"]["e2e_mrr_at20"],
                rule["test_main_rules"]["e2e_hits10_at20"],
                rule["test_no_rules"]["invalid_rate"],
                rule["test_no_rules"]["avg_graph_size"],
            ],
            [
                "random_rules",
                rule["test_main_rules"]["gold_at20"],
                rule["test_main_rules"]["candidate_mrr_at20"],
                rule["test_random_rules"]["e2e_mrr_at20"],
                rule["test_main_rules"]["e2e_hits10_at20"],
                rule["test_random_rules"]["invalid_rate"],
                rule["test_random_rules"]["avg_graph_size"],
            ],
        ],
    ))
    lines.append("")
    lines.append("**Conclusion:** rule variants are almost tied in E2E MRR under fixed candidate ordering. This means the paper should not overclaim rule superiority. The useful claim is that the main fuzzy retrieval package preserves E2E behavior while using a much smaller graph than the no-rule/source-graph variant and keeping invalid output lower.")
    lines.append("")

    lines.append("## 3. Question-template sensitivity\n")
    lines.append(md_table(
        ["Template", "E2E MRR", "Invalid", "Prediction change vs T0"],
        [
            ["T0_canonical", template["test_rows"]["T0_canonical"]["e2e_mrr_at20"], template["test_rows"]["T0_canonical"]["invalid_rate"], template["test_rows"]["T0_canonical"]["prediction_change_rate_vs_T0"]],
            ["T1_treatment", template["test_rows"]["T1_treatment"]["e2e_mrr_at20"], template["test_rows"]["T1_treatment"]["invalid_rate"], template["test_rows"]["T1_treatment"]["prediction_change_rate_vs_T0"]],
            ["T2_medication", template["test_rows"]["T2_medication"]["e2e_mrr_at20"], template["test_rows"]["T2_medication"]["invalid_rate"], template["test_rows"]["T2_medication"]["prediction_change_rate_vs_T0"]],
            ["T3_association_neutral", template["test_rows"]["T3_association_neutral"]["e2e_mrr_at20"], template["test_rows"]["T3_association_neutral"]["invalid_rate"], template["test_rows"]["T3_association_neutral"]["prediction_change_rate_vs_T0"]],
        ],
    ))
    lines.append("")
    lines.append(f"**Conclusion:** template sensitivity is minimal. Test E2E MRR range is only `{fmt(template['test_e2e_mrr_range'], 6)}`. The canonical indication prompt remains the main prompt because it matches the PrimeKG relation definition.")
    lines.append("")

    lines.append("## 4. Small-noise robustness\n")
    lines.append("### 4.1 Support-score noise\n")
    lines.append(md_table(
        ["Variant", "MRR@20", "Same top1", "Interpretation"],
        [
            ["N0_no_noise", noise["test_no_noise"]["candidate_mrr_at20"], 1.0, "main retrieval ranking"],
            ["Score noise s1", noise["support_score_noise"]["seed1_mrr"], noise["support_score_noise"]["seed1_same_top1"], "ranking drops"],
            ["Score noise s2", noise["support_score_noise"]["seed2_mrr"], noise["support_score_noise"]["seed2_same_top1"], "ranking drops"],
            ["Score noise s3", noise["support_score_noise"]["seed3_mrr"], noise["support_score_noise"]["seed3_same_top1"], "ranking drops"],
        ],
    ))
    lines.append("")
    lines.append("**Conclusion:** support-score noise is a real limitation. The model should not be described as robust to arbitrary score perturbations.")
    lines.append("")

    lines.append("### 4.2 Edge dropout\n")
    lines.append(md_table(
        ["Variant", "MRR@20", "Avg graph", "Candidate coverage", "Interpretation"],
        [
            ["N0_no_noise", noise["test_no_noise"]["candidate_mrr_at20"], noise["test_no_noise"]["avg_graph_size"], noise["test_no_noise"]["candidate_coverage_rate"], "main graph"],
            ["Edge drop s1", noise["edge_dropout_5"]["seed1_mrr"], noise["edge_dropout_5"]["avg_graph_size_seed1"], noise["edge_dropout_5"]["candidate_coverage_seed1"], "stable"],
            ["Edge drop s2", noise["edge_dropout_5"]["seed2_mrr"], noise["edge_dropout_5"]["avg_graph_size_seed2"], noise["edge_dropout_5"]["candidate_coverage_seed1"], "stable"],
            ["Edge drop s3", noise["edge_dropout_5"]["seed3_mrr"], noise["edge_dropout_5"]["avg_graph_size_seed3"], noise["edge_dropout_5"]["candidate_coverage_seed1"], "stable"],
        ],
    ))
    lines.append("")
    lines.append("**Conclusion:** light edge dropout preserves ranking and coverage. This supports the claim that fuzzy retrieval is not fragile to minor edge loss.")
    lines.append("")

    lines.append("## 5. Paper-ready stance\n")
    lines.append("Use Week 25 as:")
    lines.append("")
    lines.append("- An appendix table set.")
    lines.append("- A sensitivity/robustness paragraph.")
    lines.append("- A limitation paragraph.")
    lines.append("")
    lines.append("Do **not** use Week 25 as:")
    lines.append("")
    lines.append("- A third novelty.")
    lines.append("- A replacement for Week 24 main results.")
    lines.append("- Evidence that FOG-RAG is robust to support-score noise.")
    lines.append("")

    lines.append("## 6. Recommended paragraph for paper\n")
    lines.append("FOG-RAG is not sensitive to prompt wording under the frozen candidate-constrained setting, and its fuzzy evidence package is stable under light subgraph edge dropout. However, support-score perturbation substantially changes candidate ordering, indicating that the soft-support score remains sensitive near close score ties. Therefore, the final paper should present Week 25 as robustness and limitation evidence rather than a new method contribution.")
    lines.append("")

    lines.append("## 7. Final decision\n")
    lines.append(f"**{closeout['decision']}**")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    missing = check_inputs()
    if missing:
        raise FileNotFoundError("Missing Week25 closeout inputs: " + ", ".join(missing))

    protocol = load_json(PROTOCOL_JSON)
    rule = load_json(RULE_JSON)
    template = load_json(TEMPLATE_JSON)
    noise = load_json(NOISE_JSON)
    paper_assets = load_json(PAPER_ASSETS_JSON)

    expected = {
        "protocol": "WEEK25_SENSITIVITY_PROTOCOL_READY",
        "rule": "RULE_SENSITIVITY_TEST_E2E_READY",
        "template": "QUESTION_TEMPLATE_SENSITIVITY_READY",
        "noise": "NOISE_ROBUSTNESS_READY",
        "paper_assets": "WEEK25_SENSITIVITY_PAPER_ASSETS_READY",
    }

    errors = []
    if protocol.get("decision") != expected["protocol"]:
        errors.append(f"protocol decision = {protocol.get('decision')}")
    if rule.get("decision") != expected["rule"]:
        errors.append(f"rule decision = {rule.get('decision')}")
    if template.get("decision") != expected["template"]:
        errors.append(f"template decision = {template.get('decision')}")
    if noise.get("decision") != expected["noise"]:
        errors.append(f"noise decision = {noise.get('decision')}")
    if paper_assets.get("decision") != expected["paper_assets"]:
        errors.append(f"paper_assets decision = {paper_assets.get('decision')}")

    if errors:
        raise RuntimeError("Bad input decisions: " + "; ".join(errors))

    closeout = build_closeout(protocol, rule, template, noise, paper_assets)
    go_decision = build_go_decision(closeout)
    markdown = build_markdown(closeout)

    write_json(closeout, OUT_CLOSEOUT_JSON)
    write_json(go_decision, OUT_GO_JSON)
    write_text(markdown, OUT_DAY7_MD)
    write_text(markdown, OUT_CLOSEOUT_MD)

    print("=" * 100)
    print("decision =", closeout["decision"])
    print("closeout_json =", rel(OUT_CLOSEOUT_JSON))
    print("go_decision_json =", rel(OUT_GO_JSON))
    print("day7_report =", rel(OUT_DAY7_MD))
    print("week25_closeout_md =", rel(OUT_CLOSEOUT_MD))
    print("=" * 100)

    print("key conclusions:")
    for item in closeout["paper_positioning"]["main_claim_supported"]:
        print("-", item)
    print("limitations:")
    for item in closeout["paper_positioning"]["limitations_to_state"]:
        print("-", item)


if __name__ == "__main__":
    main()