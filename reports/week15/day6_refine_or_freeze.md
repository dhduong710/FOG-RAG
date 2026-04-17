# Week 15 - Day 6 Refine or Freeze

- variant_name: soft_support_fuzzy_retrieval_v1
- recommended_action: freeze_v1
- rationale: Retrieval v1 reduces shortcut-heavy evidence clearly, preserves candidate coverage, and does not worsen ranking-like proxy relative to soft_support_raw.

## Freeze checks
{
  "coverage_ok": true,
  "shortcut_gain_ok": true,
  "no_worsened_vs_soft": true,
  "mrr_not_collapsed": true
}

- shortcut_gain_vs_soft_support: 0.055262

## Day 5 bucket counts
{
  "preserved_improvement_vs_backbone": 80,
  "same_rank_cleaner_subgraph": 251,
  "unchanged_bad": 415,
  "raw_bottleneck_failure": 407
}

## Anchor diagnostics
{
  "avg_query_touch_count_before": 23.854,
  "avg_query_touch_count_after": 9.73,
  "avg_non_direct_query_touch_count_before": 13.85,
  "avg_non_direct_query_touch_count_after": 5.162,
  "row_has_any_query_touch_before_rate": 1.0,
  "row_has_any_query_touch_after_rate": 1.0,
  "row_has_any_non_direct_query_touch_before_rate": 0.974,
  "row_has_any_non_direct_query_touch_after_rate": 0.974,
  "non_direct_query_touch_row_preserved_rate": 1.0,
  "notes": [
    "Anchor diagnostics are reported as cautionary evidence only.",
    "They are not used as a hard blocker for week-15 freeze.",
    "Week-15 main objective is cleaner evidence without ranking collapse."
  ]
}

## Week-15 takeaway
- retrieval v1 cleans the evidence bundle without ranking collapse
- the dominant remaining failure mode is raw / candidate bottleneck rather than retrieval breakage
- query-anchoring diagnostics should be carried as a caution into week 16, but they do not block week-15 freeze