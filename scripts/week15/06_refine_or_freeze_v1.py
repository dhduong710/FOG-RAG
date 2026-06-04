from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]

DAY2_SUMMARY = ROOT / "results/week15/path_feature_summary.json"
DAY3_MANIFEST = ROOT / "dataset/setting_a/27_n2_fuzzy_retrieval/path_score_manifest.json"
DAY4_COMPARE = ROOT / "results/week15/retrieval_valid_compare_v1.json"
DAY5_CASES = ROOT / "results/week15/retrieval_case_samples_v1.json"

FEATURE_PATH = ROOT / "dataset/setting_a/27_n2_fuzzy_retrieval/valid_path_features.json"
FUZZY_PATH = ROOT / "dataset/setting_a/27_n2_fuzzy_retrieval/valid_fuzzy_retrieval_v1.json"

OUT_JSON = ROOT / "results/week15/path_score_report_v1.json"
OUT_REPORT = ROOT / "reports/week15/day6_refine_or_freeze.md"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def safe_rate(num: float, den: float) -> float | None:
    if den == 0:
        return None
    return round(num / den, 6)


def main() -> None:
    day2 = load_json(DAY2_SUMMARY)
    day3 = load_json(DAY3_MANIFEST)
    day4 = load_json(DAY4_COMPARE)
    day5 = load_json(DAY5_CASES)

    feature_rows = load_json(FEATURE_PATH)
    fuzzy_rows = load_json(FUZZY_PATH)

    assert len(feature_rows) == len(fuzzy_rows) == 500, "feature_rows and fuzzy_rows must both have 500 rows"

    # ------------------------------------------------------------------
    # Anchor diagnostics: query-touch / non-direct query-touch before/after
    # ------------------------------------------------------------------
    total_orig_query_touch = 0
    total_sel_query_touch = 0
    total_orig_non_direct_query_touch = 0
    total_sel_non_direct_query_touch = 0

    rows_with_orig_query_touch = 0
    rows_with_sel_query_touch = 0
    rows_with_orig_non_direct_query_touch = 0
    rows_with_sel_non_direct_query_touch = 0

    for feat_row, fuzzy_row in zip(feature_rows, fuzzy_rows):
        orig_rows = feat_row["triple_feature_rows"]
        sel_rows = fuzzy_row["triple_score_rows"]

        orig_q = sum(bool(tr.get("touches_query", False)) for tr in orig_rows)
        sel_q = sum(bool(tr.get("touches_query", False)) for tr in sel_rows)

        orig_q_non_direct = sum(
            bool(tr.get("touches_query", False)) and not bool(tr.get("direct_candidate_query_flag", False))
            for tr in orig_rows
        )
        sel_q_non_direct = sum(
            bool(tr.get("touches_query", False)) and not bool(tr.get("direct_candidate_query_flag", False))
            for tr in sel_rows
        )

        total_orig_query_touch += orig_q
        total_sel_query_touch += sel_q
        total_orig_non_direct_query_touch += orig_q_non_direct
        total_sel_non_direct_query_touch += sel_q_non_direct

        if orig_q > 0:
            rows_with_orig_query_touch += 1
        if sel_q > 0:
            rows_with_sel_query_touch += 1
        if orig_q_non_direct > 0:
            rows_with_orig_non_direct_query_touch += 1
        if sel_q_non_direct > 0:
            rows_with_sel_non_direct_query_touch += 1

    anchor_diag = {
        "avg_query_touch_count_before": round(total_orig_query_touch / 500, 6),
        "avg_query_touch_count_after": round(total_sel_query_touch / 500, 6),
        "avg_non_direct_query_touch_count_before": round(total_orig_non_direct_query_touch / 500, 6),
        "avg_non_direct_query_touch_count_after": round(total_sel_non_direct_query_touch / 500, 6),
        "row_has_any_query_touch_before_rate": round(rows_with_orig_query_touch / 500, 6),
        "row_has_any_query_touch_after_rate": round(rows_with_sel_query_touch / 500, 6),
        "row_has_any_non_direct_query_touch_before_rate": round(rows_with_orig_non_direct_query_touch / 500, 6),
        "row_has_any_non_direct_query_touch_after_rate": round(rows_with_sel_non_direct_query_touch / 500, 6),
        "non_direct_query_touch_row_preserved_rate": safe_rate(
            rows_with_sel_non_direct_query_touch,
            rows_with_orig_non_direct_query_touch
        ),
        "notes": [
            "Anchor diagnostics are reported as cautionary evidence only.",
            "They are not used as a hard blocker for week-15 freeze.",
            "Week-15 main objective is cleaner evidence without ranking collapse."
        ]
    }

    # ------------------------------------------------------------------
    # Freeze decision
    # ------------------------------------------------------------------
    fuzzy_metrics = day4["rows"]["soft_support_fuzzy_retrieval_v1"]
    soft_metrics = day4["rows"]["soft_support_raw"]
    delta_fuzzy_vs_soft = day4["delta"]["fuzzy_vs_soft_support"]
    case_level = day4["case_level"]

    shortcut_gain = round(
        soft_metrics["direct_shortcut_path_rate"] - fuzzy_metrics["direct_shortcut_path_rate"],
        6
    )
    coverage = fuzzy_metrics["candidate_coverage_preserved_rate"]
    worsened_vs_soft = case_level["worsened_vs_soft_support"]
    mrr_delta_vs_soft = delta_fuzzy_vs_soft["mrr_like"]

    freeze_checks = {
        "coverage_ok": coverage >= 0.999,
        "shortcut_gain_ok": shortcut_gain >= 0.03,
        "no_worsened_vs_soft": worsened_vs_soft == 0,
        "mrr_not_collapsed": mrr_delta_vs_soft >= -0.001,
    }

    if all(freeze_checks.values()):
        recommended_action = "freeze_v1"
        rationale = (
            "Retrieval v1 reduces shortcut-heavy evidence clearly, preserves candidate coverage, "
            "and does not worsen ranking-like proxy relative to soft_support_raw."
        )
    else:
        recommended_action = "needs_one_small_repair"
        rationale = (
            "At least one of the freeze checks failed, so a small repair would be justified before closeout."
        )

    # ------------------------------------------------------------------
    # Final structured report
    # ------------------------------------------------------------------
    out = {
        "week": 15,
        "day": 6,
        "variant_name": day3["variant_name"],
        "day2_supporting_summary": {
            "avg_subgraph_size_before": day2["avg_subgraph_size"],
            "touch_candidate_rate_before": day2["touch_candidate_rate"],
            "direct_candidate_query_rate_before": day2["direct_candidate_query_rate"],
            "contra_flag_rate_before": day2["contra_flag_rate"],
        },
        "day3_retrieval_build_summary": day3["summary"],
        "day4_compare_summary": {
            "backbone_raw": day4["rows"]["backbone_raw"],
            "soft_support_raw": day4["rows"]["soft_support_raw"],
            "soft_support_fuzzy_retrieval_v1": day4["rows"]["soft_support_fuzzy_retrieval_v1"],
            "delta_fuzzy_vs_soft_support": day4["delta"]["fuzzy_vs_soft_support"],
            "delta_fuzzy_vs_backbone": day4["delta"]["fuzzy_vs_backbone"],
            "case_level": day4["case_level"],
        },
        "day5_bucket_counts": day5["bucket_counts"],
        "anchor_diagnostics": anchor_diag,
        "freeze_checks": freeze_checks,
        "shortcut_gain_vs_soft_support": shortcut_gain,
        "recommended_action": recommended_action,
        "rationale": rationale,
        "week15_takeaway": [
            "retrieval v1 cleans the evidence bundle without ranking collapse",
            "the dominant remaining failure mode is raw / candidate bottleneck rather than retrieval breakage",
            "query-anchoring diagnostics should be carried as a caution into week 16, but they do not block week-15 freeze"
        ]
    }

    save_json(OUT_JSON, out)

    report_lines = [
        "# Week 15 - Day 6 Refine or Freeze",
        "",
        f"- variant_name: {out['variant_name']}",
        f"- recommended_action: {out['recommended_action']}",
        f"- rationale: {out['rationale']}",
        "",
        "## Freeze checks",
        json.dumps(out["freeze_checks"], ensure_ascii=False, indent=2),
        "",
        f"- shortcut_gain_vs_soft_support: {out['shortcut_gain_vs_soft_support']}",
        "",
        "## Day 5 bucket counts",
        json.dumps(out["day5_bucket_counts"], ensure_ascii=False, indent=2),
        "",
        "## Anchor diagnostics",
        json.dumps(out["anchor_diagnostics"], ensure_ascii=False, indent=2),
        "",
        "## Week-15 takeaway",
        "\n".join([f"- {x}" for x in out["week15_takeaway"]]),
    ]
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print("=" * 80)
    print("DAY 6 REFINE/FREEZE REPORT BUILT")
    print("json  :", OUT_JSON)
    print("report:", OUT_REPORT)
    print("=" * 80)
    print(json.dumps({
        "recommended_action": out["recommended_action"],
        "freeze_checks": out["freeze_checks"],
        "shortcut_gain_vs_soft_support": out["shortcut_gain_vs_soft_support"],
        "day5_bucket_counts": out["day5_bucket_counts"],
        "anchor_diagnostics": out["anchor_diagnostics"],
    }, ensure_ascii=False, indent=2))
    print("=" * 80)


if __name__ == "__main__":
    main()