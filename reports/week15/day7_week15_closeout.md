# Week 15 Closeout

## Decision
- **GO**

## Main rows
- Main input row: `soft_support_raw`
- Main output row: `soft_support_fuzzy_retrieval_v1`
- Reference row: `backbone_raw`
- Negative control: `ontology_raw`

## Main findings
- avg_subgraph_size: 60.45 -> 36.714
- avg_triple_score (fuzzy only): 0.440709
- direct_shortcut_path_rate: 0.184775 -> 0.129513
- shortcut_gain_vs_soft_support: 0.055262
- candidate_coverage_preserved_rate: 1.0
- mrr_like: 0.097644 -> 0.097644
- hits1_like: 0.056 -> 0.056
- avg_gold_rank: 17.676 -> 17.676

## Interpretation
- Retrieval v1 clearly improves evidence cleanliness.
- Retrieval v1 does not add extra ranking gain over soft_support_raw yet, but it also does not collapse ranking-like proxy.
- The dominant remaining failure mode is raw / candidate bottleneck rather than retrieval breakage.

## Case review summary
{
  "preserved_improvement_vs_backbone": 80,
  "same_rank_cleaner_subgraph": 251,
  "unchanged_bad": 415,
  "raw_bottleneck_failure": 407,
  "improved_vs_soft_support": 0,
  "worsened_vs_soft_support": 0
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

## GO checks
{
  "valid_fuzzy_retrieval_v1_built_cleanly": true,
  "shortcut_noise_reduced_vs_soft_support": true,
  "ranking_like_proxy_not_collapsed": true,
  "case_review_supports_cleaner_subgraph": true
}

## Week 16 recommendation
{
  "theme": "retrieval_sweep_and_main_row_selection",
  "main_goal": "select or refine the main retrieval-stage row on valid before any encoder-stage expansion",
  "do_not_do": [
    "do_not_change_raw_source",
    "do_not_reopen_candidate_stage",
    "do_not_jump_to_encoder_without_retrieval_selection",
    "do_not_run_test_yet"
  ]
}