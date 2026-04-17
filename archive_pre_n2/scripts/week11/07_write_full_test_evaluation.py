#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def fmt(x):
    if isinstance(x, float):
        return f"{x:.6f}"
    return str(x)


def main():
    variant_test = load_json("results/week11_test/variant_comparison_test.json")

    rows = variant_test["rows"]
    decision = variant_test["decision"]

    by_name = {r["row_name"]: r for r in rows}

    # Main test ablation payload
    payload = {
        "title": "Novelty 1 full test evaluation",
        "rows": rows,
        "decision": decision,
        "main_takeaways": [
            "hard_main is the best overall test-time trade-off row for Novelty 1.",
            "soft_best remains a useful supporting ablation but does not outperform hard_main.",
            "The test results confirm the valid-side decision and support closing Novelty 1 before moving to Novelty 2.",
        ],
        "paper_use_policy": {
            "main_results_split": "test",
            "validation_split_role": "variant_selection_and_protocol_freeze",
            "main_row": decision["main_row"],
            "supporting_row": decision["supporting_row"],
        },
    }

    save_json(payload, "results/week11_test/ablation_novelty1_test_v1.json")

    # Main markdown table for paper
    md = []
    md.append("# Novelty 1 — Full Test Evaluation")
    md.append("")
    md.append("| Row | MRR | Hits@1 | Hits@3 | Hits@10 | SafetyViolation@10 | Contra@10 | SafetyViolation@final | Contra@final |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        md.append(
            f"| {r['row_name']} | {fmt(r['mrr'])} | {fmt(r['hits1'])} | {fmt(r['hits3'])} | {fmt(r['hits10'])} | "
            f"{fmt(r['SafetyViolation@10'])} | {fmt(r['Contra@10'])} | {fmt(r['SafetyViolation@final'])} | {fmt(r['Contra@final'])} |"
        )
    md.append("")
    md.append("## Decision")
    md.append(f"- main_row: `{decision['main_row']}`")
    md.append(f"- supporting_row: `{decision['supporting_row']}`")
    md.append(f"- reason: {decision['reason']}")
    md.append("")
    md.append("## Main takeaways")
    for x in payload["main_takeaways"]:
        md.append(f"- {x}")
    md.append("")
    md.append("## Note for paper writing")
    md.append("- Test is the official split for final reporting.")
    md.append("- Valid is used for variant selection and protocol freezing.")
    md.append("")
    Path("results/week11_test").mkdir(parents=True, exist_ok=True)
    Path("results/week11_test/ablation_novelty1_test_v1.md").write_text("\n".join(md), encoding="utf-8")

    # Supporting table
    support = []
    support.append("# Novelty 1 — Test Support Table")
    support.append("")
    support.append("| Row | AvgCandidateSize | GoldInFinalListRate | RowsWithContraFinal | SafetyViolation@final | Contra@final |")
    support.append("|---|---:|---:|---:|---:|---:|")
    for r in rows:
        support.append(
            f"| {r['row_name']} | {fmt(r['AvgCandidateSize'])} | {fmt(r['GoldInFinalListRate'])} | "
            f"{fmt(r['RowsWithContraFinal'])} | {fmt(r['SafetyViolation@final'])} | {fmt(r['Contra@final'])} |"
        )
    support.append("")
    support.append("## Interpretation")
    support.append("- backbone is the reference row.")
    support.append("- ontology is the intermediate ablation row.")
    support.append("- hard_main is the cleanest and strongest overall test-time row.")
    support.append("- soft_best is a supporting ablation row, not the final main row.")
    support.append("")
    Path("results/week11_test/novelty1_test_support_table.md").write_text("\n".join(support), encoding="utf-8")

    # Full report
    rpt = []
    rpt.append("# Week 11 - Full Test Evaluation for Novelty 1")
    rpt.append("")
    rpt.append("## 1. Goal")
    rpt.append("Finalize the full test-side evaluation of Novelty 1 and prepare the final closeout.")
    rpt.append("")
    rpt.append("## 2. Final decision")
    rpt.append(f"- main_row: `{decision['main_row']}`")
    rpt.append(f"- supporting_row: `{decision['supporting_row']}`")
    rpt.append(f"- reason: {decision['reason']}")
    rpt.append("")
    rpt.append("## 3. Test rows")
    for r in rows:
        rpt.append(
            f"- {r['row_name']}: MRR={fmt(r['mrr'])}, Hits@10={fmt(r['hits10'])}, "
            f"SafetyViolation@10={fmt(r['SafetyViolation@10'])}, Contra@10={fmt(r['Contra@10'])}, "
            f"SafetyViolation@final={fmt(r['SafetyViolation@final'])}, Contra@final={fmt(r['Contra@final'])}"
        )
    rpt.append("")
    rpt.append("## 4. Main interpretation")
    rpt.append("- The test results confirm the valid-side decision.")
    rpt.append("- hard_main remains the best overall trade-off row for Novelty 1.")
    rpt.append("- soft_best remains useful as a supporting ablation but is not stronger than hard_main.")
    rpt.append("")
    rpt.append("## 5. Paper policy")
    rpt.append("- Use test results as the official main table for Novelty 1.")
    rpt.append("- Use valid results to explain how the row was selected.")
    rpt.append("")
    rpt.append("## 6. Output files")
    rpt.append("- results/week11_test/ablation_novelty1_test_v1.json")
    rpt.append("- results/week11_test/ablation_novelty1_test_v1.md")
    rpt.append("- results/week11_test/novelty1_test_support_table.md")
    rpt.append("")
    Path("reports/week11").mkdir(parents=True, exist_ok=True)
    Path("reports/week11/dayY_full_test_evaluation.md").write_text("\n".join(rpt), encoding="utf-8")

    print("Saved: results/week11_test/ablation_novelty1_test_v1.json")
    print("Saved: results/week11_test/ablation_novelty1_test_v1.md")
    print("Saved: results/week11_test/novelty1_test_support_table.md")
    print("Saved: reports/week11/dayY_full_test_evaluation.md")
    print("Decision:", decision)


if __name__ == "__main__":
    main()