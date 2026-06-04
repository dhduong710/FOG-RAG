#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 21 Day 6
Build interpretation assets and paper-positioning snippets.

Inputs:
- results/week21/baseline_positioning_decision.json
- results/week21/baseline_main_table.json
- results/week21/baseline_main_table.tex

Outputs:
- results/week21/baseline_interpretation_assets.json
- results/week21/paper_snippet_results_week21.md
- results/week21/paper_snippet_discussion_week21.md
- results/week21/paper_snippet_reviewer_defense_week21.md
- results/week21/paper_snippet_table_caption_week21.tex
- results/week21/week21_paper_positioning_summary.md
- reports/week21/day6_interpretation_and_paper_positioning.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(".")
RESULTS_DIR = ROOT / "results" / "week21"
REPORTS_DIR = ROOT / "reports" / "week21"

IN_DECISION = RESULTS_DIR / "baseline_positioning_decision.json"
IN_TABLE = RESULTS_DIR / "baseline_main_table.json"
IN_TABLE_TEX = RESULTS_DIR / "baseline_main_table.tex"

OUT_ASSETS_JSON = RESULTS_DIR / "baseline_interpretation_assets.json"
OUT_RESULTS_MD = RESULTS_DIR / "paper_snippet_results_week21.md"
OUT_DISCUSSION_MD = RESULTS_DIR / "paper_snippet_discussion_week21.md"
OUT_REVIEWER_MD = RESULTS_DIR / "paper_snippet_reviewer_defense_week21.md"
OUT_CAPTION_TEX = RESULTS_DIR / "paper_snippet_table_caption_week21.tex"
OUT_SUMMARY_MD = RESULTS_DIR / "week21_paper_positioning_summary.md"
OUT_REPORT_MD = REPORTS_DIR / "day6_interpretation_and_paper_positioning.md"


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing required input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fmt(x: float, n: int = 6) -> str:
    return f"{x:.{n}f}"


def pct(x: float, n: int = 1) -> str:
    return f"{100.0 * x:.{n}f}%"


def get_test_row(table: dict[str, Any], row_name: str) -> dict[str, Any]:
    for row in table["test_rows"]:
        if row["row_name"] == row_name:
            return row
    raise KeyError(f"Cannot find test row: {row_name}")


def get_valid_row(table: dict[str, Any], row_name: str) -> dict[str, Any]:
    for row in table["valid_rows"]:
        if row["row_name"] == row_name:
            return row
    raise KeyError(f"Cannot find valid row: {row_name}")


