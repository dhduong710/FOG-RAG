from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(".").resolve()

COMPARE_PATH = ROOT / "results/week17/encoder_probe_compare.json"
CASE_PATH = ROOT / "results/week17/encoder_case_samples.json"

OUT_JSON = ROOT / "results/week17/encoder_freeze_report.json"
OUT_MD = ROOT / "reports/week17/day6_freeze_or_defer.md"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def decide(compare: dict, cases: dict) -> dict:
    m_ret = compare["metrics"]["soft_support_fuzzy_retrieval_main"]
    m_probe = compare["metrics"]["soft_support_fuzzy_encoder_probe_v0"]
    comp = compare["probe_vs_retrieval_main"]
    buckets = cases["bucket_counts"]

    reasons = []
    positives = []
    cautions = []

    # positive signals
    if comp["improved_vs_retrieval_main"] > 0:
        positives.append(f"Probe improves {comp['improved_vs_retrieval_main']} cases over retrieval main.")
    if buckets["same_rank_but_better_graph_signal"] > 0:
        positives.append(
            f"There are {buckets['same_rank_but_better_graph_signal']} same-rank cases with possibly better graph signal."
        )

    # negative signals
    if m_probe["mrr_like"] < m_ret["mrr_like"]:
        reasons.append(
            f"MRR-like drops from {m_ret['mrr_like']} to {m_probe['mrr_like']}."
        )
    if m_probe["hits1_like"] < m_ret["hits1_like"]:
        reasons.append(
            f"Hits@1-like drops from {m_ret['hits1_like']} to {m_probe['hits1_like']}."
        )
    if m_probe["avg_gold_rank"] > m_ret["avg_gold_rank"]:
        reasons.append(
            f"Average gold rank worsens from {m_ret['avg_gold_rank']} to {m_probe['avg_gold_rank']}."
        )
    if comp["worsened_vs_retrieval_main"] > comp["improved_vs_retrieval_main"]:
        reasons.append(
            f"Worsened cases ({comp['worsened_vs_retrieval_main']}) exceed improved cases ({comp['improved_vs_retrieval_main']})."
        )
    if comp["avg_rank_delta_probe_minus_retrieval"] > 0:
        reasons.append(
            f"Average probe-minus-retrieval rank delta is positive ({comp['avg_rank_delta_probe_minus_retrieval']})."
        )
    if m_probe["avg_bridge_norm"] < 0.05:
        reasons.append(
            f"Average bridge_norm is too low ({m_probe['avg_bridge_norm']}), suggesting sparse bridge signal."
        )
    if buckets["anchor_caution_cases"] >= 100:
        reasons.append(
            f"Anchor caution cases are high ({buckets['anchor_caution_cases']})."
        )

    # cautions
    if comp["same_top1_rate_vs_retrieval_main"] < 0.5:
        cautions.append(
            f"Probe is not redundant with retrieval main (same_top1_rate={comp['same_top1_rate_vs_retrieval_main']})."
        )
    if buckets["same_rank_but_better_graph_signal"] > buckets["probe_redundant_cases"]:
        cautions.append(
            "There may still be some graph-side value, but it is not enough to justify promotion."
        )

    # hard decision
    if (
        m_probe["mrr_like"] < m_ret["mrr_like"]
        and comp["worsened_vs_retrieval_main"] > comp["improved_vs_retrieval_main"]
        and m_probe["avg_bridge_norm"] < 0.05
    ):
        decision = "DEFER_ENCODER"
        week18_mode = "do_not_open_full_encoder_stage"
    else:
        decision = "CONDITIONAL_REDESIGN"
        week18_mode = "encoder_redesign_only_if_explicitly_planned"

    return {
        "decision": decision,
        "week18_recommendation": week18_mode,
        "main_row_status": {
            "keep_retrieval_main_as_current_best_row": True,
            "promote_encoder_probe_to_main_row": False,
            "treat_probe_as_supporting_readiness_result": True,
        },
        "positive_signals": positives,
        "negative_reasons": reasons,
        "cautions": cautions,
        "retrieval_main_metrics": m_ret,
        "encoder_probe_metrics": m_probe,
        "probe_vs_retrieval_main": comp,
        "bucket_counts": buckets,
        "next_step_recommendations": [
            "Keep soft_support_fuzzy_retrieval_main as the strongest frozen row.",
            "Do not promote encoder probe v0 to a main row.",
            "Use week 17 as evidence that encoder readiness was checked in a controlled way.",
            "If encoder is revisited later, redesign bridge signal first instead of opening full training immediately.",
        ],
    }


def main():
    compare = load_json(COMPARE_PATH)
    cases = load_json(CASE_PATH)

    report = {
        "week": 17,
        "day": 6,
        "mode": "freeze_or_defer",
        "source_files": {
            "compare": str(COMPARE_PATH.relative_to(ROOT)),
            "cases": str(CASE_PATH.relative_to(ROOT)),
        },
        "result": decide(compare, cases),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    r = report["result"]

    lines = []
    lines.append("# Week 17 Day 6 — Freeze or Defer\n")
    lines.append("## Decision")
    lines.append(f"- **{r['decision']}**")
    lines.append(f"- Week-18 recommendation: `{r['week18_recommendation']}`")
    lines.append("")
    lines.append("## Main row status")
    for k, v in r["main_row_status"].items():
        lines.append(f"- **{k}**: `{v}`")
    lines.append("")
    lines.append("## Negative reasons")
    for item in r["negative_reasons"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Positive signals")
    for item in r["positive_signals"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Cautions")
    for item in r["cautions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Next-step recommendations")
    for item in r["next_step_recommendations"]:
        lines.append(f"- {item}")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote {OUT_JSON}")
    print(f"[OK] wrote {OUT_MD}")
    print(json.dumps(report["result"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()