# Week 16 Closeout

## Decision
- **GO**

## Main rows
- Main input row: `soft_support_raw`
- Main output row: `soft_support_fuzzy_retrieval_main`
- Selected source variant: `soft_support_fuzzy_retrieval_tight`
- Reference retrieval row: `soft_support_fuzzy_retrieval_v1`

## Main findings
- mrr_like: 0.097644
- hits1_like: 0.056
- hits3_like: 0.134
- hits10_like: 0.182
- avg_gold_rank: 17.676
- avg_subgraph_size: 32.556
- avg_triple_score: 0.499203
- direct_shortcut_path_rate: 0.105536
- candidate_coverage_preserved_rate: 1.0

## Comparison summary
{
  "vs_soft_support_raw": {
    "mrr_like_delta": 0.0,
    "avg_gold_rank_delta": 0.0,
    "shortcut_gain": 0.079239,
    "subgraph_size_gain": 27.894,
    "avg_query_touch_count_delta": -15.68,
    "avg_non_direct_query_touch_count_delta": -8.728
  },
  "vs_v1": {
    "mrr_like_delta": 0.0,
    "avg_gold_rank_delta": 0.0,
    "shortcut_gain": 0.023977,
    "subgraph_size_gain": 4.158,
    "avg_query_touch_count_delta": -1.556,
    "avg_non_direct_query_touch_count_delta": -0.04
  }
}

## Case review support
{
  "tight_same_rank_cleaner_than_v1": 217,
  "tight_preserved_backbone_gain": 80,
  "tight_anchor_caution_same_rank": 13,
  "directplus_redundant_vs_v1": 373,
  "raw_bottleneck_failure": 399
}

## GO checks
{
  "retrieval_main_row_selected": true,
  "retrieval_main_row_frozen_cleanly": true,
  "ranking_like_proxy_not_collapsed_vs_soft_support": true,
  "main_row_beats_v1_on_retrieval_tradeoff": true
}

## Week 17 recommendation
{
  "mode": "encoder_readiness_check",
  "main_goal": "evaluate whether retrieval is stable enough to justify a careful encoder-stage entry",
  "do_not_do": [
    "do_not_change_raw_source",
    "do_not_reopen_candidate_stage",
    "do_not_run_test_yet",
    "do_not_commit_to_encoder_without_a_day1_readiness_check"
  ]
}