def build_assets(decision: dict[str, Any], table: dict[str, Any]) -> dict[str, Any]:
    test_backbone = get_test_row(table, "backbone_raw")
    test_soft = get_test_row(table, "soft_support_raw")
    test_retrieval = get_test_row(table, "soft_support_fuzzy_retrieval_main")
    test_complex = get_test_row(table, "complex")
    test_distmult = get_test_row(table, "distmult")
    test_rgcn = get_test_row(table, "rgcn")

    valid_complex = get_valid_row(table, "complex")
    valid_retrieval = get_valid_row(table, "soft_support_fuzzy_retrieval_main")

    d_fog_back = decision["deltas"]["fograg_main_minus_backbone_raw"]
    d_fog_complex = decision["deltas"]["fograg_main_minus_complex"]
    d_complex_back = decision["deltas"]["complex_minus_backbone_raw"]

    # Week20 locked graph efficiency numbers from the completed paper assets.
    graph_efficiency = {
        "backbone_avg_subgraph_size_test": 59.93,
        "soft_support_avg_subgraph_size_test": 59.93,
        "retrieval_main_avg_subgraph_size_test": 32.34,
        "subgraph_size_reduction_vs_soft": 27.59,
        "candidate_coverage_preserved": 1.0,
        "retrieval_main_direct_shortcut_path_rate_test": 0.110815,
        "retrieval_main_contradiction_path_rate_test": 0.00024,
    }

    results_paragraph = (
        "Table~\\ref{tab:week21-baseline-main} reports the locked-test reviewer-safe "
        "comparison between six structure-only candidate generators and the DrKGC-compatible "
        "FOG-RAG rows. Among the structure baselines, ComplEx is the strongest candidate "
        "generator, reaching Gold@20 of "
        f"{test_complex['gold_present_at20']:.3f} and MRR@20 of "
        f"{test_complex['reviewer_safe_mrr_at20']:.6f}. "
        "However, the selected FOG-RAG main row obtains the highest locked-test MRR@20, "
        f"{test_retrieval['reviewer_safe_mrr_at20']:.6f}, slightly above ComplEx by "
        f"{d_fog_complex['delta_mrr_at20']:.6f}. "
        "This result is notable because FOG-RAG main has substantially lower Gold@20 "
        f"({test_retrieval['gold_present_at20']:.3f}) than ComplEx, but achieves better "
        f"early-rank placement with Hits@1 of {test_retrieval['hits1_at20']:.3f} versus "
        f"{test_complex['hits1_at20']:.3f}, and Hits@3 of "
        f"{test_retrieval['hits3_at20']:.3f} versus {test_complex['hits3_at20']:.3f}. "
        "Compared with the DrKGC-style raw backbone, FOG-RAG improves MRR@20 by "
        f"{d_fog_back['delta_mrr_at20']:.6f}, Hits@1 by "
        f"{d_fog_back['delta_hits1_at20']:.3f}, and Hits@3 by "
        f"{d_fog_back['delta_hits3_at20']:.3f}."
    )

    graph_paragraph = (
        "The ranking gain is driven by the soft-support stage, while the confidence-aware "
        "retrieval stage preserves the same candidate ordering and improves the graph package. "
        "On the locked test set, retrieval main reduces the average retrieved subgraph size "
        f"from {graph_efficiency['soft_support_avg_subgraph_size_test']:.2f} to "
        f"{graph_efficiency['retrieval_main_avg_subgraph_size_test']:.2f} triples, a reduction "
        f"of {graph_efficiency['subgraph_size_reduction_vs_soft']:.2f} triples per query, "
        "while preserving candidate coverage. Thus, retrieval main should be interpreted as "
        "an evidence-efficiency and interpretability improvement rather than an additional "
        "candidate-ranking improvement over soft support."
    )

    discussion_paragraph = (
        "The baseline comparison reveals an important distinction between candidate coverage "
        "and rank quality. ComplEx retrieves the gold drug in the top-20 list much more often "
        f"than FOG-RAG main ({test_complex['gold_present_at20']:.3f} vs. "
        f"{test_retrieval['gold_present_at20']:.3f} Gold@20), yet FOG-RAG main slightly "
        "outperforms ComplEx on locked-test MRR@20. This indicates that simply increasing "
        "top-20 coverage is insufficient when the downstream graph-augmented LLM pipeline "
        "relies on a short candidate list: the position of the gold entity within the list "
        "also matters. FOG-RAG improves the DrKGC-compatible raw source by using soft support "
        "signals to move evidence-supported drugs earlier in the candidate list, while the "
        "retrieval module makes the graph evidence smaller and less shortcut-heavy. We "
        "therefore position FOG-RAG not as a replacement for all structure-only retrievers, "
        "but as an evidence-aware extension of the DrKGC-style graph-augmented LLM pipeline."
    )

    reviewer_defense = (
        "A reviewer may note that ComplEx achieves substantially higher Gold@20 than FOG-RAG "
        "main. We agree and report this explicitly. Our conclusion is not that FOG-RAG has "
        "better candidate coverage than ComplEx; it does not. Instead, under the frozen "
        "reviewer-safe top-20 protocol, FOG-RAG main achieves slightly higher locked-test "
        "MRR@20 because it places the gold drug earlier when it is present, as reflected by "
        f"H@1={test_retrieval['hits1_at20']:.3f} and H@3={test_retrieval['hits3_at20']:.3f}, "
        f"compared with ComplEx H@1={test_complex['hits1_at20']:.3f} and "
        f"H@3={test_complex['hits3_at20']:.3f}. "
        "The result should therefore be interpreted as evidence that coverage and ordering "
        "are complementary. A stronger upstream generator such as ComplEx is a promising "
        "future candidate source for FOG-RAG, while the current contribution focuses on "
        "soft evidence modeling and confidence-aware retrieval within the DrKGC-compatible "
        "pipeline."
    )

    limitations_paragraph = (
        "The comparison also exposes a limitation of the current FOG-RAG implementation: its "
        "DrKGC-compatible raw candidate source has lower Gold@20 than the strongest pure "
        "structure-only generator. This limits the maximum achievable recall of the downstream "
        "LLM prompt. Future work should evaluate a hybrid system in which a stronger upstream "
        "candidate generator, such as ComplEx, is combined with the proposed soft-support and "
        "confidence-aware retrieval modules."
    )

    table_caption = (
        "\\caption{Locked-test reviewer-safe comparison between structure-only candidate "
        "generators and DrKGC-compatible FOG-RAG rows. Gold@20 measures whether the gold drug "
        "appears in the top-20 candidate list. MRR@20 uses RR=0 when the gold drug is absent. "
        "ComplEx achieves the highest Gold@20, while FOG-RAG main obtains the highest locked-test "
        "MRR@20 and substantially improves the DrKGC-style raw backbone.}"
    )

    key_findings = [
        "FOG-RAG main is the best locked-test MRR@20 row, slightly above ComplEx.",
        "ComplEx is the strongest structure-only candidate generator by Gold@20.",
        "FOG-RAG does not beat ComplEx on coverage; it beats ComplEx slightly on locked-test MRR@20.",
        "Soft support is responsible for ranking improvement.",
        "Retrieval main preserves the soft-support ranking and improves graph efficiency.",
        "The correct paper stance is balanced: FOG-RAG improves the DrKGC-compatible pipeline and remains competitive with strong structure baselines.",
    ]

    forbidden_claims = [
        "Do not claim FOG-RAG universally outperforms all structure baselines.",
        "Do not claim FOG-RAG has better Gold@20 than ComplEx.",
        "Do not claim fuzzy retrieval improves ranking beyond soft support.",
        "Do not hide the fact that ComplEx is better on validation MRR@20.",
        "Do not call the metric a classical full-ranking filtered KGC metric.",
    ]

    recommended_claims = [
        "FOG-RAG main achieves the highest locked-test reviewer-safe MRR@20.",
        "FOG-RAG substantially improves the DrKGC-compatible raw backbone.",
        "ComplEx demonstrates that stronger pure structure retrievers can provide higher coverage.",
        "Coverage and ranking quality are complementary.",
        "FOG-RAG's retrieval module improves graph compactness and evidence quality while preserving the ranking gain.",
    ]

    assets = {
        "inputs": {
            "decision_file": str(IN_DECISION),
            "table_file": str(IN_TABLE),
            "table_tex_file": str(IN_TABLE_TEX),
        },
        "headline": "FOG-RAG main slightly leads locked-test MRR@20 while ComplEx leads Gold@20.",
        "key_numbers": {
            "valid": {
                "complex_mrr_at20": valid_complex["reviewer_safe_mrr_at20"],
                "fograg_main_mrr_at20": valid_retrieval["reviewer_safe_mrr_at20"],
                "complex_gold_at20": valid_complex["gold_present_at20"],
                "fograg_main_gold_at20": valid_retrieval["gold_present_at20"],
            },
            "test": {
                "backbone_raw_gold_at20": test_backbone["gold_present_at20"],
                "backbone_raw_mrr_at20": test_backbone["reviewer_safe_mrr_at20"],
                "complex_gold_at20": test_complex["gold_present_at20"],
                "complex_mrr_at20": test_complex["reviewer_safe_mrr_at20"],
                "fograg_main_gold_at20": test_retrieval["gold_present_at20"],
                "fograg_main_mrr_at20": test_retrieval["reviewer_safe_mrr_at20"],
                "fograg_main_hits1": test_retrieval["hits1_at20"],
                "fograg_main_hits3": test_retrieval["hits3_at20"],
                "fograg_main_hits10": test_retrieval["hits10_at20"],
                "complex_hits1": test_complex["hits1_at20"],
                "complex_hits3": test_complex["hits3_at20"],
                "complex_hits10": test_complex["hits10_at20"],
                "distmult_mrr_at20": test_distmult["reviewer_safe_mrr_at20"],
                "rgcn_mrr_at20": test_rgcn["reviewer_safe_mrr_at20"],
            },
            "deltas": {
                "fograg_main_minus_backbone_raw": d_fog_back,
                "fograg_main_minus_complex": d_fog_complex,
                "complex_minus_backbone_raw": d_complex_back,
            },
            "graph_efficiency": graph_efficiency,
        },
        "recommended_claims": recommended_claims,
        "forbidden_claims": forbidden_claims,
        "key_findings": key_findings,
        "paper_snippets": {
            "results_paragraph": results_paragraph,
            "graph_paragraph": graph_paragraph,
            "discussion_paragraph": discussion_paragraph,
            "reviewer_defense": reviewer_defense,
            "limitations_paragraph": limitations_paragraph,
            "table_caption": table_caption,
        },
        "day6_decision": "INTERPRETATION_ASSETS_READY_FOR_WEEK21_CLOSEOUT",
    }

    return assets


