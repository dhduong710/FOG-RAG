# Week 16 - Day 6 Freeze and Bridge

## Selected main retrieval row
- canonical_row_name: `soft_support_fuzzy_retrieval_main`
- selected_source_variant: `soft_support_fuzzy_retrieval_tight`

## Freeze checks
{
  "selected_main_row_exists": true,
  "main_row_has_500_rows": true,
  "ranking_like_proxy_not_collapsed_vs_soft_support": true,
  "candidate_coverage_preserved": true,
  "main_beats_v1_on_tradeoff": true
}

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

## Recommended action
- `freeze_retrieval_main`
- The selected main retrieval row preserves ranking-like proxy, reduces shortcut-heavy evidence more than v1, and keeps full candidate coverage.

## Remaining failure modes
- raw_candidate_bottleneck
- weak_evidence_cases
- small_anchor_caution_bucket

## Week 17 bridge recommendation
{
  "mode": "encoder_readiness_check_but_not_commit_yet",
  "main_goal": "decide whether retrieval is stable enough to support an encoder-stage entry",
  "do_not_do": [
    "do_not_change_raw_source",
    "do_not_reopen_candidate_stage",
    "do_not_run_test_yet",
    "do_not_commit_to_encoder_without_week16_closeout"
  ]
}