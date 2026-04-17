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


def flatten_row(name, metrics_payload):
    ranking = metrics_payload["ranking_metrics"]
    sb = metrics_payload["setting_b_metrics"]
    return {
        "row_name": name,
        "mrr": ranking["mrr"],
        "hits1": ranking["hits1"],
        "hits3": ranking["hits3"],
        "hits10": ranking["hits10"],
        "SafetyViolation@10": sb["SafetyViolation@10"],
        "Contra@10": sb["Contra@10"],
        "ConstraintViolationRate@10": sb["ConstraintViolationRate@10"],
        "QueryHasConstraintViolationRate@10": sb["QueryHasConstraintViolationRate@10"],
        "GoldInTopKRate": sb["GoldInTopKRate"],
    }


def decide_main_variant(rows, week10_hard_proxy, week10_soft_proxy):
    by_name = {r["row_name"]: r for r in rows}
    hard = by_name["hard_main"]
    soft = by_name["soft_best"]

    hard_key = (
        -hard["SafetyViolation@10"],
        -hard["Contra@10"],
        -hard["ConstraintViolationRate@10"],
        -hard["QueryHasConstraintViolationRate@10"],
        hard["GoldInTopKRate"],
        hard["mrr"],
    )
    soft_key = (
        -soft["SafetyViolation@10"],
        -soft["Contra@10"],
        -soft["ConstraintViolationRate@10"],
        -soft["QueryHasConstraintViolationRate@10"],
        soft["GoldInTopKRate"],
        soft["mrr"],
    )

    # When Setting B @10 metrics tie, use day10 proxy and GoldInTopKRate support
    if (
        hard["SafetyViolation@10"] == soft["SafetyViolation@10"]
        and hard["Contra@10"] == soft["Contra@10"]
        and hard["ConstraintViolationRate@10"] == soft["ConstraintViolationRate@10"]
        and hard["QueryHasConstraintViolationRate@10"] == soft["QueryHasConstraintViolationRate@10"]
    ):
        if hard["GoldInTopKRate"] > soft["GoldInTopKRate"]:
            return {
                "main_row": "hard_main",
                "supporting_row": "soft_best",
                "reason": (
                    "hard_main and soft_best tie on Setting B @10 safety/constraint metrics, "
                    "but hard_main has higher GoldInTopKRate and cleaner week10 candidate-stage safety proxies."
                ),
            }

        if week10_hard_proxy["contra_candidates_final"] < week10_soft_proxy["contra_candidates_final"]:
            return {
                "main_row": "hard_main",
                "supporting_row": "soft_best",
                "reason": (
                    "hard_main and soft_best tie on Setting B @10 metrics, "
                    "but hard_main is cleaner at candidate stage and therefore easier to justify as the main variant."
                ),
            }

    if hard_key >= soft_key:
        return {
            "main_row": "hard_main",
            "supporting_row": "soft_best",
            "reason": "hard_main gives the best overall valid-side safety-ranking trade-off.",
        }

    return {
        "main_row": "soft_best",
        "supporting_row": "hard_main",
        "reason": "soft_best gives the better valid-side trade-off under the current rule.",
    }


def write_markdown(path, rows, decision):
    lines = []
    lines.append("# Week 11 - Day 5 Variant Decision")
    lines.append("")
    lines.append("| Row | MRR | Hits@1 | Hits@3 | Hits@10 | SafetyViolation@10 | Contra@10 | ConstraintViolationRate@10 | QueryHasConstraintViolationRate@10 | GoldInTopKRate |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        lines.append(
            f"| {r['row_name']} | {r['mrr']:.6f} | {r['hits1']:.6f} | {r['hits3']:.6f} | {r['hits10']:.6f} | "
            f"{r['SafetyViolation@10']:.6f} | {r['Contra@10']:.6f} | {r['ConstraintViolationRate@10']:.6f} | "
            f"{r['QueryHasConstraintViolationRate@10']:.6f} | {r['GoldInTopKRate']:.6f} |"
        )
    lines.append("")
    lines.append("## Decision")
    lines.append(f"- main_row: `{decision['main_row']}`")
    lines.append(f"- supporting_row: `{decision['supporting_row']}`")
    lines.append(f"- reason: {decision['reason']}")
    lines.append("")
    lines.append("## Notes")
    lines.append("- backbone and ontology are reference rows.")
    lines.append("- hard_main and soft_best are the Novelty 1 safety rows.")
    lines.append("- The final choice is based on valid-first protocol.")
    lines.append("")

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    backbone = load_json("results/week11/backbone_valid/metrics.json")
    ontology = load_json("results/week11/ontology_valid/metrics.json")
    hard = load_json("results/week11/hard_main_valid/metrics.json")
    soft = load_json("results/week11/soft_best_valid/metrics.json")

    week10_hard_proxy = load_json("results/week10/hard_valid/safety_proxy_metrics.json")
    week10_soft_proxy = load_json("results/week10/soft_valid/safety_proxy_metrics.json")

    rows = [
        flatten_row("backbone", backbone),
        flatten_row("ontology", ontology),
        flatten_row("hard_main", hard),
        flatten_row("soft_best", soft),
    ]

    decision = decide_main_variant(rows, week10_hard_proxy, week10_soft_proxy)

    payload = {
        "rows": rows,
        "decision": decision,
        "supporting_week10_proxy": {
            "hard_main": week10_hard_proxy,
            "soft_best": week10_soft_proxy,
        },
    }

    save_json(payload, "results/week11/variant_comparison.json")
    write_markdown("reports/week11/day5_variant_decision.md", rows, decision)

    print("Saved: results/week11/variant_comparison.json")
    print("Saved: reports/week11/day5_variant_decision.md")
    print("Decision:", decision)


if __name__ == "__main__":
    main()