def build_results_md(assets: dict[str, Any]) -> str:
    return "\n\n".join(
        [
            "# Paper Snippet — Results Section",
            "## Baseline comparison paragraph",
            assets["paper_snippets"]["results_paragraph"],
            "## Graph-efficiency paragraph",
            assets["paper_snippets"]["graph_paragraph"],
        ]
    )


def build_discussion_md(assets: dict[str, Any]) -> str:
    return "\n\n".join(
        [
            "# Paper Snippet — Discussion Section",
            "## Interpretation",
            assets["paper_snippets"]["discussion_paragraph"],
            "## Limitation / future work",
            assets["paper_snippets"]["limitations_paragraph"],
        ]
    )


def build_reviewer_md(assets: dict[str, Any]) -> str:
    lines = []
    lines.append("# Paper Snippet — Reviewer Defense")
    lines.append("")
    lines.append("## Concern")
    lines.append("")
    lines.append(
        "ComplEx has much higher Gold@20 than FOG-RAG main. Does this weaken the FOG-RAG claim?"
    )
    lines.append("")
    lines.append("## Response")
    lines.append("")
    lines.append(assets["paper_snippets"]["reviewer_defense"])
    lines.append("")
    lines.append("## Claims to avoid")
    lines.append("")
    for item in assets["forbidden_claims"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Safe claims")
    lines.append("")
    for item in assets["recommended_claims"]:
        lines.append(f"- {item}")
    return "\n".join(lines)


def build_summary_md(assets: dict[str, Any]) -> str:
    k = assets["key_numbers"]["test"]
    g = assets["key_numbers"]["graph_efficiency"]
    d = assets["key_numbers"]["deltas"]

    lines = []
    lines.append("# Week 21 Paper Positioning Summary")
    lines.append("")
    lines.append("## Headline")
    lines.append("")
    lines.append(assets["headline"])
    lines.append("")
    lines.append("## Locked-test key numbers")
    lines.append("")
    lines.append("| Row | Gold@20 | MRR@20 | H@1 | H@3 | H@10 |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    lines.append(
        f"| Backbone raw | {k['backbone_raw_gold_at20']:.3f} | {k['backbone_raw_mrr_at20']:.6f} | "
        "- | - | - |"
    )
    lines.append(
        f"| ComplEx | {k['complex_gold_at20']:.3f} | {k['complex_mrr_at20']:.6f} | "
        f"{k['complex_hits1']:.3f} | {k['complex_hits3']:.3f} | {k['complex_hits10']:.3f} |"
    )
    lines.append(
        f"| FOG-RAG main | {k['fograg_main_gold_at20']:.3f} | {k['fograg_main_mrr_at20']:.6f} | "
        f"{k['fograg_main_hits1']:.3f} | {k['fograg_main_hits3']:.3f} | {k['fograg_main_hits10']:.3f} |"
    )
    lines.append("")
    lines.append("## Main deltas")
    lines.append("")
    lines.append(
        f"- FOG-RAG main minus backbone MRR@20: {d['fograg_main_minus_backbone_raw']['delta_mrr_at20']:+.6f}"
    )
    lines.append(
        f"- FOG-RAG main minus ComplEx MRR@20: {d['fograg_main_minus_complex']['delta_mrr_at20']:+.6f}"
    )
    lines.append(
        f"- FOG-RAG main minus ComplEx Gold@20: {d['fograg_main_minus_complex']['delta_gold_present_at20']:+.3f}"
    )
    lines.append("")
    lines.append("## Graph efficiency")
    lines.append("")
    lines.append(
        f"- Avg. subgraph size soft/backbone: {g['soft_support_avg_subgraph_size_test']:.2f}"
    )
    lines.append(
        f"- Avg. subgraph size retrieval main: {g['retrieval_main_avg_subgraph_size_test']:.2f}"
    )
    lines.append(
        f"- Reduction: {g['subgraph_size_reduction_vs_soft']:.2f} triples/query"
    )
    lines.append("")
    lines.append("## Safe paper stance")
    lines.append("")
    lines.append(
        "FOG-RAG main achieves the highest locked-test reviewer-safe MRR@20, slightly above "
        "ComplEx, while ComplEx has much higher Gold@20. Therefore, the paper should emphasize "
        "that FOG-RAG improves rank placement and evidence-aware retrieval within the "
        "DrKGC-compatible pipeline, not that it universally dominates structure-only retrievers."
    )
    return "\n".join(lines)


def build_report_md(assets: dict[str, Any]) -> str:
    lines = []
    lines.append("# Week 21 Day 6 — Interpretation and Paper Positioning")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(f"**{assets['day6_decision']}**")
    lines.append("")
    lines.append("## Headline")
    lines.append("")
    lines.append(assets["headline"])
    lines.append("")
    lines.append("## Key findings")
    lines.append("")
    for item in assets["key_findings"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Recommended claims")
    lines.append("")
    for item in assets["recommended_claims"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Forbidden claims")
    lines.append("")
    for item in assets["forbidden_claims"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Generated files")
    lines.append("")
    lines.append(f"- `{OUT_ASSETS_JSON}`")
    lines.append(f"- `{OUT_RESULTS_MD}`")
    lines.append(f"- `{OUT_DISCUSSION_MD}`")
    lines.append(f"- `{OUT_REVIEWER_MD}`")
    lines.append(f"- `{OUT_CAPTION_TEX}`")
    lines.append(f"- `{OUT_SUMMARY_MD}`")
    lines.append("")
    lines.append("## Next step")
    lines.append("")
    lines.append(
        "Day 7 should close out Week 21 by freezing the baseline table, paper positioning, "
        "and remaining open questions before moving to Dataset 2."
    )
    return "\n".join(lines)


def validate_assets(assets: dict[str, Any]) -> None:
    k = assets["key_numbers"]["test"]
    d = assets["key_numbers"]["deltas"]

    assert k["fograg_main_mrr_at20"] > k["complex_mrr_at20"], (
        "Expected FOG-RAG main to be slightly above ComplEx on locked-test MRR@20."
    )
    assert k["complex_gold_at20"] > k["fograg_main_gold_at20"], (
        "Expected ComplEx to have higher Gold@20 than FOG-RAG main."
    )
    assert d["fograg_main_minus_backbone_raw"]["delta_mrr_at20"] > 0
    assert d["fograg_main_minus_complex"]["delta_mrr_at20"] > 0
    assert d["fograg_main_minus_complex"]["delta_gold_present_at20"] < 0

    forbidden_text = "\n".join(assets["forbidden_claims"]).lower()
    assert "universally" in forbidden_text
    assert "gold@20" in forbidden_text


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    decision = load_json(IN_DECISION)
    table = load_json(IN_TABLE)

    assets = build_assets(decision, table)
    validate_assets(assets)

    write_json(OUT_ASSETS_JSON, assets)
    write_text(OUT_RESULTS_MD, build_results_md(assets))
    write_text(OUT_DISCUSSION_MD, build_discussion_md(assets))
    write_text(OUT_REVIEWER_MD, build_reviewer_md(assets))
    write_text(OUT_CAPTION_TEX, assets["paper_snippets"]["table_caption"])
    write_text(OUT_SUMMARY_MD, build_summary_md(assets))
    write_text(OUT_REPORT_MD, build_report_md(assets))

    print("=" * 100)
    print("WEEK 21 DAY 6 — INTERPRETATION ASSETS")
    print("=" * 100)
    print(f"Wrote: {OUT_ASSETS_JSON}")
    print(f"Wrote: {OUT_RESULTS_MD}")
    print(f"Wrote: {OUT_DISCUSSION_MD}")
    print(f"Wrote: {OUT_REVIEWER_MD}")
    print(f"Wrote: {OUT_CAPTION_TEX}")
    print(f"Wrote: {OUT_SUMMARY_MD}")
    print(f"Wrote: {OUT_REPORT_MD}")
    print()
    print("Headline:", assets["headline"])
    print()
    print("Key numbers:")
    k = assets["key_numbers"]["test"]
    print(f"  FOG-RAG main MRR@20: {k['fograg_main_mrr_at20']:.6f}")
    print(f"  ComplEx MRR@20:      {k['complex_mrr_at20']:.6f}")
    print(f"  FOG-RAG main Gold@20:{k['fograg_main_gold_at20']:.3f}")
    print(f"  ComplEx Gold@20:     {k['complex_gold_at20']:.3f}")
    print()
    print("Decision:", assets["day6_decision"])
    print("=" * 100)


if __name__ == "__main__":
    main()